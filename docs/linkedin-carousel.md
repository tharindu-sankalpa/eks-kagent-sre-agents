# LinkedIn carousel: brief and page content

A document post on LinkedIn is a PDF that the feed renders as a swipeable carousel. This file is the complete brief for that PDF: how to produce it, the style, and the exact text, excerpts and numbers of every page. Every fact below comes from the README, the manifests and the recorded results; nothing in the pages should be changed or added by the design tool.

The PDF is the first of three layers. It is a presentation-style tour of the whole project that takes five to ten minutes without reading anything else. The [article](article.md) is the second layer, with the reasoning, the method and the full results. The repository is the third: setup guide, build record, runtime reference, manifests, code and raw responses. The last page says so.

Repository: https://github.com/tharindu-sankalpa/eks-kagent-sre-agents

## How to produce it

Give the design tool this file and, if it can read the repository, the repository itself. Then:

1. Check every page against this file: numbers, names, YAML lines, arrow directions. The tool must not add facts.
2. Export as PDF, 16 pages, A4 portrait (210 × 297 mm; 2480 × 3508 px at 300 dpi, or vector), no margins beyond the page's own padding. A4 is a deliberate choice so the same file works as a document outside LinkedIn; LinkedIn fits each page to the feed width.
3. Name the file `multi-agent-sre-on-eks.pdf`. LinkedIn shows the file name as the document title in the feed.
4. Post it with the text from [linkedin-post.md](linkedin-post.md). Links inside the PDF are not clickable on LinkedIn, so the article and repo URLs go in the post text, and pages 1 and 16 write the repo URL out plainly.

## What the first version got wrong

A first version was generated from an earlier eight-page brief. Keep these fixes:

- Page 2 drew the six specialists as two columns with double-headed arrows between each pair, which reads as specialists calling each other. Each specialist gets its own branch from the spine, with one arrowhead on the card and none between cards.
- Page 2's caption broke "ap-south-1" across two lines. The caption is now two fixed lines.
- Page 3's footnote ran off the page under a 23-line excerpt. Excerpts now start at `spec:` and no page carries more than 16 lines of code.
- The cover did not say what the system is for or what it is built with. It now does, with the repository URL.
- The cover said nothing about where the tools come from. It now has a fourth point on the tool servers, and a cover illustration.
- There was no page on how the work was tested and no page on where to read more by the time available. Pages 13 and 16 add them.
- The diagram boxes and arrows were hairlines. Cards now have 3 px outlines and arrows are 3 px with solid heads.
- "Six agents are YAML. One is a container." blurred the two agent types kagent has. The cover now names them, page 2 marks which agent is which, and a new page 5 explains Declarative versus BYO from the resource definition.
- There was no evidence from the live system. Six screenshot crops are now placed on pages 3, 6, 8, 10 and 12. The two from the AWS console come first, on page 3, so the platform is visible before the YAML.

---

## Brief for the design tool

Design a 16-page document for a LinkedIn document post (PDF carousel) that also works as a stand-alone A4 document. Pages are A4 portrait, 210 × 297 mm. It is read inside the LinkedIn feed at phone width, so everything is large relative to the page: body text at least 1/36 of the page width, captions and code at least 1/45 of the page width (on a 2480 px wide page: 68 px and 55 px). Each page is one slide of a presentation: one idea, read in twenty to thirty seconds. No page has more than one diagram, and no page has more than one code card unless this brief shows two (pages 5 and 7). Use only the text given below; do not add, reword, shorten or invent any sentence, number, file name or YAML line. Do not add stock imagery or photographs, and no illustration other than the cover illustration described under Style. If a page does not fit, do not shrink the type below the minimums; report which page overflowed.

### Style

