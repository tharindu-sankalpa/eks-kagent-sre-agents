# LinkedIn carousel: brief and page content

A document post on LinkedIn is a PDF that the feed renders as a swipeable carousel. This file is the complete brief for that PDF: how to produce it, the style, and the exact text, excerpts and numbers of every page. Every fact below comes from the README, the manifests and the recorded results; nothing in the pages should be changed or added by the design tool.

## How to produce it

Paste everything from "Brief for the design tool" to the end into Claude Design (template: Document) or build it as HTML pages and print to PDF. Then:

1. Check every page against this file: numbers, names, YAML lines, arrow directions. The tool must not add facts.
2. Export as PDF, 8 pages, 1080 × 1350 px (4:5 portrait), no margins beyond the page's own padding.
3. Name the file `multi-agent-sre-on-eks.pdf`. LinkedIn shows the file name as the document title in the feed.
4. Post it with the text from [linkedin-post.md](linkedin-post.md). Links inside the PDF are not clickable on LinkedIn, so the article and repo URLs go in the post text or the first comment, and page 8 writes them out plainly.

---

## Brief for the design tool

Design an 8-page document for a LinkedIn document post (PDF carousel). Portrait pages, 1080 × 1350 px each. It is read inside the LinkedIn feed at phone width, so everything is large: body text at least 30 px, captions at least 24 px, code at least 24 px. One idea per page. No page has more than one diagram or one code excerpt. Use only the text given below; do not add, reword, shorten or invent any sentence, number, file name or YAML line. Do not add logos, icons of brands, decorative illustrations, stock imagery or photographs.

### Style

- Canvas #FAFAFA. Text #0F172A, secondary text #475569. A thin rule in #4F46E5 across the top of every page.
- Each page has three fixed elements: a small-caps kicker in indigo #4F46E5 at the top left (letter-spaced, about 24 px), a bold headline below it (about 64 px, two lines at most), and a page number "n/8" bottom right in secondary text.
- Typeface: one clean sans-serif such as Inter for everything except code; a monospace such as JetBrains Mono for code. Consistent sizes across pages.
- Accent colours, used only for small marks, left accent bars, arrows and one highlighted word per headline: indigo #4F46E5 (orchestration, requests), blue #2563EB (diagnosis), amber #B45309 (changes that need approval), cyan #0E7490 (the custom agent), steel-blue #0369A1 (results and tool calls, dashed). Fills on cards are very pale tints of the same colours; never a saturated block.
- Diagram cards: white, 2 px slate outline, 12 px radius, a coloured left accent bar. Arrows: solid indigo for requests and delegation, dashed steel-blue for results. Every arrow has an arrowhead at its destination only.
- Code excerpts: a dark card #1E293B with light text, a header line in the card naming the file, line numbers not shown, and up to four lines highlighted with a faint amber band. Keep the YAML indentation exactly as given.
- A small person-and-check mark means "a human approves before this runs"; it appears only where the text says so.
- Plenty of empty space. If a page runs out of room, reduce nothing; report it instead.

### Page 1 · cover

Kicker: `BUILD LOG · KAGENT + KMCP ON AMAZON EKS`

Headline: `Seven agents, one orchestrator, one human approval gate` (highlight "one human approval gate" in amber)

Three numbered lines, large numerals in indigo:

1. **Six agents are YAML. One is a container.** A model, instructions and allowed tools per agent.
2. **The orchestrator's tools are the other agents.** It has no Kubernetes tools of its own.
3. **Every change pauses for a human.** The gate held even when one agent called another.

Footer line in indigo italic: `Swipe for the setup, the YAML and the numbers →`

### Page 2 · the system

Kicker: `THE SYSTEM`

Headline: `One request, six specialists, five tool servers`

Diagram, top to bottom, centred, four rows joined by arrows:

