# Build instructions — Briefing (preflight)

Build `python3 tool.py <inputs_json_path>`. Reads { "briefing_title":"...","as_of":"YYYY-MM-DD","claims":[...],"evidence_count":<int>,"observation_count":<int>,"reviewer":"..."|null }. Print markdown: '# <briefing_title>' line; blank; '_as of <as_of>_'; blank; '## Inputs' blank; '- claims: <len(claims)>' blank; '- evidence pointers: <evidence_count>' blank; '- observations: <observation_count>' blank; '## Reviewer' blank; if reviewer is null: 'NOT YET REVIEWED'; else: '<reviewer>'; blank; '## Boundary' blank; 'This briefing summarizes inputs. It does not certify, score, or authorize any action.'. On invalid JSON: 'error:' line, exit 0. Stdlib only.

Stdlib only; no network; no credentials.