- Canvas #FAFAFA. Text #0F172A, secondary text #475569. A thin rule in #4F46E5 across the top of every page.
- Each page has three fixed elements: a small-caps kicker in indigo #4F46E5 at the top left (letter-spaced, about 1/50 of the page width), a bold headline below it (about 1/18 of the page width, two lines at most), and a page number "n/16" bottom right in secondary text.
- Typeface: one clean sans-serif such as Inter for everything except code; a monospace such as JetBrains Mono for code. Consistent sizes across pages.
- Accent colours, used only for small marks, left accent bars, arrows and one highlighted phrase per headline: indigo #4F46E5 (orchestration, requests), blue #2563EB (diagnosis), amber #B45309 (changes that need approval), cyan #0E7490 (the custom agent), steel-blue #0369A1 (results and tool calls, dashed). Fills on cards are very pale tints of the same colours; never a saturated block.
- Diagram cards: white fill, a solid 3 px outline in dark slate #334155, 12 px radius, a 6 px coloured left accent bar, and the name in bold. Cards must read as solid boxes, not hairline frames. Arrows are 3 px, with a filled triangular head about 14 px long at the destination only: solid indigo for requests and delegation, dashed steel-blue for results. No double-headed arrows anywhere.
- Screenshots: the crops in `docs/screenshots/crops/` are placed as-is, full column width, inside a card with the same 3 px slate outline and 12 px radius, never re-cropped, recoloured or annotated. The console crops are cut so that the AWS header, the service breadcrumb and the left navigation stay visible: the page must read as the AWS console, and the kagent crops keep the kagent navigation bar for the same reason. Screenshot text may be smaller than body text; the caption beneath each one carries the facts.
- Code cards: a dark card #1E293B with light text, a header line in the card naming the file, no line numbers, and the lines named under each excerpt highlighted with a faint amber band. Keep the YAML indentation exactly as given. Comments after `#` are part of the excerpt.
- A small person-and-check mark means "a human approves before this runs"; it appears only where the text says so.
- Cover illustration: page 1 carries one illustration in the top two fifths of the page, drawn as vector shapes in the palette above: a large indigo disc with six smaller discs below it in the six agent colours (the fifth dashed cyan), joined by a spine with six branches, two of the discs carrying the person-and-check mark, over a faint dot grid, with soft pale tinted halos behind the discs for depth. No text inside the illustration. No photographs, stock imagery, robots, brains, circuit traces or glowing networks. It is the only illustration in the document.
- Technology marks: the cover carries three badges for Amazon EKS, kagent and kmcp. Use each project's official mark unaltered, at the same height, on a white badge with the name beside it. If a mark is not available, use a text badge with the name only. No other logos anywhere.
- Plenty of empty space.

### Page 1 · cover

Kicker: `MULTI-AGENT SYSTEM · SRE WORKFLOWS ON AMAZON EKS`

Headline: `A multi-agent system for SRE workflows on Amazon EKS with kagent and kmcp` (highlight "kagent and kmcp" in indigo)

Standfirst, one paragraph in secondary text, about 34 px: `An orchestrator uses six specialist agents as tools to diagnose Kubernetes faults and coordinate repairs. A human approves every change, including changes requested by another agent.`

Three numbered lines, large numerals in indigo:

1. **Six agents are declarative, one is bring-your-own.** Declarative: YAML that kagent's runtime executes. BYO: a container that speaks A2A.
2. **The orchestrator's tools are the other agents.** It has no Kubernetes tools of its own.
3. **Every change pauses for a human.** The gate held even when one agent called another.
4. **Tools come from MCP servers, not from agent code.** kagent's built-in server with 124 Kubernetes, Helm and Prometheus tools; servers deployed by kmcp; and one written here, four network probes in Python, containerised and deployed the same way.

A row of three technology badges: `Amazon EKS 1.34`, `kagent 0.9.10`, `kmcp 0.3.0`.

Repository line, monospace, about 28 px: `github.com/tharindu-sankalpa/eks-kagent-sre-agents`

Footer line in indigo italic: `A ten-minute tour. The article has the reasoning; the repository has everything. Swipe →`

### Page 2 · the system

Kicker: `THE SYSTEM`

Headline: `One request, six specialists, five tool servers` (highlight "six specialists" in indigo)

Diagram, top to bottom, centred:

