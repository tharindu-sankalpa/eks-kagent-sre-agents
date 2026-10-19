# LinkedIn carousel: a five-to-ten-minute project summary

This is the production brief for a **12-page PDF** summarizing the multi-agent system for SRE workflows. It should stand on its own: a reader should understand what was built, what kagent and kmcp supplied, what the custom MCP server and agent add, how a repair involved the user, and what the tests actually established.

The PDF is the first layer. The [article](article.md) supplies the explanation and full results; the repository supplies the implementation, setup guide, component READMEs, Postman collection and recorded responses. The PDF gives readers enough understanding to choose where to go next.

Repository: https://github.com/tharindu-sankalpa/eks-kagent-sre-agents

## Editorial decisions

- **Twelve pages, with a five-minute reading path.** The title and takeaway on every page should tell the story in about five minutes. Reading the evidence and excerpts should take closer to ten. These are design targets, not measured reading times.
- **Show the system, then a real repair.** Page 2 uses the existing main architecture diagram. Page 3 explains the two different human decisions and the verified outcome before introducing resource fields.
- **Give the custom work space.** netprobe and the incident reporter each get a page. Separate the framework's deployment/runtime features from the probe functions, custom loop and validation work written here.
- **Keep implementation examples selective.** One short declarative excerpt and two small BYO deployment excerpts are enough. Model-provider configuration, prompt-template variants and the three tool-source resource kinds belong in the article/reference.
- **Include interaction, not only automation.** Show the web UI, local MCP discovery/calls and invoking the deployed agent. The scripts are an optional repeatable test path.
- **Use evidence with a purpose.** One readable repair screenshot is more useful than several small UI inventory screenshots. Full schemas, tool catalogues and responses are linked from the component READMEs.
- **Bound claims to the recorded run.** The main results describe EKS on 2026-10-07. Later local or AKS captures are not substitutes for those measurements. Human input and approval are distinct; task completion and answer accuracy are distinct.

## Review of the supplied PDF

`Eight-page carousel design-v2.pdf` contains **16 A4 portrait pages**, despite its filename. The following refers to that export's page numbers; the replacement sequence below has 12 pages.

| Observation in the supplied export | Change for the next version |
|---|---|
| The cover still says “multi-agent orchestration” and has four explanatory points competing with the headline. | Use “multi-agent system,” a short purpose statement and one bounded result. |
| Page 2 redraws a simplified system and omits the OpenRouter and platform context present in the main diagram. | Embed `docs/diagrams/01-system-overview.jpg` directly. Explain the main path in three short takeaways. |
| Configuration occupies much of pages 4–10; the custom reporter's implementation has no dedicated page. | Consolidate configuration and add dedicated MCP-server and BYO-agent pages. |
| Page 3's ECR screenshot extends below the page; its second caption and footnote are absent. `ap-south-1` also wraps mid-name in the first caption. | Remove the dedicated console-gallery page. Keep environment facts in the architecture caption; retain the screenshots in the article/build record. |
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
- Every page has a short kicker, a headline, one main visual or content group, one takeaway and `n/12`. Sources can be a short repository path; no long file path squeezed into a headline.
- **Reuse supplied diagrams without regenerating or reconstructing them.** Preserve their aspect ratios and labels. On page 2 the architecture is the main visual; avoid a competing illustration, lengthy legend or code block.
- The main diagram is detailed. Fit it to the full available width without cutting off its legend, OpenRouter box or platform strip. The three takeaways beneath it must remain readable without zooming. If small diagram labels cannot be read, direct readers to the full-resolution asset in the repository; do not pretend they are legible or stretch the image vertically.
- Screenshots support a specific observation, not general claims that “everything works.” Use the supplied repair crop on page 3. Do not add every available screenshot or diagram. The detailed netprobe contracts diagram remains in the article and MCP README; shrinking it onto a summary page would hide its useful detail.
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

**Main visual:** Use **`docs/diagrams/01-system-overview.jpg`**, the same main architecture diagram used in the article and repository README. Place it full-width at its native aspect ratio. Do not draw a replacement specialist graph.

**Three takeaways beneath it:**

1. **A2A connects agents.** The orchestrator delegates to six specialists; it has no direct Kubernetes tools.
2. **MCP connects tools.** Each specialist sees a selected subset of the operational and custom tools.
3. **Two deployment layers.** kagent runs agents; kmcp runs the additional MCP servers. Models are reached through OpenRouter.

**Environment caption, two fixed lines:**

`Amazon EKS 1.34 · 2 × t3.xlarge · ap-south-1`

`kagent 0.9.10 · kmcp 0.3.0 · 2026-10-07 test environment`

Keep `ap-south-1` unbroken. All seven agents, five tool servers and the external model endpoint belong to this map; a single request need not invoke every specialist or tool server.

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

