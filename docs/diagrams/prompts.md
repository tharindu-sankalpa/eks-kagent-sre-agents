# Diagram prompts

Raster-image prompts for the README, setup guide and article. Generate each image separately and save it in this folder under the section's file name. Document captions supply the title; do not add a decorative title inside the image.

Select **16:9 landscape in the generator settings**, not just in the prompt. Use the highest available resolution so labels remain readable after embedding. Earlier outputs ignored the requested aspect ratio; check the exported dimensions.

## How every prompt is built

Each prompt has the same sections, in this order. The generator prints only quoted labels; everything else is direction.

1. **Opening line:** what the image is, 16:9 landscape, "all directions below are private; print only the quoted labels and captions".
2. **VISUAL STYLE — PRIVATE:** canvas, panels, type, fills, what to avoid, which element is the focal point.
3. **ICONS — PRIVATE** (where components have icons): one icon per component, same stroke and size, icons are identifiers inside cards and never extra nodes, no invented logos or mascots.
4. **SPATIAL LAYOUT AND EXACT LABELS — PRIVATE:** the regions and every quoted label and caption, in order.
5. **VISUAL CONNECTIONS — PRIVATE:** arrow styles with hex colours, then every arrow with its start card, end card and label, exact counts, and the list of elements that have no connectors.
6. **LEGEND — VISIBLE:** the exact rows, each once.
7. **FINAL CHECK — PRIVATE, DO NOT PRINT:** the counts and the forbidden things, so the generator can self-check.

Private text is layout instruction. Do not print coordinates, percentages, node IDs, section headings or words such as "layer", "gutter", "lifeline" or "passive platform". An earlier output printed "Left Zone 14%" on the canvas. Use pale fills with dark text for longer labels. Avoid tiny captions and fixed point sizes; name two tiers only, component name and caption, and say "clearly readable".

## Palette and shapes

One palette across the set. Colour aids scanning; labels, icons and line styles carry the meaning.

| Component | Shape | Accent | Fill |
|---|---|---|---|
| sre-orchestrator (orchestration) | Agent card, coloured left accent | Indigo #4F46E5 | #EEF2FF |
| cluster-troubleshooter (Kubernetes diagnosis) | Agent card | Blue #2563EB | #EFF6FF |
| observability-analyst (observability) | Agent card | Teal #0F766E | #F0FDFA |
| runbook-assistant (runbooks and documentation) | Agent card | Violet #7C3AED | #F5F3FF |
| release-manager, sre-operator (changes, approval-gated) | Agent card plus person-and-check badge | Amber #B45309 | #FFFBEB |
| incident-reporter (custom agent) | Agent card with a dashed border | Cyan #0E7490 | #ECFEFF |
| MCP tool servers | Rounded rectangle, amber left accent | Amber #B45309 | white; group #FFFCF5 |
| agentgateway adapter (diagram 04 only) | Rounded rectangle | Teal #0F766E | #F0FDFA |
| kagent / kmcp controllers, Kubernetes objects, cluster boundary | Rounded rectangle | Slate-blue #475569 | near-white |
| PostgreSQL | Cylinder | Green #15803D | #F0FDF4 |
| Prometheus / Grafana | Rounded rectangle | Teal #0F766E | pale teal |
| OpenRouter | Cloud | Purple #6D28D9 | #F5F3FF |
| Broken workloads, warnings, rejection evidence | Rectangle with red outline | Red #B91C1C | #FFF1F2 |
| Human / client | Person silhouette | Dark slate #0F172A | none |
| Pause / human decision band | Horizontal band | none | Pale yellow #FEF9C3 |
| Code excerpt | Monospace card | Slate #475569 | #F8FAFC |

Arrows and lines, the same in every diagram:

| Meaning | Style |
|---|---|
| Request, invocation, delegation, resource reconciliation | Medium solid indigo #4F46E5 |
| Result, pause, tool call, infrastructure access, MCP traffic | Thinner dashed steel-blue #0369A1 |
| Model call | Solid purple #6D28D9 |
| Build or apply workflow, startup dependency | Thin grey #94A3B8 |

Approval badge: a small person-and-check mark on release-manager and sre-operator only. It means a human approves before execution, not automatic approval. The dashed cyan border marks the bring-your-own runtime, not a future component.

## Facts the diagrams carry

The counts describe the recorded build: 124 tools on kagent-tools, 65 on grafana-mcp, 4 on netprobe-mcp, 1 on fetch and 1 on querydoc; seven agents, five model configurations and five fault scenarios. Counts describe server inventories, not the tools offered to every agent. The operator's six mutating tools and the release manager's three mutating Helm tools are approval-gated. The custom agent sees six Kubernetes tools and four probes. Every number in a prompt is in the README, the runtime reference or a manifest; do not round or invent.

Each image has one job. The overview (01) shows delegation and tool access; 02 shows delegation with approval through the orchestrator; 03 explains configuration; 04 explains deployment; 05 explains direct approval; 06 explains the custom loop. Keeping these concerns separate avoids dense, misleading connector networks.

## Reviewing an output

Before accepting an image, check every arrow's source, destination and direction against the real system, then the labels and counts, then the legend rows. A polished image can still describe the wrong system. Review each generated image before generating the next. When attaching an earlier output as a reference, tell the generator to follow the prompt's connector endpoints and not to copy stray lines from the reference.

Known failure modes from this set: printed layout text; a legend row repeated; an arrow whose visible origin is the group outline under the wrong card; a third arrow into a target that should have two; curved fan-outs that are hard to count; saturated fills on cards meant to be pale; a brand-like mark invented beside the cluster label.