- Row 1: a person mark labelled `SRE`, then a solid indigo arrow labelled `A2A` to a card `kagent controller`, then a solid indigo arrow to a wide indigo-accent card `sre-orchestrator` with caption `Its tools are six agents`.
- Row 2: from the orchestrator, one indigo line to a horizontal spine, and six branches down to six small cards in this order: `cluster-troubleshooter` (blue), `observability-analyst` (teal #0F766E), `runbook-assistant` (violet #7C3AED), `release-manager` (amber, person-and-check mark), `incident-reporter` (cyan, dashed outline), `sre-operator` (amber, person-and-check mark). Label on the spine: `A2A delegation · agents as tools`.
- Row 3: one dashed steel-blue arrow from the row of six to one wide amber-accent card `5 MCP tool servers`, caption `kagent-tools · grafana-mcp · netprobe-mcp · fetch · querydoc`.
- Row 4: one dashed steel-blue arrow to a plain card `Kubernetes API · Prometheus · Grafana`.

Caption under the diagram, secondary text: `Amazon EKS 1.34 · 2 × t3.xlarge · ap-south-1 · kagent 0.9.10 · kmcp 0.3.0 · models via OpenRouter`

### Page 3 · an agent is a YAML file

Kicker: `STEP 1 · DEFINE AN AGENT`

Headline: `An agent is a YAML file` (highlight "YAML file" in indigo)

Code card, header `infra/kagent/agents/sre-operator.yaml · shortened`:

```yaml
apiVersion: kagent.dev/v1alpha2
kind: Agent
metadata:
  name: sre-operator
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
          name: kagent-tool-server
          toolNames:
            - k8s_get_resources
            - k8s_scale
            - k8s_patch_resource
          requireApproval:
            - k8s_scale
            - k8s_patch_resource
```

Highlight the lines `modelConfig: grok-4-7`, `systemMessage: |`, `toolNames:` and `requireApproval:`.

Four bullets, each with the field name in bold:

- **modelConfig** names a ModelConfig resource: provider, model id and the API key Secret. Five models, one key, all through OpenRouter.
- **systemMessage** is the prompt. The orchestrator's lives in a ConfigMap instead.
- **toolNames** selects from a server's inventory. kagent-tools offers 124 tools; this agent sees 11.
- **requireApproval** lists the calls that pause for a human. Six of the operator's 11.

Footnote, secondary text: `kubectl apply creates the Deployment, Service and A2A endpoint. No code.`

### Page 4 · agents as tools

Kicker: `STEP 2 · DELEGATE`

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

Small diagram beside or under the card: card `sre-orchestrator` (indigo) with a solid indigo arrow labelled `tool call over A2A` to card `cluster-troubleshooter` (blue), and a dashed steel-blue arrow back labelled `answer = tool result`.

Three bullets:

- kagent exposes every agent over A2A. Listing one as `type: Agent` makes it callable like any other tool.
- The specialist keeps its own model, prompt and allowed tools. The orchestrator sees only its description and its answer.
- The custom container agent is called the same way. Its loop is Python; its interface is A2A.

### Page 5 · the approval gate

Kicker: `STEP 3 · THE GATE`

Headline: `Nothing changes until a human says so` (highlight "a human says so" in amber)

Three stacked rows, each a card with a left accent bar and a small-caps label on the left (as a timeline):

- Label `MODEL PICKS A TOOL`, slate bar: **The call is not executed.** `k8s_scale` is on the operator's requireApproval list, so the runtime stops before running it.
- Label `TASK PAUSES`, amber bar, person-and-check mark: **The task returns input-required** with the exact call and its arguments. The human reads them.
- Label `HUMAN DECIDES`, indigo bar: **Approve runs the call; reject discards it.** Same task, same context, one more message.

Two bullets below:

- Approved: scale `web` to 3. Replicas went 2 → 3.
- Rejected: scale `web` to 2. The tool never ran. Replicas stayed at 3.

Footnote, secondary text: `Enforced by the runtime, not the prompt. It held when the orchestrator called the operator.`

### Page 6 · one repair, two pauses

Kicker: `THE TEST · SCENARIO 15`

Headline: `"Fix checkout so it has endpoints"` (highlight "Fix checkout" in indigo)

Five numbered steps in a vertical list, large numerals, with the actor in bold:

1. **Troubleshooter** finds the Service selects `app: checkout` but the pods are `app: web`.
2. **Orchestrator** asks the human which backend it should use. Pause 1.
3. **Human** answers. The orchestrator calls the operator with the exact patch.
4. **Operator** stops on `k8s_patch_resource` for approval. Pause 2.
5. **Human** approves. Selector patched. `kubectl` shows 3 endpoints.

A small strip under the list with three stat tiles: `62 s` caption `request time, three exchanges`; `2` caption `human decisions`; `1` caption `patch applied`.

Footnote, secondary text: `32 s + 16 s + 14 s. Human thinking time not included.`

### Page 7 · the numbers

Kicker: `RESULTS · ONE CLUSTER, ONE DAY`

Headline: `What the numbers said`

Four large stat tiles in a 2 × 2 grid, number large in indigo, caption below:

- `5 / 5` — faults diagnosed by the read-only YAML agent, 5 to 52 s each
- `10 of 12` — specialist answers correct; one incomplete, one partly wrong
- `1` — orchestrator task never completed: the controller cut it at 3 minutes
- `≈ 6 USD` — model spend for the whole day, retries included

Under the grid, one line in secondary text: `The five faults: bad image · crash loop · OOMKilled · Service with no endpoints · unschedulable pod.`

### Page 8 · what broke, and where to read

Kicker: `LIMITS · AND THE REPO`

Headline: `What broke, and where everything is`

Three bullets, lead phrase bold:

- **Three-minute cut-off.** The controller ended `message/send` and `message/stream` at 180 s. The longest diagnosis never finished.
- **Out of memory.** Three overlapping requests pushed the orchestrator past its default 1 GiB. The manifest now sets 2 GiB.
- **Three integration fixes.** The Grafana MCP image's loopback-only Host check, a missing Go runtime image, and a Prometheus tool that rejects comparison operators.

A rule, then two lines in large text with the label bold:

- **Repository:** `<REPO_URL>` — manifests, custom code, setup guide, build record, raw responses
- **Article:** `<ARTICLE_URL>`

Footer line, secondary text: `Measured on 2026-10-07. kagent 0.9.10 and kmcp 0.3.0 are pre-1.0; the Agent resource changes in kagent 1.0.`

---

## Checklist before posting

- Eight pages, portrait, every page numbered.
- Page 2 has exactly six specialist cards and two person-and-check marks (release-manager, sre-operator).
- Page 3 and 4 YAML matches the text above line for line.
- Page 7 numbers match the README results table.
- Replace `<REPO_URL>` and `<ARTICLE_URL>` on page 8 and in the post text.
- Nothing printed that is not in this file.
