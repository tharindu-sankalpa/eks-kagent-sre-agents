# LinkedIn carousel: a five-to-ten-minute project summary

This is the production brief for a **12-page PDF** summarizing the multi-agent system for SRE workflows. It should stand on its own: a reader should understand what was built, what kagent and kmcp supplied, what the custom MCP server and agent add, how a repair involved the user, and what the tests actually established.

The PDF is the first layer. The [article](article.md) supplies the explanation and full results; the repository supplies the implementation, setup guide, component READMEs, Postman collection and recorded responses. The PDF gives readers enough understanding to choose where to go next.

Repository: https://github.com/tharindu-sankalpa/eks-kagent-sre-agents

## Editorial decisions

- **Twelve pages, with a five-minute reading path.** The title and takeaway on every page should tell the story in about five minutes. Reading the evidence and excerpts should take closer to ten. These are design targets, not measured reading times.
- **Show the system, then a real repair.** Page 2 uses the supplied portrait architecture diagram. Page 3 explains the two different human decisions and the verified outcome before introducing resource fields.
- **Give the custom work space.** netprobe and the incident reporter each get a page. Separate the framework's deployment/runtime features from the probe functions, custom loop and validation work written here.
- **Keep implementation examples selective.** One short declarative excerpt and two small BYO deployment excerpts are enough. Model-provider configuration, prompt-template variants and the three tool-source resource kinds belong in the article/reference.
- **Include interaction, not only automation.** Show the web UI, local MCP discovery/calls and invoking the deployed agent. The scripts are an optional repeatable test path.
- **Use three focused evidence screenshots.** The kagent question on page 3 shows the user interaction, the EKS nodes on page 4 show the test platform, and the later Langfuse trace on page 9 shows the recorded question, choices and answer. Crop each for its purpose. Full schemas, tool catalogues and responses are linked from the component READMEs.
- **Bound claims to the recorded run.** The main results describe EKS on 2026-10-07. Later local or AKS captures are not substitutes for those measurements. Human input and approval are distinct; task completion and answer accuracy are distinct.

## Review of the supplied PDF

`Eight-page carousel design-v2.pdf` contains **16 A4 portrait pages**, despite its filename. The following refers to that export's page numbers; the replacement sequence below has 12 pages.

| Observation in the supplied export | Change for the next version |
|---|---|
| The cover still says “multi-agent orchestration” and has four explanatory points competing with the headline. | Use “multi-agent system,” a short purpose statement and one bounded result. |
| Page 2 redraws a simplified system and omits the OpenRouter and platform context present in the main diagram. | Embed the supplied portrait version, `docs/diagrams/08-system-overview-portrait.jpg`, directly. Give it most of the page. |
| Configuration occupies much of pages 4–10; the custom reporter's implementation has no dedicated page. | Consolidate configuration and add dedicated MCP-server and BYO-agent pages. |
| Page 3's ECR screenshot extends below the page; its second caption and footnote are absent. `ap-south-1` also wraps mid-name in the first caption. | Remove the console-gallery layout. Use one focused EKS node-table crop on the new page 4 with its own reserved caption space. |
| Page 8 reaches the lower edge; the stdio-package explanation and reserved footer space are lost. | Use shorter excerpts and a fixed footer exclusion area. Treat overflow as an error. |
| Page 5's narrow columns wrap code, image names and endpoints into awkward fragments. Other code cards also carry long lines. | Stack short full-width code cards. Use selected fields, not two miniature manifests side by side. |
| Results arrive only on page 14, and the repair is first explained on page 12. | Put a result on the cover and the repair on page 3; keep the complete outcome breakdown near the end. |
| The last page includes the literal `<ARTICLE_URL>` placeholder. | Insert the published URL when available; otherwise use the repository's article path. No unresolved placeholder in the export. |

Keep the consistent typography, restrained palette, clear stat tiles and separation of findings from limitations. The main changes are the content hierarchy, ownership of the custom work and the overflow fixes.

## Production and visual rules

