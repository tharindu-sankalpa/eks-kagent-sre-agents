# Multi-agent SRE workflows on Amazon EKS

This repository builds and tests multi-agent orchestration for SRE workflows using kagent and kmcp. An orchestrator uses six specialist agents as tools to diagnose Kubernetes faults and coordinate repairs. Changes pause at the operator's execution-approval gate, including when the operator is invoked by another agent.

Six of the seven agents are YAML configurations: a model reference, system instructions and allowed tools. kagent supplies the deployment model, its Google ADK-based Python runtime and built-in operational tool servers. kmcp runs additional Model Context Protocol (MCP) servers. The custom work includes an in-cluster network-probe server, an incident reporter with its own tool-calling loop and Agent-to-Agent (A2A) interface, and scripts that capture and check the behavior.

> **Recorded results:** the troubleshooter diagnosed all five individual faults in 5–52 s each. Of twelve specialist answers, ten were correct, one incomplete and one partly wrong. The orchestrator repaired a Service after a backend-selection question and execution approval; its longest diagnostic task never completed. Direct approve/reject tests checked that the execution gate controlled actual changes. [Results](#results).

## Start here

| If you want to… | Read |
|---|---|
| Understand the workflow and engineering decisions | [Article](docs/article.md) |
| Deploy the stack and run the demonstrations | [Setup guide](docs/setup-guide.md) |
| Inspect resource fields, ADK, MCP, A2A and API boundaries | [Runtime and protocol reference](docs/runtime-and-protocols.md) |
| Follow the original commands, outputs and investigations | [Build record](docs/build-record.md) |
| Review the short public post | [LinkedIn draft](docs/linkedin-post.md) |

The experiment ran on 2026-10-07. Its cluster was subsequently deleted; the recorded responses and screenshots document that run. The reordered setup procedure is reconstructed from the final manifests and has not been rerun on a fresh cluster.

![System overview: SRE, kagent controller, sre-orchestrator, six specialist agents, five MCP tool servers, demo-broken and monitoring targets, platform strip](docs/diagrams/01-system-overview.jpg)

*The system. An SRE reaches the orchestrator through the kagent controller over A2A; the orchestrator delegates to six specialists, which use selected tools on five MCP servers; the tools act on the demo namespace and the monitoring stack. kmcp, PostgreSQL and kagent are the platform underneath.*

## Contents

- [What this builds](#what-this-builds)
- [Architecture](#architecture)
- [Method](#method)
- [Results](#results)
- [Findings](#findings)
- [Limitations](#limitations)
- [Versions](#versions)
- [Repository layout](#repository-layout)
- [Reproducing](#reproducing)

## What this builds

- **kagent 0.9.10:** Kubernetes resources configure models, agents and tool sources. The controller creates agent Deployments and Services; the declarative Python runtime builds on Google ADK. The chart supplies operational tools and PostgreSQL-backed sessions. See the [pinned runtime sources](docs/runtime-and-protocols.md#who-runs-what).
- **kmcp 0.3.0:** an `MCPServer` resource becomes a Deployment and Service. For stdio packages, an init container copies agentgateway and the main container runs the adapter with the package as its child. Native HTTP servers run directly. The CLI scaffolds, builds and deploys.
- **Seven agents**, six in [infra/kagent/agents/](infra/kagent/agents/) as YAML and one in [byo/incident-reporter-agent/](byo/incident-reporter-agent/) as code. Longer introductions are in the [article](docs/article.md).

## Architecture

A2A (Agent-to-Agent) carries client requests and specialist delegation. MCP (Model Context Protocol) carries tool discovery and execution. The repair path is user → orchestrator → specialist → tool server → Kubernetes API. The orchestrator has no direct Kubernetes tools; model calls go to OpenRouter.

- **Cluster:** Amazon EKS 1.34 in `ap-south-1`, two availability zones, one NAT gateway, 2 × `t3.xlarge` managed nodes (4 vCPU, 16 GiB each) in private subnets, Amazon Linux 2023. Add-ons: VPC CNI, CoreDNS, kube-proxy, metrics-server, EKS Pod Identity agent, EBS CSI driver. A `gp3` StorageClass is the default.
- **Namespace `kagent`:** kagent controller and UI, kmcp controller, PostgreSQL 18 (2 GiB volume), the `kagent-tools`, `querydoc` and `grafana-mcp` servers, the `fetch` and `netprobe-mcp` servers run by kmcp, and seven agent pods.
- **Namespace `monitoring`:** kube-prometheus-stack 83.6.0 (Prometheus with 10 GiB volume, Grafana, kube-state-metrics, node-exporter).
- **Namespace `demo-broken`:** five workloads, each failing in one documented way ([infra/demo/broken-workloads.yaml](infra/demo/broken-workloads.yaml)).
- **Models:** five `ModelConfig` resources, all `provider: OpenAI` with `baseUrl: https://openrouter.ai/api/v1` and one Secret, `kagent-openrouter`.
- **Images built here:** `netprobe-mcp:0.1.0` (98 MB) and `incident-reporter-agent:0.1.0` (57 MB), in Amazon ECR.
- **Exposure:** every Service is `ClusterIP`; the UI, the controller API and the tool servers are reached with `kubectl port-forward`.

## Method

**The agents.**

| Agent | Model (OpenRouter) | Tool sources | Changes the cluster | Distinctive feature |
|---|---|---|---|---|
| `cluster-troubleshooter` | deepseek-v4.1-flash | 9 read-only `k8s_*` tools | no | `promptTemplate` with kagent's built-in prompt snippets |
| `sre-operator` | grok-4.7 | 11 `k8s_*` tools | yes, 6 under `requireApproval` | human approval per change |
| `observability-analyst` | gemini-3.8-flash | 5 `prometheus_*` + 3 `k8s_*` + 5 Grafana tools | no | two routes to Prometheus |
| `release-manager` | kimi-k3 | 6 `helm_*` + 2 `k8s_*`, upgrades under approval | with approval | Go runtime tried; its image is missing from the registry |
| `runbook-assistant` | claude-sonnet-5.5 | 4 `k8s_*`, `fetch` (kmcp), `query_documentation` (labelled Service) | no | three kinds of tool source |
| `incident-reporter` | deepseek-v4.1-flash | tool server + netprobe over MCP, directly | no | bring your own container |
| `sre-orchestrator` | claude-sonnet-5.5 | the six agents, as `type: Agent` tools | tested repair via `sre-operator` | prompt in a ConfigMap |

**The faults.**

| Workload | Fault | Expected diagnosis |
|---|---|---|
| `api` | image `nginx:1.99.99-does-not-exist` | ImagePullBackOff |
| `worker` | prints "config file ... not found", exits 1 | CrashLoopBackOff with that log line |
| `cache` | allocates 200 MiB under a 64 MiB limit | OOMKilled |
| `checkout` Service | selector `app: checkout`, pods are `app: web` | no endpoints |
| `batch` | requests 16 CPU on 4-CPU nodes | Pending, Insufficient cpu |

**The scenarios.** Fourteen initial questions in [scripts/scenarios.txt](scripts/scenarios.txt), sent as A2A `message/send` through the controller by [scripts/run-scenarios.sh](scripts/run-scenarios.sh). Specialist questions were run once; orchestrator questions were retried over streaming, and scenario 13 was also attempted directly against its Service. Scenario 15 added delegated repair. Each answer was compared with the fault table above and with `kubectl`. A completed task is not counted as correct unless the diagnosis names the fault. Plus the approval flow, run twice ([scripts/approval-demo.sh](scripts/approval-demo.sh)): one approve, one reject.

**What was recorded.** Raw A2A responses and answer text under [results/answers/](results/answers/), summarised by [scripts/summarise-scenarios.py](scripts/summarise-scenarios.py) into [results/summary/](results/summary/). REST and MCP responses under [results/raw/](results/raw/).

## Results

Measured on 2026-10-07, one run per specialist question. Orchestrator rows describe the outcomes after the documented retries. Full answers in [results/answers/](results/answers/), summary in [results/summary/scenarios.md](results/summary/scenarios.md).

| # | Agent | Question (short) | Time (s) | Tool calls | Verdict |
|---|---|---|---|---|---|
| s01 | cluster-troubleshooter | why is `api` not running | 11 | 4 | correct |
| s02 | cluster-troubleshooter | why does `worker` restart, quote the log | 8 | 5 | correct |
| s03 | cluster-troubleshooter | what happens to `cache` | 12 | 5 | correct |
| s04 | cluster-troubleshooter | why `checkout` refuses connections | 52 | 8 | correct |
| s05 | cluster-troubleshooter | why is `batch` Pending | 5 | 4 | correct |
| s06 | cluster-troubleshooter | which pods healthy / unhealthy | 9 | 2 | partly wrong (`batch` in both lists) |
| s07 | observability-analyst | most restarts in 30 min | 30 | 9 | correct |
| s08 | observability-analyst | node CPU and memory vs capacity | 46 | 11 | correct |
| s09 | observability-analyst | alert rules, any firing | 33 | 6 | correct but incomplete (4 cluster-wide alerts missed) |
| s10 | release-manager | Helm releases and versions | 7 | 1 | correct |
| s11 | runbook-assistant | diagnose `cache`, quote the docs | 35 | 9 | correct |
| s12 | incident-reporter (BYO) | incident report for the namespace | 161 | 21 | correct, all five faults |
| s13 | sre-orchestrator | find every problem and the fixes | 180+ | 2 agents | never completed (controller 3-minute timeout, twice; direct re-run stopped on cost) |
| s14 | sre-orchestrator | CPU/memory pressure, restarts because of it | 78 | 2 agents | correct |
| s15 | sre-orchestrator | fix `checkout` so it has endpoints | 62 | 2 agents, 2 human turns | fixed: selector patched after an `ask_user` choice and the operator's approval; 3 endpoints |

**Approval flow (`sre-operator`):** scale `web` to 3, approved: `input-required` → `completed`, replicas 2 → 3. Scale `web` to 2, rejected: `input-required` → `completed`, replicas unchanged at 3.

![kagent UI chat with sre-orchestrator paused at a three-choice question](docs/screenshots/kagent-ui-orchestrator-ask-user-question.png)

*Scenario 15 in the kagent UI: the troubleshooter has answered and the orchestrator is asking the human which backend the Service should select before it calls the operator.*

**Start-up:** Python runtime agent pods Ready 17 s after start with the image cached (15 s of that is the first readiness probe delay), 51 to 59 s on a first pull; the BYO pod 19 s.

**Cost:** about 6 USD of OpenRouter usage for the day, including the abandoned orchestrator runs; not broken down per scenario.

## Findings

**A nine-tool YAML agent diagnosed all five faults.** 5 to 52 s and 4 to 8 tool calls each, on the cheapest model. No code.

**`toolNames` and `requireApproval` are enforced by the runtime.** On reject, the operator's `k8s_scale` never ran and the deployment was unchanged; nothing in the prompt decided that.

**Agents as tools work, and the approval gate survives the nesting.** The orchestrator fixed the broken Service via the troubleshooter and the operator, with the operator's approval surfacing at the orchestrator.

**Completed is not correct.** Two completed specialist answers were wrong or incomplete. The orchestrator combined resource and metrics evidence in scenario 14; no controlled comparison established a general accuracy improvement.

**Controller calls hit a three-minute timeout.** Both `message/send` and `message/stream` were cut at 180 s; recorded task lookups remained `working`. Direct Service access bypasses this controller boundary, but the longest direct run was stopped on cost and did not complete.

**Abandoned work can overlap with retries.** Three concurrent requests were present when the orchestrator exceeded its default 1 GiB memory limit. The final manifest sets 2 GiB. The roughly 6 USD model total includes retries, but there is no per-request cost breakdown.

**Three integration issues required investigation:** the Grafana MCP image's loopback-only `Host` check, the Go runtime's missing image digest, the Prometheus tool's rejection of comparison operators.

## Limitations

- **One cluster and no repeated specialist trials.** Orchestrator questions were retried during troubleshooting. Pass counts describe the recorded experiment, not general agent or model accuracy.
- **Known faults, hand-written questions.** The questions point at the namespace; a real incident does not.
- **Not a production setup.** The controller runs in its default `unsecure` auth mode (any caller is `admin@kagent.dev`), nothing is exposed outside the cluster, there is no NetworkPolicy, and the tool server's Kubernetes permissions are the chart's defaults.
- **kmcp 0.3.0 adds no readiness or liveness probes** to the pods it creates.
- **The `prometheus_query_tool` rejects comparison operators** (`>`, `<`, `==`) as "potentially dangerous characters".
- **Pre-1.0 software.** kagent 0.9.10 and kmcp 0.3.0; kagent's 1.0 alphas replace the `Agent` resource model used here, and 0.10.3 was released after the source review and was not evaluated.
- **Model spend was not recorded per scenario.** Only the day's total (about 6 USD) is known, from the OpenRouter account page.
- **The Postman collection was not run in Postman.** Its requests mirror the `curl` calls that were run.

## Versions

| Component | Version |
|---|---|
| Amazon EKS | 1.34 (platform `eks.34`), nodes `v1.34.11-eks-3b4a6ca` |
| `aws-ebs-csi-driver` / `eks-pod-identity-agent` / `metrics-server` add-ons | v1.66.0-eksbuild.1 / v1.3.10-eksbuild.3 / v0.9.0-eksbuild.11 |
| kagent | 0.9.10 (charts `kagent-crds`, `kagent`; images `cr.kagent.dev/kagent-dev/kagent/{controller,ui,app,golang-adk}:0.9.10`) |
| kagent-tools | 0.2.1 (`ghcr.io/kagent-dev/kagent/tools:0.2.1`) |
| kmcp | 0.3.0 (`ghcr.io/kagent-dev/kmcp/controller:0.3.0`), agentgateway 0.9.0-musl |
| Grafana MCP | `mcp/grafana:latest` as pinned by the chart (pulled 2026-10-07) |
| querydoc | `ghcr.io/kagent-dev/doc2vec/mcp:1.1.14` |
| kagent PostgreSQL | `postgres:18.3-alpine` |
| kube-prometheus-stack | chart 83.6.0, operator v0.90.1, Grafana 12.4.3 |
| kmcp CLI | v0.3.0 |
| FastMCP (netprobe) | 3.0.0; `mcp` 1.30.0; Python 3.12 |
| a2a-sdk (incident-reporter) | 0.3.26; `openai` 3.26.0 |
| eksctl / kubectl / helm / aws-cli / uv | 0.230.0-dev / v1.35.0 / v4.2.4 / 2.37.4 / (see setup guide) |

## Repository layout

```
README.md
.env.example                        the two values the build needs (OpenRouter key, Grafana password)
docs/setup-guide.md                 dependency-ordered deployment, checks, demonstrations and teardown
docs/build-record.md                original commands, outputs, screenshots and investigations
docs/runtime-and-protocols.md       resource fields, ADK runtime, MCP/A2A and API boundaries
docs/article.md                     workflow, implementation, method, results and limitations
docs/linkedin-post.md               short post
docs/linkedin-carousel.md           brief and page content for the LinkedIn document post
docs/diagrams/                      generated diagrams (NN-name.jpg) and their image prompts (prompts.md)
docs/screenshots/                   captures from the live system
infra/eks/                          eksctl ClusterConfig, default StorageClass
infra/kagent/values.yaml            kagent Helm values (OpenRouter default model, Grafana MCP, bundled agents off)
infra/kagent/models/                four ModelConfigs
infra/kagent/prompts/               the orchestrator's prompt as a ConfigMap
infra/kagent/agents/                the seven Agent resources
infra/kmcp/                         MCPServer resources: fetch (public package), netprobe-mcp (built here)
infra/monitoring/values.yaml        kube-prometheus-stack values
infra/demo/broken-workloads.yaml    the five faults
byo/netprobe-mcp/                   the FastMCP server (kmcp init scaffold + four tools + tests)
byo/incident-reporter-agent/        the bring-your-own agent (loop + A2A SDK server + Dockerfile)
postman/                            build_collection.py and the generated collection
scripts/                            ask-agent.sh, run-scenarios.sh, approval-demo.sh, summarise-scenarios.py
results/raw/                        REST and MCP responses, build logs
results/answers/<agent>/            raw A2A responses and answer text per scenario
results/summary/                    scenario table
```

`.env`, `.kube/` and `repos/` (the kagent and kmcp source checkouts used as the reference) are gitignored.

## Reproducing

Start at [docs/setup-guide.md](docs/setup-guide.md) for the prerequisites, variables and deployment sequence. You need AWS access with eight spare on-demand vCPUs, Docker, the listed command-line tools and an OpenRouter API key. Billed while they exist: the EKS control plane, 2 × `t3.xlarge`, one NAT gateway, 12 GiB of application volumes, two 50 GiB node root volumes and two ECR repositories. The hourly total was not calculated; price it with the AWS Pricing Calculator. Teardown is the last section of the setup guide.

## License

`TODO`: no LICENSE file yet.
