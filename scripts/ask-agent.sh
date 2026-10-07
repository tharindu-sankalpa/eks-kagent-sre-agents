#!/usr/bin/env bash
# Sends one question to a kagent agent over A2A, through the kagent
# controller, and writes the raw JSON-RPC response and the answer text to
# results/answers/<agent>/<id>.{json,txt}.
#
#   ./scripts/ask-agent.sh <agent-name> <id> "<question>"
#
# Needs: kubectl -n kagent port-forward svc/kagent-controller 8083:8083
set -euo pipefail

KAGENT="${KAGENT:-http://127.0.0.1:8083}"
NS="${NS:-kagent}"
agent="$1"; id="$2"; question="$3"
out="results/answers/$agent"; mkdir -p "$out"

body=$(jq -n --arg t "$question" --arg m "$id-$(date +%s)" \
  '{jsonrpc:"2.0", id:"1", method:"message/send",
    params:{message:{role:"user", kind:"message", messageId:$m,
                     parts:[{kind:"text", text:$t}]}}}')
start=$(date +%s)
curl -s -m 600 -X POST "$KAGENT/api/a2a/$NS/$agent/" \
  -H 'Content-Type: application/json' -d "$body" > "$out/$id.json"
secs=$(( $(date +%s) - start ))
state=$(jq -r '.result.status.state // .result.task.status.state // .error.message // "no-task"' "$out/$id.json")
{
  echo "Agent: $agent"
  echo "Q: $question"
  echo "State: $state (${secs}s)"
  echo
  jq -r '[(.result.artifacts // .result.task.artifacts // [])[].parts[]?.text] | last // "(no text artifact)"' "$out/$id.json"
} > "$out/$id.txt"
echo "$agent/$id  $state  ${secs}s"