- Export **12 pages, A4 portrait (210 × 297 mm)**. Use `multi-agent-sre-on-eks-summary.pdf`. Do not edit or overwrite the supplied PDF as part of this brief update.
- Keep at least 14 mm page padding and reserve the bottom 16 mm for page number/source text. Content never enters that footer area.
- Use Inter or a similar sans-serif. Suggested A4 sizes: headline 28–34 pt, body 16–18 pt, captions 12–14 pt, code 12–14 pt. The cover may have a three-line headline; other pages should have at most two. Font sizes are starting points: check the exported document at phone width as well as at 100% on desktop.
- Aim for roughly 60–110 words of visible prose per page, excluding the architecture image, code and source labels. Page 10's results table is the intentional exception. Cut content before reducing type size.
- Canvas `#FAFAFA`; dark text `#0F172A`; secondary text `#475569`. Use indigo `#4F46E5` for requests/orchestration, blue `#2563EB` for diagnosis, amber `#B45309` for execution approval, cyan `#0E7490` for BYO components. Keep fills pale.
- Every page has a short kicker, a headline, one main visual or content group, one takeaway and `n/12`. The portrait architecture page uses a compact header and caption to maximize the image area. Sources can be a short repository path; no long file path squeezed into a headline.
- **Reuse supplied diagrams without regenerating or reconstructing them.** Preserve their aspect ratios and labels. On page 2 the architecture is the main visual; avoid a competing illustration, lengthy legend or code block.
- The portrait diagram is detailed. Fit the complete image inside the available width and height, preserving its legend, OpenRouter box and platform strip. Allow approximately 225 mm of image height on page 2; reduce header copy to make room. Do not squeeze three extra explanation paragraphs beneath it. If small diagram labels cannot be read, direct readers to the full-resolution asset in the repository; do not stretch or crop the architecture to force a fit.
- The three requested screenshot placements are required. Crop browser chrome, desktop UI and unrelated sidebars so the evidence is large enough to read. Keep the original files unchanged; cropping instructions below describe the PDF placements. Crops must preserve complete questions, choices, answer text and node rows. Do not regenerate, repaint or edit the observed values. The detailed netprobe contracts diagram remains in the article and MCP README.
- Use full-width code cards, a monospace face, no line numbers and no more than 12 lines per card. Page 8 has two stacked cards of 7 and 5 lines. Label every excerpt as selected fields, not an apply-ready manifest. Do not wrap an identifier, hostname or image tag in the middle; shorten the excerpt instead.
- No decorative cover graph, invented logos, stock imagery or generic AI art. Preserve the exact source text and numbers below. A designer may change line breaks and spacing, but must report any substantive edit or overflow.
- Keep links clickable in the exported PDF where supported, and print the repository address as readable text. Put the destination links in the accompanying post too. Do not make platform-dependent link behavior the only way to find the work.

## Page 1 · the build and the result

**Kicker:** `MULTI-AGENT SYSTEM · SRE WORKFLOWS`

**Headline:** `A multi-agent system for SRE workflows`

**Subtitle:** `Amazon EKS · kagent · kmcp`

**Visible copy:**

> Seven agents diagnose Kubernetes faults and coordinate repairs. The workflow can pause for missing information and separately for execution approval.
>
> In the recorded repair: two human decisions, one Service patch, three verified endpoints.

**Main visual:** Three clean stat cards: `7 agents` / `4 custom probes` / `2 human decisions in the repair`. No architecture illustration on the cover; the actual architecture follows on page 2.

**Takeaway:** `A working repair, diagnostic results and documented failures—not a production reliability claim.`

**Footer:** `A five-to-ten-minute summary · Recorded EKS tests: 2026-10-07`

Print the repository address on a separate readable line: `github.com/tharindu-sankalpa/eks-kagent-sre-agents`.

## Page 2 · the actual architecture

**Kicker:** `THE SYSTEM`

**Headline:** `How the pieces fit`

**Main visual:** Use **`docs/diagrams/08-system-overview-portrait.jpg`**, the user-supplied portrait architecture image. This replaces the previous landscape asset for this PDF. Keep `01-system-overview.jpg` as the existing landscape asset used in the other documents. Place the new image at its native aspect ratio, centered and fitted to the available page height. Do not draw a replacement specialist graph.

**Layout:** Reserve most of the page for the image: approximately 225 mm high, a short header above and one compact caption below. Keep the whole architecture, including the legend and platform strip. No screenshot, code card or additional diagram on this page.

**Caption:** `A2A connects agents; MCP connects tools. kagent runs agents, kmcp runs the additional MCP servers, and models are reached through OpenRouter.`

**Small source line:** `Recorded EKS environment: 2026-10-07 · Full-resolution diagram in the repository.` All seven agents, five tool servers and the external model endpoint belong to this map; a single request need not invoke every specialist or tool server.

## Page 3 · one repair, two different human decisions

**Kicker:** `THE REPAIR · SCENARIO 15`

