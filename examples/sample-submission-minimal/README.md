# Minimal Viable Submission — Worked Example

The **smallest plausible-and-valid** `team-submission-v0`. About 50 lines of JSON. A team with 90 minutes and a single offering could plausibly write this.

## When to show this

A team is overwhelmed by the rich Kelp Watch / Story Receipts / Pool Routing samples (~150 lines of JSON each) and asks "what's the minimum we have to fill in?"

This is the answer. It's not the **best** submission — it's the smallest one that the freeze checklist accepts.

## What's in it

`team-submission.json`:

- **Team** (id, name, site, 2 members with display names)
- **Vision** (one sentence)
- **Spec** (a few sentences describing a single-file CLI that counts distinct authors)
- **One source offering** (a hand-rolled JSON fixture)
- **No boundaries** (empty array — the team has no protected/cultural/private material in this submission)
- **Build request**: `telus-lane`, `single-file-cli`
- **Witnessed working**: short description + 3 acceptance criteria
- **Authorization**: `whole` / `whole` / `ask-first`
- **Freeze**: confirmed, all 6 facilitator checkboxes

## What's NOT in it

- Multiple offerings or composition with other teams
- Boundaries (the team genuinely doesn't have any — it's a small ecological-public tool)
- Complex consent layers
- Detailed help-wanted
- Specific contributor display names per offering

## When a team should NOT use this as a template

If the team has:
- Any cultural / ceremonial / Nation-specific material → use boundaries; do not leave them empty
- Multiple contributors with different consent preferences → use `source_offerings[].visibility` and detailed contributor displays
- Anything they want held back from public Tuesday sharing → use `display_scope: partial` or `spoken-only`
- An optional CLI argument → write at least one acceptance criterion that exercises it (see `docs/troubleshooting-and-failure-modes.md`)

## What this teaches mentors

The schema's full size (~340 lines in `templates/team-submission-v0.md`) can scare teams. Show them this minimal example first if they're feeling overwhelmed. **Most fields are optional.** What's required is what the freeze checklist requires.

## Comparison to richer samples

| | This minimal | Kelp Watch | Story Receipts |
|---|---|---|---|
| JSON lines | ~50 | ~95 | ~95 |
| Offerings | 1 | 3 | 2 |
| Boundaries | 0 | 2 | 2 |
| Acceptance criteria | 3 | 7 | 8 |
| Display scope | `whole` | `whole` | `whole` |
| AI scope | `whole` | `whole` | `whole` |

## Boundary

Fictional. The "team" is illustrative. The minimal pattern is the real artifact.
