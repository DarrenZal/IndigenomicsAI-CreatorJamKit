---
name: telus-hermes-backends
description: Use when setting up, verifying, or troubleshooting Hermes Agent with TELUS OpenAI-compatible backends or the Indigenomics Gateway for Creator Jam workflows. Covers GPT OSS, Gemma, and Qwen endpoint configuration, Gateway tool calling, safe secret handling, verification commands, and model choice.
---

# TELUS Hermes Backends

Use this skill when an operator asks to run Hermes Agent against TELUS-hosted models or the Indigenomics Gateway.

Do not commit TELUS API keys, participant Gateway keys, `.env` files, request dumps, logs with Authorization headers, or generated `~/.hermes/config.yaml` files that contain secrets.

For deeper model-choice, reasoning, context, tool-use, and parameter guidance, read `references/hermes-telus-operator-guide.md`.

## Decision

- Use the **Creator Jam Gateway** for participants, student API examples, and Gateway-mediated Hermes sessions.
- Use **direct TELUS model endpoints** for staff/operator diagnostics or when Gateway policy, rate limits, or event access gates should be bypassed.
- The Indigenomics Gateway must support OpenAI-style tool calling for Hermes: `tools`, `tool_choice`, `parallel_tool_calls`, assistant `tool_calls`, tool-result messages, and streamed tool-call deltas.

## TELUS model map

| Hermes label | Base URL | Model |
|---|---|---|
| `telus-gpt-oss` | `https://ollama-gpt-oss-120b-0b50s.paas.ai.telus.com/v1` | `gpt-oss:120b` |
| `telus-gemma` | `https://gemma-4-31b-it-2-0b50s.paas.ai.telus.com/v1` | `google/gemma-4-31b-it` |
| `telus-qwen` | `https://qwen-0b50s.paas.ai.telus.com/v1` | `Qwen/Qwen3.6-35B-A3B` |

Keys are per TELUS service. Set them outside the repo:

```bash
export TELUS_GPT_OSS_KEY='...'
export TELUS_GEMMA_KEY='...'
export TELUS_QWEN_KEY='...'
```

Model selection guidance:

- Prefer `telus-qwen` for complex reasoning, coding, decomposition, and multi-step tool use. Use `max_tokens` of at least `4096` for operator work; raise it further for long-form generation.
- Prefer `telus-gemma` for concise writing, extraction, review, and low-latency checks.
- Prefer `telus-gpt-oss` as a broad general fallback when Qwen or Gemma behavior is not ideal for the task.

## Configure Hermes

Preferred: write the active Hermes config from environment variables using the helper:

```bash
python3 skills/telus-hermes-backends/scripts/write_hermes_telus_config.py qwen
python3 skills/telus-hermes-backends/scripts/write_hermes_telus_config.py gemma
python3 skills/telus-hermes-backends/scripts/write_hermes_telus_config.py gpt-oss
```

The script writes to `${HERMES_HOME:-~/.hermes}/config.yaml`.

Set a repo working directory for terminal tools when needed:

```bash
python3 skills/telus-hermes-backends/scripts/write_hermes_telus_config.py qwen --cwd /path/to/repo --max-tokens 4096
```

Manual config shape:

```yaml
model:
  provider: custom
  default: Qwen/Qwen3.6-35B-A3B
  base_url: https://qwen-0b50s.paas.ai.telus.com/v1
  api_key: "<TELUS_QWEN_KEY>"
  api_mode: chat_completions
  context_length: 262144
  max_tokens: 4096

agent:
  max_turns: 90

display:
  streaming: false
  show_reasoning: false
  tool_progress: off
```

For Gemma or GPT OSS, change `default`, `base_url`, and `api_key` to the matching row above.

Gateway-mediated Hermes config shape:

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

Use the public Gateway model id, such as `telus-qwen`, when the base URL is the Gateway.

## Verify

Run a simple chat check:

```bash
hermes chat \
  --query 'Reply READY only.' \
  --max-turns 1 \
  --quiet
```

Run a tool-loop check:

```bash
hermes chat \
  --toolsets terminal \
  --query 'Use the terminal to run pwd, then tell me the directory.' \
  --max-turns 4 \
  --quiet \
  --yolo
```

Expected result: Hermes reports a directory and the session summary includes tool calls.

## Troubleshooting

- `401` or `403`: wrong key for that TELUS service, wrong endpoint, missing `Bearer` auth, or a stale copied key.
- Empty Qwen content with `finish_reason=length`: raise `max_tokens`; use at least `4096` for Qwen/Hermes work.
- Hermes works for chat but not tools through the Gateway: regression. Confirm the Gateway is forwarding request `tools` fields and preserving streamed `tool_calls` deltas.
- `System message must be at the beginning`: the Gateway or proxy is inserting another system message after Hermes' system message. Merge all system messages into the first message before forwarding.
- `OPENAI_API_KEY` interpolation in `model.api_key` may not be reliable across Hermes versions. Write the config with the helper script in an operator-owned Hermes home.
