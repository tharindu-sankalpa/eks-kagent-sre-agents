# Diagram prompts

Image prompts for the diagrams used in the README, setup guide and article. Each is generated with an image model and saved in this folder under the file name given. The prompts ask for no title inside the image; the caption in the document does that job.

Colours and shapes are the same across all of them:

| Component | Shape | Colour |
|---|---|---|
| kagent and kmcp controllers, cluster boundary, Kubernetes objects | Rounded rectangle / large boundary box | Sky blue #0288d1 |
| Agents | Rectangle with a thin darker left accent bar | Sky blue #0288d1 |
| MCP tool servers | Rounded rectangle | Amber #f57f17 |
| LLM provider (OpenRouter) | Cloud with spark icon | Deep purple #6a1b9a |
| PostgreSQL | Tall cylinder | Forest green #2d7d32 |
| Prometheus / Grafana | Rounded rectangle | Warm grey #546e7a |
| Human / client | Person silhouette | Dark grey |
| Broken workloads | Rounded rectangle with a thin red outline | Light red #ffebee fill |

Every number below comes from the live system: 124 tools on the tool server, 65 on the Grafana server, 4 on netprobe, 1 on fetch, 1 on querydoc; seven agents; five models; five broken workloads. The story runs through the orchestrator: one request from an SRE, delegated to specialists, with a human approval gate in front of every change.

---

## 01-system-overview.jpg

Where it is used: README, setup guide opening, article opening.

```
A clean, flat-design software architecture diagram on a pure white background, landscape orientation.
No title or heading text anywhere in the image; the diagram starts at the top edge.
Overall visual style: flat minimalist corporate vector art, crisp sans-serif font (Inter), no shadows, no gradients, no textures.

SPATIAL LAYOUT: Three vertical zones. Left zone, 14% of the width: the people and clients. Center zone, 66% of the width: one large rounded-corner boundary box with a thin sky blue (#0288d1) outline and a small header label at its top-left reading "Amazon EKS 1.34: kagent-sre-lab (2 x t3.xlarge, ap-south-1)". Right zone, 20% of the width: the model provider.

Inside the cluster box, four horizontal bands top to bottom, separated by thin light grey lines, each with a small grey label at its left edge: "kagent control plane", "orchestrator", "specialist agents", "tool servers and targets".

ELEMENTS:
Left zone, top: a dark grey person silhouette labeled beneath "SRE" with an 8pt caption "kagent UI / Postman / curl". Left zone, bottom: a small dark grey laptop icon labeled "kubectl apply" with an 8pt caption "YAML in git".

Band 1, left to right: a sky blue (#0288d1) rounded rectangle labeled in white "kagent controller 0.9.10" with an 8pt caption "A2A :8083, REST API, MCP /mcp"; a sky blue rounded rectangle labeled in white "kagent UI"; a sky blue rounded rectangle labeled in white "kmcp controller 0.3.0"; a forest green (#2d7d32) tall cylinder labeled beneath "PostgreSQL" with an 8pt caption "sessions, tasks".

Band 2: one wide sky blue rectangle with a thin darker left accent bar, centered, labeled in white bold "sre-orchestrator", with an 8pt caption "claude-sonnet-5.5 · no Kubernetes tools · its tools are the six agents below · prompt from a ConfigMap".

Band 3: six sky blue rectangles of equal size in a row, each with a thin darker left accent bar. Labels in white, with an 8pt caption under each:
"cluster-troubleshooter" caption "read-only · deepseek-v4.1-flash";
"observability-analyst" caption "PromQL + Grafana · gemini-3.8-flash";
"runbook-assistant" caption "docs + fetch · claude-sonnet-5.5";
"release-manager" caption "Helm · kimi-k3";
"incident-reporter" caption "bring your own container";
"sre-operator" caption "changes need approval · grok-4.7".
The "incident-reporter" rectangle has a dashed outline instead of solid, to mark it as the one that is code. The "sre-operator" rectangle has a small dark grey person silhouette drawn on its top edge, to mark the approval gate.

Band 4, left to right: three amber (#f57f17) rounded rectangles labeled in white "kagent-tools" caption "124 tools (k8s, helm, prometheus, ...)", "grafana-mcp" caption "65 tools", "netprobe-mcp" caption "4 tools, built here, run by kmcp"; two smaller amber rounded rectangles labeled "fetch" caption "run by kmcp" and "querydoc" caption "labelled Service". Then a warm grey (#546e7a) rounded rectangle labeled in white "Prometheus + Grafana" caption "namespace monitoring". Then a rounded rectangle with a thin red outline and light red (#ffebee) fill labeled "demo-broken" with five small lines of dark text "api: bad image", "worker: crash loop", "cache: OOMKilled", "checkout: no endpoints", "batch: unschedulable".

Right zone: a deep purple (#6a1b9a) cloud with a spark icon, labeled beneath "OpenRouter" with an 8pt caption "5 models, 1 API key".

CONNECTIONS:
A thick solid red-orange (#e64a19) arrow from the SRE silhouette to "sre-orchestrator", labeled "one request (A2A)".
A thin solid red-orange arrow from the laptop icon to "kagent controller 0.9.10", labeled "Agent, ModelConfig, MCPServer YAML".
Six thin solid red-orange arrows fanning out from the bottom of "sre-orchestrator" to each of the six specialist rectangles, with one shared label at the fan's origin reading "delegates (A2A, type: Agent tools)".
A thick dashed steel blue (#1976d2) arrow from the row of specialists down to "kagent-tools", labeled "MCP tools/call".
A thin dashed steel blue arrow from "observability-analyst" down to "grafana-mcp" and on to "Prometheus + Grafana", labeled "PromQL".
A thin dashed steel blue arrow from "incident-reporter" down to "netprobe-mcp", labeled "probes".
A thin dashed steel blue arrow from "kagent-tools" to "demo-broken", labeled "Kubernetes API".
A thin solid red-orange arrow from "kmcp controller 0.3.0" down to "netprobe-mcp" and "fetch", labeled "runs MCPServer resources".
A thick solid red-orange arrow from the right edge of bands 2 and 3, leaving the cluster box, to the purple cloud, labeled "chat completions with tools".

CALLOUT BOXES: A yellow (#fff9c4) box with a thin border at the bottom-left reading "Six agents are YAML only. One is a container. The orchestrator is YAML too: its tool list is six agent names."

LEGEND: a small box in the bottom-right corner listing: sky blue square "kagent / kmcp / agent", amber square "MCP tool server", purple square "LLM provider", green square "PostgreSQL", grey square "monitoring", red-outlined square "broken workloads", person on an edge "human approval", solid red-orange line "request", dashed steel blue line "tool call".

Overall aesthetic: professional whitepaper.
```