**Headline:** `First clarify intent. Then approve execution.`

**User request:** `Fix checkout so it has endpoints. Tell me what you intend to change first.` Label this as the shortened request.

**Main visual:** A five-step vertical sequence with two distinct pale-yellow pause bands:

1. The troubleshooter finds `checkout` selects `app: checkout`; the ready pods have `app: web`.
2. **User input:** the orchestrator asks which backend is intended.
3. The user's answer selects the repair; the orchestrator delegates to the operator.
4. **Execution approval:** the runtime pauses the operator's exact `k8s_patch_resource` call.
5. The approved patch changes the selector. `kubectl` confirms **three endpoints**.

**Required screenshot:** Crop **`docs/screenshots/kagent-ui-orchestrator-ask-user-question.png`** to the main conversation panel. Make the completed `cluster-troubleshooter` card and the full **Questions for you** panel visible, including the proposed selector change, all three choices and the Submit button. Remove browser chrome, the desktop dock, chat history and Agent Details sidebar. The existing `docs/screenshots/crops/s15-orchestrator-ask-user.png` can be used only if it retains those details at readable size.

**Caption:** `A separate UI run shows the proposed repair and asks which backend is intended. The original API transcripts and kubectl checks establish the measured repair outcome.` Reserve the lower part of the page for the crop. If it competes with the sequence, shorten the sequence's labels; keep both the screenshot and the two distinct pause bands.

**Takeaway:** `Choosing the repair and approving its execution are separate decisions.`

**Measured note:** `62 s across three exchanges: 32 + 16 + 14 s. Human deliberation time excluded.`

**Source:** `docs/build-record.md, section 16; results/answers/sre-orchestrator/s15.*`.

## Page 4 · supplied platform and custom work

**Kicker:** `WHAT WAS BUILT`

**Headline:** `Framework capabilities, custom implementation`

**Main visual:** Two compact stacked groups above a full-width EKS node-table crop. Keep four short bullets in total so the screenshot and caption fit.

**kagent and kmcp supplied:**

- Agent deployment, the declarative ADK-based runtime, A2A integration and approval support.
- Bundled operational tools; kmcp deployment of existing or custom MCP servers.

**This project added:**

- Six declarative agent definitions, four FastMCP probes and a BYO reporter with its own Python loop.
- ECR image builds, a broken-workload lab, manual/API walkthroughs and recorded checks.

**Required screenshot:** Crop **`docs/screenshots/aws-console-eks-compute-nodes.png`** to **Nodes (2)**, the column headings and both node rows. Retain the instance-type, node-group and Ready-status columns; remove browser chrome, the desktop dock, the left navigation and the large empty overview area. Do not cut off the right-hand status column as the earlier export did. The crop should show both rows together, rather than two disconnected node snippets.

**Caption:** `Amazon EKS console, 2026-10-07: two t3.xlarge On-Demand nodes in workers, both Ready. Region: ap-south-1.` Keep `ap-south-1` unbroken.

**Takeaway:** `The deployment platform is reusable; the roles, custom code and evidence define this project.`

**Scope line:** `Six declarative agents + one BYO agent. Both are kagent Agent resources.`

## Page 5 · the declarative agent contract

**Kicker:** `DECLARATIVE AGENTS`

**Headline:** `Configure the model, instructions and tools`

**Code card:** `sre-operator.yaml · selected fields, not a complete manifest`

```yaml
spec:
  type: Declarative
  declarative:
    modelConfig: grok-4-7
    systemMessage: "Diagnose before proposing a change."
    tools:
      - type: McpServer
        mcpServer:
          kind: RemoteMCPServer
          name: kagent-tool-server
          toolNames: [k8s_scale]
          requireApproval: [k8s_scale]
```

**Visible copy:**

- `modelConfig` names the model configuration; `systemMessage` supplies instructions.
- `toolNames` limits the tools offered to the model. `requireApproval` pauses listed operations in the runtime.
- Six agents use kagent's ADK-based runtime. The BYO reporter owns its implementation.

**Takeaway:** `An instruction asks for behavior; a runtime gate controls execution.`

**Small context line:** `Five ModelConfigs share an OpenRouter Secret. Full provider and prompt configuration is in the article.`

**Source:** `infra/kagent/agents/sre-operator.yaml`. The excerpt's prompt is condensed, not a verbatim quotation. The deployed operator has 11 tools, six under approval; only one is shown here.

## Page 6 · the custom MCP server

**Kicker:** `BYO TOOL SERVER · NETPROBE`

