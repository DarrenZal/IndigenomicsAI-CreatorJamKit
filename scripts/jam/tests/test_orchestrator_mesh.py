"""Tests for orchestrator mesh-mode + wall-root wire-in + refusal-
gatekeeper v0.4 scope-awareness.

Run from kit root:
    python3 -m unittest scripts.jam.tests.test_orchestrator_mesh -v
"""

import inspect
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import orchestrator as orch  # noqa: E402


KIT_ROOT = Path(__file__).resolve().parents[3]


class AttemptSpecSignatureTests(unittest.TestCase):
    def test_attempt_spec_has_mesh_mode_param(self):
        sig = inspect.signature(orch.attempt_spec)
        self.assertIn("mesh_mode", sig.parameters)
        self.assertFalse(sig.parameters["mesh_mode"].default)

    def test_attempt_spec_has_wall_root_param(self):
        sig = inspect.signature(orch.attempt_spec)
        self.assertIn("wall_root", sig.parameters)
        self.assertIsNone(sig.parameters["wall_root"].default)


class CLIFlagsPresent(unittest.TestCase):
    def _run_help(self):
        proc = subprocess.run(
            ["python3", str(KIT_ROOT / "scripts/jam/orchestrator.py"),
             "run", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        return proc.stdout + proc.stderr

    def test_help_lists_mesh_mode_flag(self):
        out = self._run_help()
        self.assertIn("--mesh-mode", out)

    def test_help_lists_wall_root_flag(self):
        out = self._run_help()
        self.assertIn("--wall-root", out)


class ReviewerImportedAtModuleLevel(unittest.TestCase):
    def test_reviewer_review_function_imported(self):
        self.assertTrue(hasattr(orch, "reviewer_review"))
        self.assertTrue(callable(orch.reviewer_review))


class WallRootDefaultBehavior(unittest.TestCase):
    """Reading source confirms the default fallback is out_dir/wall when
    wall_root is None — but the explicit flag substitutes when provided.
    This is a smoke-level sanity check; full end-to-end behavior is in
    the smoke-test phase."""

    def test_source_has_effective_wall_root_branch(self):
        src = Path(orch.__file__).read_text()
        self.assertIn("effective_wall_root", src)
        self.assertIn(
            "wall_root if wall_root is not None",
            src,
            "wall_root override branch missing — explicit flag wouldn't work",
        )


class RefusalGatekeeperV04Tests(unittest.TestCase):
    """Tests for the v0.4 scope-aware refusal gatekeeper.

    Background (2026-05-26 substrate-on-team-specs experiment):
    The v0.3 gatekeeper did pure substring match on a list of cultural-
    content terms. It caught 3 of 4 team-spec refusals tonight (V5,
    SignalGraph, Consent Layers), and at least 2 of those were false-
    positives — the teams used those terms to declare scope EXCLUSIONS
    (e.g., 'not ceremonial', 'not cultural witnessing') but the regex
    couldn't tell exclusion from inclusion.

    v0.4 adds:
      (a) framework names (OCAP, FPIC, 'indigenous data sovereignty')
          REMOVED from the gatekeeper list — these are governance
          frameworks systems should be able to ADOPT, not refused for
          mentioning.
      (b) scope-exclusion regex — a remaining sensitive term within
          ~80 chars of a negation/exclusion marker passes the gate.

    Same descriptive-negation pattern we added to the validator at
    commit 541f146.
    """

    def _write_spec(self, body: str) -> Path:
        """Write a spec body to a temp file and return the path."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        )
        tmp.write(body)
        tmp.close()
        return Path(tmp.name)

    # ----- Framework-name removal (Phase 1) ----- #

    def test_ocap_no_longer_in_gatekeeper_terms(self):
        self.assertNotIn("ocap", orch.CULTURAL_GATEKEEPER_TERMS)

    def test_fpic_no_longer_in_gatekeeper_terms(self):
        self.assertNotIn("fpic", orch.CULTURAL_GATEKEEPER_TERMS)

    def test_indigenous_data_sovereignty_no_longer_in_gatekeeper_terms(self):
        self.assertNotIn(
            "indigenous data sovereignty",
            orch.CULTURAL_GATEKEEPER_TERMS,
        )

    def test_framework_adoption_passes_gatekeeper(self):
        """A spec that adopts OCAP / UNDRIP / FPIC frameworks should
        pass the gate. (V5-style case.)"""
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Living Lab Co-Utile Talent Matching\n\n"
            "This system follows OCAP principles for data stewardship. "
            "Engagements honor FPIC, with explicit reference to UNDRIP. "
            "The token economy supports Indigenous data sovereignty. "
            "Community-led connections are the governance primitive."
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNone(
                result,
                f"framework adoption should pass; got: {result}",
            )
        finally:
            path.unlink()

    # ----- Scope-exclusion carve-out (Phase 2) ----- #

    def test_scope_exclusion_not_ceremonial_passes(self):
        """Consent Layers case: 'Software receipts only; not ceremonial
        or cultural witnessing' should pass the gate."""
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Consent Layers\n\n"
            "This tool surfaces consent state for in-event participants. "
            "Software receipts only; not ceremonial or cultural witnessing. "
            "Multi-party conflicts escalate to humans, never auto-decide."
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNone(
                result,
                f"'not ceremonial' should pass; got: {result}",
            )
        finally:
            path.unlink()

    def test_scope_exclusion_does_not_process_traditional_knowledge_passes(self):
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Some Tool\n\n"
            "This tool does not process traditional knowledge. "
            "Marker-only inputs are surfaced; nothing more."
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNone(
                result,
                f"scope-exclusion of traditional knowledge should pass; "
                f"got: {result}",
            )
        finally:
            path.unlink()

    def test_scope_exclusion_explicitly_excludes_elder_passes(self):
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Build\n\n"
            "Explicitly excludes elder-only content. "
            "Routes participant comments without invoking authority."
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNone(result)
        finally:
            path.unlink()

    def test_marker_only_context_passes(self):
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Build\n\n"
            "Ceremonial content is marker-only; "
            "the body of ceremonial material is never indexed or summarized."
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNone(result)
        finally:
            path.unlink()

    # ----- Extractive patterns STILL refused ----- #

    def test_extractive_traditional_knowledge_now_passes_at_regex_layer(self):
        """As of refusal-v0.4, 'traditional knowledge' is NO LONGER in
        the regex gatekeeper. Genuinely extractive uses are now caught
        at the MODEL layer (stage 2 offering generation, where the
        model reads the spec body in prose and refuses with
        'requires cultural authorization').

        This test pins the v0.4 behavior at the regex layer: a spec
        mentioning 'traditional knowledge' even in extractive context
        passes the gatekeeper. The next layer is the model.

        Rationale: keyword presence in regex cannot distinguish
        adoption from extraction; the model layer reads context.
        """
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Auto-classifier\n\n"
            "Indexes and synthesizes traditional knowledge entries "
            "into a searchable embedding store. Outputs ranked summaries."
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNone(
                result,
                "v0.4: 'traditional knowledge' no longer in regex "
                "gatekeeper; extractive uses caught at model layer.",
            )
        finally:
            path.unlink()

    def test_nation_specific_still_refused(self):
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Build\n\n"
            "Builds a nation-specific routing layer for Ahousaht participants. "
            "Routes claim review to per-Nation reviewer pools."
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNotNone(result)
        finally:
            path.unlink()

    def test_carol_anne_named_authority_still_refused(self):
        """Operator-author-specific gatekeeper stays — substrate has no
        standing to act in CAH's voice without explicit consent."""
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Build\n\n"
            "Tool drafts speeches and statements in Carol Anne's voice "
            "for distribution to media partners."
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNotNone(result)
            self.assertIn("carol anne", result.lower())
        finally:
            path.unlink()

    # ----- Multi-line behavior ----- #

    def test_first_unscoped_match_triggers_refusal(self):
        """If a term appears with exclusion on one line AND without
        exclusion on another, the unscoped occurrence wins.

        Uses 'nation-specific' (still in the gatekeeper list as of v0.4)
        as the test vector since 'traditional knowledge', 'ceremonial',
        and 'elder' were removed."""
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Build\n\n"
            "This tool does not implement nation-specific routing.\n\n"
            "Later: it classifies users by nation-specific membership "
            "into category buckets."
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNotNone(
                result,
                "an unscoped occurrence on a separate line should "
                "still trigger refusal even if another line has "
                "exclusion context",
            )
        finally:
            path.unlink()

    # ----- Public API + helper exposure ----- #

    def test_scope_exclusion_helper_exposed(self):
        self.assertTrue(hasattr(orch, "_is_in_scope_exclusion"))
        self.assertTrue(callable(orch._is_in_scope_exclusion))

    def test_scope_exclusion_regex_exposed(self):
        self.assertTrue(hasattr(orch, "_SCOPE_EXCLUSION_REGEX"))

    def test_structural_exclusion_regex_exposed(self):
        self.assertTrue(hasattr(orch, "_STRUCTURAL_EXCLUSION_KEYS_REGEX"))

    # ----- Structural-key scope-exclusion (covers Consent Layers
    #       not_established JSON pattern) ----- #

    def test_not_established_json_list_passes(self):
        """Consent Layers actual pattern: term inside not_established
        list value, far from the not_established key itself."""
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Build\n\n"
            '  "human_signed_by": "organizer",\n'
            '  "not_established": ["public/external display","authority","legitimacy","certification","fundability","permission for other uses","ceremonial or Knowledge Keeper witnessing"]'
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNone(
                result,
                "not_established JSON list should mark whole line "
                f"as scope-exclusion; got: {result}",
            )
        finally:
            path.unlink()

    def test_excluded_fields_yaml_passes(self):
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Build\n\n"
            "excluded_fields:\n"
            "  - traditional knowledge\n"
            "  - ceremonial content\n"
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNone(result)
        finally:
            path.unlink()

    def test_do_not_compute_marker_passes(self):
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Build\n\n"
            "do_not_compute: ceremonial content from any field"
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNone(result)
        finally:
            path.unlink()

    # ----- Elder removal (V5 governance-circle pattern) ----- #

    def test_elder_no_longer_in_gatekeeper_terms(self):
        self.assertNotIn("elder", orch.CULTURAL_GATEKEEPER_TERMS)

    def test_governance_circle_with_elder_role_passes(self):
        """V5's actual pattern: 'rotating group of Indigenous elders,
        student reps, and immigrant leaders set the rules' — a
        governance role definition, not extractive."""
        body = (
            "---\ndoc_kind: jam-spec\n---\n\n"
            "# Living Lab Governance\n\n"
            "A rotating group of Indigenous elders, student reps, and "
            "immigrant leaders set the rules for token distribution and "
            "conflict resolution."
        )
        path = self._write_spec(body)
        try:
            result = orch.refusal_gatekeeper(path)
            self.assertIsNone(
                result,
                f"governance-circle definition involving elder role "
                f"should pass; got: {result}",
            )
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
