# Build instructions — Spec Composer (preflight)

Build `python3 tool.py <fragments_json_path>`. Reads { "fragments": [ {"id":"...","produces":["..."],"consumes":["..."]}, ... ] }. A pair (A, B) FORMS A CANDIDATE BUNDLE if A.produces shares at least one item with B.consumes. Print: header 'BUNDLE BOARD (<P> candidate pairs of <N> fragments)', blank, for each candidate pair sorted by (A.id, B.id) ascending: '<A.id> -> <B.id> via <shared comma-separated alphabetical>', blank, 'SUMMARY: <P> candidate pairs, <N> fragments, <S> distinct interfaces'. Distinct interfaces = union of all produces and consumes lists (deduplicated). Skip fragments missing 'id' or with non-list produces/consumes. On invalid JSON: 'error:' line, exit 0. Stdlib only.

Stdlib only; no network; no credentials.