**Headline:** `Four Python functions become discoverable tools`

**Main visual:** A compact tool table:

| Tool | Input | Observation returned |
|---|---|---|
| `dns_lookup` | hostname | addresses and resolution status |
| `tcp_connect` | host, port | connection status and time |
| `http_check` | URL | HTTP status, latency and redirect target |
| `tls_cert_expiry` | host; port defaults to 443 | certificate validity and remaining days |

**Discovery strip, four readable labels in order:**

`Separate tool files` → `Loader imports modules` → `@mcp.tool() registration` → `tools/list returns definitions`

**Visible copy:** `FastMCP supplies schemas, validation and MCP message handling. The probe functions perform the checks and return evidence.`

**Takeaway:** `A resolved Service name does not prove there is a healthy backend.`

**Small note:** `Optional timeout arguments are omitted from this summary. Current output schemas describe a broad object; the detailed README explains the returned fields.`

**Sources:** `byo/netprobe-mcp/README.md`; `docs/diagrams/07-netprobe-tool-discovery.jpg`; `results/raw/netprobe-call-*.json`. Keep the detailed schema diagram in the linked documentation rather than reproducing it at unreadable size.

## Page 7 · the custom agent

**Kicker:** `BYO AGENT · INCIDENT REPORTER`

**Headline:** `Python owns the loop. A2A serves the report.`

**Main visual:** Five numbered steps in one simple loop, using this exact text:

1. `Discover and select MCP tools at startup`
2. `Send the request and tool schemas to the model`
3. `Run requested MCP tools and append observations`
4. `Repeat until the model returns report text`
5. `Publish an A2A incident-report artifact`

Draw the loop-back only from step 3 to step 2; the report is the exit. Step 1 is startup setup outside the repeated loop. Use the existing `docs/diagrams/06-byo-agent-loop.jpg` as a correctness reference; do not shrink its full technical labels onto this page.

**Visible copy:** `I wrote the ReAct tool-calling loop. The A2A Python SDK handles the server interface; it does not supply the loop. The reporter selects six Kubernetes tools and four probes and proposes fixes without applying them.`

**Measured result:** `Scenario s12: all five configured faults diagnosed · 161 s · 21 tool calls.`

**Takeaway:** `The agent decides which evidence to gather; MCP servers execute the individual checks.`

**Sources:** `byo/incident-reporter-agent/README.md`; `results/answers/incident-reporter/s12.json`. A 20-turn limit also terminates the loop; reaching it does not establish a complete report.

## Page 8 · deploying both custom components

**Kicker:** `FROM CODE TO KUBERNETES`

**Headline:** `Two images, two resource contracts`

**Introductory line:** `Both custom components were built as images and pushed to ECR. Their YAML describes how to run them.`

**First full-width code card:** `netprobe-mcpserver.yaml · selected fields`

```yaml
kind: MCPServer
spec:
  transportType: http
  httpTransport: {targetPort: 3000, path: /mcp}
  deployment:
    image: <ECR>/netprobe-mcp:0.1.0
    port: 3000
```

Caption: `kmcp runs the tool server. FastMCP serves MCP at /mcp; the actual startup command binds to 0.0.0.0.`

**Second full-width code card:** `incident-reporter.yaml · selected fields`

```yaml
kind: Agent
spec:
  type: BYO
  byo:
    deployment: {image: "<ECR>/incident-reporter-agent:0.1.0"}
```

Caption: `kagent runs the custom agent. Its container serves A2A at / on port 8080; the model, prompt and loop belong to the application.`

**Takeaway:** `MCPServer describes a tool server. Agent with type: BYO describes an agent container.`

**Small note:** `Excerpts omit API versions, metadata, startup arguments, environment variables and Secret references. Use the complete manifests to deploy. fetch uses a pre-built package in kmcp's default image; it needs no custom image build.`

**Sources:** `infra/kmcp/netprobe-mcpserver.yaml`; `infra/kagent/agents/incident-reporter.yaml`; `docs/setup-guide.md`.

## Page 9 · inspect the question, answer and delegation

**Kicker:** `INTERACTIVE WALKTHROUGHS`

**Headline:** `See what the agent asked—and what the user chose`

**Required screenshot:** Use **`docs/screenshots/langfuse-orchestrator-operator-trace.png`** as the main evidence, focused on the selected `ask_user` observation. Keep the trace identity (`sre-orchestrator` / `ask_user`) and the right-hand **Input** and **Output** details, including the backend-selection question, all four choices and the recorded answer choosing `app=web`.