---

## 00: no separate cover

The Medium title image and the LinkedIn image are page 1 of the LinkedIn document post, specified in [linkedin-carousel.md](../linkedin-carousel.md). A generated cover and a script-rendered cover were both tried and dropped: the generator produced an unlabelled wireframe, and the rendered one was a bare org chart. A carousel cover can lean on its title text and is judged at the same size as the other pages.

---

## 01-system-overview.jpg

Where it is used: README, setup guide opening, article opening.

Visual direction: use the latest regenerated image as a reference for the component inventory and four-layer layout. The new prompt gives agents distinct role accents, adds functional icons, and makes the orchestrator the focal point. Keep configuration and deployment in their dedicated diagrams. When attaching the reference image, tell the generator to follow the prompt's connector endpoints rather than copying ambiguous lines from the reference.

The role colours below refine the shared agent style for this overview. Use the same role accents when generating the other diagrams; agent cards retain the same shape across roles. Colour is an aid to scanning, while labels, icons and line styles carry the meaning.

```text
Create a polished technical architecture illustration of a multi-agent system for SRE workflows on Amazon EKS. Output a high-resolution 16:9 landscape raster image. All directions below are private; print only the quoted labels and captions. No extra title, layout terminology or invented text.

VISUAL STYLE — PRIVATE:
Use a white canvas, near-white group panels, crisp sans-serif typography such as Inter, consistent rounded corners, fine borders and generous whitespace. Text is dark slate #0F172A; secondary text is #475569. Component names are medium bold, captions smaller but clearly readable. Wrap long agent names onto two lines without abbreviating them. Avoid condensed type, tiny footnotes, broad grey backgrounds, heavy black outlines, gradients, 3D objects, glows and decorative textures.

Use colour deliberately: saturated colour on small icons, left accent bars and outlines; very pale tinted fills on cards. Do not turn entire layers into large blocks of saturated colour. Give the orchestrator the strongest border and largest name; tool servers and platform cards remain visually quieter. Flat cards and restrained colour should feel like a carefully designed engineering publication.

Use this exact role palette:
- Orchestrator: indigo #4F46E5, fill #EEF2FF.
- Kubernetes diagnosis: blue #2563EB, fill #EFF6FF.
- Observability: teal #0F766E, fill #F0FDFA.
- Runbooks and documentation: violet #7C3AED, fill #F5F3FF.
- Release and operating changes: amber #B45309, fill #FFFBEB.
- Custom incident reporter: cyan #0E7490, fill #ECFEFF.
- MCP server category: amber #B45309 accent on white cards; group fill #FFFCF5.
- Cluster and controllers: slate-blue #475569 / #2563EB, near-white fill.
- Database: green #15803D, fill #F0FDF4.
- Fault scenarios: muted red #B91C1C, fill #FFF1F2.
- Model provider: purple #6D28D9, fill #F5F3FF.

ICONS — PRIVATE:
Place one small, simple line icon beside each component name, not behind its text. Use the same icon size, stroke weight and visual style throughout. Agent role icons: branching hub for orchestrator; magnifying glass over a small Kubernetes wheel for troubleshooter; chart for observability; open book for runbook; package for release; clipboard with pulse line for incident reporter; wrench for operator. Server icons: toolbox for kagent-tools; connected network nodes for netprobe; globe with download arrow for fetch; document with magnifying glass for querydoc; dashboard for grafana-mcp. Platform icons: container stack for kmcp, cylinder for PostgreSQL, small connected nodes for kagent. Use a person for SRE, cloud with spark for OpenRouter, small warning triangle for demo-broken, chart for monitoring and Kubernetes wheel beside the cluster label.
Icons are identifiers inside cards, not additional nodes. Do not invent brand logos or add mascot robots. Put a separate small person-and-check badge on release-manager and sre-operator only; this badge means human approval, not automatic approval. Retain their explicit approval captions.

SPATIAL LAYOUT AND EXACT LABELS — PRIVATE:
Draw a large, thin slate-blue rounded cluster boundary, occupying most of the canvas. At its top, place the large bold label "Amazon EKS 1.34 · kagent-sre-lab", with subtitle "2 × t3.xlarge · ap-south-1". Keep the cluster interior white. Arrange four well-spaced horizontal layers, with a compact platform strip below them. Put the SRE outside the left boundary and OpenRouter outside the right boundary. Reserve a narrow right gutter for the provider and legend. Make the specialist row wide enough for six readable cards.

Top layer:
- Outside left: person icon "SRE", caption "UI / Postman / curl".
- Inside: compact controller card "kagent controller".
- Then a wider indigo agent card "sre-orchestrator", caption "Its tools are six agents". Second caption line: "No direct Kubernetes or MCP tools".

Second layer: six equal specialist cards in one near-white group boundary, in this left-to-right order. Each has a coloured left accent, pale role fill and its assigned icon:
- Blue "cluster-troubleshooter", caption "Read-only Kubernetes".
- Teal "observability-analyst", caption "PromQL + Grafana".
- Violet "runbook-assistant", caption "Diagnosis + documentation".
- Amber "release-manager", caption "Helm · approval before changes".
- Cyan "incident-reporter", caption "Custom Python loop + A2A SDK". Use a dashed cyan card border to identify the BYO agent; this does not mean a future component.
- Amber "sre-operator", caption "Kubernetes · approval before changes".
Below the cards, inside the group, render: "6 YAML agents use kagent's Google ADK runtime; incident-reporter uses its own loop."

Third layer: five white MCP cards with amber category accents, inside one pale cream group boundary labelled "Selected tools over MCP". Use the assigned server icons. Arrange left to right:
- "kagent-tools", caption "124 tools · Kubernetes / Helm / Prometheus".
- "netprobe-mcp", caption "4 custom network probes".
- "fetch", caption "1 tool".
- "querydoc", caption "1 tool".
- "grafana-mcp", caption "65 tools".
Below the cards, within the group, render two readable lines:
"Each specialist has a selected tool set."
"incident-reporter: netprobe · runbook-assistant: fetch + querydoc · observability-analyst: Grafana"

Fourth layer:
- Left: muted-red card "demo-broken", caption "Bad image · crash loop · OOM · no endpoints · unschedulable". Wrap the caption cleanly if needed.
- Right: pale-teal card "Prometheus + Grafana", caption "namespace monitoring".

Bottom platform strip: three small descriptive cards with subtle neutral outlines and coloured icons:
- "kmcp 0.3.0", caption "Deploys fetch and netprobe MCPServer resources".
- Green cylinder "PostgreSQL", caption "Sessions and tasks".
- "kagent 0.9.10", caption "Controller + UI + agent runtime".
Do not print "passive platform" or other layout instructions as a heading.
Outside right: a small purple cloud "OpenRouter", caption "All 7 agents · 5 models · 1 API key". Wrap its caption rather than shrinking the type.

VISUAL CONNECTIONS — PRIVATE:
Use medium solid indigo #4F46E5 arrows for invocation and delegation, with consistent arrowheads. Use thinner dashed steel-blue #0369A1 arrows for MCP and infrastructure access. Lines run in clear gutters and must not overlap icons, card text or captions. Use short orthogonal paths with gently rounded corners. At crossings, use a small bridge or gap; a crossing is not a junction.

Invocation: one solid indigo arrow from SRE to kagent controller, labelled "A2A"; a second from kagent controller to sre-orchestrator, labelled "A2A invocation". Each arrowhead touches its own destination card.

Delegation: one solid indigo line leaves the bottom of sre-orchestrator and reaches a horizontal branching spine ABOVE the specialist group. Exactly six branches descend from this spine, each ending with an arrowhead on the top of its own specialist card. Centre the shared label "A2A delegation · agents as tools" above the spine. Do not use a tangle of curved fan-out lines.

Aggregate MCP access: draw exactly ONE dashed steel-blue arrow from the bottom-centre boundary of the specialist group to the top-centre boundary of the MCP group, labelled "Selected MCP tools". The arrowhead must stop on the GROUP OUTLINE, not on kagent-tools or any other server card. This is aggregate access; no individual specialist-to-server arrows appear in this overview. No line starts at the orchestrator and ends on an MCP server.

Infrastructure access: draw exactly FOUR dashed steel-blue arrows. Each begins visibly on its named server CARD, not on the containing group outline, and ends on its named target CARD:
1. From the lower-left edge of kagent-tools downward to the top-left of demo-broken; label "Kubernetes API".
2. From the bottom of netprobe-mcp downward to the top-right of demo-broken; label "DNS / TCP / HTTP".
3. From the lower-right edge of kagent-tools, through a reserved horizontal gutter beneath the MCP group, then to the top-left of Prometheus + Grafana; label "Prometheus queries". Its source MUST visibly remain kagent-tools, never fetch or querydoc.
4. From the bottom of grafana-mcp downward to the top-right of Prometheus + Grafana; label "Grafana API".
Keep arrow labels separate from the two access-note lines. Fetch and querydoc have NO outgoing infrastructure arrows. Demo-broken has exactly TWO incoming arrows; monitoring has exactly TWO.

The three platform-strip cards and OpenRouter have NO connectors. They are descriptive context; configuration, deployment, storage and model traffic are omitted here and covered elsewhere. Do not copy stray connector endpoints from a reference image.

LEGEND — VISIBLE:
Place a compact legend below the provider, outside the cluster. Use two small colour-key rows:
Indigo "Orchestration"; blue "Diagnosis"; teal "Observability"; violet "Documentation"; amber "Changes / MCP"; cyan "Custom agent". Exactly six colour rows; no label appears twice and no extra swatch is added.
Then show three samples: solid indigo arrow "Invocation / delegation"; dashed steel-blue arrow "Tool / infrastructure access"; person-and-check badge "Human approval". Dashed card sample: "BYO runtime".
Use short labels and readable type; the legend must not compete with the agent row.

FINAL CHECK — PRIVATE, DO NOT PRINT:
Exactly seven agent cards and five MCP server cards, with counts 124, 4, 1, 1, 65. Exactly six delegation arrowheads. Exactly one group-to-group MCP arrow and four infrastructure arrows with the specified endpoints. No infrastructure arrow from fetch or querydoc; no third incoming arrow to demo-broken. Only release-manager and sre-operator carry human-approval badges. The custom agent stays distinct from the ADK agents. All original labels, counts, versions and fault scenarios remain present. The legend has six colour rows and four samples, each once. Infrastructure arrows start on their server cards, not on the group outline; the Prometheus-queries arrow visibly leaves kagent-tools. The orchestrator and controller cards keep pale fills with dark text. The mark beside the cluster label is a plain Kubernetes wheel, not an invented logo. No decorative extras, accidental connections or private instructions are visible.
```


