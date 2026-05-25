"""stub_model — deterministic canned responses for offline / acceptance testing
of the agentic-spec-drafting-loop.

Purpose: let the loop's pipeline tests pass even when no gateway and no
direct TELUS endpoint are available. The stub returns content shaped like
what each prompt produces, with explicit `stub:` markers so callers can
detect they're not real inference.

Used by scripts/jam/spec_drafting_loop.py when --model-source=stub.

Not for production. Not a replacement for actual model inference.
Demonstrates the loop's interface, not its semantic value.

Usage in code:
    from jam.stub_model import StubModelAdapter
    adapter = StubModelAdapter()
    response = adapter.complete(prompt_name="spec-drafter", payload={...})
"""

import hashlib
import json
from typing import Any, Dict


class StubModelAdapter:
    """A deterministic stub. Same payload → same response."""

    def __init__(self, model_label: str = "stub-deterministic-v0"):
        self.model_label = model_label

    def complete(self, prompt_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return a deterministic canned response keyed by prompt_name."""
        # Stable hash of the input for reproducibility across runs.
        seed = hashlib.sha256(
            json.dumps({"prompt": prompt_name, "payload": payload}, sort_keys=True).encode()
        ).hexdigest()[:12]

        if prompt_name == "spec-drafter":
            return self._spec_drafter(payload, seed)
        elif prompt_name == "boundary-checker":
            return self._boundary_checker(payload, seed)
        elif prompt_name == "collaboration-facilitator":
            return self._collaboration_facilitator(payload, seed)
        elif prompt_name == "witness-drafter":
            return self._witness_drafter(payload, seed)
        else:
            raise ValueError(f"stub_model: unknown prompt_name {prompt_name!r}")

    def _spec_drafter(self, payload, seed):
        """Stage 2 (Prompt 1) — draft a spec fragment from an offering."""
        offering_title = payload.get("offering", {}).get("title", "unnamed offering")
        offering_body = payload.get("offering", {}).get("body", "")
        return {
            "model_source": "stub",
            "model_label": self.model_label,
            "seed": seed,
            "stage": "spec-drafting",
            "draft_spec": {
                "title": f"[stub] Spec draft from offering: {offering_title}",
                "vision": (
                    f"[stub:spec-drafter] What should exist: a small tool or "
                    f"practice that makes the offering visible / felt / possible. "
                    f"Offering excerpt: {offering_body[:120]}"
                ),
                "spec": (
                    f"[stub:spec-drafter] The team wants to build a working "
                    f"reference implementation of {offering_title!r}. v0 is a "
                    f"single-file CLI that takes the offering's data and "
                    f"produces a small markdown receipt."
                ),
                "build_target": "single-file CLI",
                "acceptance_criteria_draft": [
                    "CLI runs without arguments and prints usage",
                    "CLI accepts a JSON input file and produces markdown output",
                    "Output references the offering's title verbatim",
                ],
            },
        }

    def _boundary_checker(self, payload, seed):
        """Stage 3 (Prompt 2) — annotate a draft spec with boundaries."""
        draft = payload.get("draft_spec", {})
        return {
            "model_source": "stub",
            "model_label": self.model_label,
            "seed": seed,
            "stage": "boundary-checking",
            "annotated_spec": {
                **draft,
                "boundaries": [
                    {
                        "id": f"b-{seed[:6]}-001",
                        "label": "stub-default-boundary",
                        "boundary_type": "not-for-reuse",
                        "marker_text": "[stub] Default not-for-reuse boundary while this is a draft",
                        "disallowed_use": ["embed", "send-to-ai", "aggregate"],
                    }
                ],
                "boundary_check_passed": True,
                "boundary_notes": (
                    "[stub:boundary-checker] No protected content detected in this "
                    "draft. Default not-for-reuse boundary applied; team can lift "
                    "this on freeze if they want public-ok reuse."
                ),
            },
        }

    def _collaboration_facilitator(self, payload, seed):
        """Stage 4 sub-stage (Prompt 4) — assess cross-team composition.

        Returns whether the proposed composition should proceed and whether
        consent moments are needed. Stub default: green-light with consent
        moments flagged."""
        proposed = payload.get("proposed_bundle", {})
        team_count = len(proposed.get("composes", []))
        return {
            "model_source": "stub",
            "model_label": self.model_label,
            "seed": seed,
            "stage": "collaboration-facilitation",
            "assessment": {
                "should_proceed": True,
                "consent_moments_needed": team_count - 1 if team_count > 1 else 0,
                "notes": (
                    f"[stub:collaboration-facilitator] {team_count}-team composition "
                    f"looks structurally OK. Surface consent moment with each "
                    f"non-originating team before freeze."
                ),
                "refusal_path_available": True,
            },
        }

    def _witness_drafter(self, payload, seed):
        """Stage 6 (Prompt 3) — draft a witness record from build outputs."""
        team = payload.get("team", {}).get("name", "stub team")
        outcome = payload.get("build_outcome", "no-build-attempted")
        return {
            "model_source": "stub",
            "model_label": self.model_label,
            "seed": seed,
            "stage": "witness-drafting",
            "witness_record_draft": {
                "team": team,
                "date": "[stub:today]",
                "what_we_brought": "[stub:witness-drafter] The offering described in the team spec.",
                "what_we_attempted": (
                    "[stub:witness-drafter] One bounded build attempt against the "
                    "frozen acceptance criteria."
                ),
                "what_happened": (
                    f"[stub:witness-drafter] Outcome: {outcome}. "
                    "This record uses verb discipline (we observed, we recorded; "
                    "we do not certify, approve, or grant authority)."
                ),
                "what_we_did_not_do": (
                    "[stub:witness-drafter] We did not produce a public dataset, "
                    "we did not assert correctness, and we did not gain reuse "
                    "permissions beyond what the team's authorization scope grants."
                ),
                "receipt_statement": (
                    "This witness record states what happened. It does not "
                    "establish authority, approval, certification, legitimacy, "
                    "or reuse permission."
                ),
            },
        }
