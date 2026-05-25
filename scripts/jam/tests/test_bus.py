"""Tests for scripts/jam/bus.py — stdlib-only (unittest).

Run from kit root:
    python3 -m unittest scripts.jam.tests.test_bus -v
Or directly:
    python3 scripts/jam/tests/test_bus.py

Tests cover:
- All 7 wire types validate cleanly when well-formed (happy paths)
- Three explicit failure cases from coordination-protocol-v0.md §First Build Step:
  * silent-share: share_request whose preview body leaks protected content
  * aggregated-yes: composition_propose with empty acceptance_required_from
  * ignored-withdrawal: withdraw_notice with empty acknowledgment_required_from
- Append-only invariant: audit detects duplicate message_ids
- Refusal-without-reason: share_refuse with no `reason` field is accepted
- witness_observe rejection when not_an_authority_claim is missing/false
- boundary_marker rejection when marker_text leaks protected content
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Make `scripts.jam.bus` importable when running from kit root.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import bus  # noqa: E402


def env(from_team="A", to_team="B", mtype="share_request", refs=None):
    return bus.make_envelope(from_team, to_team, mtype, references=refs)


class WireTypeHappyPaths(unittest.TestCase):
    def test_share_request_happy(self):
        msg = env(mtype="share_request")
        msg["payload"] = {
            "what": {
                "content_kind": "offering",
                "preview": {"mode": "paraphrased", "body": "salmon-count observation"},
            },
            "why": {"intent": "We want to combine with your kelp-bed map"},
            "consent_terms": {
                "display_scope": "partial",
                "ai_input_scope": "none",
                "reuse_scope": "ask-first",
            },
        }
        bus.validate_message(msg)

    def test_share_grant_happy(self):
        # First make a share_request to reference
        req = env(mtype="share_request")
        msg = env(from_team="B", to_team="A", mtype="share_grant", refs=[req["message_id"]])
        msg["payload"] = {"granted": True, "added_conditions": [{"condition": "attribution required"}]}
        bus.validate_message(msg)

    def test_share_refuse_no_reason_accepted(self):
        req = env(mtype="share_request")
        msg = env(from_team="B", to_team="A", mtype="share_refuse", refs=[req["message_id"]])
        msg["payload"] = {"granted": False}  # NO reason field
        # The spec is explicit: reason is optional.
        bus.validate_message(msg)

    def test_share_refuse_with_reason(self):
        req = env(mtype="share_request")
        msg = env(from_team="B", to_team="A", mtype="share_refuse", refs=[req["message_id"]])
        msg["payload"] = {"granted": False, "reason": "not aligned with our scope", "log_as_learning": True}
        bus.validate_message(msg)

    def test_withdraw_notice_happy(self):
        req = env(mtype="share_request")
        grant = env(from_team="B", to_team="A", mtype="share_grant", refs=[req["message_id"]])
        msg = env(mtype="withdraw_notice", refs=[req["message_id"], grant["message_id"]])
        msg["payload"] = {
            "withdrawn_record_ids": ["offering-001"],
            "acknowledgment_required_from": ["B"],
        }
        bus.validate_message(msg)

    def test_boundary_marker_happy(self):
        msg = env(mtype="boundary_marker")
        msg["payload"] = {
            "label": "ceremonial-content",
            "boundary_type": "protected",
            "marker_text": "Cultural framing held by team lead; do not summarize",
            "disallowed_use": ["summarize", "tag", "embed", "send-to-ai"],
            "review_authority": "Carol Anne",
        }
        bus.validate_message(msg)

    def test_composition_propose_happy(self):
        msg = env(mtype="composition_propose")
        msg["payload"] = {
            "proposed_bundle_id": "bundle-001",
            "composes": [
                {"team_id": "A", "submission_id": "sub-A", "offerings": ["off-A1"]},
                {"team_id": "B", "submission_id": "sub-B", "offerings": ["off-B1"]},
            ],
            "acceptance_required_from": [{"team_id": "A"}, {"team_id": "B"}],
        }
        bus.validate_message(msg)

    def test_witness_observe_happy(self):
        msg = env(mtype="witness_observe")
        msg["payload"] = {
            "observed": {"kind": "refusal_tested", "body": "Team B refused share_request without reason"},
            "not_an_authority_claim": True,
            "routing": "witness_drafter",
        }
        bus.validate_message(msg)


class ExplicitFailureCases(unittest.TestCase):
    """Three failure cases named in coordination-protocol-v0.md First Build Step."""

    def test_silent_share_protected_leak_rejected(self):
        msg = env(mtype="share_request")
        msg["payload"] = {
            "what": {
                "content_kind": "offering",
                "preview": {
                    "mode": "marker_only",
                    "body": "Here is the [PROTECTED] cultural framing detail leaking through",
                },
            },
            "why": {"intent": "Trying to share content via marker_only mode"},
            "consent_terms": {
                "display_scope": "partial",
                "ai_input_scope": "none",
                "reuse_scope": "ask-first",
            },
        }
        with self.assertRaises(bus.ValidationError) as cm:
            bus.validate_message(msg)
        self.assertIn("leak marker", str(cm.exception).lower())

    def test_aggregated_yes_rejected(self):
        msg = env(mtype="composition_propose")
        msg["payload"] = {
            "proposed_bundle_id": "bundle-001",
            "composes": [
                {"team_id": "A", "submission_id": "sub-A", "offerings": ["off-A1"]},
                {"team_id": "B", "submission_id": "sub-B", "offerings": ["off-B1"]},
            ],
            # Empty acceptance_required_from = bulk-yes shortcut. Rejected.
            "acceptance_required_from": [],
        }
        with self.assertRaises(bus.ValidationError) as cm:
            bus.validate_message(msg)
        self.assertIn("acceptance_required_from", str(cm.exception))

    def test_ignored_withdrawal_rejected(self):
        req = env(mtype="share_request")
        msg = env(mtype="withdraw_notice", refs=[req["message_id"]])
        msg["payload"] = {
            "withdrawn_record_ids": ["offering-001"],
            # Empty acknowledgment_required_from = silently absorbed. Rejected.
            "acknowledgment_required_from": [],
        }
        with self.assertRaises(bus.ValidationError) as cm:
            bus.validate_message(msg)
        self.assertIn("acknowledgment_required_from", str(cm.exception))


class BoundaryAndAuthorityChecks(unittest.TestCase):
    def test_boundary_marker_text_leak_rejected(self):
        msg = env(mtype="boundary_marker")
        msg["payload"] = {
            "label": "x",
            "boundary_type": "protected",
            "marker_text": "Actual [PROTECTED] content leaking via marker_text",
            "disallowed_use": ["summarize"],
        }
        with self.assertRaises(bus.ValidationError):
            bus.validate_message(msg)

    def test_witness_observe_missing_not_an_authority_claim(self):
        msg = env(mtype="witness_observe")
        msg["payload"] = {
            "observed": {"kind": "refusal_tested", "body": "..."},
            # not_an_authority_claim is MISSING
            "routing": "witness_drafter",
        }
        with self.assertRaises(bus.ValidationError):
            bus.validate_message(msg)

    def test_witness_observe_authority_claim_false_rejected(self):
        msg = env(mtype="witness_observe")
        msg["payload"] = {
            "observed": {"kind": "composition_landed", "body": "..."},
            "not_an_authority_claim": False,  # explicit attempt to claim authority
            "routing": "operator",
        }
        with self.assertRaises(bus.ValidationError):
            bus.validate_message(msg)

    def test_unknown_message_type_rejected(self):
        msg = env(mtype="share_request")
        msg["message_type"] = "some_made_up_type"
        msg["payload"] = {}
        with self.assertRaises(bus.ValidationError):
            bus.validate_message(msg)

    def test_share_request_vague_intent_rejected(self):
        msg = env(mtype="share_request")
        msg["payload"] = {
            "what": {"content_kind": "offering", "preview": {"mode": "paraphrased", "body": "x"}},
            "why": {"intent": "hi"},  # too short
            "consent_terms": {"display_scope": "partial", "ai_input_scope": "none", "reuse_scope": "ask-first"},
        }
        with self.assertRaises(bus.ValidationError):
            bus.validate_message(msg)


class StorageAndAudit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.bus_root = Path(self.tmp)
        bus.init_bus(self.bus_root, team_id="A")
        bus.init_bus(self.bus_root, team_id="B")

    def _make_share_request_msg(self):
        msg = env(from_team="A", to_team="B", mtype="share_request")
        msg["payload"] = {
            "what": {"content_kind": "offering",
                     "preview": {"mode": "paraphrased", "body": "kelp-bed sample"}},
            "why": {"intent": "Combining with your salmon-count for joint observation"},
            "consent_terms": {"display_scope": "partial",
                              "ai_input_scope": "none",
                              "reuse_scope": "ask-first"},
        }
        return msg

    def test_append_to_both_team_logs_and_global(self):
        msg = self._make_share_request_msg()
        bus.append_message(self.bus_root, msg)
        paths = bus.bus_paths(self.bus_root)
        a_log = bus.read_log(paths["teams_dir"] / "A.jsonl")
        b_log = bus.read_log(paths["teams_dir"] / "B.jsonl")
        glob = bus.read_log(paths["global_log"])
        self.assertEqual(len(a_log), 1)
        self.assertEqual(len(b_log), 1)
        self.assertEqual(len(glob), 1)
        self.assertEqual(a_log[0]["message_id"], msg["message_id"])

    def test_audit_detects_duplicate_message_id(self):
        msg = self._make_share_request_msg()
        bus.append_message(self.bus_root, msg)
        # Forge a duplicate by appending the same line raw.
        paths = bus.bus_paths(self.bus_root)
        with paths["global_log"].open("a") as f:
            f.write(json.dumps(msg, sort_keys=True) + "\n")
        result = bus.audit_append_only(paths["global_log"])
        self.assertFalse(result["ok"])
        self.assertEqual(len(result["duplicates"]), 1)

    def test_audit_clean_log(self):
        msg = self._make_share_request_msg()
        bus.append_message(self.bus_root, msg)
        paths = bus.bus_paths(self.bus_root)
        result = bus.audit_append_only(paths["global_log"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["lines"], 1)

    def test_appending_invalid_message_rejected(self):
        msg = env(mtype="share_request")
        msg["payload"] = {"what": {}, "why": {"intent": "hi"}, "consent_terms": {}}
        with self.assertRaises(bus.ValidationError):
            bus.append_message(self.bus_root, msg)


if __name__ == "__main__":
    unittest.main(verbosity=2)
