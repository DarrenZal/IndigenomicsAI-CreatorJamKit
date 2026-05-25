# Build instructions — Layer Board (preflight)

Build `python3 tool.py <layers_json_path>`. Reads { "layers": [ {"layer_id":"...","category":"ecological"|"cultural"|"economic"|"governance","consent_tier":"public"|"steward-review"|"private","feature_count":<int>}, ... ] }. Print header 'LAYER BOARD (<P> public / <S> steward-review / <X> private of <N> total layers)', blank, then a section 'PUBLIC LAYERS:' followed by per public layer in input order: '- <layer_id> [<category>]: <feature_count> features', then blank, then a section 'WITHHELD: <S> steward-review + <X> private layers — content not displayed.'. On invalid JSON: 'error:' line, exit 0. Stdlib only.

Stdlib only; no network; no credentials.
