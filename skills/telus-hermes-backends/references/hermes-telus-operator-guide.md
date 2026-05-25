# Hermes Agent on TELUS Models: Operator Guide

This guide explains the configuration points that matter when running Hermes Agent against direct TELUS OpenAI-compatible endpoints or the Indigenomics Gateway.

Use the Creator Jam Gateway for participant API access and Gateway-mediated Hermes sessions. Use direct TELUS endpoints for staff/operator diagnostics or when event Gateway policy and access gates should be bypassed.

## Model Choice

| Backend | Best fit | Watch points |
|---|---|---|
| Qwen `Qwen/Qwen3.6-35B-A3B` | Complex reasoning, coding, decomposition, multi-step tool loops | Reasoning can consume output tokens. Start with `max_tokens: 4096`; raise it for long-form generation. |
| Gemma `google/gemma-4-31b-it` | Fast concise answers, writing, review, extraction, low-latency operator checks | Keep tool instructions explicit and bounded. |
| GPT OSS `gpt-oss:120b` | General fallback, broad reasoning, robust chat and tool calls | May spend more tokens on reasoning; keep max-turn and output budgets visible. |

All three direct TELUS endpoints have been verified for OpenAI chat completions and OpenAI-style tool calls. Hermes terminal tool-loop checks have also been verified for all three when configured with direct TELUS keys. The Indigenomics Gateway has also been verified with Hermes terminal tool use through streamed OpenAI-style tool-call deltas.

## Qwen vLLM Deployment Notes

The TELUS Qwen backend is deployed on one NVIDIA H200 with vLLM and these relevant serving settings:

```bash
vllm serve <model> \
  --trust-remote-code \
  --dtype bfloat16 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml \
  --reasoning-parser qwen3 \
  --enable-chunked-prefill \
  --max-num-batched-tokens 131072 \
  --enable-prefix-caching \
  --gpu-memory-utilization 0.95 \
  --max-num-seqs 8 \
  --max-model-len 262144
```

Operational implications:

- `--max-model-len 262144` supports the Hermes/Gateway `context_length: 262144` setting.
- `--enable-auto-tool-choice` and `--tool-call-parser qwen3_xml` mean OpenAI-style `tools` plus `tool_choice: "auto"` are the right interface.
- `--reasoning-parser qwen3` means reasoning may be returned separately from final content; keep `max_tokens` high enough that reasoning does not consume the whole response budget.
- `--enable-chunked-prefill` and `--enable-prefix-caching` help long prompts and repeated Hermes/Gateway system/tool prefixes, but they do not remove the need to manage tool-output size and agent turns.
- `--max-num-batched-tokens 131072`, `--max-num-seqs 8`, and `--gpu-memory-utilization 0.95` describe throughput/concurrency posture. Under event load, failures can be capacity symptoms even when individual prompts are valid.

## Core Hermes Configuration

```yaml
model:
  provider: custom
  default: Qwen/Qwen3.6-35B-A3B
  base_url: https://qwen-0b50s.paas.ai.telus.com/v1
  api_key: "<TELUS_QWEN_KEY>"
  api_mode: chat_completions
  context_length: 262144
  max_tokens: 4096

terminal:
  backend: local
  cwd: "."
  timeout: 180

display:
  streaming: false
  show_reasoning: false
  tool_progress: off
```

### `model.provider`

Use `custom` for TELUS endpoints. This tells Hermes to use a generic provider profile instead of a built-in commercial provider profile.

### `model.default`

The exact upstream model id. This must match the TELUS endpoint:

- Qwen: `Qwen/Qwen3.6-35B-A3B`
- Gemma: `google/gemma-4-31b-it`
- GPT OSS: `gpt-oss:120b`

Wrong model ids often show up as `400`, `404`, or provider-specific validation errors.

### `model.base_url`

The OpenAI-compatible API root ending in `/v1`.

For direct TELUS work, use direct TELUS URLs. For participant or team-mediated work, use the Gateway URL and public Gateway model ids.

Gateway example:

```yaml
model:
  provider: custom
  default: telus-qwen
  base_url: https://regen.gaiaai.xyz/events/creator-jam/api/v1
  api_key: "<TEAM_GATEWAY_KEY>"
  api_mode: chat_completions
  context_length: 262144
  max_tokens: 4096
```

### `model.api_key`

The TELUS service key for the selected backend. The keys are service-specific; a Qwen key should be used with the Qwen base URL, not Gemma or GPT OSS.

Do not commit `~/.hermes/config.yaml` if it contains `api_key`.

### `model.api_mode`

Use `chat_completions` for the TELUS endpoints. Hermes also has other API modes for providers such as Anthropic-style messages or Codex-style responses, but those are not the right default for these TELUS services.

### `model.context_length`

The total context budget Hermes believes the model can handle. This includes system prompt, conversation history, tool schemas, tool results, and the next response.

If this is too low, Hermes compresses earlier and may lose useful context. If this is too high for the actual backend, long sessions can fail at the provider. Start with `262144` for Qwen and adjust only after real provider limits are confirmed under load.

### `model.max_tokens`

The output cap for a single model response. It is not the total context size.

Low values can break reasoning models because internal reasoning and visible output compete for the same response budget. For Qwen/Hermes work, use at least `4096`; raise it further for long planning, long writing, or complicated tool use.

### `agent.max_turns`

