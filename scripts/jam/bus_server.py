#!/usr/bin/env python3
"""bus_server.py — HTTP wrapper for the agent-coordination-bus.

v0.1 enhancement to specs/agent-coordination-bus-v0/: lets multi-machine
teams hit the file-based JSONL bus over HTTP. Authentication via a
shared bearer token (env: BUS_SERVER_TOKEN).

Storage stays file-based (JSONL append-only). HTTP is just transport.
The validator + audit logic come from bus.py — this is a thin shim.

Endpoints:
  GET  /health                 → {"status":"ok","bus_root":"..."}
  POST /messages               → validate + append (bearer auth)
                                  body: full message JSON per
                                  coordination-protocol-v0.md
  GET  /teams/<team-id>        → list messages for a team
  GET  /global                 → global log
  GET  /audit/<team-id>        → append-only audit for a team
  GET  /audit                  → global audit

Auth:
  Authorization: Bearer <token>  required on /messages POST
  GET endpoints are public (read-only) by default — set
  BUS_SERVER_READ_AUTH=required to gate reads too.

Discipline:
  - Same validators as bus.py (refusal-boundary rules enforced)
  - Append-only invariant preserved (HTTP can't bypass storage)
  - No team-token issuance (use the gateway for that; this is just
    HTTP transport for an already-trusted bus root)
  - Stdlib only (matches kit pattern; no FastAPI / uvicorn dependency)

Usage:
  BUS_SERVER_TOKEN=<random> BUS_ROOT=/path/to/bus_root \\
    python3 scripts/jam/bus_server.py --port 8765

  # Read-side gating (optional):
  BUS_SERVER_READ_AUTH=required ... python3 scripts/jam/bus_server.py

Boundary:
  v0.1 transport for a file-based bus. NOT a production agent network.
  NOT certification. Bearer token is a single shared secret — fine for
  development + small jams, NOT for multi-team prod.
"""

import argparse
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote

# Make `jam.bus` importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jam import bus  # noqa: E402


# Global state set at boot
_BUS_ROOT = None
_WRITE_TOKEN = None
_READ_TOKEN_REQUIRED = False


def _json_response(handler, status, body):
    payload = json.dumps(body).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


def _require_bearer(handler) -> bool:
    """Return True if the request is authorized for write. False on
    failure (handler already sent 401)."""
    auth = handler.headers.get("Authorization", "")
    expected = f"Bearer {_WRITE_TOKEN}"
    if auth != expected:
        _json_response(handler, 401, {"error": "unauthorized"})
        return False
    return True


def _require_read_bearer(handler) -> bool:
    """Return True if read is authorized OR read auth not required."""
    if not _READ_TOKEN_REQUIRED:
        return True
    return _require_bearer(handler)


class BusHandler(BaseHTTPRequestHandler):
    """Single dispatching handler. ThreadingHTTPServer parallelizes."""

    # Silence default per-request logging (BaseHTTPRequestHandler is noisy)
    def log_message(self, format, *args):
        if os.environ.get("BUS_SERVER_VERBOSE"):
            super().log_message(format, *args)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health":
            _json_response(self, 200, {
                "status": "ok",
                "bus_root": str(_BUS_ROOT),
                "read_auth_required": _READ_TOKEN_REQUIRED,
            })
            return

        if path == "/global":
            if not _require_read_bearer(self):
                return
            paths = bus.bus_paths(_BUS_ROOT)
            msgs = bus.read_log(paths["global_log"])
            _json_response(self, 200, {"count": len(msgs), "messages": msgs})
            return

        if path == "/audit":
            if not _require_read_bearer(self):
                return
            paths = bus.bus_paths(_BUS_ROOT)
            result = bus.audit_append_only(paths["global_log"])
            _json_response(self, 200, result)
            return

        if path.startswith("/teams/"):
            if not _require_read_bearer(self):
                return
            team_id = unquote(path[len("/teams/"):])
            if not team_id or "/" in team_id or ".." in team_id:
                _json_response(self, 400, {"error": "invalid team_id"})
                return
            paths = bus.bus_paths(_BUS_ROOT)
            team_log = paths["teams_dir"] / f"{team_id}.jsonl"
            msgs = bus.read_log(team_log)
            _json_response(self, 200, {"team_id": team_id, "count": len(msgs), "messages": msgs})
            return

        if path.startswith("/audit/"):
            if not _require_read_bearer(self):
                return
            team_id = unquote(path[len("/audit/"):])
            if not team_id or "/" in team_id or ".." in team_id:
                _json_response(self, 400, {"error": "invalid team_id"})
                return
            paths = bus.bus_paths(_BUS_ROOT)
            team_log = paths["teams_dir"] / f"{team_id}.jsonl"
            result = bus.audit_append_only(team_log)
            _json_response(self, 200, {**result, "team_id": team_id})
            return

        _json_response(self, 404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/messages":
            _json_response(self, 404, {"error": "not found"})
            return

        if not _require_bearer(self):
            return

        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > 256 * 1024:  # 256KB cap
            _json_response(self, 400, {"error": "missing or too-large body"})
            return

        raw = self.rfile.read(length)
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError as e:
            _json_response(self, 400, {"error": f"invalid json: {e}"})
            return

        try:
            bus.append_message(_BUS_ROOT, msg)
        except bus.ValidationError as e:
            _json_response(self, 422, {"error": "validation failed", "detail": str(e)})
            return
        except Exception as e:
            _json_response(self, 500, {"error": f"append failed: {e}"})
            return

        _json_response(self, 200, {
            "ok": True,
            "message_id": msg.get("message_id"),
            "message_type": msg.get("message_type"),
        })


def serve(bus_root: Path, host: str, port: int,
           write_token: str, read_auth_required: bool):
    global _BUS_ROOT, _WRITE_TOKEN, _READ_TOKEN_REQUIRED
    _BUS_ROOT = Path(bus_root)
    _WRITE_TOKEN = write_token
    _READ_TOKEN_REQUIRED = read_auth_required

    # Ensure bus is initialized
    bus.init_bus(_BUS_ROOT)

    httpd = ThreadingHTTPServer((host, port), BusHandler)
    print(f"bus_server listening on http://{host}:{port}  bus_root={_BUS_ROOT}")
    print(f"  POST /messages requires Bearer auth")
    print(f"  Reads {'require' if read_auth_required else 'do not require'} auth")
    return httpd


def main():
    ap = argparse.ArgumentParser(prog="bus_server.py")
    ap.add_argument("--bus-root", default=os.environ.get("BUS_ROOT", "/tmp/bus"),
                    help="bus root directory (env: BUS_ROOT, default: /tmp/bus)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()

    token = os.environ.get("BUS_SERVER_TOKEN")
    if not token:
        print("error: set BUS_SERVER_TOKEN env var", file=sys.stderr)
        sys.exit(2)

    read_auth = os.environ.get("BUS_SERVER_READ_AUTH", "open") == "required"

    httpd = serve(Path(args.bus_root), args.host, args.port, token, read_auth)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
        httpd.server_close()


if __name__ == "__main__":
    main()