**Crop treatment:** Remove the browser chrome and URL bar, desktop dock, left navigation, project/trace listing, account label and unrelated RAG traces. Prefer a focused crop of the relevant trace branch beside the question-and-answer panel. If the input and selected answer become too small together, use two clearly labelled detail crops from the same screenshot: **Question and choices** and **Recorded answer**. Do not stitch them into a fabricated continuous UI view. Keep the `ask_user` label visible. Reduce surrounding prose before reducing the screenshot size.

**Caption:** `Later run, 2026-10-18: the Langfuse trace records the backend question, four choices and the answer selecting app=web. It also shows delegation to sre-operator. This is separate from the original EKS measurements.` If a detail crop omits the delegation branch, omit the sentence about the branch from the caption too.

**Native PDF callout:** `Selected answer: repoint checkout to app=web.` This repeats the visible choice in readable PDF text; it is not evidence that the patch executed.

**Compact try-it strip:** `Web UI: ask and respond · Local MCP: initialize → list → call · BYO agent: port-forward → A2A request`. In the source note, clarify that the full MCP sequence includes `notifications/initialized` before listing tools.

**Takeaway:** `Inspect the question and response as well as the final answer. User input is distinct from tool execution approval.`

**Source line:** `Postman folders 4b and 6 · component READMEs · setup guide section 12`. The READMEs have the complete curl/jq commands: local netprobe without a container, and `svc/incident-reporter` forwarded on `8091:8080`. MCP uses `/mcp`; direct reporter A2A uses `/`; controller A2A uses `/api/a2a/...`. Scripts remain the repeatable test path. Do not add a full third code or text panel to this screenshot-led page.

## Page 10 · method and measured outcomes

**Kicker:** `RESULTS · EKS · 2026-10-07`

**Headline:** `15 scenarios: completion was not enough`

**Method line:** `Five known faults: bad image, command exits 1, memory-limit OOM, Service without endpoints, and an unschedulable CPU request. Answers were evaluated against the configured faults and cluster evidence.`

**Main visual:** Four outcome rows or bars. Counts are counts, not percentage estimates:

| Outcome across 15 numbered scenarios | Count |
|---|---:|
| Correct diagnosis or verified repair | **12** |
| Partly incorrect answer | **1** |
| Correct but incomplete answer | **1** |
| Never completed | **1** |

**Two supporting facts:**

- The troubleshooter diagnosed all five faults individually in **5–52 s** each.
- Two additional direct approval tests behaved as intended: approved scale **2 → 3**; rejected scale left **3 → 3**.

**Takeaway:** `Fourteen tasks completed; two of those answers had quality issues.`

**Scope note:** `12 specialist questions + 3 orchestrator scenarios. s15 was added after the initial 14 questions. Retries and human follow-up messages are not extra scenarios. Two approval tests are additional cases.`

**Sources:** `docs/article.md, Results`; `results/summary/scenarios.json`; `results/answers/`. The JSON summary records execution data, not accuracy grades.

## Page 11 · limitations and operational lessons

**Kicker:** `WHAT DID NOT WORK`

**Headline:** `The failures matter as much as the repair`

**Main visual:** Three stacked finding cards:

- **Long tasks:** scenario s13 never completed. Two controller attempts timed out at **180 s**; a direct retry was stopped manually because of cost. Streaming did not remove the controller deadline.
- **Abandoned work:** overlapping requests exceeded the orchestrator's **1 GiB** limit. The manifest now sets **2 GiB**; later tests were serialized.
- **Answer quality:** one answer listed `batch` as both healthy and unhealthy; another missed four cluster-wide firing alerts. A completed task did not prove a correct answer.

**Takeaway:** `Verify external state, inspect the answer and account for work after a client disconnects.`

**Scope note:** `One cluster and one specialist run per question. About USD 6 of model spend for the day, including retries; not per scenario and not the AWS infrastructure cost.`

**Source:** `docs/build-record.md, sections 15–16`. Host-header discovery, the unavailable Go image and PromQL filtering are additional integration findings documented in the article; they do not need another slide.

## Page 12 · what readers can take away and reproduce

**Kicker:** `READ MORE · TRY IT`

**Headline:** `Inspect the mechanism. Reproduce the evidence.`

**Three takeaways:**

- Declarative specialists and a custom agent can share an A2A interface.
- MCP exposes discoverable tool contracts; custom functions still own the actual checks.
- Clarification and execution approval are different pauses, and both were exercised in the repair.