- Row 1: a person mark labelled `SRE`, a solid indigo arrow labelled `A2A` to a card `kagent controller`, a solid indigo arrow down to a wide indigo-accent card `sre-orchestrator` with caption `Its tools are six agents`.
- Row 2: one indigo line leaves the bottom of the orchestrator to a horizontal spine labelled `A2A delegation · agents as tools`. From the spine, six separate branches go down, each ending with one arrowhead on the top of its own card. Six small cards in two rows of three, in this order: `cluster-troubleshooter` (blue), `observability-analyst` (teal #0F766E), `runbook-assistant` (violet #7C3AED); `release-manager` (amber, person-and-check mark), `incident-reporter` (cyan, dashed outline), `sre-operator` (amber, person-and-check mark). No arrow joins two specialist cards.
- Row 3: one dashed steel-blue arrow from below the six cards to one wide amber-accent card `5 MCP tool servers`, caption `kagent-tools · grafana-mcp · netprobe-mcp · fetch · querydoc`.
- Row 4: one dashed steel-blue arrow to a plain card `Kubernetes API · Prometheus · Grafana`.

Under the six cards, inside the specialist group, one line in secondary text: `Solid cards: declarative agents on kagent's runtime. Dashed card: bring-your-own container. The orchestrator is declarative too.`

Caption under the diagram, secondary text, exactly two lines:
`Amazon EKS 1.34 · 2 × t3.xlarge · ap-south-1`
`kagent 0.9.10 · kmcp 0.3.0 · models via OpenRouter`

### Page 3 · on the cluster

Kicker: `THE CLUSTER · ON AWS`

Headline: `What it looked like on AWS` (highlight "on AWS" in amber)

Two screenshot cards stacked, full width, each with its caption:

1. `docs/screenshots/crops/aws-eks-console-nodes.png`. Caption: `Amazon EKS console, cluster kagent-sre-lab: two t3.xlarge on-demand nodes in ap-south-1, no node health issues, three minutes after creation.`
2. `docs/screenshots/crops/aws-ecr-console-repos.png`. Caption: `Amazon ECR: the two images built here, incident-reporter-agent and netprobe-mcp, pushed to private repositories in the same region.`

Footnote, secondary text: `Captured on 2026-10-07. The cluster was deleted after the run; the repository keeps every raw response.`

### Page 4 · an agent is a YAML file

Kicker: `STEP 1 · DEFINE AN AGENT`

Headline: `An agent is a YAML file` (highlight "YAML file" in indigo)

Code card, header `infra/kagent/agents/sre-operator.yaml · shortened`:

```yaml
spec:
  type: Declarative
  declarative:
    modelConfig: grok-4-7
    systemMessage: |
      Diagnose before you act.
      Make the smallest change that fixes the problem.
      Every change goes through an approval prompt.
    tools:
      - type: McpServer
        mcpServer:
          kind: RemoteMCPServer
          name: kagent-tool-server
          toolNames: [k8s_get_resources, k8s_scale, k8s_patch_resource]
          requireApproval: [k8s_scale, k8s_patch_resource]
```

Highlight the lines starting `modelConfig:`, `systemMessage:`, `toolNames:` and `requireApproval:`.

Four bullets, field name in bold:

- **modelConfig** names a ModelConfig resource. Page 6.
- **systemMessage** is the prompt. Inline here; a ConfigMap or kagent's snippets elsewhere. Page 7.
- **toolNames** selects from a server's inventory. kagent-tools offers 124 tools; this agent sees 11.
- **requireApproval** lists the calls that pause for a human. Six of the operator's 11.

Footnote, secondary text: `kubectl apply creates the Deployment, Service and A2A endpoint. The pod runs kagent's runtime, built on Google ADK. No code.`

### Page 5 · two kinds of agent

Kicker: `STEP 1 · DECLARATIVE OR BRING YOUR OWN`

Headline: `Two kinds of agent, one resource` (highlight "one resource" in indigo)

Two columns, each a card with a heading, a short code excerpt and three bullets. Left column indigo accent, right column cyan #0E7490 accent with a dashed outline, matching the agent cards on page 2.

Left heading: `type: Declarative` · caption `six agents here, including the orchestrator`

Left code card, header `infra/kagent/agents/sre-operator.yaml · shortened`:

```yaml
spec:
  type: Declarative
  declarative:
    modelConfig: grok-4-7
    systemMessage: |
      ...
    tools: [...]
    # runtime: go   # python is the default
```

Left bullets:

- You write the YAML. The controller creates the Deployment, Service and A2A endpoint.
- The pod runs kagent's runtime, built on Google ADK. `runtime` picks the Python ADK (default) or the Go ADK.
- MCP tools, A2A, sessions and the approval gate come with the runtime.

Right heading: `type: BYO` · caption `one agent here: incident-reporter`

Right code card, header `infra/kagent/agents/incident-reporter.yaml · shortened`:

```yaml
spec:
  type: BYO
  byo:
    deployment:
      image: <ECR>/incident-reporter-agent:0.1.0
      env:
        - name: KAGENT_TOOLS_URL
          value: http://kagent-tools.kagent:8084/mcp
```

Right bullets:

- You point at an image. kagent deploys it and calls it like any other agent.
- The contract is one thing: serve A2A on port 8080. The model, prompt and loop live in the image.
- Any framework that speaks A2A: Google ADK, LangGraph and CrewAI are in kagent's examples. Here it is a plain Python loop with the A2A SDK.

Footnote, secondary text: `Both are the same Agent resource with a different type. Both appear to the orchestrator as tools.`

### Page 6 · the model

Kicker: `STEP 1 · THE MODEL`

Headline: `Five models, one key, one API shape` (highlight "one API shape" in indigo)

Code card, header `infra/kagent/models/grok-4-7.yaml`:

```yaml
apiVersion: kagent.dev/v1alpha2
kind: ModelConfig
metadata:
  name: grok-4-7
spec:
  provider: OpenAI          # OpenRouter speaks the OpenAI API
  model: x-ai/grok-4.7      # OpenRouter model id
  apiKeySecret: kagent-openrouter
  apiKeySecretKey: OPENROUTER_API_KEY
  openAI:
    baseUrl: https://openrouter.ai/api/v1
```

Highlight the lines starting `provider:`, `model:` and `baseUrl:`.

Screenshot card: `docs/screenshots/crops/ui-models-five.png`. Caption: `The five ModelConfigs in the kagent UI. Provider OpenAI on every row: OpenRouter speaks that API.`

Two bullets:

- Every ModelConfig in this build has this shape. Only the name and the model id change.
- One Secret, `kagent-openrouter`, serves all five. An agent picks its model by name.

### Page 7 · the prompts

Kicker: `STEP 1 · THE PROMPTS`

Headline: `Three ways to give an agent its instructions` (highlight "its instructions" in indigo)

Two code cards, stacked.

First card, header `infra/kagent/agents/cluster-troubleshooter.yaml · shortened`:

```yaml
promptTemplate:
  dataSources:
    - kind: ConfigMap
      name: kagent-builtin-prompts
      alias: builtin
systemMessage: |
  You are a Kubernetes troubleshooter for one Amazon EKS cluster.
  {{include "builtin/kubernetes-context"}}
  {{include "builtin/safety-guardrails"}}
```

Highlight the two `{{include` lines.

Second card, header `infra/kagent/agents/sre-orchestrator.yaml · shortened`:

```yaml
systemMessageFrom:
  type: ConfigMap
  name: sre-orchestrator-prompt
  key: system.md
```

Three bullets:

- **Inline.** `systemMessage` holds the text, as on page 4.
- **kagent's snippets.** `promptTemplate` makes the text a template; `{{include}}` pulls the methodology kagent ships for its own agents.
- **A ConfigMap.** `systemMessageFrom` keeps a long prompt as its own object, reviewable in Git without touching the Agent.

### Page 8 · an MCP server

Kicker: `STEP 2 · ADD A TOOL SERVER`

Headline: `An MCP server is a YAML file too` (highlight "YAML file too" in amber)

Code card, header `infra/kmcp/netprobe-mcpserver.yaml · shortened`:

```yaml
apiVersion: kagent.dev/v1alpha1
kind: MCPServer
metadata:
  name: netprobe-mcp
spec:
  transportType: http       # the container serves MCP itself
  httpTransport: { targetPort: 3000, path: /mcp }
  deployment:
    image: <ECR>/netprobe-mcp:0.1.0
    port: 3000
    cmd: python
    args: [src/main.py, --transport, http]
```

Highlight the lines starting `transportType:` and `image:`.

Screenshot card: `docs/screenshots/crops/ui-mcp-five-servers.png`. Caption: `Five tool sources discovered by kagent, 195 tools. fetch and netprobe-mcp are the two that kmcp runs.`

Two bullets:

- `netprobe-mcp` is four network probes written with FastMCP, scaffolded, built and pushed with the kmcp CLI. kmcp turns the resource into a Deployment and a Service.
- A public stdio package needs no image at all: `fetch` runs on kmcp's default image behind an agentgateway adapter.

### Page 9 · three kinds of tool source

Kicker: `STEP 2 · WIRE TOOLS TO AN AGENT`

Headline: `Three kinds of tool source, one field` (highlight "one field" in amber)

Code card, header `infra/kagent/agents/runbook-assistant.yaml · shortened`:

```yaml
tools:
  - type: McpServer
    mcpServer:
      kind: RemoteMCPServer   # kagent's own server, 124 tools
      name: kagent-tool-server
      toolNames: [k8s_get_resources, k8s_get_pod_logs]
  - type: McpServer
    mcpServer:
      kind: MCPServer         # deployed by kmcp
      name: fetch
      toolNames: [fetch]
  - type: McpServer
    mcpServer:
      kind: Service           # labelled kagent.dev/mcp-service
      name: kagent-querydoc
      toolNames: [query_documentation]
```

Highlight the three `kind:` lines.

Three bullets, kind in bold:

- **RemoteMCPServer** points at an MCP endpoint that already exists. kagent's chart registers its tool server and the Grafana server this way.
- **MCPServer** is a server kmcp deploys and runs: `fetch` and `netprobe-mcp`.
- **Service** is any Service carrying the `kagent.dev/mcp-service: "true"` label. Referencing querydoc any other way was rejected.

Footnote, secondary text: `toolNames is the allow-list. A server's inventory is not the agent's tool set.`

### Page 10 · agents as tools

Kicker: `STEP 3 · DELEGATE`

Headline: `The orchestrator's tools are agents` (highlight "are agents" in indigo)

Code card, header `infra/kagent/agents/sre-orchestrator.yaml · shortened`:

```yaml
spec:
  declarative:
    modelConfig: claude-sonnet-5-5
    systemMessageFrom:
      type: ConfigMap
      name: sre-orchestrator-prompt
    tools:
      - type: Agent
        agent: { name: cluster-troubleshooter }
      - type: Agent
        agent: { name: sre-operator }
      # four more specialists
```

Highlight the two `type: Agent` lines.

Screenshot card: `docs/screenshots/crops/k9s-agents-six.png`. Caption: `k9s, Agent resources: six of the seven agents before the orchestrator was added. incident-reporter is the BYO container; runbook-assistant was not yet accepted (page 9).`

Three bullets:

- kagent exposes every agent over A2A. Listing one as `type: Agent` makes it callable like any other tool.
- The specialist keeps its own model, prompt and allowed tools. The orchestrator sees only its description and its answer.
- The BYO agent, incident-reporter, is called the same way. Its loop is Python; its interface is A2A.

### Page 11 · the approval gate

Kicker: `STEP 4 · THE GATE`

Headline: `Nothing changes until a human says so` (highlight "a human says so" in amber)

Three stacked rows, each a card with a left accent bar and a small-caps label on the left:

- Label `MODEL PICKS A TOOL`, slate bar: **The call is not executed.** `k8s_scale` is on the operator's requireApproval list, so the runtime stops before running it.
- Label `TASK PAUSES`, amber bar, person-and-check mark: **The task returns input-required** with the exact call and its arguments. The human reads them.
- Label `HUMAN DECIDES`, indigo bar: **Approve runs the call; reject discards it.** Same task, same context, one more message.

Two bullets:

- Approved: scale `web` to 3. Replicas went 2 → 3.
- Rejected: scale `web` to 2. The tool never ran. Replicas stayed at 3.

Footnote, secondary text: `Enforced by the runtime, not the prompt. It held when the orchestrator called the operator.`

### Page 12 · one repair, two pauses

Kicker: `THE TEST · SCENARIO 15`

Headline: `"Fix checkout so it has endpoints"` (highlight "Fix checkout" in indigo)

Five numbered steps, large numerals, actor in bold:

1. **Troubleshooter** finds the Service selects `app: checkout` but the pods are `app: web`.
2. **Orchestrator** asks the human which backend it should use. Pause 1.
3. **Human** answers. The orchestrator calls the operator with the exact patch.
4. **Operator** stops on `k8s_patch_resource` for approval. Pause 2.
5. **Human** approves. Selector patched. `kubectl` shows 3 endpoints.

Screenshot card: `docs/screenshots/crops/s15-orchestrator-ask-user.png`. Caption: `Pause 1 in the kagent UI: the troubleshooter has completed and the orchestrator asks which backend to use, with the patch and the rollback spelled out.`

Footnote, secondary text: `62 s of request time across three exchanges (32 + 16 + 14 s), 2 human decisions, 1 patch. Human thinking time not included.`

### Page 13 · how it was tested

Kicker: `THE METHOD · FIVE FAULTS, FIFTEEN QUESTIONS`

Headline: `Known faults, checked answers` (highlight "checked answers" in indigo)

A five-row table with three columns, headers `Workload`, `Fault`, `Expected diagnosis`, in large readable type:

| Workload | Fault | Expected diagnosis |
|---|---|---|
| `api` | image `nginx:1.99.99-does-not-exist` | ImagePullBackOff |
| `worker` | prints "config file ... not found", exits 1 | CrashLoopBackOff |
| `cache` | allocates 200 MiB under a 64 MiB limit | OOMKilled |
| `checkout` Service | selector `app: checkout`, pods are `app: web` | no endpoints |
| `batch` | requests 16 CPU on 4-CPU nodes | Pending, Insufficient cpu |

Three bullets:

- Fifteen questions sent over A2A through the controller by a script: twelve to specialists, three to the orchestrator. The approval flow was run twice, one approve and one reject.
- Every answer was compared with this table and with `kubectl`. A completed task does not count as correct unless the diagnosis names the fault.
- Raw A2A responses, answer text, REST and MCP responses and build logs are in the repository under `results/`.

Footnote, secondary text: `One cluster, one day, one run per specialist question. Orchestrator questions were retried while troubleshooting the timeout.`

### Page 14 · the numbers

Kicker: `RESULTS · ONE CLUSTER, ONE DAY`

Headline: `What the numbers said` (highlight "numbers" in indigo)

Four stat tiles in a 2 × 2 grid, number large in indigo, caption below:

- `5 / 5` — faults diagnosed by the read-only YAML agent, 5 to 52 s each
- `10 of 12` — specialist answers correct; one incomplete, one partly wrong
- `1` — orchestrator task never completed: the controller cut it at 3 minutes
- `≈ 6 USD` — model spend for the whole day, retries included

One line under the grid, secondary text: `The five faults: bad image · crash loop · OOMKilled · Service with no endpoints · unschedulable pod.`

### Page 15 · what broke

Kicker: `LIMITS · AND THE REPO`

Headline: `What broke` (highlight "broke" in amber)

Three bullets, lead phrase bold:

- **Three-minute cut-off.** The controller ended `message/send` and `message/stream` at 180 s. The longest diagnosis never finished.
- **Out of memory.** Three overlapping requests pushed the orchestrator past its default 1 GiB. The manifest now sets 2 GiB.
- **Three integration fixes.** The Grafana MCP image's loopback-only Host check, a missing Go runtime image, and a Prometheus tool that rejects comparison operators.

Footer line, secondary text: `Measured on 2026-10-07. kagent 0.9.10 and kmcp 0.3.0 are pre-1.0; the Agent resource changes in kagent 1.0.`

### Page 16 · where to go next

Kicker: `READ MORE · BY THE TIME YOU HAVE`

Headline: `Three layers, pick yours` (highlight "pick yours" in indigo)

Three stacked rows, each a card with a left accent bar, a bold time label on the left and text on the right:

- Label `10 minutes`, indigo bar: **This document.** The system, the YAML, the gate, one repair and the numbers.
- Label `30 minutes`, violet #7C3AED bar: **The article.** The reasoning behind each choice, the method, every result and the limitations. `<ARTICLE_URL>`
- Label `As long as you like`, amber bar: **The repository.** Setup guide in dependency order, the original build record with every command and output, the runtime and protocol reference, manifests, the custom MCP server and agent, scripts, the Postman collection and raw responses. `github.com/tharindu-sankalpa/eks-kagent-sre-agents`

Footnote, secondary text: `Links are not clickable in a LinkedIn document; both URLs are in the post text.`

---

## Checklist before posting

- Sixteen pages, A4 portrait, every page numbered n/16.
- Page 1 names the use case, the three technologies and the repository URL, has four numbered points, and carries the one illustration.
- Page 2 has exactly six specialist cards, six arrowheads from the spine, no arrow between two specialists, and two person-and-check marks (release-manager, sre-operator). The caption is two lines and "ap-south-1" is unbroken.
- Pages 4 to 10: every YAML line matches this file, including the `#` comments. Nothing runs off a page.
- Diagram cards on page 2 have solid 3 px outlines; arrows have filled heads.
- Six screenshot crops placed unaltered, from `docs/screenshots/crops/`, each with its caption: pages 3, 6, 8, 10 and 12. The two on page 3 show the AWS header and breadcrumb.
- Page 13 matches the README fault table; page 14 numbers match the README results table.
- Replace `<ARTICLE_URL>` on page 16 once the article is published; it is also in the post text.
- Nothing printed that is not in this file.
