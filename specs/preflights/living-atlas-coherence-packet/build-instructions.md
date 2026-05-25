# Build instructions — Living Atlas (preflight)

Build `python3 tool.py <contribs_json_path>`. Reads { "contributions": [ {"id":"...","layer":"ecological"|"cultural"|"economic"|"governance","text":"...","consent":"public"|"steward-review"|"private","cited_sources":["..."]}, ... ] }. Per contribution, evaluate three coherence checks: (1) missing_consent if consent not in {public, steward-review, private}; (2) needs_steward_review if consent==steward-review; (3) uncited_public if consent==public AND cited_sources is empty. Print header 'ATLAS COHERENCE PACKET (<C> clean / <F> flagged of <N> contributions)', blank, for each contribution in input order: '<id> [<layer>]: <findings>' (findings = 'clean' or alphabetical comma-joined), blank, 'BOUNDARY: this packet flags coherence; it does not force fit, replace steward review, or grant any visibility upgrade.'. On invalid JSON: 'error:' line, exit 0. Stdlib only.

Stdlib only; no network; no credentials.
