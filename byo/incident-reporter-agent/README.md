# incident-reporter: a bring-your-own SRE agent

This agent writes an incident report for a Kubernetes namespace: summary, evidence, root cause and suggested fixes. I wrote its Python ReAct tool-calling loop myself. The A2A Python SDK serves the agent to clients; it does not supply the loop. The agent reads cluster state and runs network probes through MCP servers, then returns a report without applying repairs.

The [article](../../docs/article.md#custom-agent-owning-the-tool-calling-loop) explains its role in the multi-agent system. The [setup guide](../../docs/setup-guide.md#9-build-the-custom-agent-image) covers the image build; the committed [BYO Agent manifest](../../infra/kagent/agents/incident-reporter.yaml) configures its deployment.

## Contents

- [What belongs to the agent and what the SDK supplies](#what-belongs-to-the-agent-and-what-the-sdk-supplies)
- [The loop, one request at a time](#the-loop-one-request-at-a-time)
- [Invoke the deployed agent with curl and jq](#invoke-the-deployed-agent-with-curl-and-jq)
- [Watch tool steps with message/stream](#watch-tool-steps-with-messagestream)
- [Use the existing Postman collection](#use-the-existing-postman-collection)
- [Configuration and deployment](#configuration-and-deployment)
- [Learning priorities](#learning-priorities)
- [Recorded results and current limits](#recorded-results-and-current-limits)

## What belongs to the agent and what the SDK supplies

An agent is an application that calls a model, interprets its response and decides what to execute next. In this example, the model can request tools. The application executes those requests and returns the observations to the model until it produces its report.

| Piece | Responsibility in this project |
|---|---|
| [agent.py](src/agent.py) | Instructions, model calls, tool discovery and filtering, routing tool calls and the ReAct loop |
| [server.py](src/server.py) | The A2A agent card, executor, progress updates, task artifacts and HTTP startup |
| MCP Python SDK | Connections, initialization, tool discovery and calls to the two MCP servers |
| OpenAI Python client | Requests to the configured OpenAI-compatible model endpoint, OpenRouter by default |
| A2A Python SDK | A2A request handling, task events and HTTP serving through `A2AStarletteApplication` |
| kagent | Runs the BYO container as a Deployment and Service and makes it callable by clients and other agents |

A **declarative** kagent agent defines a model, instructions and tools in YAML and uses kagent's runtime. This **BYO** agent packages its own implementation in an image. Its `Agent` resource uses `type: BYO`; the model interaction and tool handling live in the application code.

There are two protocol boundaries. A client talks **A2A to the agent** to ask for a report. The agent talks **MCP to tool servers** to gather evidence. The client does not need to initialize the agent as an MCP server. See the [MCP README](../netprobe-mcp/README.md#mcp-fundamentals-using-dns_lookup) for the tool-side handshake, schemas and error categories.

## The loop, one request at a time

At startup, `IncidentReporter.connect()` opens one MCP session to each server, initializes it and lists its tools. It keeps only the configured names:

| Server | Tools offered to the model |
|---|---|
| `kagent-tools` | `k8s_get_resources`, `k8s_describe_resource`, `k8s_get_events`, `k8s_get_pod_logs`, `k8s_get_resource_yaml`, `k8s_check_service_connectivity` |
| `netprobe` | `dns_lookup`, `tcp_connect`, `http_check`, `tls_cert_expiry` |

The application converts each MCP `inputSchema` into the model's function `parameters`. It also records which server owns each tool name. The model sees the allowed definitions, rather than every tool exposed by the servers.

For `Write an incident report for namespace demo-broken.`, the loop works as follows:

1. Start a message list with the system instructions and the user's request.
2. Send that conversation and the discovered tool definitions to the model.
3. If the model requests a tool, parse its arguments, find the owning MCP session and call the tool.
4. Append the model's tool request and the tool result to the conversation. The model's `tool_call_id` connects the observation to the requested call.
5. Ask the model again with the new evidence. Repeat until it returns text without tool calls, or the turn limit is reached.

This is the ReAct pattern here: the model chooses an action, receives an observation and uses it to choose the next step. The application controls execution. It does not expose the model's private reasoning. One model response can request several tools; the implementation executes them sequentially.

The probe results are evidence, not the diagnosis itself. DNS may resolve a Service with no endpoints. A failed TCP connection adds another observation; Kubernetes resource state can then explain why. The report should combine those facts and quote the event messages or logs that support the conclusion.

The A2A executor surrounds this loop. It starts a task, emits `working` updates for tool calls and results, publishes the final text as an artifact named `incident-report`, and completes the task. An exception escaping the loop becomes a `failed` task. A successful HTTP response alone does not establish an accurate report.

## Invoke the deployed agent with curl and jq

Use an already deployed agent with working model credentials, access to both MCP servers and a namespace to inspect. This keeps the reporter and its probes inside the cluster; the laptop only sends requests. These commands do not deploy or repair workloads.

In a terminal using the intended Kubernetes context:

```bash
kubectl config current-context
kubectl -n kagent get svc incident-reporter
kubectl -n kagent port-forward svc/incident-reporter 8091:8080
```

Leave the port-forward running. In another terminal, inspect the agent card:

```bash
AGENT_URL='http://127.0.0.1:8091'
curl -sS "$AGENT_URL/.well-known/agent-card.json" | jq .
```

The card describes the agent, its incident-report skill and streaming support. Use the forwarded URL explicitly for these manual requests; the card's advertised URL can differ from the port-forward address.

Send a request using A2A 0.3 JSON-RPC, the interface used by this build:

```bash
AGENT_RESPONSE=$(mktemp)

curl -sS --max-time 600 "$AGENT_URL/" \
  -H 'Content-Type: application/json' \
  --data "$(jq -n --arg message_id "$(uuidgen)" '{
    jsonrpc:"2.0", id:"report-1", method:"message/send",
    params:{message:{role:"user",kind:"message",messageId:$message_id,
      parts:[{kind:"text",text:"Write an incident report for namespace demo-broken."}]}}
  }')" | jq . | tee "$AGENT_RESPONSE"
```

This calls the model and can incur provider charges. Allow time for the tool loop: the original report took 161 seconds. The curl limit is a client deadline, not a guarantee that work stops when the client disconnects.

Inspect the task state and extract the report from the saved response:

```bash
jq '{error, task_id:.result.id, context_id:.result.contextId, state:.result.status.state}' "$AGENT_RESPONSE"
jq -r '.result.artifacts[]?.parts[]? | select(.kind == "text") | .text' "$AGENT_RESPONSE"
```

For the original completed report, the [recorded A2A response](../../results/answers/incident-reporter/s12.json) contains the task and report; the [text response](../../results/answers/incident-reporter/s12.txt) is easier to read. Current names, observations and timings depend on the cluster. The saved files are historical EKS evidence, not a promise of identical output.

The identifiers have different jobs:

| Identifier | Meaning |
|---|---|
| JSON-RPC `id`, here `report-1` | Client-selected ID matching one response to its request |
| `messageId` | Identifies the user message; generated here with `uuidgen` |
| Task `id` in the result | Server-issued ID used to retrieve this task |
| `contextId` | Groups related A2A interactions; does not by itself give this custom loop conversation memory |

There is no `Mcp-Session-Id` on these A2A requests. The reporter maintains its own MCP sessions internally. The [A2A 0.3 specification](https://a2a-protocol.org/v0.3.0/specification/) describes the message, task and artifact fields.

To retrieve the task from the same running instance after receiving its ID:

```bash
TASK_ID=$(jq -r '.result.id // empty' "$AGENT_RESPONSE")
curl -sS "$AGENT_URL/" \
  -H 'Content-Type: application/json' \
  --data "$(jq -n --arg task_id "$TASK_ID" '{
    jsonrpc:"2.0", id:"task-1", method:"tasks/get", params:{id:$task_id}
  }')" | jq .

rm "$AGENT_RESPONSE"
```

Retrieve only a task ID actually returned by the server. `InMemoryTaskStore` retains tasks in that process; a restart loses them.

## Watch tool steps with message/stream

Use the same port-forward and change the A2A method to `message/stream`:

```bash
curl -sSN --max-time 600 "$AGENT_URL/" \
  -H 'Content-Type: application/json' \
  -H 'Accept: text/event-stream' \
  --data "$(jq -n --arg message_id "$(uuidgen)" '{
    jsonrpc:"2.0", id:"report-stream-1", method:"message/stream",
    params:{message:{role:"user",kind:"message",messageId:$message_id,
      parts:[{kind:"text",text:"Write an incident report for namespace demo-broken."}]}}
  }')" |
sed -E '/^(event:|id:|retry:|:)/d; s/^data: *//' | jq --unbuffered .
```

This starts another report, rather than watching the preceding `message/send` task. Run one demonstration at a time. The `working` updates contain `call: ...` and `result: ...` messages from the custom executor, followed by the report artifact and the final task status. They show tool activity, not private model reasoning.

SSE carries JSON inside `data:` lines. The formatter removes single-line SSE framing and lets jq print each event as it arrives; it is not a full SSE client with multiline-event handling or reconnection.

Direct Service access bypasses the controller's forwarding path. In the original kagent 0.9.10 tests, the controller cut long requests at 180 seconds, including streams. Bypassing that boundary does not remove model, MCP or client timeouts. See the [timeout investigation](../../docs/build-record.md#16-the-orchestrator-over-messagestream).

## Use the existing Postman collection

Import [postman/kagent.postman_collection.json](../../postman/kagent.postman_collection.json). **4b · Call the bring-your-own MCP server directly** tests netprobe tools. **6 · Invoke an agent (A2A)** asks an agent to use tools and produce an answer.

For the collection's existing controller routes, leave this port-forward running:

```bash
kubectl -n kagent port-forward svc/kagent-controller 8083:8083
```

Set these collection variables, checking for environment overrides:

| Variable | Value |
|---|---|
| `base_url` | `http://127.0.0.1:8083` |
| `ns` | `kagent` |
| `agent` | `incident-reporter` |

In folder **6**:

1. Send **1 · agent card** to inspect the reporter through the controller.
2. Duplicate **2 · message/send · ask the troubleshooter** and name the copy for the incident reporter. Its URL uses `{{agent}}`, despite the original request title.
3. Replace the text in `params.message.parts` with `Write an incident report for namespace demo-broken.` and send it.
4. Inspect `result.status.state` and `result.artifacts`, rather than only the HTTP status. The existing response script saves `task_id` and `session_id` and prints artifact text to the Postman console.
5. Use **4 · tasks/get** to inspect the returned task. The collection's `session_id` stores the A2A `contextId`; it is unrelated to an MCP session header.

For direct Service access, keep the `8091:8080` reporter port-forward instead and change the duplicated request's URL to `http://127.0.0.1:8091/`. The direct card URL is `http://127.0.0.1:8091/.well-known/agent-card.json`. Changing only `base_url` leaves `/api/a2a/...` attached, which is a controller route and does not exist on this server. Point a duplicated `tasks/get` request at `/` too when using direct access.

To stream, duplicate the request and change its method in the JSON body to `message/stream`; the HTTP method remains POST. For long requests, raise the Postman request timeout, for example to 600,000 ms. A larger Postman timeout does not override the controller's own deadline. The collection's request labelled **A2A-Version 1.0** is not the example for this A2A 0.3 server.

## Configuration and deployment

The application reads environment variables directly; it does not automatically load a `.env` file. The model setting for this BYO agent comes from its own environment, not a declarative kagent `ModelConfig`.

| Variable | Default or requirement |
|---|---|
| `OPENROUTER_API_KEY` | Required; supplied from the `kagent-openrouter` Secret in the manifest |
| `OPENAI_BASE_URL` | `https://openrouter.ai/api/v1` |
| `MODEL` | `deepseek/deepseek-v4.1-flash` |
| `KAGENT_TOOLS_URL` | `http://kagent-tools.kagent:8084/mcp` |
| `NETPROBE_URL` | `http://netprobe-mcp.kagent:3000/mcp` |
| `MAX_TURNS` | `20` model calls per request |
| `PORT` | `8080` |
| `PUBLIC_URL` | `http://localhost:8080/`, advertised in the agent card |

`main()` connects to both MCP servers before starting the A2A HTTP server. Missing credentials or unreachable MCP endpoints can therefore prevent the card endpoint from becoming available. The defaults use cluster DNS; running `uv run python src/server.py` on a laptop also requires exported credentials and reachable MCP URLs, usually through two more port-forwards. The deployed-agent walkthrough avoids that extra setup.

The [Dockerfile](Dockerfile) installs the Python environment in a build stage and copies it and `src/` into a non-root runtime image. kagent expects this build to listen on port 8080, serve `/.well-known/agent-card.json` and accept A2A JSON-RPC at `/`. The [setup guide](../../docs/setup-guide.md) contains the image build, registry push and manifest application commands.

## Learning priorities

Read these in order while following [agent.py](src/agent.py) and [server.py](src/server.py):

1. **Own the execution loop.** The model proposes calls; Python runs them. Trace one model response, one MCP call and the observation returned to the model before adding more orchestration.
2. **Separate the goal from observations.** The system prompt asks for a report; events, logs and probes supply facts. Check whether each conclusion follows from a quoted observation, rather than trusting fluent text.
3. **Discover tools and expose only what the agent needs.** The MCP schema becomes the model's input contract. The allowlists and tool-owner map determine which calls can actually be routed.
4. **Keep protocol boundaries clear.** A2A accepts a user task and returns progress and artifacts. MCP lists and executes tools. An MCP request ID, a model tool-call ID and an A2A task ID belong to different exchanges.
5. **Make progress and results explicit.** `TaskUpdater` publishes tool-step status and the final artifact. `completed` means the task ended; it does not independently establish correctness.
6. **Bound the loop and its context.** `MAX_TURNS` limits model calls, and each tool result is truncated to 12,000 characters. Neither is a total time limit; truncation can also remove evidence the model needs.
7. **Decide what state survives.** Each `run()` starts a new conversation. The A2A task store is in memory, and no persistent conversational memory is implemented.
8. **Handle failures deliberately.** Malformed model argument JSON becomes `{}` in this implementation; MCP/model exceptions can fail the task. Tool error text is currently passed back to the model without structured `isError` handling.
9. **Separate permissions from instructions.** The prompt and allowlists limit this application's intended actions. Kubernetes RBAC, tool-server authorization and network access provide the underlying permission boundaries.
10. **Package, deploy and verify each boundary.** Check startup, card discovery, tool access, model access and the report against live evidence. A Ready pod or HTTP 200 alone does not prove the whole workflow worked.

## Recorded results and current limits

On 2026-10-07, scenario **s12** diagnosed all five configured EKS faults in **161 seconds with 21 tool calls**. See the [full response](../../results/answers/incident-reporter/s12.json), [readable answer](../../results/answers/incident-reporter/s12.txt) and [evaluated article results](../../docs/article.md#results). The [generated scenario summary](../../results/summary/scenarios.json) records execution state and tool counts; it does not grade diagnostic accuracy.

This is a small learning implementation. Its current behavior has practical limits:

- MCP discovery runs once at startup; tool name collisions across servers are not handled explicitly.
- The loop reads text content from MCP results, rather than preserving `structuredContent` or checking `isError` separately.
- Reaching the turn limit returns a "Stopped after ..." string; the wrapper still publishes it and marks the task `completed`.
- There is no conversation persistence, request queue, explicit total deadline or custom retry policy. The model SDK can apply its own retries.
- Cancellation is not implemented, and disconnecting curl does not establish that the model/tool work stopped.
- The custom server adds no authentication layer. The loop is intended for read-only reporting and has no human-approval implementation; suggested repair commands are report text, not executed changes.

These limits are visible in the code and are useful next steps when adapting the example. The original report establishes what this implementation did for the recorded namespace, rather than general reliability across incidents.
