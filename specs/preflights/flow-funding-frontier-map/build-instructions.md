# Build instructions — Flow Frontier (preflight)

Build a single-file Python tool, run as `python3 tool.py <graph_json_path>`. Reads { "nodes": [{"id":"...","type":"dream"|"commitment"|"pool"|"receipt","status":"open"|"closed"|"witnessed"|"funded"}], "edges": [{"from":"...","to":"...","kind":"intends"|"fulfills"|"routes_to"|"witnesses"}] }. An edge is FUNDABLE if: from.type==dream AND to.type==commitment AND from.status==open AND to.status==open; OR from.type==commitment AND to.type==pool AND from.status==witnessed AND to.status==open. Print: header 'FLOW FUNDING FRONTIER (<F> fundable / <E> total edges)', blank, for each fundable edge in input order: '- <from>(<from.type>) --[<kind>]--> <to>(<to.type>)', blank, 'SUMMARY: <F> fundable, <N> nodes, <E> edges'. On invalid JSON: 'error:' line, exit 0. Stdlib only.

Stdlib only; no network; no credentials.
