# SRE agents on Amazon EKS with kagent and kmcp: six agents from YAML, one tool server, one broken namespace

An agent that can look at a cluster and say why a pod is failing is not hard to imagine. What is hard is everything around it: where the agent runs, how it reaches the Kubernetes API, which operations it is allowed to perform, who approves the ones that change things, and how a second and third agent get the same treatment without a new deployment pipeline each time. kagent answers those questions with Kubernetes resources: a model is a `ModelConfig`, a tool source is a `RemoteMCPServer` or an `MCPServer`, an agent is an `Agent`. This article builds six agents on one EKS cluster that way, points them at five deliberately broken workloads, and records what they found, what they got wrong, and what the YAML did not cover.

The environment is one Amazon EKS 1.34 cluster in `ap-south-1` with two `t3.xlarge` nodes. Every command, manifest and raw response is in the repository, and the build is recorded step by step in its setup guide, including the three things that went wrong.

Repository: `<REPO_URL>`

<!-- TODO(diagram): docs/diagrams/01-system-overview.jpg -->
*The whole system. Look at the arrows that leave the agent pods: every one goes to an MCP server, and the main one is the tool server kagent installs.*

## The building blocks

### kagent: AI agents as Kubernetes resources

kagent is a Kubernetes-native framework that brings agent, tool and model configuration into Kubernetes through custom resources. It includes a controller, an agent runtime, a UI and a CLI. Solo.io open sourced kagent in March 2025 and donated it to the CNCF at KubeCon Europe.

**The problem it solves.** Without something like it, teams end up with agents running as ad-hoc Python scripts and MCP servers running on laptops or in random containers, with no consistent security, scaling or visibility. Each agent is its own deployment problem.

**How it works.** You define an agent in YAML: its system prompt, which model it uses, and which tools it can call. Then you `kubectl apply` it, and the controller runs it. In version 0.9.10, the version this build uses, the resources are:

- **`ModelConfig`**: a provider, a model name, and a reference to the Secret holding the API key. kagent supports OpenAI, Anthropic, Azure OpenAI, Gemini, Vertex AI, Bedrock, Ollama and others; anything with an OpenAI-compatible API works through the `OpenAI` provider with a `baseUrl`, which is how OpenRouter is used here.
- **`RemoteMCPServer`**: the URL of an MCP server that already exists. The controller connects to it, lists its tools and records them in the resource's status.
- **`Agent`**: a description, a `ModelConfig` reference, a system message, and a list of tools picked by name from one or more tool sources. The controller turns it into a Deployment and a Service, and exposes it over the A2A protocol at `/api/a2a/<namespace>/<name>/`.

Two fields on an agent's tool list do most of the governance work in this article. `toolNames` is an allow-list: the agent's model never sees a tool that is not on it. `requireApproval` is a subset of that list: before any of those tools runs, the agent pauses, the task goes to the `input-required` state, and a human approves or rejects the call.

**The built-in tool server.** kagent's chart ships ready-made tool servers. The main one, `kagent-tools`, exposed 124 tools in this build: 22 for Kubernetes (`k8s_get_resources`, `k8s_get_pod_logs`, `k8s_describe_resource`, `k8s_get_events`, `k8s_scale`, `k8s_rollout`, `k8s_apply_manifest`, `k8s_delete_resource`, ...), 6 for Helm, 5 for Prometheus, and the rest for Istio, Cilium, Argo Rollouts and Kubescape, plus `shell`. That is what makes the SRE pitch real: the tools that a troubleshooting agent needs are already running in the cluster before you write your first agent. The chart also ships a Grafana MCP server (65 tools in this build) and a documentation search server.

**Memory, observability, multiple runtimes.** Agents can have long-term memory backed by a vector store, emit OpenTelemetry traces, and run on a Python or a Go runtime. None of these are used in this build.

**Downsides.** It needs a Kubernetes cluster and a PostgreSQL database, which is a lot for a single chatbot or a quick prototype. It is pre-1.0, and its 1.0 alphas replace the `Agent` resource with a different model (covered under "Setup").