---

## 02-orchestrator-delegation.jpg

Where it is used: article, "The key concept" section; README.

```
A clean, flat-design sequence-style diagram on a pure white background, landscape orientation.
No title or heading text anywhere in the image; the diagram starts at the top edge.
Overall visual style: flat minimalist corporate vector art, crisp sans-serif font (Inter), no shadows, no gradients, no textures.

SPATIAL LAYOUT: Five equal-width columns left to right, each with a shape at the top and a thin light grey vertical line running down to the bottom of the frame.

ELEMENTS, column headers left to right:
Column 1: a dark grey person silhouette, label beneath "SRE".
Column 2: a sky blue (#0288d1) rectangle with a thin darker left accent bar, label in white "sre-orchestrator", 8pt caption "tools = six agents".
Column 3: a sky blue rectangle with a thin darker left accent bar, label in white "cluster-troubleshooter", 8pt caption "read-only k8s tools".
Column 4: a sky blue rectangle with a thin darker left accent bar, label in white "sre-operator", 8pt caption "k8s_scale under approval".
Column 5: an amber (#f57f17) rounded rectangle, label in white "kagent-tools", 8pt caption "124 tools".

CONNECTIONS, horizontal arrows ordered top to bottom, each with a numbered dark circle at its start:
1. Thick solid red-orange (#e64a19) arrow from column 1 to column 2, labeled "fix the web service so checkout has endpoints".
2. Medium solid red-orange arrow from column 2 to column 3, labeled "why does checkout have no endpoints?".
3. Medium dashed steel blue (#1976d2) arrow from column 3 to column 5, labeled "k8s_get_resources, k8s_get_events".
4. Medium dashed steel blue arrow from column 5 back to column 3, labeled "selector app=checkout, pods app=web".
5. Medium dashed steel blue arrow from column 3 back to column 2, labeled "diagnosis + fix".
6. Medium dashed steel blue arrow from column 2 to column 1, labeled "input-required: ask_user: patch selector to app=web? (3 choices)"; a small dark grey person silhouette sits on the column 1 line at this height.
7. Thick solid red-orange arrow from column 1 to column 2, labeled "answer: yes, patch the selector".
8. Medium solid red-orange arrow from column 2 to column 4, labeled "patch Service checkout selector to app=web".
9. Medium dashed steel blue arrow from column 4 back through column 2 to column 1, labeled "input-required: k8s_patch_resource(...)"; a second small dark grey person silhouette sits on the column 1 line at this height.
10. Thick solid red-orange arrow from column 1 through column 2 to column 4, labeled "decision_type: approve".
11. Medium dashed steel blue arrow from column 4 to column 5, labeled "k8s_patch_resource".
12. Medium dashed steel blue arrow from column 4 back to column 2, labeled "patched, endpoints: 3".
13. Thick dashed steel blue arrow from column 2 to column 1, labeled "what was wrong, evidence, change made, rollback, specialists used".

CALLOUT BOXES: A yellow (#fff9c4) box with a thin border at the bottom-center reading "Three client calls, 62 seconds, two human decisions, one change. The orchestrator never touches the cluster."

LEGEND: a small box in the bottom-right corner listing: sky blue square "agent", amber square "tool server", person icon "human approval", solid red-orange line "request", dashed steel blue line "response or tool call".

Overall aesthetic: clean technical reference map.
```

