#!/usr/bin/env bash
# Continues a paused (input-required) orchestrator task over message/stream.
#   ./scripts/orchestrator-continue.sh <id> <contextId> <taskId> approve            # approve a pending tool call
#   ./scripts/orchestrator-continue.sh <id> <contextId> <taskId> answer "<choice>"  # answer an ask_user question
# Appends the new events to results/answers/sre-orchestrator/<id>.events.jsonl and rewrites <id>.txt.
set -euo pipefail
KAGENT="${KAGENT:-http://127.0.0.1:8083}"; A="$KAGENT/api/a2a/kagent/sre-orchestrator/"
id="$1"; ctx="$2"; task="$3"; mode="$4"; choice="${5:-}"
out=results/answers/sre-orchestrator
if [ "$mode" = "answer" ]; then
  data=$(jq -n --arg c "$choice" '{decision_type:"approve", ask_user_answers:[{answer:[$c]}]}')
  text="$choice"
else
  data='{"decision_type":"approve"}'; text="Approved"
fi
body=$(jq -n --arg m "$id-$mode-$(date +%s)" --arg c "$ctx" --arg t "$task" --argjson d "$data" --arg x "$text" \
  '{jsonrpc:"2.0", id:"1", method:"message/stream", params:{message:{role:"user", kind:"message", messageId:$m, contextId:$c, taskId:$t,
    parts:[{kind:"data", data:$d},{kind:"text", text:$x}]}}}')
start=$(date +%s)
curl -sN -m 1800 -X POST "$A" -H 'Content-Type: application/json' -H 'Accept: text/event-stream' -d "$body" | sed -n 's/^data: //p' >> "$out/$id.events.jsonl"
secs=$(( $(date +%s) - start ))
state=$(jq -rs '[.[].result|select(.kind=="status-update")]|last|.status.state // "no-status"' "$out/$id.events.jsonl")
jq -rs '[.[].result|select(.kind=="artifact-update")|.artifact.parts[]?|select(.kind=="text")|.text]|join("")' "$out/$id.events.jsonl" > "$out/$id.answer.txt"
{ echo "Agent: sre-orchestrator"; grep -m1 '^Q:' "$out/$id.txt" 2>/dev/null || true; echo "State: $state (continued, +${secs}s)"; echo; cat "$out/$id.answer.txt"; } > "$out/$id.txt.new" && mv "$out/$id.txt.new" "$out/$id.txt"
echo "$id  $state  +${secs}s"
jq -rs '[.[].result|select(.kind=="status-update" and .status.state=="input-required")]|last|.status.message.parts[]?|select(.kind=="data")|.data.args.originalFunctionCall|{name,args}' "$out/$id.events.jsonl" 2>/dev/null | head -c 500