In short: kagent makes an agent a Kubernetes resource and ships the Kubernetes tools an SRE agent needs.

Sources: [kagent.dev](https://kagent.dev), [source](https://github.com/kagent-dev/kagent).

### kmcp: building and deploying MCP servers

Agents are only useful if they can reach tools, and MCP (Model Context Protocol) is now the standard way to expose tools to agents. kmcp is Solo.io's open source suite for lightweight MCP tool development and operations, and it is now part of the kagent project. Put simply, kmcp builds and hosts the tools, and kagent runs the agents that use them.

**The problem it solves.** Many MCP servers are packages meant to be started by a desktop client and spoken to over stdin and stdout; nothing in a cluster can call that. And a team that writes its own MCP servers needs a repeatable way to scaffold, build, deploy and have them discovered.

**How it works.**

- **The CLI** scaffolds a project (`kmcp init python`, from a FastMCP template; Go, TypeScript and Java templates exist too), builds its image (`kmcp build`, a `docker build` with a tag derived from the project), and deploys it (`kmcp deploy`, which generates an `MCPServer` resource).
- **The `MCPServer` resource** describes a server: an image or a package command, a port and a transport. The controller creates a Deployment, a Service, a ConfigMap and a ServiceAccount from it.
- **The stdio adapter.** For a server that only speaks stdio, the controller adds an init container that copies the `agentgateway` binary into the pod; `agentgateway` starts the package as a child process and serves its stdio as MCP over streamable HTTP. For `npx` and `uvx` commands it even supplies a default image, so a public package becomes an in-cluster HTTP endpoint from six lines of YAML.
- **Existing Services as tool sources.** A Kubernetes Service becomes a tool source for kagent if it carries the label `kagent.dev/mcp-service: "true"` and a port with `appProtocol: mcp` (or the `kagent.dev/mcp-service-port` annotation). kagent's own documentation search server is exposed that way.

**Downsides.** kmcp ships no MCP servers of its own; it is machinery. At version 0.3.0 it adds no readiness or liveness probes to the pods it creates.

In short: kmcp turns "write an MCP server" into scaffold, build, deploy, discovered.

<!-- TODO(diagram): docs/diagrams/04-kmcp-two-ways.jpg -->
*Two `MCPServer` resources, two pods. Left: a public stdio package, adapted to HTTP by agentgateway. Right: the server built in this article, serving HTTP itself. kagent discovers both the same way.*

Sources: [source](https://github.com/kagent-dev/kmcp), [agentgateway](https://agentgateway.dev).

### Why you'd need them, and the value

kagent and kmcp address the agent-deployment problem in several ways:

1. **Same operating model as the rest of your platform.** Agents, tools and model configs become declarative YAML. That gives you GitOps, version control, RBAC, namespaces and review workflows for free, and no separate "AI platform" to learn.
2. **Agents close to the systems they operate.** Running in-cluster, agents can directly observe and act on Kubernetes, Prometheus, Grafana, Istio and so on. This makes them well suited to platform-engineering and SRE automation: diagnosing failing pods, analysing events, rolling out changes.
3. **Standardized tool lifecycle.** kmcp turns "write an MCP server" into a repeatable path: scaffold, build an image, deploy, and get discovered by agents. You don't need a custom deployment approach for every tool.
4. **Avoids lock-in.** It works with many LLM providers and agent frameworks, and it uses open protocols (MCP, A2A), so you can swap models or reuse tools elsewhere.
5. **Observability and governance.** Built-in tracing lets you see what an agent did and which tools it called, which matters once agents can change production systems. Paired with agentgateway, an agent-native data plane for MCP, A2A and LLM traffic, you also get centralized authentication and policy for agent-to-tool traffic.

**When it's (and isn't) worth it.** These projects fit well if you already run Kubernetes and want production AI agents, especially agents that operate infrastructure, or if several teams build MCP tools that need a shared, governed way to deploy them. They are overkill for a single chatbot or a quick prototype; a plain agent framework running locally is simpler there.

### What an agent is, on the wire

Before the YAML, the two mechanisms every agent in this article runs on. Both are wire formats, not frameworks.

**A tool-bearing chat completion is a different request.** A normal call to a chat model is one request, one text answer. Add a `tools` array to the request body, in the OpenAI function-calling format (name, description, JSON Schema `parameters`), and the model gains a second way to answer: instead of text, it can return `tool_calls`, with `finish_reason` set to `"tool_calls"` and `content` set to `null`. Nothing has been executed. The model has asked your code to run a function with these arguments and tell it the result. Your code runs the tool, appends the assistant's `tool_calls` message and a `role: "tool"` message carrying the result (matched by `tool_call_id`), and sends the whole conversation again. When the model has enough, it answers in text with `finish_reason: "stop"`. The API is stateless, so the growing message list is the model's only memory of what it asked for; drop the tool message and the request is refused. That branch on `finish_reason` is the whole difference between "a model" and "an agent", and it is what kagent's runtime does for every agent below, including the sub-agents of the orchestrator. Two consequences follow: the tool schemas are rendered into the prompt on every turn (so they cost tokens whether or not they are used), and a capable model may skip a tool and answer directly, so the system prompt has to say when a tool is required.

**The Responses API is the other shape.** OpenAI's newer Responses API (`/v1/responses`) keeps conversation state on the server (`previous_response_id`) and can execute some tools itself, including remote MCP servers declared in the request, so the client does not run the loop for those. Function tools still come back as `function_call` items the client must answer. kagent 0.9.10 speaks chat completions only (its `ModelConfig` has no field for the Responses API; the 1.0 alphas add one), and so does this build, because every model behind OpenRouter supports it.

**MCP is how the tools get into that `tools` array.** An MCP server lists its tools (`tools/list`) with the same JSON Schema the model needs, and runs them (`tools/call`). The agent runtime copies the schemas into the chat request and forwards each `tool_calls` entry to the server that owns it. So an MCP server is a tool catalogue plus a standard way to call it, and nothing else. kagent's tool server, the Grafana server, the `fetch` server run by kmcp and the probe server built in this article are all exactly that. The transport throughout is streamable HTTP: JSON-RPC over POST, one `initialize` handshake, then a session header. The repository's Postman collection drives it by hand, with no model involved.

**A2A is how a finished agent is called.** Two things only:

- **Discovery.** `GET /.well-known/agent-card.json` returns the agent card: name, description, `capabilities` (streaming or not), `skills` (prose for the calling model to read, because agents take free-form messages, not typed arguments), and the `url` where invocation lives. It is the agent-level analogue of one entry in the `tools` array, and the orchestrator in this article reads the cards of its six specialists the same way a model reads tool schemas.
- **Invocation.** `message/send`, a JSON-RPC call to that URL with a message (role, parts, ids), returns a task with a lifecycle: `submitted`, `working`, `completed`, `failed`, or `input-required` when the agent is waiting for a human. `message/stream` is the same call with progress arriving as server-sent events, and `tasks/get` fetches a task later. kagent serves every agent this way at `/api/a2a/<namespace>/<name>/`, and a "bring your own" agent only has to serve the same card and the same methods on port 8080.

In short: tools enter through MCP, the model asks for them through `tool_calls`, the runtime loops until `finish_reason` is `stop`, and the result leaves through A2A.

## Why build it this way

- **Five of six agents are YAML only.** No code, no image. Each one differs in its model, its system prompt and its tool list.
- **Governance is in the resource.** Read-only agents simply do not list the tools that change the cluster. The operator agent lists them under `requireApproval`.
- **One model Secret, several models.** Every `ModelConfig` points at OpenRouter with the same Secret; each agent names a different model.
- **The sixth agent is code, to show the boundary.** A plain `while` loop with tool calling, no framework, served with the A2A SDK, containerised, and run by kagent as a BYO agent. It uses a bring-your-own MCP server built with kmcp.
- **Known-broken workloads instead of a healthy cluster.** Five workloads with five documented faults, so each answer can be checked.
- **The source code is the reference.** Chart values, CRD fields, routes and tool schemas were read from the kagent and kmcp checkouts at pinned versions, and the tool server's live `tools/list`.

## Setup

The full commands, outputs and errors are in the [setup guide](setup-guide.md).

1. **Cluster.** EKS 1.34 from one `eksctl` file: two `t3.xlarge` nodes in private subnets, one NAT gateway, the EBS CSI driver and Pod Identity agent, a default `gp3` StorageClass.
2. **kagent and kmcp.** kagent 0.9.10 from its published charts, which bring kmcp 0.3.0, the built-in tool server (124 tools), the documentation server, the UI and a bundled PostgreSQL. The default `ModelConfig` points at OpenRouter; the key lives in one Secret.
3. **Prometheus and Grafana** (kube-prometheus-stack), and the Grafana MCP server kagent ships, with a service-account token.
4. **Two MCP servers through kmcp.** `fetch`, a public stdio package that kmcp wraps with agentgateway (no image built), and `netprobe-mcp`, written here with FastMCP, scaffolded with `kmcp init`, built with `kmcp build`, pushed to ECR, run with the HTTP transport.
5. **Five broken workloads** in namespace `demo-broken`: a bad image tag, a crash-looping command, an OOMKilled container, a Service selector that matches nothing, an unschedulable CPU request.
6. **Five models** as `ModelConfig` resources, all through OpenRouter, each six lines.
7. **Seven agents**: six from YAML, one from a container (the bring-your-own agent).
8. **Scenarios**: fourteen questions to the agents, the approval flow with an approve and a reject, and the orchestrator run.

### Why not the newest kagent

The first checkout of kagent was `v1.0.0-alpha4`. Its chart installs no `Agent` CRD: an agent is a `Harness` plus an `AgentTemplate`, a running one is an `AgentInstance` in PostgreSQL, and the controller needs a separate runtime (Substrate: a gVisor worker pool, certificate and JWT pools, S3 snapshots) before any agent starts. `v1.0.0-alpha5`, two days later, renames the CRD group. The article is built on v0.9.10, the latest release at review time, where one YAML file is one agent. kagent 0.10.3 has since been released and was not evaluated. The lesson: check which resources a chart installs before designing around a project; the README did not show the difference, the CRD directory did.

### The most instructive problem: a tool server that refused its own controller

After enabling the Grafana MCP server that kagent's chart ships, kagent could not discover its tools:

```
calling "initialize": sending "initialize": Forbidden
```

The same `initialize` through a port-forward returned 200. With the in-cluster `Host` header it returned 403. The image the chart pins, `mcp/grafana:latest`, validates the HTTP `Host` header against a loopback-only allow-list by default, as protection against DNS rebinding, and the kagent controller calls it by its Service name. The fix is two values in the chart (`args: [--allowed-hosts, kagent-grafana-mcp.kagent:8000,...]`), after which kagent found 65 tools. The general lesson is about `latest`: a chart that pins a floating tag inherits whatever default the image adopts next, and the chart's own defaults did not account for this one. A second, smaller lesson: the resource's status stayed `Forbidden` after the fix until the controller reconciled it again, so a stale `False` is not proof a fix failed.

### What an agent is made of

Every YAML agent in this build is the same four parts, and the differences between the six are only in their values:

<!-- TODO(diagram): docs/diagrams/03-agent-anatomy.jpg -->
*One Agent resource, taken apart. Look at the two tool fields: `toolNames` is what the model can see, `requireApproval` is what a human must confirm.*

- **A model**: `modelConfig: grok-4-7`, one of five `ModelConfig` resources that differ in one line each.
- **A system prompt**: inline, or from a ConfigMap (`systemMessageFrom`), or a Go template that includes the snippets kagent ships (`promptTemplate` with `{{include "builtin/kubernetes-context"}}`). The orchestrator uses all three.
- **Tools, by name**: picked from one or more tool sources. The tool server offers 124; `cluster-troubleshooter` is given 9. Nothing outside the list exists for the agent.
- **Approval**: a subset of those names. Before any of them runs, the task pauses in `input-required` and a human approves or rejects the exact call and arguments.

The seventh field that matters is `type: Agent` in a tool list: an agent as a tool of another agent. The orchestrator has six of those and no MCP server.

| Agent | Model | Tool sources | Changes the cluster | Distinctive feature |
|---|---|---|---|---|
| `cluster-troubleshooter` | deepseek-v4.1-flash | 9 read-only `k8s_*` | no | built-in prompt snippets |
| `sre-operator` | grok-4.7 | 11 `k8s_*`, 6 under approval | with approval | `requireApproval` |
| `observability-analyst` | gemini-3.8-flash | `prometheus_*`, Grafana MCP, `k8s_*` | no | two routes to Prometheus |
| `release-manager` | kimi-k3 | `helm_*`, upgrades under approval | with approval | Go runtime tried; its image was missing |
| `runbook-assistant` | claude-sonnet-5.5 | `k8s_*`, `fetch` (kmcp), `query_documentation` (Service) | no | three kinds of tool source |
| `incident-reporter` | deepseek-v4.1-flash | tool server + netprobe, over MCP directly | no | bring your own container |
| `sre-orchestrator` | claude-sonnet-5.5 | the six agents above | through `sre-operator` only | `type: Agent` tools, prompt in a ConfigMap |

### Bring your own agent

<!-- TODO(diagram): docs/diagrams/06-byo-agent-loop.jpg -->
*The bring-your-own agent. Look at what kagent touches: only the A2A server on port 8080. The loop, the model and the MCP sessions are the container's own.*

The bring-your-own agent is about 230 lines in two files. `agent.py` opens an MCP session to each of two servers, copies their tool schemas into the chat request, and runs the tool-calling loop described above until the model answers in text. `server.py` wraps that in an `AgentExecutor` for the A2A Python SDK: a `working` status per tool step, the report as an artifact, `completed` at the end. kagent asks three things of the container: port 8080, the agent card at `/.well-known/agent-card.json` (its readiness probe), and A2A 0.3 JSON-RPC at `/`. The controller publishes its own card for the agent, forwards `message/send` to the pod, and injects `KAGENT_NAME`, `KAGENT_NAMESPACE` and `KAGENT_URL`. The image is 57 MB and the pod was Ready in 19 seconds.

The bring-your-own MCP server is smaller still: four Python functions with type hints and docstrings under `src/tools/`, which FastMCP turns into tool schemas; `kmcp init` wrote everything else, `kmcp build` built the image, and an `MCPServer` resource with `transportType: http` ran it. kagent discovered its four tools with no further resource.

## The key concept: delegation with a gate in the path

The orchestrator is the agent this article is about, because it is where the governance either holds or does not. It has no Kubernetes tools. Its `tools` list is six entries of `type: Agent`, and kagent presents each one to its model as a callable tool whose description is the other agent's `description` field, the same way an MCP server's tools are presented. When the orchestrator calls one, the runtime sends an A2A `message/send` to that agent's Service and feeds the answer back as a tool result. The specialists keep their own models, prompts and tool lists; the orchestrator never sees a `k8s_*` tool.

<!-- TODO(diagram): docs/diagrams/02-orchestrator-delegation.jpg -->
*Scenario 15 as it ran. Look at the two pauses on the SRE's line: one question from the orchestrator, one approval from the operator, and the orchestrator in between never touching the cluster.*

Scenario 15 is the whole mechanism in one request: "Fix the Service checkout in namespace demo-broken so that it has endpoints. Tell me what you intend to change before you do it."

1. The orchestrator called `cluster_troubleshooter`, which found the selector mismatch.
2. Rather than guess which pods the Service should select, it used the `ask_user` tool every kagent agent has, and the task paused in `input-required` with three choices and the exact patch it proposed, including the rollback.
3. The answer went back as a data part on the same task. The orchestrator called `sre_operator` with a precise request.
4. The operator decided on `k8s_patch_resource`, which is in its `requireApproval` list, so it paused. kagent surfaces a nested agent's pause at the parent, so the orchestrator's task went to `input-required` a second time, naming the operator's pending call.
5. One `approve` later, the patch ran, the operator verified three endpoints, and the orchestrator reported what was wrong, what changed, how to roll back, and which specialists it used.

Three calls from the client, 62 seconds, two human decisions, one change. The approval gate on the operator was defined once, on the operator, and it held when the operator was called by another agent rather than by a person.

<!-- TODO(diagram): docs/diagrams/05-approval-flow.jpg -->
*The approval gate on its own, from the earlier direct test of `sre-operator`: the request, the pause with the pending call, the decision, the result. Reject follows the same path and runs nothing.*

The same mechanism has a cost, which scenario 13 showed. A delegated call is a full A2A round trip to another agent that runs its own loop, so an orchestrator's wall-clock time is the sum of its specialists' times plus its own model calls. Through the kagent controller, that sum has to fit in three minutes.

## Method

**The faults are known in advance.** Five workloads in `demo-broken`, each broken one way: a bad image tag (`ImagePullBackOff`), a command that prints a line and exits 1 (`CrashLoopBackOff`), 200 MiB allocated under a 64 MiB limit (`OOMKilled`), a Service selector that matches no pod (no endpoints), a 16-CPU request on 4-CPU nodes (`Pending`). An answer counts as correct only if it names the fault; a completed task that says something else is a completed task, not a correct answer.

**The questions.** Fourteen in [scripts/scenarios.txt](../scripts/scenarios.txt): six to the troubleshooter (one per fault, plus a "which pods are unhealthy" question), three to the observability analyst, one to the release manager, one to the runbook assistant, one to the bring-your-own agent (a full incident report), and two to the orchestrator. Each was sent once, as an A2A `message/send` to the kagent controller, by a script that stores the raw response and the answer text. A third orchestrator question, which asks for a fix, was added after the first two.

**The approval flow** was exercised twice against `sre-operator` with its own script: a scale request approved, and a scale request rejected, with the deployment's replica count checked before and after.

**What was recorded.** For each scenario: the task state, wall-clock seconds for the request, the number and names of tool calls (from the function-call parts in the A2A task history), and the answer. Tool counts for the bring-your-own agent come from its own progress messages, since it does not emit kagent's metadata. Checks against the cluster used `kubectl`, `helm list` and a direct Prometheus query at the time of the run.

**What was not done.** No question was repeated, no model was swapped on the same question, and nothing was timed below a second. Model cost per scenario was not recorded.

## Results

Measured on 2026-10-07 on the cluster described above. Seconds are wall-clock for one request, run once. Tool calls are counted from the A2A task history. Full answers and raw responses are in `results/answers/`.

**The six specialist agents and the bring-your-own agent, twelve questions:**

| # | Agent | Question | s | Tool calls | Verdict |
|---|---|---|---|---|---|
| 1 | cluster-troubleshooter | why is `api` not running | 11 | 4 | correct: `ImagePullBackOff`, quoted the `not found` event |
| 2 | cluster-troubleshooter | why does `worker` restart, quote the log | 8 | 5 | correct: quoted `config file /etc/worker/config.yaml not found` |
| 3 | cluster-troubleshooter | what happens to `cache` | 12 | 5 | correct: `OOMKilled`, 200M under 64Mi |
| 4 | cluster-troubleshooter | why `checkout` refuses connections | 52 | 8 | correct: selector matches no pod, empty Endpoints |
| 5 | cluster-troubleshooter | why is `batch` Pending | 5 | 4 | correct: `cpu: 16`, `Insufficient cpu` |
| 6 | cluster-troubleshooter | which pods are healthy, which not | 9 | 2 | partly wrong: the four unhealthy pods are right, but `batch` also appears in the healthy list |
| 7 | observability-analyst | most restarts in 30 min | 30 | 9 | correct on its metric: `worker` and `cache`, 6 each |
| 8 | observability-analyst | node CPU and memory vs capacity | 46 | 11 | correct: 2 nodes, 4 cores and 16.55 GB each, `rate(node_cpu_seconds_total)` per node |
| 9 | observability-analyst | alert rules, any firing | 33 | 6 | correct but incomplete: six firing alerts in `demo-broken` found; four others firing cluster-wide not listed |
| 10 | release-manager | Helm releases and versions | 7 | 1 | correct: three releases, matching `helm list` |
| 11 | runbook-assistant | diagnose `cache`, quote the docs | 35 | 9 | correct: diagnosis plus the Kubernetes "Resource Management" page, fetched and quoted with its URL |
| 12 | incident-reporter (BYO) | incident report for the namespace | 161 | 21 | correct: all five faults, with in-cluster probes of `checkout` |

Twelve of twelve completed; ten correct, one correct but incomplete, one partly wrong. All five faults were found by the troubleshooter one at a time, and all five again by the bring-your-own agent in one report.

**The approval flow, `sre-operator`:**

| Request | After `message/send` | After the decision | Deployment `web` replicas |
|---|---|---|---|
| scale `web` to 3 | `input-required`, pending `k8s_scale(name=web, namespace=demo-broken, replicas=3)` | approve: `completed`, "3/3 ready" | 2 → 3 |
| scale `web` to 2 | `input-required`, pending `k8s_scale(..., replicas=2)` | reject: `completed`, "The scale was not applied" | 3 → 3 |

**The orchestrator** (`sre-orchestrator`, whose only tools are the six agents above):

| # | Question | Outcome | Delegated to | Human turns | s |
|---|---|---|---|---|---|
| 13 | find every problem in `demo-broken` and the fix for each | **never completed**: cut at 180 s twice by the controller's client timeout, and the direct re-run was stopped by hand on cost | `incident_reporter`, `cluster_troubleshooter` | 0 | 180+ |
| 14 | is the cluster under CPU or memory pressure, is anything restarting because of it | **completed, correct**: no pressure (4.7% and 7.6% CPU, 15.9% and 17.4% memory), `cache` restarts from its own 64Mi limit, `worker` from exit 1; also flagged, unasked, a kagent pod with a missing image | `observability_analyst`, `cluster_troubleshooter` | 0 | 78 |
| 15 | fix the `checkout` Service so it has endpoints; say what you intend to change first | **completed, fixed**: asked which backend to use (three choices), then the operator's `k8s_patch_resource` paused for approval, then patched the selector to `app: web`; `kubectl` showed three endpoints | `cluster_troubleshooter`, `sre_operator` | 2 | 32 + 16 + 14 |

Model spend for the day, all scenarios and all retries included, was about 6 USD on OpenRouter, most of it the orchestrator.

## Findings

**The built-in tool server is enough for a troubleshooting agent.** Five faults, five correct diagnoses from a nine-tool read-only agent on the cheapest model in the set, in 5 to 52 seconds each, with 4 to 8 tool calls. The agent is 60 lines of YAML and no code. That is the claim kagent makes, and it held.

**Two fields govern what an agent can do, and they are enforced by the runtime, not the prompt.** `toolNames` decides what the model sees; `requireApproval` decides what a human must confirm. The reject test shows the second one: the operator stated the change it intended, the human said no, the tool never ran, and the deployment was unchanged. No prompt instruction was involved in that outcome.

**Agents as tools work, and the approval gate survives the nesting.** The orchestrator fixed a broken Service by asking the troubleshooter why, asking the human which backend, calling the operator, and surfacing the operator's own approval prompt one level up. Two human decisions, one patch, verified endpoints. Its tool list is six agent names.

**A completed task is not a correct answer, and an orchestrator does not fix that.** The troubleshooter listed `batch` as both healthy and unhealthy; the analyst listed six firing alerts and missed four. Both tasks were `completed`. The orchestrator's value in scenario 14 was cross-checking: it reported that two specialists "agreed on every point", which is a stronger statement than either alone.

**Long-running agents hit a 3-minute wall at the controller.** The A2A client library kagent 0.9.10 forwards through has a 3-minute HTTP timeout, and in Go that timeout also cuts a streaming response. Any agent that works longer than that cannot be completed through the controller, with `message/send` or `message/stream`, and the task stays `working` forever. The pod's own Service has no such limit. An agent that calls other agents reaches three minutes easily.

**Abandoned requests keep running, and that is where the money went.** When the controller gave up, the orchestrator pod did not: it finished the run with nobody listening, and a retry stacked a second run on top. Three concurrent orchestrations OOM-killed the pod at its default 1 GiB limit, and the day's model spend, about 6 USD, is mostly those runs. Two things follow for anyone deploying this: give an orchestrator more memory than a specialist, and do not retry a cut request until you know the first one has finished.

**kmcp made the two "bring your own" pieces small.** The MCP server is four functions; `kmcp init` wrote the rest, `kmcp build` built it, and one `MCPServer` resource ran it. The agent is one loop and one A2A executor; kagent asked only for a port, a card and JSON-RPC. The orchestrator used the bring-your-own agent and the bring-your-own server without knowing either was not kagent's own.

**Three chart details would have gone wrong silently.** The Grafana MCP image refuses non-loopback `Host` headers by default (`latest` tag); the Go runtime's pinned image digest is not in the registry; the Prometheus query tool rejects comparison operators. None is in a README. Each cost an hour and each has a one-line fix in the setup guide.

In short: the YAML agents did the SRE work the pitch promises, the governance fields held under test including when agents call agents, and the limits that matter in practice are the controller's 3-minute timeout and the absence of cancellation.

## Limitations

- **One run of each question.** Fourteen scenarios, each asked once, on one cluster on one day. "Ten of twelve correct" is what happened, not an accuracy figure for these agents or models.
- **Known faults and pointed questions.** The questions name the namespace and often the workload. A real incident starts with a symptom, not a resource name. The orchestrator scenarios are the closest this build comes to that.
- **Verification was partial for the metrics answers.** The restart counts and firing alerts were checked against Prometheus at the time; the per-node CPU and memory shares were not recomputed by hand.
- **Not a production setup.** The controller runs in its default `unsecure` auth mode (every caller is `admin@kagent.dev`), nothing is exposed outside the cluster, there is no NetworkPolicy, the tool server's Kubernetes permissions are the chart's defaults, and kmcp 0.3.0 adds no readiness or liveness probes to the pods it creates.
- **Pre-1.0 software.** kagent 0.9.10 and kmcp 0.3.0. kagent's 1.0 alphas replace the `Agent` resource model used here; 0.10.3 was released after the source review and was not evaluated.
- **The tool server is not part of the kagent source.** `kagent-tools` 0.2.1 is a separate image. Its argument names and its PromQL filter (which rejects comparison operators) were taken from its live `tools/list` and from calling it, not from code.
- **Cost was not recorded.** OpenRouter charges per request; model spend per scenario was not captured.
- **Not compared.** No other agent runtime, no other way of hosting MCP servers, no latency or throughput measurement.

## Reproduce it

Repository: `<REPO_URL>`. Start at `docs/setup-guide.md`. You need an AWS account with 8 spare on-demand vCPUs in the region, Docker, and an OpenRouter API key. The EKS control plane, two `t3.xlarge` nodes, one NAT gateway, 12 GiB of volumes and two ECR repositories are billed while they exist; the hourly total was not calculated. Teardown is the last section of the guide.
