# Build instructions — Dream Board (preflight)

Build `python3 tool.py <items_json_path>`. Reads { "items": [ {"id":"...","title":"...","stage":"dream"|"offer_or_need"|"promise"|"witnessed"|"fulfilled"|"withdrawn","updated_at":"YYYY-MM-DD"}, ... ] }. Valid stages: dream, offer_or_need, promise, witnessed, fulfilled, withdrawn. Drop items with unknown stage or missing id. Print header 'DREAM-TO-FULFILLMENT BOARD (<K> items across <S> stages)' where K=kept items count, S=count of distinct stages present in kept items. Then blank, then in stage order [dream, offer_or_need, promise, witnessed, fulfilled, withdrawn], for stages with at least one item, a block: '## <stage> (<count>)' newline then for each item in that stage sorted by updated_at desc then id asc: '- <id>: <title>' newline, then blank between stage blocks. On invalid JSON: 'error:' line, exit 0. Stdlib only.

Stdlib only; no network; no credentials.
