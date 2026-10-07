#!/usr/bin/env bash
# Runs every line of scripts/scenarios.txt through scripts/ask-agent.sh and
# prints one summary line per scenario. Needs the controller port-forward:
#   kubectl -n kagent port-forward svc/kagent-controller 8083:8083
set -euo pipefail
grep -v '^#' scripts/scenarios.txt | while IFS='|' read -r agent id question; do
  [ -z "$agent" ] && continue
  ./scripts/ask-agent.sh "$agent" "$id" "$question"
done
