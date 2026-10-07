#!/usr/bin/env bash
# The human-approval flow over A2A, end to end:
#   1. ask sre-operator for a change (k8s_scale is in its requireApproval list)
#   2. the task pauses in state input-required with a pending adk_request_confirmation call
#   3. send the decision (approve or reject) on the same contextId and taskId
#   4. the task continues and completes
# Usage: scripts/approval-demo.sh [approve|reject] [request text] [file tag]
# Writes results/answers/sre-operator/<tag>-{1,2}.json.
set -euo pipefail
KAGENT="${KAGENT:-http://127.0.0.1:8083}"
A="$KAGENT/api/a2a/kagent/sre-operator/"
DECISION="${1:-approve}"
REQUEST="${2:-Scale the deployment web in namespace demo-broken to 3 replicas.}"
TAG="${3:-approval}"
OUT=results/answers/sre-operator; mkdir -p "$OUT"

send() { curl -s -m 600 -X POST "$A" -H 'Content-Type: application/json' -d "$1"; }

echo "== 1. request the change"
R1=$(send "$(jq -n --arg m "appr-$(date +%s)" --arg q "$REQUEST" '{jsonrpc:"2.0",id:"1",method:"message/send",params:{message:{role:"user",kind:"message",messageId:$m,parts:[{kind:"text",text:$q}]}}}')")
echo "$R1" > "$OUT/$TAG-1.json"
TASK=$(echo "$R1" | jq -r '.result.id'); CTX=$(echo "$R1" | jq -r '.result.contextId'); STATE=$(echo "$R1" | jq -r '.result.status.state')
echo "task=$TASK context=$CTX state=$STATE"
echo "pending call:"; echo "$R1" | jq -c '.result.status.message.parts[]?|select(.kind=="data")|.data' | cut -c1-400
[ "$STATE" = "input-required" ] || { echo "expected input-required, got $STATE"; exit 1; }

echo "== 2. send the decision: $DECISION"
R2=$(send "$(jq -n --arg m "dec-$(date +%s)" --arg c "$CTX" --arg t "$TASK" --arg d "$DECISION" '{jsonrpc:"2.0",id:"2",method:"message/send",params:{message:{role:"user",kind:"message",messageId:$m,contextId:$c,taskId:$t,parts:[{kind:"data",data:{decision_type:$d}},{kind:"text",text:($d|ascii_upcase)}]}}}')")
echo "$R2" > "$OUT/$TAG-2.json"
echo "state=$(echo "$R2" | jq -r '.result.status.state')"
echo "$R2" | jq -r '[.result.artifacts[]?.parts[]?.text]|last // "(no artifact)"'