---

## 03-agent-anatomy.jpg

Where it is used: article, "What an agent is made of" section.

```
A clean, flat-design diagram on a pure white background, landscape orientation.
No title or heading text anywhere in the image; the diagram starts at the top edge.
Overall visual style: flat minimalist corporate vector art, crisp sans-serif font (Inter), no shadows, no gradients, no textures.

SPATIAL LAYOUT: Left half, 45% width: one white document-shaped card with a thin sky blue (#0288d1) outline, a folded top-right corner, and a header label "Agent: sre-operator". Right half, 55% width: four rounded rectangles stacked vertically with space between them.

ELEMENTS:
The card holds four blocks of small monospaced text, each block with a small numbered dark circle at its left:
Block 1: "modelConfig: grok-4-7"
Block 2: "systemMessage: |" then "  Diagnose before you act." then "  Make the smallest change." then "  Never touch kube-system."
Block 3: "tools:" then "  toolNames: k8s_get_resources," then "    k8s_get_events, k8s_scale," then "    k8s_rollout, k8s_patch_resource, ..."
Block 4: "  requireApproval: k8s_scale," then "    k8s_rollout, k8s_patch_resource, ..."

Right half, top to bottom:
A deep purple (#6a1b9a) rounded rectangle labeled in white "ModelConfig grok-4-7" with an 8pt caption "provider OpenAI, baseUrl openrouter.ai, Secret kagent-openrouter".
A light grey rounded rectangle labeled "system prompt" with an 8pt caption "sent with every model call".
An amber (#f57f17) rounded rectangle labeled in white "kagent-tools: 124 tools" with a white inner panel labeled "offered to the model: 11" and an 8pt caption "everything else is invisible to the agent".
A sky blue (#0288d1) rounded rectangle labeled in white "approval gate" with a small dark grey person silhouette beside it and an 8pt caption "task state: input-required until a human approves or rejects".

CONNECTIONS:
Four thin solid red-orange (#e64a19) arrows, one from each numbered block on the card to the matching rectangle on the right, labeled "1", "2", "3", "4".
A thin dashed steel blue (#1976d2) arrow from the amber rectangle to the approval gate, labeled "6 of the 11 tools".

CALLOUT BOXES: A yellow (#fff9c4) box with a thin border at the bottom-center reading "kubectl apply this file and the controller creates a Deployment, a Service and an A2A endpoint. Nothing else is written."

LEGEND: a small box in the bottom-right corner listing: sky blue square "kagent resource / gate", purple square "model", amber square "tool server", grey square "prompt".

Overall aesthetic: clean technical reference map.
```

---

## 04-kmcp-two-ways.jpg

Where it is used: article, kmcp building block; setup guide steps 7 and 10.

