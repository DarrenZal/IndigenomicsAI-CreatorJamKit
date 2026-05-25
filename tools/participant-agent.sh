#!/usr/bin/env bash
# participant-agent.sh — wrap `claude -p` with the kit's participant-agent-context bundle pre-loaded.
#
# A small jam-day helper. Participants run this on their laptops to get a Claude instance
# that's already been given the Creator Jam knowledge bundle and one of the three system prompts.
#
# Usage:
#     ./participant-agent.sh [spec-drafting | boundary-checker | witness-drafter]
#
# Then type your question (or paste it). Hit Ctrl-D to send.
#
# Requires:
#     - `claude` CLI installed and authenticated
#     - This script run from the kit repo root (so participant-agent-context/ is at ./participant-agent-context/)
#
# Standard utilities only. Read-only on the bundle files.

set -e

MODE="${1:-spec-drafting}"

# Determine kit root (allow running from anywhere if KIT_ROOT is set)
if [ -n "$KIT_ROOT" ]; then
    KIT="$KIT_ROOT"
elif [ -d "./participant-agent-context" ]; then
    KIT="$PWD"
elif [ -d "$HOME/projects/IndigenomicsAI-CreatorJamKit/participant-agent-context" ]; then
    KIT="$HOME/projects/IndigenomicsAI-CreatorJamKit"
else
    echo "error: cannot find participant-agent-context/. Run from the kit repo root, or set KIT_ROOT." >&2
    exit 2
fi

CTX="$KIT/participant-agent-context"

if [ ! -d "$CTX" ]; then
    echo "error: $CTX does not exist" >&2
    exit 2
fi

# Build the system prompt by concatenating the bundle files
case "$MODE" in
    spec-drafting)
        PROMPT_HEADER="You are a Spec Drafting Partner. See your system prompt below, in PROMPTS_FOR_AGENTS.md §1."
        ;;
    boundary-checker)
        PROMPT_HEADER="You are a Boundary Discipline Checker. See your system prompt below, in PROMPTS_FOR_AGENTS.md §2."
        ;;
    witness-drafter)
        PROMPT_HEADER="You are a Witness Record Drafter. See your system prompt below, in PROMPTS_FOR_AGENTS.md §3."
        ;;
    *)
        echo "error: unknown mode '$MODE'. Use: spec-drafting | boundary-checker | witness-drafter" >&2
        exit 2
        ;;
esac

# Compose the context bundle
{
    echo "# Creator Jam Participant Agent — Context Bundle"
    echo ""
    echo "$PROMPT_HEADER"
    echo ""
    echo "Read the entire context below carefully, then wait for the user's query."
    echo ""
    echo "---"
    echo ""
    cat "$CTX/PROMPTS_FOR_AGENTS.md"
    echo ""
    echo "---"
    echo ""
    cat "$CTX/carol-anne-voice.md"
    echo ""
    echo "---"
    echo ""
    cat "$CTX/25-themes-summary.md"
    echo ""
    echo "---"
    echo ""
    cat "$CTX/compositional-field-orientation.md"
    echo ""
    echo "---"
    echo ""
    cat "$CTX/ruddick-cpp-primer.md"
    echo ""
    echo "---"
    echo ""
    cat "$CTX/johar-discipline.md"
    echo ""
    echo "---"
    echo ""
    echo "USER QUERY FOLLOWS. Read the entire bundle above first."
    echo ""
    cat -  # read from stdin
} | claude -p --model sonnet

echo ""
echo "---"
echo "Boundary: this agent's output is one LLM's response. It does not certify, approve,"
echo "or authorize anything. Your team's judgment remains the deciding voice."
