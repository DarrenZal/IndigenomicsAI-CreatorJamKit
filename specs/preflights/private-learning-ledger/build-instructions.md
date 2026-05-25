# Build instructions — Private Learning (preflight)

Build `python3 tool.py <ledger_json_path>`. Reads { "actions": [ {"action_id":"...","action_type":"review"|"approval"|"refusal"|"correction","steward_visibility":"public"|"private","private_notes":"...","outcome_summary":"..."}, ... ] }. Output public summary that NEVER includes private_notes (regardless of visibility). For public steward_visibility actions, include outcome_summary. For private, only count the action. Print header 'PRIVATE LEARNING LEDGER (<P> public / <H> hidden of <N> total)', blank, for each action in input order: if steward_visibility==public: '<action_id> [<action_type>]: <outcome_summary>'; else: '<action_id> [<action_type>]: held by steward', blank, 'BY ACTION TYPE:', for each action_type alphabetical: '  <type>: <count>', blank, 'BOUNDARY: private_notes never appear in this output. Counts do not imply judgment.'. On invalid JSON: 'error:' line, exit 0. Stdlib only.

Stdlib only; no network; no credentials.