The maximum number of model/tool iterations in one Hermes run. Tool calls consume turns. A terminal workflow that needs inspect, edit, test, and summarize may need more than four turns.

Use small values for smoke tests and larger values for real work:

- Smoke test: `--max-turns 1`
- Single terminal tool check: `--max-turns 4`
- Real coding/research session: `--max-turns 20` or higher

### `agent.reasoning_effort`

Hermes exposes this for providers that support a reasoning-effort parameter. For TELUS custom endpoints, treat it as provider-dependent and verify before relying on it.

Reasoning-heavy models can produce better plans and tool choices, but may be slower and may consume more output budget. If final answers are truncated, raise `max_tokens` before changing model strategy.

### `display.show_reasoning`

Controls whether Hermes displays captured reasoning when available. This is a UX/debugging setting, not a model quality setting.

Keep it off for normal participant-facing demos. Turn it on only for operator debugging if the provider returns useful reasoning metadata and the content is safe to display.

### `display.streaming`

Streaming changes interactivity and perceived latency. It does not make the model smarter.

If a provider or proxy has streaming quirks, set `streaming: false` for reliability. This has worked well with TELUS smoke tests.

### `terminal.cwd`

The working directory for local terminal tools. Set it intentionally for operator work so Hermes edits and tests the intended repo.

Examples:

```yaml
terminal:
  cwd: "/home/shawn/CreatorJamSpecKit"
```

or:

```yaml
terminal:
  cwd: "/home/shawn/indigenomics-ai-gateway"
```

### `terminal.timeout`

Maximum shell command time. Raise it for test suites or installs. Lower it for constrained demos.

### Toolsets

Hermes tool schemas consume context and influence behavior. Enable only what the session needs.

For a terminal-only check:

```bash
hermes chat --toolsets terminal --query 'Use terminal to run pwd, then report the directory.' --max-turns 4 --quiet --yolo
```

For simple chat:

```bash
hermes chat --query 'Reply READY only.' --max-turns 1 --quiet
```

Tool use improves capability but increases latency, token use, and risk. Keep prompts explicit: say what tool to use, what command to run, and what result to report.

## Parameter Effects

| Parameter | Primary effect | Failure mode |
|---|---|---|
| `model.default` | Selects model behavior, latency, reasoning style, and tool-call reliability | Wrong model id fails or silently routes badly if a proxy aliases names |
| `base_url` | Selects backend service | Wrong endpoint gives auth/model errors |
| `api_key` | Authenticates to selected service | `401` or `403` |
| `context_length` | Controls Hermes context accounting and compression timing | Too low compresses too early; too high may fail on long requests |
| `max_tokens` | Caps one response | Too low causes truncation or empty final content after reasoning |
| `max_turns` | Caps agent loop length | Too low stops before tools finish; too high can waste budget |
| `toolsets` | Defines available capabilities | Too many tools add context and confusion; too few block the task |
| `temperature` / `top_p` | Changes randomness when supported | High values can make tool use less deterministic |
| `streaming` | Changes output delivery | Streaming bugs can look like model failures |
| `show_reasoning` | Displays reasoning metadata if available | Can expose internal or sensitive reasoning content |

## Recommended Defaults

For Qwen operator setup:

```yaml
model:
  provider: custom
  default: Qwen/Qwen3.6-35B-A3B
  base_url: https://qwen-0b50s.paas.ai.telus.com/v1
  api_mode: chat_completions
  context_length: 262144
  max_tokens: 4096
display:
  streaming: false
  show_reasoning: false
  tool_progress: off
```

Use `max_tokens: 4096` for normal Gateway/Hermes work. Use lower values only for deliberate smoke tests, and raise it for long-form generation.

## Verification Ladder

1. Raw chat completion succeeds.
2. Raw OpenAI tool-call completion returns `finish_reason=tool_calls`.
3. Hermes simple chat returns a short answer.
4. Hermes terminal tool-loop runs `pwd` and summarizes the directory.
5. Hermes performs a small real repo task with tests.

For Gateway verification, include a streaming Hermes tool-loop check. The Gateway must preserve `tools`, `tool_choice`, `parallel_tool_calls`, assistant `tool_calls`, tool-result messages, and streamed `tool_calls` deltas.

Do not skip directly to a complex workflow when validating a new key or endpoint.

## Troubleshooting

- `401` or `403`: key does not match the TELUS service, key is stale, or Hermes is not reading the intended config.
- `404` or unknown model: `model.default` does not match the TELUS backend.
- Empty content with `finish_reason=length`: raise `max_tokens`.
- Tool call not made: make the prompt explicit, enable the right toolset, and allow more turns.
- Hermes works through direct TELUS but not Gateway: regression. Confirm the Gateway request schema allows extra OpenAI fields, strips invalid `stream_options` when forcing upstream non-streaming, and emits streamed tool-call deltas.
- `System message must be at the beginning`: a proxy is injecting another system message after Hermes' system message. Merge system messages before forwarding.
- Config env interpolation fails: write an explicit operator-local `api_key` via the helper.

## Security

- Keep TELUS keys in operator environment variables or local Hermes config only.
- Never commit `.env`, request dumps, logs with Authorization headers, or `~/.hermes/config.yaml`.
- Gateway keys are team-scoped credentials. Do not commit them; rotate or revoke temporary smoke-test keys after verification.
- If sharing commands, show placeholders for keys.
