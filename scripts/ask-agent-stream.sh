#!/usr/bin/env bash
# Same as ask-agent.sh but over message/stream (server-sent events), for agents
# whose work takes longer than the controller's 180-second wait on message/send
# (the orchestrator, which calls other agents in turn). Collects every event,
# keeps the final task state and the artifact text.
#
#   ./scripts/ask-agent-stream.sh <agent-name> <id> "<question>"
set -euo pipefail
KAGENT="${KAGENT:-http://127.0.0.1:8083}"; NS="${NS:-kagent}"
agent="$1"; id="$2"; question="$3"
out="results/answers/$agent"; mkdir -p "$out"
body=$(jq -n --arg t "$question" --arg m "$id-$(date +%s)" \
  '{jsonrpc:"2.0", id:"1", method:"message/stream",
    params:{message:{role:"user", kind:"message", messageId:$m, parts:[{kind:"text", text:$t}]}}}')
start=$(date +%s)
curl -sN -m 1800 -X POST "$KAGENT/api/a2a/$NS/$agent/" -H 'Content-Type: application/json' \
  -H 'Accept: text/event-stream' -d "$body" | sed -n 's/^data: //p' > "$out/$id.events.jsonl"
secs=$(( $(date +%s) - start ))
# final state: last status-update event; answer: concatenated artifact text parts
state=$(jq -rs '[.[].result|select(.kind=="status-update")]|last|.status.state // "no-status"' "$out/$id.events.jsonl")
jq -rs '[.[].result|select(.kind=="artifact-update")|.artifact.parts[]?|select(.kind=="text")|.text]|join("")' "$out/$id.events.jsonl" > "$out/$id.answer.txt"
{
  echo "Agent: $agent"; echo "Q: $question"; echo "State: $state (${secs}s, streamed)"; echo
  cat "$out/$id.answer.txt"
} > "$out/$id.txt"
# tool calls the orchestrator made (its sub-agents appear as tools)
calls=$(jq -rs '[.[].result|select(.kind=="status-update")|.status.message.parts[]?|select(.kind=="data" and .metadata.kagent_type=="function_call")|.data.name]|group_by(.)|map("\(.[0])×\(length)")|join(" ")' "$out/$id.events.jsonl")
echo "$agent/$id  $state  ${secs}s  tools: $calls"
