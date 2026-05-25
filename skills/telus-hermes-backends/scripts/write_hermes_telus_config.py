#!/usr/bin/env python3
"""Write Hermes Agent config for a direct TELUS model backend.

The script reads TELUS keys from environment variables and writes
${HERMES_HOME:-~/.hermes}/config.yaml. It does not print secrets.
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path


MODELS = {
    "gpt-oss": {
        "base_url": "https://ollama-gpt-oss-120b-0b50s.paas.ai.telus.com/v1",
        "model": "gpt-oss:120b",
        "key_env": "TELUS_GPT_OSS_KEY",
    },
    "gemma": {
        "base_url": "https://gemma-4-31b-it-2-0b50s.paas.ai.telus.com/v1",
        "model": "google/gemma-4-31b-it",
        "key_env": "TELUS_GEMMA_KEY",
    },
    "qwen": {
        "base_url": "https://qwen-0b50s.paas.ai.telus.com/v1",
        "model": "Qwen/Qwen3.6-35B-A3B",
        "key_env": "TELUS_QWEN_KEY",
    },
}


def hermes_home() -> Path:
    value = os.getenv("HERMES_HOME", "").strip()
    return Path(value).expanduser() if value else Path.home() / ".hermes"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("backend", choices=sorted(MODELS))
    parser.add_argument(
        "--context-length",
        type=int,
        default=262144,
        help="Hermes context_length to write.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1024,
        help="Hermes max_tokens to write.",
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="Working directory for Hermes terminal tools.",
    )
    parser.add_argument(
        "--agent-max-turns",
        type=int,
        default=90,
        help="Default Hermes agent.max_turns to write.",
    )
    args = parser.parse_args()

    selected = MODELS[args.backend]
    api_key = os.getenv(selected["key_env"], "").strip()
    if not api_key:
        raise SystemExit(f"Missing required environment variable: {selected['key_env']}")

    home = hermes_home()
    home.mkdir(parents=True, exist_ok=True)
    config_path = home / "config.yaml"
    if config_path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = home / f"config.yaml.bak.{stamp}"
        backup_path.write_text(config_path.read_text())

    config_path.write_text(
        "\n".join(
            [
                "model:",
                "  provider: custom",
                f"  default: {selected['model']}",
                f"  base_url: {selected['base_url']}",
                f"  api_key: {api_key}",
                "  api_mode: chat_completions",
                f"  context_length: {args.context_length}",
                f"  max_tokens: {args.max_tokens}",
                "",
                "agent:",
                f"  max_turns: {args.agent_max_turns}",
                "",
                "terminal:",
                "  backend: local",
                f'  cwd: "{args.cwd}"',
                "  timeout: 180",
                "",
                "display:",
                "  streaming: false",
                "  show_reasoning: false",
                "  tool_progress: off",
                "",
            ]
        )
    )
    config_path.chmod(0o600)
    print(f"Wrote Hermes TELUS {args.backend} config to {config_path}")
    print(f"Model: {selected['model']}")
    print(f"Base URL: {selected['base_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