**Evidence:** `docs/screenshots/crops/s15-orchestrator-ask-user.png`, placed below the sequence only if the question remains readable. Caption: `A separate UI run shows the backend-selection question. The original API transcripts and kubectl checks establish the recorded repair outcome.` If the crop is too small, omit it and retain the source path; do not shrink the five-step explanation.

**Takeaway:** `Choosing the repair and approving its execution are separate decisions.`

**Measured note:** `62 s across three exchanges: 32 + 16 + 14 s. Human deliberation time excluded.`

**Source:** `docs/build-record.md, section 16; results/answers/sre-orchestrator/s15.*`.

## Page 4 · supplied platform and custom work

**Kicker:** `WHAT WAS BUILT`

**Headline:** `Framework capabilities, custom implementation`

**Main visual:** Two readable stacked groups, not narrow text columns.

**kagent and kmcp supplied:**

- Agent deployment, the declarative ADK-based runtime, A2A integration and approval support.
- Bundled operational MCP tools for Kubernetes, Helm, Prometheus, Grafana and other systems.
- MCP server deployment from an existing package or a custom image.

**This project added:**

- Six declarative agent definitions, including the orchestrator, with selected tools and instructions.
- Four FastMCP network probes and a BYO incident reporter with its own Python loop.
- Container builds pushed to ECR, a broken-workload lab, manual/API walkthroughs and recorded checks.

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

## Page 9 · trying the interfaces yourself

**Kicker:** `INTERACTIVE WALKTHROUGHS`

**Headline:** `Start with the UI. Inspect the protocols next.`

**Main visual:** Three stacked cards with these labels and text:

- **Ask an agent.** Port-forward the kagent UI, select an agent and send a question. Expand tool calls and respond to input or approval prompts when they appear.
- **Call MCP directly.** Run netprobe locally with uv, without a container. Use curl/jq or Postman: initialize, send the initialized notification, list tools, call a tool. No model is needed.
- **Invoke the BYO agent.** Port-forward `svc/incident-reporter` on `8091:8080`. Read its card, then use A2A `message/send` or `message/stream`. The agent makes its own model and MCP calls.

**Takeaway:** `MCP at /mcp and A2A at / are different interfaces; both have copyable examples in the repository.`

**Source line:** `Postman folders 4b and 6 · component READMEs · setup guide section 12`. Add a smaller note: `A2A at / refers to the direct reporter Service; the controller uses /api/a2a/... routes. The scripts remain available for repeatable runs.`

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

- Main architecture: **`docs/diagrams/01-system-overview.jpg` on page 2**, reused directly.
- Repair screenshot: `docs/screenshots/crops/s15-orchestrator-ask-user.png` on page 3 if readable. It is a separate UI run; the original API results supply the measured timing and endpoint verification.
- The new `07-netprobe-tool-discovery.jpg` and existing `06-byo-agent-loop.jpg` are source references for pages 6–7 and remain embedded at useful resolution in the component documentation/article.
- Do not use the AKS pod screenshot or the 2026-10-18 Langfuse trace to illustrate the original EKS measurements without an explicit later-run label. They are not necessary for this summary.
- Full MCP results: `results/raw/netprobe-call-dns_lookup.json`, `netprobe-call-tcp_connect.json`, `netprobe-call-http_check.json`, `netprobe-call-tls_cert_expiry.json` and `kagent-tools-tools-list.json`.
- Reporter evidence: `results/answers/incident-reporter/s12.json` and `s12.txt`. Scenario listing: `scripts/scenarios.txt` for s01–s14; s15 and its human exchanges are in build-record section 16. Outcome verdicts are in the article.

## Checklist before exporting and posting

- Twelve A4 portrait pages, every page numbered `n/12`, with no old `n/16` footers.
- Cover uses “multi-agent system,” describes the SRE purpose and includes one measured outcome.
- Page 2 uses the actual main architecture image, without redrawing, cropping, stretching or swapping it for a simplified graph.
- The repair appears before configuration details. User input is distinct from execution approval.
- netprobe and the reporter each have a dedicated page. FastMCP and the A2A Python SDK are credited for their actual roles; the custom loop is not attributed to ADK.
- YAML excerpts have source labels and are visibly partial. No wrapped image tags, dropped indentation or implication that the snippets are deployable as shown.
- Page 10 counts sum to 15. Approval tests, retries and human follow-ups are distinguished from those 15 scenarios.
- Task completion is not presented as accuracy. Scope, versions, timing exclusions and the daily cost boundary remain visible.
- Source assets and code names match the repository. No later AKS/local evidence is passed off as original EKS output.
- No unresolved URL placeholders, private account labels, internal hostnames or credentials in the export.
- Inspect all exported pages visually, including pages with the most content. No cropped screenshot edges, missing captions, footer collisions or content outside the page. Check at phone width and 100% on desktop.
- Open the final PDF and test its links. Include repository/article destinations in the accompanying [LinkedIn post](linkedin-post.md).