---

## 02-orchestrator-delegation.jpg

Where it is used: article, "Delegation and approval in one repair" section; README.

What it shows: scenario 15, the repair of the `checkout` Service, as a logical sequence between the SRE and three agents. Controller forwarding and individual MCP reads are omitted; diagram 05 shows the controller hop.

```text
Create a readable sequence diagram of one multi-agent repair with two human pauses. Output a high-resolution 16:9 landscape raster image. All directions below are private; print only the quoted labels and captions. No extra title, layout terminology or invented text.

VISUAL STYLE — PRIVATE:
White canvas, crisp sans-serif typography such as Inter, dark slate #0F172A text, secondary text #475569, fine borders, generous row spacing. Four column headers are cards with a coloured left accent and a very pale fill; the vertical lines below them are thin light grey. Message labels are clearly readable and sit above their arrows. Avoid condensed type, tiny captions, gradients, 3D, glows and textures. The two pause bands are the focal points.

Header palette: SRE is a dark slate person icon with no card. "sre-orchestrator" indigo #4F46E5 accent, fill #EEF2FF. "cluster-troubleshooter" blue #2563EB accent, fill #EFF6FF. "sre-operator" amber #B45309 accent, fill #FFFBEB, with a small person-and-check badge in its top-right corner meaning human approval.

ICONS — PRIVATE:
One small line icon beside each header name, same stroke and size: branching hub for the orchestrator, magnifying glass over a Kubernetes wheel for the troubleshooter, wrench for the operator. Icons are identifiers inside the cards, not extra nodes. No brand logos, no mascots.

SPATIAL LAYOUT AND EXACT LABELS — PRIVATE:
Four equal columns, left to right, each with a header at the top and a thin vertical line to the bottom:
- Person icon, name "SRE", caption "UI / Postman / curl".
- Card "sre-orchestrator", caption "Tools = six agents".
- Card "cluster-troubleshooter", caption "Read-only diagnosis".
- Card "sre-operator", caption "Approval-gated changes".

Twelve horizontal messages in this exact top-to-bottom order, each with a small numbered circle at its start:
1. SRE → sre-orchestrator: "Fix checkout's missing endpoints".
2. sre-orchestrator → cluster-troubleshooter: "Diagnose the Service".
3. cluster-troubleshooter → sre-orchestrator: "Selector app=checkout; pods app=web".
4. sre-orchestrator → SRE: "ask_user: confirm backend".
5. SRE → sre-orchestrator: "Use the web pods".
6. sre-orchestrator → sre-operator: "Patch checkout selector to app=web".
7. sre-operator → sre-orchestrator: "input-required: pending k8s_patch_resource".
8. sre-orchestrator → SRE: "Approve this exact patch?".
9. SRE → sre-orchestrator: "Approve".
10. sre-orchestrator → sre-operator: "Resume with approval".
11. sre-operator → sre-orchestrator: "Patched; 3 endpoints verified".
12. sre-orchestrator → SRE: "Evidence + change + rollback".

Two pale yellow #FEF9C3 bands span all four columns: one behind row 4, labelled at its left edge "Pause 1 · clarify intent"; one behind row 8, labelled "Pause 2 · execution approval". Place a small person icon on the SRE line inside each band. Between rows 10 and 11, on the operator line, a small activity box "MCP patch + verification".

Below the sequence, a readable evidence box with a slate outline:
"3 client exchanges · 62 s of request time · 2 human decisions · 1 patch"
Second line: "Human response time excluded. Three endpoints also confirmed with kubectl."

Below it, a small scope note in secondary text: "Logical agent sequence: controller forwarding and individual MCP reads are omitted. The orchestrator has no direct Kubernetes tools."

VISUAL CONNECTIONS — PRIVATE:
Rows 1, 2, 5, 6, 9 and 10 are medium solid indigo #4F46E5 arrows (requests). Rows 3, 4, 7, 8, 11 and 12 are thinner dashed steel-blue #0369A1 arrows (results and pauses). Every arrow starts on the sender's vertical line and ends with one arrowhead on the recipient's vertical line. No arrow passes through the orchestrator's line to reach another column: the SRE never exchanges a message directly with the troubleshooter or the operator. No arrow touches the troubleshooter after row 3. There is no Kubernetes API or tool-server column. Exactly twelve arrows.

LEGEND — VISIBLE:
A compact legend in the bottom-right corner with exactly four rows: solid indigo arrow "Request"; dashed steel-blue arrow "Result or pause"; pale yellow band "Human decision"; person-and-check badge "Approval before execution".

FINAL CHECK — PRIVATE, DO NOT PRINT:
Four columns, twelve numbered arrows in the given order, six solid and six dashed, two yellow bands at rows 4 and 8, one activity box, one evidence box, one scope note, four legend rows. No arrow from SRE to troubleshooter or operator. No arrow from the operator to the SRE. The pending patch at row 7 is executed only after rows 9 and 10; clarification at row 5 does not authorise execution. No printed layout words, no title, no decorative extras.
```

