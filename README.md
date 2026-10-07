# SRE agents on Amazon EKS with kagent and kmcp

This repository builds seven AI agents for platform and SRE work on one Amazon EKS cluster, using kagent (agents as Kubernetes resources) and kmcp (MCP servers as Kubernetes resources). Six agents are YAML only. They use the 124-tool server kagent installs, a Grafana MCP server, two MCP servers run by kmcp (one a public package, one written here with FastMCP), five models through OpenRouter, and human approval for every change. The seventh agent is a container: a tool-calling loop without a framework, served with the A2A SDK. All of them are pointed at a namespace with five deliberately broken workloads, and their answers are checked against the known faults.

The point of the repo is not only the agents. It contains every command in the order it was run, the exact chart values and manifests, the raw A2A and REST responses, a Postman collection for the kagent API and the tool servers, and the problems hit on the way, including a tool server that refused its own controller.

> **Results:** the read-only troubleshooter diagnosed all five faults correctly (5 to 52 s, 4 to 8 tool calls each); 10 of 12 specialist answers were correct, 1 incomplete, 1 partly wrong. The approval gate held on approve and on reject. The orchestrator fixed a broken Service through two human approvals, and could not finish its longest task because the controller cuts any A2A call at 3 minutes. See [Results](#results).

<!-- TODO(diagram): docs/diagrams/01-system-overview.jpg -->

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

- **kagent 0.9.10**: an `Agent` resource is a model reference, a system prompt and a list of tools; the controller runs it as a Deployment and exposes it over A2A. Its chart installs the `kagent-tools` MCP server (124 tools for Kubernetes, Helm, Prometheus, Istio, Cilium, Argo, Kubescape), a Grafana MCP server and a documentation server, plus a bundled PostgreSQL for sessions.
- **kmcp 0.3.0**: an `MCPServer` resource becomes a Deployment and a Service. A stdio package is adapted to HTTP by an `agentgateway` sidecar; a server with its own HTTP transport runs as is. The CLI scaffolds, builds and deploys.
- **Seven agents**, six in [infra/kagent/agents/](infra/kagent/agents/) as YAML and one in [byo/incident-reporter-agent/](byo/incident-reporter-agent/) as code. Longer introductions are in the [article](docs/article.md).

## Architecture

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
| `sre-orchestrator` | claude-sonnet-5.5 | the six agents, as `type: Agent` tools | through `sre-operator` only | prompt in a ConfigMap |

**The faults.**

| Workload | Fault | Expected diagnosis |
|---|---|---|
| `api` | image `nginx:1.99.99-does-not-exist` | ImagePullBackOff |
| `worker` | prints "config file ... not found", exits 1 | CrashLoopBackOff with that log line |
| `cache` | allocates 200 MiB under a 64 MiB limit | OOMKilled |
| `checkout` Service | selector `app: checkout`, pods are `app: web` | no endpoints |
| `batch` | requests 16 CPU on 4-CPU nodes | Pending, Insufficient cpu |

**The scenarios.** Fourteen questions in [scripts/scenarios.txt](scripts/scenarios.txt), each sent once as an A2A `message/send` through the kagent controller by [scripts/run-scenarios.sh](scripts/run-scenarios.sh). Each answer was compared with the fault table above and with `kubectl`. A completed task is not counted as correct unless the diagnosis names the fault. Plus the approval flow, run twice ([scripts/approval-demo.sh](scripts/approval-demo.sh)): one approve, one reject.

**What was recorded.** Raw A2A responses and answer text under [results/answers/](results/answers/), summarised by [scripts/summarise-scenarios.py](scripts/summarise-scenarios.py) into [results/summary/](results/summary/). REST and MCP responses under [results/raw/](results/raw/).

## Results

Measured on 2026-10-07, one run per question. Full answers in [results/answers/](results/answers/), summary in [results/summary/scenarios.md](results/summary/scenarios.md).

| # | Agent | Question (short) | s | Tool calls | Verdict |
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

**Start-up:** Python runtime agent pods Ready 17 s after start with the image cached (15 s of that is the first readiness probe delay), 51 to 59 s on a first pull; the BYO pod 19 s.

**Cost:** about 6 USD of OpenRouter usage for the day, including the abandoned orchestrator runs; not broken down per scenario.

## Findings

**A nine-tool YAML agent diagnosed all five faults.** 5 to 52 s and 4 to 8 tool calls each, on the cheapest model. No code.

**`toolNames` and `requireApproval` are enforced by the runtime.** On reject, the operator's `k8s_scale` never ran and the deployment was unchanged; nothing in the prompt decided that.

**Agents as tools work, and the approval gate survives the nesting.** The orchestrator fixed the broken Service via the troubleshooter and the operator, with the operator's approval surfacing at the orchestrator.

**Completed is not correct.** Two `completed` answers were wrong or incomplete; the orchestrator's cross-check ("they agreed on every point") is worth more than either specialist alone.

**The controller cuts every A2A call at 3 minutes**, `message/send` and `message/stream` alike (the a2a-go client's default timeout), and the task then stays `working` forever. The agent's own Service has no such limit.

**Abandoned requests keep running.** They OOM-killed the orchestrator at the default 1 GiB limit when retried, and they are where most of the 6 USD went.

**Three chart details fail silently:** the Grafana MCP image's loopback-only `Host` check, the Go runtime's missing image digest, the Prometheus tool's rejection of comparison operators.

## Limitations

- **One cluster, one run.** Each scenario was asked once. Pass counts describe this run, not the agents' accuracy in general.
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
docs/setup-guide.md                 every command, in order, with output, errors and teardown
docs/article.md                     Medium article draft
docs/linkedin-post.md               short post
docs/diagrams/prompts.md            image prompts for the diagrams
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

Start at [docs/setup-guide.md](docs/setup-guide.md). You need an AWS account with 8 spare on-demand vCPUs in the region, Docker, and an OpenRouter API key. Billed while they exist: the EKS control plane, 2 × `t3.xlarge`, one NAT gateway, 12 GiB of gp3 volumes, two ECR repositories. The hourly total was not calculated; price it with the AWS Pricing Calculator. Teardown is the last section of the setup guide.

## License

`TODO`: no LICENSE file yet.