**Two next-step cards:**

- **Understand the build:** article, component READMEs and the runtime/protocol reference.
- **Try it:** setup guide, UI walkthrough, Postman collection, scripts and recorded JSON responses.

**Repository, printed clearly:** `github.com/tharindu-sankalpa/eks-kagent-sre-agents`

Link the repository text to `https://github.com/tharindu-sankalpa/eks-kagent-sre-agents`. Add a small clickable `Read the article` label linking to `https://github.com/tharindu-sankalpa/eks-kagent-sre-agents/blob/main/docs/article.md` until a published article URL exists. Do not print a placeholder URL.

**Footer:** `Recorded versions: kagent 0.9.10 · kmcp 0.3.0. The setup guide covers infrastructure costs and teardown; provisioned AWS resources incur charges.`

## Asset and evidence policy

- PDF architecture: **`docs/diagrams/08-system-overview-portrait.jpg` on page 2**, reused directly. The prior landscape `01-system-overview.jpg` remains in the article and README; it is not the page 2 asset for this export.
- Required repair screenshot: **`docs/screenshots/kagent-ui-orchestrator-ask-user-question.png` on page 3**, cropped to the completed specialist call and full user-question panel. It is a separate UI run; the original API results supply the measured timing and endpoint verification.
- Required EKS screenshot: **`docs/screenshots/aws-console-eks-compute-nodes.png` on page 4**, cropped to the two-node table with instance types and Ready status. Preserve both rows and the complete caption.
- Required trace screenshot: **`docs/screenshots/langfuse-orchestrator-operator-trace.png` on page 9**, cropped to the relevant `ask_user` trace and its question, choices and recorded answer. Remove the URL/project/account UI. Label it as a later 2026-10-18 run; do not transfer its durations, choices or two-pod count into the original EKS results.
- The new `07-netprobe-tool-discovery.jpg` and existing `06-byo-agent-loop.jpg` are source references for pages 6–7 and remain embedded at useful resolution in the component documentation/article.
- The AKS pod screenshot is not needed for this summary. The later Langfuse capture illustrates the interaction; its caption must distinguish it from the original EKS measurements.
- Full MCP results: `results/raw/netprobe-call-dns_lookup.json`, `netprobe-call-tcp_connect.json`, `netprobe-call-http_check.json`, `netprobe-call-tls_cert_expiry.json` and `kagent-tools-tools-list.json`.
- Reporter evidence: `results/answers/incident-reporter/s12.json` and `s12.txt`. Scenario listing: `scripts/scenarios.txt` for s01–s14; s15 and its human exchanges are in build-record section 16. Outcome verdicts are in the article.

## Checklist before exporting and posting

- Twelve A4 portrait pages, every page numbered `n/12`, with no old `n/16` footers.
- Cover uses “multi-agent system,” describes the SRE purpose and includes one measured outcome.
- Page 2 uses `08-system-overview-portrait.jpg`, fitted by height and width without redrawing, cropping or stretching. Its whole legend, OpenRouter box and platform strip remain visible.
- The repair appears before configuration details. User input is distinct from execution approval.
- All three requested screenshots appear: kagent question on page 3, EKS nodes on page 4, Langfuse question/answer on page 9. Browser chrome and unrelated UI are cropped out; original source files remain unchanged.
- The EKS crop retains both node rows, instance types and Ready status. The kagent crop retains the full question and three choices. The Langfuse crop retains the question, four choices and selected answer, with a later-run caption. No crop silently removes the evidence it is meant to show.
- netprobe and the reporter each have a dedicated page. FastMCP and the A2A Python SDK are credited for their actual roles; the custom loop is not attributed to ADK.
- YAML excerpts have source labels and are visibly partial. No wrapped image tags, dropped indentation or implication that the snippets are deployable as shown.
- Page 10 counts sum to 15. Approval tests, retries and human follow-ups are distinguished from those 15 scenarios.
- Task completion is not presented as accuracy. Scope, versions, timing exclusions and the daily cost boundary remain visible.
- Source assets and code names match the repository. No later AKS/local evidence is passed off as original EKS output.
- No unresolved URL placeholders, private account labels, internal hostnames or credentials in the export.
- Inspect all exported pages visually, including pages with the most content. No cropped screenshot edges, missing captions, footer collisions or content outside the page. Check at phone width and 100% on desktop.
- Open the final PDF and test its links. Include repository/article destinations in the accompanying [LinkedIn post](linkedin-post.md).