---

## 03-agent-anatomy.jpg

Where it is used: article, "Defining an agent in YAML" section.

What it shows: the four fields of the `sre-operator` Agent resource that decide its behaviour, as excerpts paired with explanations. Source: `infra/kagent/agents/sre-operator.yaml` and `infra/kagent/models/grok-4-7.yaml`.

```text
Create a clean explanatory diagram of how one declarative agent is configured. Output a high-resolution 16:9 landscape raster image. All directions below are private; print only the quoted labels, captions and code excerpts. No extra title, layout terminology or invented text.

VISUAL STYLE — PRIVATE:
White canvas, crisp sans-serif typography such as Inter for labels, a clearly readable monospace face for code, dark slate #0F172A text, secondary text #475569, fine borders, consistent rounded corners. Code cards have a #F8FAFC fill and a slate #475569 left accent; explanation cards have a coloured left accent and a very pale fill of their role colour. Avoid condensed type, tiny captions, gradients, 3D and textures. The four code excerpts are the focal points; the explanation cards are quieter.

ICONS — PRIVATE:
One small line icon beside each explanation-card name, same stroke and size: cloud for the model card, document with lines for the instructions card, toolbox for the tool-selection card, person-and-check badge for the approval card. Icons are identifiers inside cards, not extra nodes. No brand logos.

SPATIAL LAYOUT AND EXACT LABELS — PRIVATE:
Above the left column, a bold heading "Agent: sre-operator" and beneath it the prominent subtitle "Selected fields — not a complete manifest". Four horizontal rows below, each with a code card on the left (about two fifths of the width) and an explanation card on the right. Each code card has a small caption above its excerpt. The four excerpts are separate and must not be merged into one YAML document.

ROW 1, model. Code caption "Within spec.declarative", excerpt:
modelConfig: grok-4-7
Explanation card, purple #6D28D9 accent, fill #F5F3FF, name "ModelConfig grok-4-7", caption "OpenAI-compatible API → OpenRouter", second line "Model: x-ai/grok-4.7 · Secret: kagent-openrouter".

ROW 2, instructions. Code caption "Within spec.declarative · shortened excerpt", excerpt:
systemMessage: |
  Diagnose before you act.
  Make the smallest change.
Explanation card, slate #475569 accent, near-white fill, name "System instructions", caption "Diagnosis, scope, verification and reporting rules", second line "Instructions guide behaviour; they are not Kubernetes RBAC."

ROW 3, tool selection. Code caption "Within tools[].mcpServer · two examples", excerpt:
toolNames:
  - k8s_get_resources
  - k8s_patch_resource
Explanation card, amber #B45309 accent, white fill, name "kagent-tools: 124 server tools", caption "11 tools offered to sre-operator", second line "Only the configured names enter its tool set."

ROW 4, approval. Code caption "Within tools[].mcpServer · one example", excerpt:
requireApproval:
  - k8s_patch_resource
Explanation card, amber #B45309 accent, fill #FFFBEB, with the person-and-check badge, name "Runtime approval gate", caption "6 of the operator's 11 tools require approval", second line "Pause before execution; resume with approve or reject."

Below the four rows, one wide callout card with a slate outline:
"Apply the complete Agent manifest: kagent creates a Deployment, Service and A2A endpoint."
Second line: "kagent supplies the declarative runtime and tool integration, built on Google ADK."

Small source note in secondary text at the bottom: "Full definition: infra/kagent/agents/sre-operator.yaml".

VISUAL CONNECTIONS — PRIVATE:
Exactly four thin solid indigo #4F46E5 arrows, one per row, each from the right edge of a code card to the left edge of the explanation card in the same row. No arrow connects different rows, and nothing connects to the callout or the source note. Lines must not cross text.

LEGEND — VISIBLE:
A compact legend in the bottom-right corner with exactly three rows: code card sample "YAML excerpt"; person-and-check badge "Human approval before execution"; solid indigo arrow "Field → effect".

FINAL CHECK — PRIVATE, DO NOT PRINT:
Four rows, four code excerpts rendered exactly as given with their indentation, four explanation cards, four arrows, one callout, one source note, three legend rows. The excerpts are not labelled ready to apply. Row 4 does not imply that every selected tool requires approval: six of eleven do. Prompt instructions, the runtime gate and cluster permissions are three different things and stay in their own rows. No printed layout words, no title.
```

