---
doc_id: indigenomics.jam.sample-receipt-wall.team-submission
doc_kind: worked-example
status: sample
date: 2026-05-25
schema: team-submission-v0
---

# Sample Team Submission — Story Receipts

A worked example: a small text-aggregation tool (different shape from Kelp Watch's numeric rollup or Tide Tally's tag counter).

This pattern fits teams interested in:
- making contribution + consent visible
- producing a public-safe display from records where each contributor sets the scope
- the gap between "the records exist" and "what may be shown"

```json
{
  "schema_version": "team-submission-v0",
  "submission_id": "team-spec-story-receipts-01",
  "created_at": "2026-05-25T09:30:00-07:00",
  "updated_at": "2026-05-25T11:30:00-07:00",
  "surface": "shared-doc",
  "team": {
    "id": "team-story-receipts",
    "name": "Story Receipts",
    "site": "Vancouver",
    "members": [
      {"display": "A. Cedar"},
      {"display": "M. Salal"}
    ]
  },
  "vision": {
    "text": "A tool that turns a small set of public-safe story-receipts into a markdown wall the room can read on Tuesday — each entry only appearing if the contributor cleared it for display.",
    "prompt": "What should exist, and what does it make visible, felt, or possible?"
  },
  "spec": {
    "text": "Build a single-file Python tool, run as `python3 tool.py <receipts_json_path>`, that reads the JSON file at the path given as its first command-line argument. The file is an object shaped { \"receipts\": [ { \"id\": \"...\", \"contributor\": \"...\", \"date\": \"YYYY-MM-DD\", \"text\": \"...\", \"display_scope\": \"public\"|\"team-only\"|\"spoken-only\"|\"none\", \"tags\": optional list of strings }, ... ] }. Print to stdout a markdown wall, in this order: (1) a header line exactly '# Story Receipts Wall (<S> shown / <N> total)' where S is the count of receipts with display_scope == 'public' and N is the total receipt count; (2) one blank line; (3) for each public receipt, sorted by date ascending then by id ascending for ties, a block of: '## <contributor> — <date>', one blank line, then the receipt's `text` quoted with `> ` prefix on each line, one blank line, then `tags: <comma-separated tags>` if tags are non-empty (else omit the tags line), then one blank line; (4) at the bottom, a footer line exactly '---' on its own line, one blank line, then 'Receipts withheld from display: <W>' where W = N - S. Skip every receipt whose display_scope is not exactly 'public' (treat 'team-only', 'spoken-only', 'none', and any missing/unknown value as withheld). Receipts with empty `text` after stripping are also withheld. The output is markdown; do not strip or modify the receipt text other than quoting each of its lines. If the input cannot be read or is not valid JSON, print a single line beginning with 'error:' and exit 0. Standard library only; no network; no credential access.",
    "prompt": "What does the team want made real over the two days?"
  },
  "source_offerings": [
    {
      "id": "o1",
      "title": "Sample receipt JSON fixture (fictional)",
      "contributor_display": "A. Cedar",
      "visibility": "public",
      "included_in_build": true,
      "cleared_text": "A small hand-rolled JSON file with 6 fictional receipts across 4 fictional contributors; mix of display_scope values; cleared for the build."
    },
    {
      "id": "o2",
      "title": "Markdown-formatting convention notes",
      "contributor_display": "M. Salal",
      "visibility": "public",
      "included_in_build": true,
      "cleared_text": "A short note on the markdown blockquote pattern + header levels the team wants the wall to use; cleared for the build."
    }
  ],
  "boundaries": [
    {
      "id": "boundary-non-public-scopes",
      "label": "Non-public receipts (team-only / spoken-only / none)",
      "boundary_type": "marker-only",
      "marker_text": "Receipts whose contributors did not clear them for public display are named only as a count at the bottom of the wall. Their text is never rendered, never embedded, never summarized.",
      "private_content_included": false,
      "disallowed_use": ["summarize", "tag", "embed", "route", "transform", "send-to-ai"]
    },
    {
      "id": "boundary-contributor-contact",
      "label": "Contributor email / phone (held by team)",
      "boundary_type": "not-for-AI",
      "marker_text": "Contributor contact details are held by the team and never enter the build attempt or the rendered wall.",
      "private_content_included": false,
      "disallowed_use": ["summarize", "tag", "embed", "route", "transform", "send-to-ai"]
    }
  ],
  "build_request": {
    "path": "telus-lane",
    "target": "single-file-cli",
    "notes": "Python standard library only. Output is markdown to stdout."
  },
  "witnessed_working": {
    "description": "On Tuesday, the team can show the tool reading a small JSON fixture of receipts and printing a markdown wall the room can read aloud — only public-cleared receipts appear, the withheld count is honest.",
    "acceptance_criteria": [
      "prints the exact header '# Story Receipts Wall (<S> shown / <N> total)'",
      "shows only receipts with display_scope == 'public'; counts every other value (including missing) as withheld",
      "renders each public receipt as: '## <contributor> — <date>', blank, quoted text, blank, optional tags line, blank",
      "sorts public receipts by date ascending, then id ascending for ties",
      "skips receipts with empty stripped text (counts them as withheld)",
      "emits the '---' footer + 'Receipts withheld from display: <W>' line at the bottom",
      "prints a line beginning with 'error:' on unreadable or invalid JSON, exits 0",
      "uses standard library only, no network, no credential access"
    ]
  },
  "help_wanted": ["a mentor pair for the first hour"],
  "authorization": {
    "visible_to_facilitators": true,
    "display_scope": "whole",
    "display_allowed_parts": [],
    "ai_input_scope": "whole",
    "ai_allowed_parts": [],
    "reuse_scope": "ask-first",
    "authorization_notes": "Non-public receipts and contributor-contact details are named only as boundaries."
  },
  "freeze": {
    "status": "frozen",
    "frozen_by": "team + jam facilitator (sample)",
    "frozen_at": "2026-05-25T11:30:00-07:00",
    "facilitator_confirmed": {
      "consent_privacy_complete": true,
      "boundaries_reviewed": true,
      "public_private_status_confirmed": true,
      "ai_input_scope_confirmed": true,
      "build_path_confirmed": true,
      "witnessed_working_clear": true
    },
    "change_policy": "new ideas require re-freeze"
  }
}
```

## What this example demonstrates differently from Kelp Watch

| | Kelp Watch | Story Receipts |
|---|---|---|
| Shape | numeric rollup | text aggregation |
| Per-record gate | drop-rules (bad value / empty key) | consent gate (display_scope) |
| Output | tabular CLI | markdown formatted |
| Counting semantics | what got tallied | what got withheld |
| Boundary illustration | site held privately by team | per-record display gates set by contributor |

The display-scope gate is the load-bearing detail. A receipt being IN the file ≠ the receipt being SHOWN. The team chose to be transparent about the withheld count at the bottom — it makes the wall honest without disclosing what was withheld.