```
A clean, flat-design comparison diagram on a pure white background, landscape orientation.
No title or heading text anywhere in the image; the diagram starts at the top edge.
Overall visual style: flat minimalist corporate vector art, crisp sans-serif font (Inter), no shadows, no gradients, no textures.

SPATIAL LAYOUT: Two columns of equal width separated by a thin vertical light grey line. Each column is a left-to-right chain: a document card, then a pod box, then a Service box. Above each column a medium bold header: left "stdio package, no image built", right "your own server, built with kmcp".

LEFT COLUMN ELEMENTS:
A white document card with a thin sky blue (#0288d1) outline, header "MCPServer: fetch", and four lines of small monospaced text "transportType: stdio", "cmd: uvx", "args: mcp-server-fetch", "port: 3000".
A large rounded rectangle with a thin sky blue outline, header "Pod: fetch". Inside, left: a small light grey rounded rectangle labeled "init: copy-binary" caption "agentgateway 0.9.0". Inside, right: a light grey rounded rectangle labeled "container" caption "image: uv:debian (default)", containing two stacked boxes: a teal (#00695c) rounded rectangle "agentgateway" caption ":3000/mcp" above an amber (#f57f17) rounded rectangle "uvx mcp-server-fetch" caption "stdin / stdout".
A sky blue rounded rectangle labeled in white "Service fetch :3000".

RIGHT COLUMN ELEMENTS:
A white document card with a thin sky blue outline, header "MCPServer: netprobe-mcp", and four lines of small monospaced text "transportType: http", "image: <ECR>/netprobe-mcp:0.1.0", "cmd: python src/main.py --transport http", "port: 3000".
A large rounded rectangle with a thin sky blue outline, header "Pod: netprobe-mcp". Inside, one light grey rounded rectangle labeled "container" caption "image from ECR", containing one amber rounded rectangle "FastMCP server" caption "4 tools, serves :3000/mcp itself".
A sky blue rounded rectangle labeled in white "Service netprobe-mcp :3000".
Above the right column's document card, a small row of three light grey pills in a line labeled "kmcp init", "kmcp build --push", "kubectl apply", connected by thin grey arrows pointing right.

CONNECTIONS, both columns:
A medium solid red-orange (#e64a19) arrow from the document card to the pod, labeled "kmcp controller".
A thin dashed steel blue (#1976d2) double-headed arrow between "agentgateway" and "uvx mcp-server-fetch" in the left pod, labeled "stdio".
A medium dashed steel blue arrow from the Service back into the pod, labeled "HTTP /mcp".
Below both columns, one sky blue rounded rectangle centered, labeled in white "kagent controller", with two thin dashed steel blue arrows going up to the two Services, each labeled "tools/list".

CALLOUT BOXES: A yellow (#fff9c4) box with a thin border at the bottom-left reading "Same resource kind, same Service shape, same discovery by kagent. The difference is whether kmcp has to adapt stdio to HTTP."

LEGEND: a small box in the bottom-right corner listing: sky blue square "Kubernetes object", teal square "agentgateway adapter", amber square "MCP server process", solid red-orange line "create", dashed steel blue line "MCP traffic".

Overall aesthetic: professional whitepaper.
```

---

## 05-approval-flow.jpg

Where it is used: article, "The key concept" section.