---

## 04-kmcp-two-ways.jpg

Where it is used: runtime reference, "kmcp deployment paths"; setup guide steps 7 and 8.

What it shows: the two ways kmcp 0.3.0 ran an MCP server in this build: the public stdio package `fetch` behind an agentgateway adapter, and the custom HTTP server `netprobe-mcp` built with `kmcp build`. Source: `infra/kmcp/*.yaml`, runtime reference "kmcp deployment paths", build record sections 9 and 10.

```text
Create a two-column comparison diagram of two ways to run an MCP server on Kubernetes. Output a high-resolution 16:9 landscape raster image. All directions below are private; print only the quoted labels and captions. No extra title, layout terminology or invented text.

VISUAL STYLE — PRIVATE:
White canvas, two equal near-white column panels, crisp sans-serif typography such as Inter, a readable monospace face for the resource-field lines, dark slate #0F172A text, secondary text #475569, fine borders. Kubernetes objects (resource cards, Deployment / Pod boundaries, Services, controllers) are slate-blue #475569 outlined cards with near-white fill. Server processes are white cards with an amber #B45309 left accent. The agentgateway adapter is a teal #0F766E outlined card with fill #F0FDFA. Avoid saturated fills, gradients, 3D, glows and textures. The two Pod boundaries are the focal points.

ICONS — PRIVATE:
One small line icon per card, same stroke and size: document for each resource card, container stack for each Pod boundary, small connected nodes for both controllers, globe with download arrow for the fetch process, connected network nodes for the FastMCP process, a plain arrow-in-box for the agentgateway adapter, a small hammer for the build step. Icons are identifiers, not nodes. No brand logos.

SPATIAL LAYOUT AND EXACT LABELS — PRIVATE:
Top centre, above both columns: card "kmcp controller 0.3.0", caption "Reconciles MCPServer resources".
Left column heading: "stdio package · no custom image build". Right column heading: "Custom HTTP server · image built with kmcp".

LEFT COLUMN, top to bottom:
- Resource card "MCPServer: fetch", subtitle "Selected resource fields", four monospace lines:
"transportType: stdio"
"deployment.cmd: uvx"
"deployment.args: [mcp-server-fetch]"
"deployment.port: 3000"
- Large boundary "Deployment / Pod: fetch" containing, top to bottom:
  a small grey box "Init container: copy-binary", caption "Copies the agentgateway binary only";
  a main-container boundary "Main container · default image uv:debian" containing two stacked process cards: teal "agentgateway", caption "Serves HTTP /mcp on port 3000"; amber "uvx mcp-server-fetch", caption "Child process · stdin / stdout".
- Below the Pod: card "Service fetch :3000".

RIGHT COLUMN, top to bottom:
- A short preparation row of three grey pills joined by thin grey arrows: "kmcp init" → "kmcp build --push" → "kubectl apply". This row exists only on the right.
- Resource card "MCPServer: netprobe-mcp", subtitle "Selected resource fields", four monospace lines:
"transportType: http"
"deployment.image: ECR / netprobe-mcp:0.1.0"
"deployment.cmd: python · args: src/main.py --transport http"
"deployment.port: 3000"
- Large boundary "Deployment / Pod: netprobe-mcp" containing one amber process card "FastMCP server", caption "Custom image · 4 tools · HTTP :3000/mcp". No init container and no adapter on this side.
- Below the Pod: card "Service netprobe-mcp :3000".

Bottom centre, below both columns: card "kagent controller 0.9.10", caption "MCP discovery".

Bottom callout, full width, slate outline:
"Both expose HTTP MCP to kagent. Only the stdio package needs an adapter."
Second line: "kmcp manages server deployment; kagent discovers and uses the tools."

VISUAL CONNECTIONS — PRIVATE:
Reconciliation: exactly two medium solid indigo #4F46E5 arrows from the bottom of "kmcp controller 0.3.0", one to the top edge of each Pod boundary, each labelled "Reconciles MCPServer → Deployment + Service". They end on the boundary, not on a process inside it.
Resource to Pod: exactly two thin grey #94A3B8 arrows, one per column, from the resource card down to its Pod boundary, unlabelled.
Stdio: one thin dashed steel-blue #0369A1 double-headed arrow between "agentgateway" and "uvx mcp-server-fetch", labelled "stdio". The adapter and the child are in the same main container; the init container has no arrows except the grey resource-to-Pod flow passing beside it.
Service to process: one thin dashed steel-blue arrow from "Service fetch :3000" up to "agentgateway", labelled "HTTP /mcp"; one from "Service netprobe-mcp :3000" up to "FastMCP server", labelled "HTTP /mcp". The left Service never points at the stdio child.
Discovery: exactly two thin dashed steel-blue arrows from "kagent controller 0.9.10", one to each Service card, each labelled "HTTP MCP · tools/list". They do not touch resource cards or processes.
Build workflow: the three pills are joined by thin grey arrows only; a single thin grey arrow from "kubectl apply" to the right resource card, unlabelled.
Nothing else is connected. Lines run in clear gutters and do not cross text. A crossing is drawn as a small bridge, never a junction.

LEGEND — VISIBLE:
A compact legend in the bottom-right corner with exactly five rows: solid indigo arrow "Resource reconciliation"; dashed steel-blue arrow "MCP traffic"; thin grey arrow "Build / apply workflow"; teal card "agentgateway adapter"; amber card "MCP server process".

FINAL CHECK — PRIVATE, DO NOT PRINT:
Two columns, two resource cards with four lines each, two Pod boundaries, two Services, two controllers, exactly two reconciliation arrows, two discovery arrows, two Service arrows, one stdio arrow, one build row on the right only. agentgateway is a main-container process, not a sidecar and not the init container. fetch runs on kmcp's default image without a custom build; netprobe-mcp has no adapter. Resource cards show selected fields, not complete manifests. Five legend rows, each once. No printed layout words, no title.
```

---

## 05-approval-flow.jpg

Where it is used: runtime reference, "A2A discovery, invocation and continuation".

What it shows: the approval gate exercised directly against `sre-operator` through the controller, as recorded by `scripts/approval-demo.sh`: an approved scale from 2 to 3 replicas, and a separate rejected scale from 3 to 2.

```text
Create a readable sequence diagram of a human-approved tool call. Output a high-resolution 16:9 landscape raster image. All directions below are private; print only the quoted labels and captions. No extra title, layout terminology or invented text.

VISUAL STYLE — PRIVATE:
White canvas, crisp sans-serif typography such as Inter, dark slate #0F172A text, secondary text #475569, fine borders, generous row spacing. Column headers are cards with a coloured left accent and a very pale fill; vertical lines below them are thin light grey. Message labels are clearly readable and sit above their arrows. Avoid condensed type, tiny captions, gradients, 3D, glows and textures. The pause band is the focal point. Reserve the lower part of the canvas for a separate rejection box.

Header palette: "SRE / client" is a dark slate person icon with no card. "kagent controller" slate-blue #475569 accent, near-white fill. "sre-operator" amber #B45309 accent, fill #FFFBEB, with a small person-and-check badge in its top-right corner. "kagent-tools" white card with an amber #B45309 left accent.

ICONS — PRIVATE:
One small line icon beside each header name, same stroke and size: small connected nodes for the controller, wrench for the operator, toolbox for kagent-tools. Icons are identifiers inside the cards, not extra nodes. No brand logos.

SPATIAL LAYOUT AND EXACT LABELS — PRIVATE:
Four equal columns, left to right, each with a header and a thin vertical line:
- Person icon, name "SRE / client", caption "Postman / curl".
- Card "kagent controller", caption "/api/a2a/kagent/sre-operator/".
- Card "sre-operator", caption "requireApproval: k8s_scale".
- Card "kagent-tools", caption "MCP tool server".

Ten horizontal messages in this exact top-to-bottom order, each with a small numbered circle at its start:
1. SRE / client → kagent controller: "message/send: scale web to 3".
2. kagent controller → sre-operator: "Forward request".
Below row 2, on the operator line, a small activity box "Model selects k8s_scale(web, 3)".
3. sre-operator → kagent controller: "input-required: adk_request_confirmation".
4. kagent controller → SRE / client: "Pending call + arguments".
Between rows 4 and 5, a pale yellow #FEF9C3 band spanning all four columns, labelled at its left edge "Paused · tool has not executed". Place a small person icon on the client line inside the band.
5. SRE / client → kagent controller: "decision_type: approve · same task + context".
6. kagent controller → sre-operator: "Resume with approval".
7. sre-operator → kagent-tools: "tools/call: k8s_scale".
8. kagent-tools → sre-operator: "web scaled to 3".
9. sre-operator → kagent controller: "Verification + completed result".
10. kagent controller → SRE / client: "task: completed".

Below the sequence, clearly separate, a box with a red #B91C1C outline and fill #FFF1F2, heading "Separate rejection test":
"Request: scale web from 3 to 2 → pending confirmation → reject"
"No mutating tool call; replicas remain 3."

Two small notes in secondary text under the rejection box:
"Controller endpoint: /api/a2a/kagent/sre-operator/"
"Direct operator invocation. Diagram 02 shows approval propagated through an orchestrator."

VISUAL CONNECTIONS — PRIVATE:
Rows 1, 2, 5, 6 and 7 are medium solid indigo #4F46E5 arrows (requests). Rows 3, 4, 8, 9 and 10 are thinner dashed steel-blue #0369A1 arrows (results and pauses). Every arrow starts on the sender's line and ends with one arrowhead on the recipient's line; no arrow passes through the controller to another column as if forwarding were one hop. The first and only arrow into kagent-tools is row 7, below the yellow band. Verification reads are summarised in row 9, not drawn. Exactly ten arrows. The rejection box has no arrows.

LEGEND — VISIBLE:
A compact legend in the bottom-right corner with exactly four rows: solid indigo arrow "Request"; dashed steel-blue arrow "Result or pause"; pale yellow band "Human decision"; person-and-check badge "Approval before execution".

FINAL CHECK — PRIVATE, DO NOT PRINT:
Four columns, ten numbered arrows in the given order, five solid and five dashed, one activity box, one yellow band between rows 4 and 5, one rejection box, two notes, four legend rows. Nothing reaches kagent-tools before row 7. No automatic approval, no bypass around the band, no second branch for the same scale-to-3 call: the rejection is a separate later request. No printed layout words, no title.
```