```
A clean, flat-design sequence-style diagram on a pure white background, landscape orientation.
No title or heading text anywhere in the image; the diagram starts at the top edge.
Overall visual style: flat minimalist corporate vector art, crisp sans-serif font (Inter), no shadows, no gradients, no textures.

SPATIAL LAYOUT: Four equal-width columns left to right, each with a shape at the top and a thin light grey vertical line running down to the bottom of the frame.

ELEMENTS, column headers left to right:
Column 1: a dark grey person silhouette, label beneath "SRE".
Column 2: a sky blue (#0288d1) rounded rectangle, label in white "kagent controller", 8pt caption "/api/a2a/kagent/sre-operator/".
Column 3: a sky blue rectangle with a thin darker left accent bar, label in white "sre-operator", 8pt caption "model: grok-4.7".
Column 4: an amber (#f57f17) rounded rectangle, label in white "kagent-tools", 8pt caption "k8s_scale".

CONNECTIONS, horizontal arrows ordered top to bottom, each with a numbered dark circle at its start:
1. Thick solid red-orange (#e64a19) arrow from column 1 to column 2, labeled "message/send: scale web to 3".
2. Medium solid red-orange arrow from column 2 to column 3, labeled "forward".
3. A small deep purple (#6a1b9a) cloud icon on the column 3 line with an 8pt caption "model decides: k8s_scale(web, 3)".
4. Medium dashed steel blue (#1976d2) arrow from column 3 back to column 1, passing through column 2, labeled "task: input-required, adk_request_confirmation".
A yellow (#fff9c4) callout attached to the column 1 line at this height reading "The SRE reads the pending call and its arguments."
5. Thick solid red-orange arrow from column 1 to column 3, passing through column 2, labeled "message/send: decision_type approve, same taskId".
6. Medium dashed steel blue arrow from column 3 to column 4, labeled "tools/call k8s_scale".
7. Medium dashed steel blue arrow from column 4 back to column 3, labeled "deployment.apps/web scaled".
8. Thick dashed steel blue arrow from column 3 to column 1, passing through column 2, labeled "task: completed".

At the bottom-left, a light red (#ffebee) box with dark text reading "A reject sends decision_type: reject. The tool never runs and the model is told why."

LEGEND: a small box in the bottom-right corner listing: solid red-orange line "request", dashed steel blue line "response or tool call", purple cloud "model call".

Overall aesthetic: clean technical reference map.
```

---

## 06-byo-agent-loop.jpg

Where it is used: article, "Bring your own agent" section.

```
A clean, flat-design diagram on a pure white background, landscape orientation.
No title or heading text anywhere in the image; the diagram starts at the top edge.
Overall visual style: flat minimalist corporate vector art, crisp sans-serif font (Inter), no shadows, no gradients, no textures.

SPATIAL LAYOUT: Left 30% of the width: a tall sky blue (#0288d1) rounded rectangle labeled in white "kagent controller" with an 8pt caption "A2A /api/a2a/kagent/incident-reporter/". Center 40%: one large rounded rectangle with a dashed sky blue outline and a header "Pod: incident-reporter (BYO image)". Right 30%: three stacked boxes.

ELEMENTS:
Inside the pod box, two parts stacked vertically. Top: a light grey rounded rectangle labeled "A2A server (a2a-sdk 0.3)" with an 8pt caption "port 8080, /.well-known/agent-card.json, JSON-RPC at /". Bottom: a white panel with a thin dark outline labeled "agent.py: the loop", containing a circular arrangement of four small boxes connected clockwise by thin dark arrows: "1 send messages to model" at 12 o'clock, "2 tool calls?" at 3 o'clock (a diamond shape), "3 run tools over MCP, append results" at 6 o'clock, "4 no tool calls: answer" at 9 o'clock. An arrow from the diamond labeled "yes" goes to box 3, and an arrow from box 3 goes back up to box 1 labeled "next turn". An arrow from the diamond labeled "no" goes to box 4.

Right column, top to bottom: a deep purple (#6a1b9a) cloud with a spark icon labeled "OpenRouter" caption "deepseek-v4.1-flash, tool calling"; an amber (#f57f17) rounded rectangle labeled in white "kagent-tools" caption "6 read-only k8s tools allowed"; an amber rounded rectangle labeled in white "netprobe-mcp" caption "4 probe tools".

CONNECTIONS:
A thick solid red-orange (#e64a19) arrow from "kagent controller" to the A2A server box, labeled "message/send".
A thin solid red-orange arrow from the A2A server box down to the loop panel, labeled "user text".
A medium solid red-orange arrow from box 1 of the loop to the purple cloud, labeled "chat.completions with tool schemas".
A medium dashed steel blue (#1976d2) arrow from box 3 of the loop to "kagent-tools", labeled "tools/call".
A medium dashed steel blue arrow from box 3 of the loop to "netprobe-mcp", labeled "tools/call".
A thick dashed steel blue arrow from the A2A server box back to "kagent controller", labeled "task: completed, artifact: report".

CALLOUT BOXES: A yellow (#fff9c4) box with a thin border at the bottom-left reading "No framework. Tool schemas come from the MCP servers' tools/list and are passed to the model unchanged."

LEGEND: a small box in the bottom-right corner listing: sky blue square "kagent", grey square "A2A SDK server", amber square "MCP server", purple cloud "model", solid red-orange line "request", dashed steel blue line "tool call or response".

Overall aesthetic: clean technical reference map.
```