---

## 06-byo-agent-loop.jpg

Where it is used: article, "Custom agent: owning the tool-calling loop" section.

What it shows: the incident-reporter container: an A2A SDK server (`server.py`), a startup discovery step, and the hand-written tool-calling loop (`agent.py`) with its two MCP servers and its model. Source: `byo/incident-reporter-agent/src/`, runtime reference "The model tool-calling loop" and "The custom agent boundary".

Layout note: two generations attached the model call to the nearest box and reversed the report return. The placement below puts every connector's two ends next to each other, so the shortest line is the correct one. Keep the positions exactly.

```text
Create a precise flowchart of a custom agent's tool-calling loop inside one container. Output a high-resolution 16:9 landscape raster image. All directions below are private; print only the quoted labels and captions. No extra title, layout terminology, letters or invented text.

VISUAL STYLE — PRIVATE:
White canvas, crisp sans-serif typography such as Inter, dark slate #0F172A text, secondary text #475569, fine borders, consistent rounded corners. The container boundary is a large dashed cyan #0E7490 rounded rectangle with fill #ECFEFF. Inside it, the server box and the setup box are slate-blue #475569 outlined cards with near-white fill and dark text, and the loop panel is a near-white panel with a slate outline. Flow boxes inside the loop are white with a thin slate outline; the diamond is white with a cyan outline; the terminal box has a cyan #0E7490 left accent. External cards: "OpenRouter" purple #6D28D9 outline with fill #F5F3FF; "kagent-tools" and "netprobe-mcp" white with an amber #B45309 left accent. Avoid saturated fills, gradients, 3D, glows and textures. The loop panel is the focal point.

ICONS — PRIVATE:
One small line icon per card, same stroke and size: small connected nodes for the kagent controller, server rack for the A2A server box, plug for the setup box, clipboard with pulse line beside the container name, cloud for OpenRouter, toolbox for kagent-tools, connected network nodes for netprobe-mcp. Icons are identifiers, not nodes. No brand logos.

SPATIAL LAYOUT AND EXACT LABELS — PRIVATE:
Three vertical regions: a narrow left region outside the container, the wide container in the centre, and a narrow right region outside the container.

Left region, two cards stacked with a large gap between them:
- Top: card "kagent controller", caption "A2A /api/a2a/kagent/incident-reporter/". It sits level with the server box.
- Bottom: card "OpenRouter", caption "deepseek-v4.1-flash". It sits level with the first loop step, and nothing else is on the left side.

Container, name at top-left "incident-reporter · BYO container", caption "Python 3.12 · a2a-sdk 0.3 · no agent framework". Inside, top row, two boxes:
- Left: box "server.py · A2A SDK server", caption "Port 8080 · JSON-RPC at /".
- Right: box "Startup: connect MCP · tools/list · select allowed tools", caption "Once, before requests are served". It sits level with the two MCP cards on the right, not with OpenRouter.
Below the top row, a wide panel "agent.py · custom tool-calling loop" containing five flow shapes arranged as a rectangle:
- Top-left of the panel: rectangle "Send messages + tool schemas to model". This is the first step; it is the closest shape to OpenRouter.
- Top-right of the panel: diamond "Tool calls returned?".
- Right side, below the diamond: rectangle "Record assistant tool-call message".
- Bottom-right of the panel: rectangle "Run each MCP call + append matched tool result". This is the closest shape to the two MCP cards.
- Bottom-left of the panel, directly below the first step: terminal box "Return final text". This is the closest shape to the server box's lower edge.
Inside the panel, between the first step and the terminal box, a small readable limits note:
"Up to 20 model turns · each tool result capped at 12,000 characters"
Second line: "Turn limit returns a stop message; server exceptions mark the task failed."

Right region, two cards stacked: "kagent-tools", caption "6 read-only tools selected from 124"; below it "netprobe-mcp", caption "4 probe tools". They sit level with the Startup box and the bottom-right loop step.

Below the container, a full-width callout with a slate outline: "MCP supplies tool schemas; Python owns message history, routing, execution and termination."
Under it, a small protocol note in secondary text: "Agent card: /.well-known/agent-card.json".

VISUAL CONNECTIONS — PRIVATE:
Exactly fifteen connectors. Each is listed with its style, its two ends and its label. Nothing else is connected; in particular the callout, the protocol note, the limits note and the container boundary have no connectors.

Between the controller and the server, exactly two: one medium solid indigo #4F46E5 arrow "kagent controller" → "server.py · A2A SDK server", labelled "message/send"; one thinner dashed steel-blue #0369A1 arrow "server.py · A2A SDK server" → "kagent controller", labelled "Working updates + completed report", drawn beside the first, not as a double head on it.

From the server into the loop, one medium solid indigo arrow server → "Send messages + tool schemas to model", labelled "User text".

Out of the loop to the server, one dashed steel-blue arrow "Return final text" → "server.py · A2A SDK server", labelled "Report text → A2A artifact". Its arrowhead is on the server box. It runs up the left side of the panel, outside the loop edges. It never points at "Return final text".

Startup, thin grey #94A3B8: two dashed double-headed connectors, "Startup: connect MCP · tools/list · select allowed tools" ↔ "kagent-tools" and the same box ↔ "netprobe-mcp", each labelled "Discover schemas"; one thin grey arrow from the Startup box down to "Send messages + tool schemas to model", labelled "Tool definitions ready". No connector runs between the server box and the Startup box.

Model call, one solid purple #6D28D9 double-headed connector between "Send messages + tool schemas to model" and "OpenRouter", labelled "chat.completions". It crosses the container's left boundary. OpenRouter has no other connector; in particular it is never joined to the Startup box, to the server box or to the MCP cards.

Tool execution, two dashed steel-blue double-headed connectors, "Run each MCP call + append matched tool result" ↔ "kagent-tools" and the same box ↔ "netprobe-mcp", each labelled "tools/call + result". They cross the container's right boundary and are blue, so they differ visibly from the grey discovery connectors to the same cards.

Loop edges, thin solid cyan #0E7490 inside the panel, five in total: "Send messages + tool schemas to model" → "Tool calls returned?"; "Tool calls returned?" → "Record assistant tool-call message", labelled "Yes"; "Record assistant tool-call message" → "Run each MCP call + append matched tool result"; "Run each MCP call + append matched tool result" → "Send messages + tool schemas to model", labelled "Next turn", running along the bottom and up the left inside the panel; "Tool calls returned?" → "Return final text", labelled "No", running down the middle of the panel. The "Next turn" edge is the only edge that returns to the first step. "Return final text" has no outgoing edge inside the panel.

Lines run in gutters and do not cross text; a crossing is a small bridge, never a junction. No two connectors share a label.

LEGEND — VISIBLE:
A compact legend in the bottom-right corner, outside the container, with exactly five rows: solid indigo arrow "Request"; dashed steel-blue arrow "Result or tool call"; solid purple arrow "Model call"; thin grey arrow "Startup discovery"; dashed cyan card sample "BYO container".

FINAL CHECK — PRIVATE, DO NOT PRINT:
One container boundary, one "kagent controller" card and one "OpenRouter" card on the left, one server box, one Startup box, one loop panel with five shapes, two MCP cards on the right, one callout, one note, five legend rows. Fifteen connectors: two between controller and server, one server → first step, one terminal → server, two grey discovery pairs plus one grey dependency, one purple model connector on the first step only, two blue execution pairs on the bottom-right step only, five cyan loop edges. Exactly one "message/send" label. The purple connector touches OpenRouter and the first step and nothing else. The report arrow's head is on the server box. Discovery connectors are grey; execution connectors are blue; both reach both MCP cards. No line joins the callout. No letters A to E are printed. No tool execution on the "No" branch. No printed layout words, no title.
```
