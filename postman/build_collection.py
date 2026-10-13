#!/usr/bin/env python3
"""Builds postman/kagent.postman_collection.json.

Requests target the kagent controller (port 8083), built-in tool server
(port 8084), or custom netprobe server (local port 3002) through port-forwards. Routes come from the kagent
v0.9.10 source (go/core/internal/httpserver/server.go); the comments name the
file that defines each one.

    python3 postman/build_collection.py
"""
import json
import pathlib

OUT = pathlib.Path(__file__).with_name("kagent.postman_collection.json")

MCP_HEADERS = {"Accept": "application/json, text/event-stream"}


def req(name, method, url, body=None, desc="", headers=None, tests=None, var="base_url"):
    h = [{"key": k, "value": v} for k, v in (headers or {}).items()]
    if body is not None:
        h.insert(0, {"key": "Content-Type", "value": "application/json"})
    path = url.split("?")[0].strip("/").split("/")
    r = {
        "name": name,
        "request": {
            "method": method,
            "header": h,
            "url": {"raw": "{{%s}}%s" % (var, url), "host": ["{{%s}}" % var], "path": path},
            "description": desc,
        },
    }
    if "?" in url:
        r["request"]["url"]["query"] = [
            {"key": q.split("=")[0], "value": q.split("=", 1)[1] if "=" in q else ""}
            for q in url.split("?", 1)[1].split("&")
        ]
    if body is not None:
        r["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, indent=2),
            "options": {"raw": {"language": "json"}},
        }
    script = tests or "pm.test('HTTP 2xx', () => pm.response.to.be.success);"
    r["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": script.split("\n")}}]
    return r


def folder(name, desc, items):
    return {"name": name, "description": desc, "item": items}


def rpc(id_, method, params=None):
    b = {"jsonrpc": "2.0", "id": id_, "method": method}
    if params is not None:
        b["params"] = params
    return b


def a2a_message(text, extra=None):
    m = {"role": "user", "kind": "message", "messageId": "{{$guid}}", "parts": [{"kind": "text", "text": text}]}
    m.update(extra or {})
    return rpc("1", "message/send", {"message": m})


SESSION_TEST = (
    "pm.test('HTTP 2xx', () => pm.response.to.be.success);\n"
    "const h = pm.response.headers.get('mcp-session-id');\n"
    "if (h) { pm.collectionVariables.set('%s', h); console.log('session', h); }"
)

A2A_TEST = (
    "pm.test('HTTP 2xx', () => pm.response.to.be.success);\n"
    "const r = pm.response.json().result || {};\n"
    "if (r.id) pm.collectionVariables.set('task_id', r.id);\n"
    "if (r.contextId) pm.collectionVariables.set('session_id', r.contextId);\n"
    "console.log('state:', r.status && r.status.state);\n"
    "const texts = (r.artifacts || []).flatMap(a => a.parts || []).filter(p => p.text).map(p => p.text);\n"
    "if (texts.length) console.log('ANSWER:\\n' + texts.at(-1));"
)

collection = {
    "info": {
        "name": "kagent on EKS: controller API, tool server, agents",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        "description": (
            "The kagent controller's HTTP API (port 8083), the built-in tool server's MCP endpoint "
            "(port 8084), and the agents of this build, all through kubectl port-forwards:\n\n"
            "    kubectl -n kagent port-forward svc/kagent-controller 8083:8083\n"
            "    kubectl -n kagent port-forward svc/kagent-tools 8084:8084\n"
            "    kubectl -n kagent port-forward svc/netprobe-mcp 3002:3000\n\n"
            "Authentication: the controller runs in its default `unsecure` mode. It takes the user "
            "from `?user_id=` or the `X-User-Id` header and otherwise uses `admin@kagent.dev`. "
            "No request is rejected. Sessions are filtered by that user.\n\n"
            "Routes were read from kagent v0.9.10 `go/core/internal/httpserver/server.go`. "
            "Most responses are wrapped as `{error, data, message}`."
        ),
    },
    "variable": [
        {"key": "base_url", "value": "http://127.0.0.1:8083", "description": "kagent controller port-forward"},
        {"key": "tools_url", "value": "http://127.0.0.1:8084", "description": "kagent-tools port-forward"},
        {"key": "ns", "value": "kagent", "description": "namespace of the agents"},
        {"key": "agent", "value": "cluster-troubleshooter", "description": "agent name for the A2A and session requests"},
        {"key": "user_id", "value": "admin@kagent.dev", "description": "user the controller attributes sessions to"},
        {"key": "session_id", "value": "", "description": "set by 'create session' and by A2A responses (= A2A contextId)"},
        {"key": "task_id", "value": "", "description": "set by A2A responses"},
        {"key": "mcp_session_id", "value": "", "description": "Mcp-Session-Id from the controller /mcp initialize"},
        {"key": "tools_session_id", "value": "", "description": "Mcp-Session-Id from the tool server initialize"},
        {"key": "netprobe_url", "value": "http://127.0.0.1:3002", "description": "netprobe-mcp port-forward (svc/netprobe-mcp 3002:3000)"},
        {"key": "netprobe_session_id", "value": "", "description": "Mcp-Session-Id from the netprobe initialize"},
    ],
    "item": [],
}

# 1 ---------------------------------------------------------------- system
collection["item"].append(folder("1 · System", "Routes that need no body. /health and /version skip authentication.", [
    req("health", "GET", "/health", desc="`{error:false, data:{status:'OK'}}`. handlers/health.go"),
    req("version", "GET", "/version", desc="`{kagent_version, git_commit, build_date}`; not wrapped. server.go:219"),
    req("current user (/api/me)", "GET", "/api/me", desc="In unsecure mode returns `{sub: '<user id>'}` for the resolved user. Try it with `?user_id=someone@example.com` to see the fallback logic.", headers={"X-User-Id": "{{user_id}}"}),
    req("namespaces", "GET", "/api/namespaces", desc="`[{name, status}]` for every namespace the controller can see."),
]))

# 2 ---------------------------------------------------------- model configs
mc_spec = {
    "provider": "OpenAI",
    "model": "x-ai/grok-4.7",
    "apiKeySecret": "kagent-openrouter",
    "apiKeySecretKey": "OPENROUTER_API_KEY",
    "openAI": {"baseUrl": "https://openrouter.ai/api/v1"},
    "defaultHeaders": {"HTTP-Referer": "https://github.com/tharindu-sankalpa/eks-kagent-sre-agents", "X-Title": "kagent SRE agents"},
}
collection["item"].append(folder("2 · Model configs", "A ModelConfig is kagent's 'model an agent can use'. Every one in this build points at OpenRouter through its OpenAI-compatible API and reads the key from the Secret `kagent-openrouter`. handlers/modelconfig.go", [
    req("list model configs", "GET", "/api/modelconfigs", desc="`[{ref: 'ns/name', spec, status}]`."),
    req("get one model config", "GET", "/api/modelconfigs/{{ns}}/grok-4-7"),
    req("create model config (API instead of YAML)", "POST", "/api/modelconfigs",
        {"ref": "{{ns}}/grok-4-7-from-api", "spec": mc_spec},
        desc="Same result as `kubectl apply` of a ModelConfig. `ref` is `namespace/name`. Optional `apiKey` creates the Secret for you; here the existing Secret is referenced instead. `defaultHeaders` are sent on every LLM request (OpenRouter uses HTTP-Referer and X-Title for attribution). Returns 201."),
    req("update model config", "PUT", "/api/modelconfigs/{{ns}}/grok-4-7-from-api",
        {"spec": dict(mc_spec, openAI={"baseUrl": "https://openrouter.ai/api/v1", "temperature": "0.2"})},
        desc="Body is `{spec, apiKey?, secrets?}`; the whole spec is replaced."),
    req("delete model config", "DELETE", "/api/modelconfigs/{{ns}}/grok-4-7-from-api"),
    req("supported providers", "GET", "/api/modelproviderconfigs/models", desc="`[{name, type, requiredParams, optionalParams}]`: the providers kagent knows and what each needs."),
    req("known models per provider", "GET", "/api/models", desc="A hardcoded provider→models map used by the UI's dropdowns (handlers/models.go). OpenRouter models are not in it; any model id works in a ModelConfig regardless."),
]))

# 3 ---------------------------------------------------- tool servers / tools
rmcp = {
    "type": "RemoteMCPServer",
    "remoteMCPServer": {
        "apiVersion": "kagent.dev/v1alpha2", "kind": "RemoteMCPServer",
        "metadata": {"name": "fetch-via-api", "namespace": "{{ns}}"},
        "spec": {"description": "The kmcp-run fetch server, registered a second time through the API", "protocol": "STREAMABLE_HTTP", "url": "http://fetch.kagent:3000/mcp", "timeout": "30s"},
    },
}
collection["item"].append(folder("3 · Tool servers and tools", "Tool sources kagent knows: RemoteMCPServer resources (a URL), MCPServer resources (run by kmcp), and Services labelled `kagent.dev/mcp-service: \"true\"`. The controller connects to each, lists its tools and stores them. handlers/toolservers.go, handlers/tools.go", [
    req("list tool servers with their discovered tools", "GET", "/api/toolservers", desc="`[{ref, groupKind, discoveredTools: [{name, description}]}]`. The built-in server `kagent/kagent-tool-server` lists 124 tools."),
    req("list all tools (flat)", "GET", "/api/tools", desc="`[{id, server_name, group_kind, description, ...}]`. `id` is the MCP tool name. No input schema here; get that from the server itself (folder 4)."),
    req("tool server types", "GET", "/api/toolservertypes"),
    req("register a RemoteMCPServer through the API", "POST", "/api/toolservers", rmcp,
        desc="Body: `{type, remoteMCPServer | mcpServer, secrets?}`. Equivalent to applying the RemoteMCPServer YAML."),
    req("delete the API-registered tool server", "DELETE", "/api/toolservers/{{ns}}/fetch-via-api"),
]))

# 4 ------------------------------------------ call tools directly (no LLM)
tools = [
    req("1 · initialize", "POST", "/mcp", rpc(1, "initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "postman", "version": "1.0"}}),
        desc="Standard MCP handshake against the tool server itself (`kagent-tools`, port 8084). The test script stores the `Mcp-Session-Id` response header for the following requests.",
        headers=MCP_HEADERS, tests=SESSION_TEST % "tools_session_id", var="tools_url"),
    req("2 · notifications/initialized", "POST", "/mcp", {"jsonrpc": "2.0", "method": "notifications/initialized"},
        desc="Second half of the handshake. Expect HTTP 202 with an empty body.",
        headers=dict(MCP_HEADERS, **{"Mcp-Session-Id": "{{tools_session_id}}"}), var="tools_url"),
    req("3 · tools/list (124 tools with input schemas)", "POST", "/mcp", rpc(2, "tools/list"),
        desc="Every tool with its description and `inputSchema`. This is where the argument names for the calls below come from.",
        headers=dict(MCP_HEADERS, **{"Mcp-Session-Id": "{{tools_session_id}}"}), var="tools_url"),
]
calls = [
    ("k8s_get_resources · all pods", "k8s_get_resources", {"resource_type": "pods", "all_namespaces": True, "output": "wide"}, "The same data `kubectl get pods -A -o wide` returns, as text."),
    ("k8s_get_events · demo-broken", "k8s_get_events", {"namespace": "demo-broken"}, "Events of the namespace with the deliberately broken workloads."),
    ("k8s_describe_resource · deployment api", "k8s_describe_resource", {"resource_type": "deployment", "resource_name": "api", "namespace": "demo-broken"}, ""),
    ("k8s_get_pod_logs · worker", "k8s_get_pod_logs", {"pod_name": "<a worker pod name from the pods call>", "namespace": "demo-broken", "tail_lines": 20}, "Replace the pod name with one from the first call."),
    ("helm_list_releases", "helm_list_releases", {"all_namespaces": True}, "Helm releases in the cluster."),
    ("prometheus_query_tool · pod restarts", "prometheus_query_tool", {"prometheus_url": "http://prometheus-kube-prometheus-prometheus.monitoring:9090", "query": "topk(5, sum by (namespace, pod) (kube_pod_container_status_restarts_total))"}, "Needs the kube-prometheus-stack from the setup guide monitoring step. The tool rejects comparison operators (`>`, `<`, `==`) as \"potentially dangerous characters\", so filter with topk() instead of `> 0`."),
    ("datetime_get_current_time", "datetime_get_current_time", {}, ""),
    ("k8s_delete_resource · the agents do not have this tool", "k8s_delete_resource", {"resource_type": "pod", "resource_name": "does-not-exist", "namespace": "demo-broken"}, "The tool server exposes 124 tools including this one and `shell`. No agent in this build is given them: `toolNames` on each Agent is the allow-list. Calling the server directly, as here, is not subject to that list."),
]
for i, (name, tool, args, d) in enumerate(calls, start=3):
    tools.append(req(f"{i+1} · tools/call · {name}", "POST", "/mcp", rpc(i, "tools/call", {"name": tool, "arguments": args}),
                     desc=d, headers=dict(MCP_HEADERS, **{"Mcp-Session-Id": "{{tools_session_id}}"}), var="tools_url"))
collection["item"].append(folder("4 · Call the built-in tools directly (no LLM)", "`kubectl -n kagent port-forward svc/kagent-tools 8084:8084`. The tool server is a plain MCP server over streamable HTTP, with no authentication. These requests are what an agent's runtime does when the model asks for a tool. Argument names are from `tools/list`; check them there if a call returns an error, since the tool server (kagent-tools 0.2.1) is not part of the kagent source.", tools))

# 4b --------------------------------------- call the BYO netprobe server
np = [
    req("1 · initialize", "POST", "/mcp", rpc(1, "initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "postman", "version": "1.0"}}),
        desc="The bring-your-own MCP server from byo/netprobe-mcp, run by kmcp with the HTTP transport. `kubectl -n kagent port-forward svc/netprobe-mcp 3002:3000`.",
        headers=MCP_HEADERS, tests=SESSION_TEST % "netprobe_session_id", var="netprobe_url"),
    req("2 · notifications/initialized", "POST", "/mcp", {"jsonrpc": "2.0", "method": "notifications/initialized"},
        headers=dict(MCP_HEADERS, **{"Mcp-Session-Id": "{{netprobe_session_id}}"}), var="netprobe_url"),
    req("3 · tools/list (4 tools)", "POST", "/mcp", rpc(2, "tools/list"),
        headers=dict(MCP_HEADERS, **{"Mcp-Session-Id": "{{netprobe_session_id}}"}), var="netprobe_url"),
]
for i, (name, tool, args, d) in enumerate([
    ("dns_lookup · the broken Service still resolves", "dns_lookup", {"hostname": "checkout.demo-broken.svc.cluster.local"}, "A ClusterIP Service resolves even with no endpoints: DNS is not the problem."),
    ("tcp_connect · but nothing answers on it", "tcp_connect", {"host": "checkout.demo-broken.svc.cluster.local", "port": 80}, "The selector matches no pod, so the connection fails. Together with the previous call this is the diagnosis."),
    ("http_check · a working Service", "http_check", {"url": "http://kagent-ui.kagent.svc.cluster.local:8080/"}, "A probe from inside the cluster to a healthy Service."),
    ("tls_cert_expiry · a public host", "tls_cert_expiry", {"host": "example.com"}, ""),
], start=3):
    np.append(req(f"{i+1} · tools/call · {name}", "POST", "/mcp", rpc(i, "tools/call", {"name": tool, "arguments": args}),
                  desc=d, headers=dict(MCP_HEADERS, **{"Mcp-Session-Id": "{{netprobe_session_id}}"}), var="netprobe_url"))
collection["item"].append(folder("4b · Call the bring-your-own MCP server directly", "Same handshake as folder 4, against the server built in byo/netprobe-mcp and deployed with kmcp (setup guide custom MCP server step).", np))

# 5 ------------------------------------------------------------------ agents
agent_obj = {
    "apiVersion": "kagent.dev/v1alpha2", "kind": "Agent",
    "metadata": {"name": "node-reporter", "namespace": "{{ns}}"},
    "spec": {
        "description": "Created through the controller API instead of kubectl. Reports on nodes only.",
        "type": "Declarative",
        "declarative": {
            "modelConfig": "default-model-config",
            "systemMessage": "You report on the nodes of this cluster. Use k8s_get_resources with resource_type nodes and output wide, then k8s_describe_resource for details. Answer only from tool results.",
            "tools": [{"type": "McpServer", "mcpServer": {"apiGroup": "kagent.dev", "kind": "RemoteMCPServer", "name": "kagent-tool-server", "toolNames": ["k8s_get_resources", "k8s_describe_resource"]}}],
        },
    },
}
collection["item"].append(folder("5 · Agents", "An Agent is one YAML resource: description, type (Declarative or BYO), model config, system message, tools. The API takes and returns the same object `kubectl` does. handlers/agents.go", [
    req("list agents", "GET", "/api/agents?namespace={{ns}}", desc="`[{id, agent: {spec, status...}, modelProvider, model, tools, deploymentReady, accepted}]`. `deploymentReady` and `accepted` are what the UI shows as the agent's health."),
    req("get one agent", "GET", "/api/agents/{{ns}}/{{agent}}"),
    req("create an agent through the API", "POST", "/api/agents", agent_obj,
        desc="The body is a full `kagent.dev/v1alpha2` Agent object. The controller creates the Deployment and Service for it; `deploymentReady` turns true after about a minute. Returns 201."),
    req("update the agent (PUT, no path params)", "PUT", "/api/agents", dict(agent_obj, spec=dict(agent_obj["spec"], description="Updated through the API")),
        desc="PUT has no namespace/name in the path; they come from `metadata`. Only `spec` is replaced."),
    req("delete the API-created agent", "DELETE", "/api/agents/{{ns}}/node-reporter"),
]))

# 6 ----------------------------------------------------------- A2A invoke
collection["item"].append(folder("6 · Invoke an agent (A2A)", "Agents are invoked over the A2A protocol at `/api/a2a/{ns}/{name}/`: JSON-RPC 2.0, method `message/send`. The controller forwards to the agent pod and returns a Task whose `status.state` is `completed`, `failed`, `working` or `input-required` (waiting for a human). Without an `A2A-Version` header the wire format is A2A 0.3 (lowercase states); with `A2A-Version: 1.0` the v1 format. a2a/a2a_handler_mux.go", [
    req("1 · agent card", "GET", "/api/a2a/{{ns}}/{{agent}}/.well-known/agent-card.json",
        desc="Built by the controller from the Agent resource: name, description, skills, and the URL callers should use."),
    req("2 · message/send · ask the troubleshooter", "POST", "/api/a2a/{{ns}}/{{agent}}/",
        a2a_message("Which pods in namespace demo-broken are not Running, and why? One line per pod."),
        desc="One JSON-RPC call; the agent's whole tool loop runs behind it (30 s to 2 min). The test script stores `task_id` and `session_id` (= `contextId`) and prints the answer. Set the `agent` variable to try the other agents.",
        tests=A2A_TEST),
    req("3 · message/send · follow-up in the same session", "POST", "/api/a2a/{{ns}}/{{agent}}/",
        a2a_message("Which of those would you fix first, and how?", {"contextId": "{{session_id}}"}),
        desc="Same `contextId` = same session: the agent sees the previous turn.", tests=A2A_TEST),
    req("4 · tasks/get", "POST", "/api/a2a/{{ns}}/{{agent}}/", rpc("2", "tasks/get", {"id": "{{task_id}}"}),
        desc="The stored task with its history and artifacts."),
    req("5 · sre-operator · a change that needs approval", "POST", "/api/a2a/{{ns}}/sre-operator/",
        a2a_message("Scale the deployment web in namespace demo-broken to 3 replicas."),
        desc="`sre-operator` lists `k8s_scale` in `requireApproval`. Expect `status.state: input-required`: the runtime emitted an `adk_request_confirmation` call and is waiting. The pending call is in the task's last message as a data part.",
        tests=A2A_TEST),
    req("6 · sre-operator · approve the pending change", "POST", "/api/a2a/{{ns}}/sre-operator/",
        rpc("1", "message/send", {"message": {"role": "user", "kind": "message", "messageId": "{{$guid}}", "contextId": "{{session_id}}", "taskId": "{{task_id}}",
            "parts": [{"kind": "data", "data": {"decision_type": "approve"}}, {"kind": "text", "text": "Approved"}]}}),
        desc="Approval is another `message/send` on the same `contextId` and `taskId`, with a data part `{decision_type: approve}` (or `reject`, optionally with `rejection_reason`). This is what the UI's Approve button sends (ui/src/components/chat/ChatInterface.tsx). The task then continues and completes.",
        tests=A2A_TEST),
    req("7 · message/stream · the orchestrator (long-running agents)", "POST", "/api/a2a/{{ns}}/sre-orchestrator/",
        rpc("1", "message/stream", {"message": {"role": "user", "kind": "message", "messageId": "{{$guid}}", "parts": [{"kind": "text", "text": "Is the cluster under CPU or memory pressure right now, and is anything in demo-broken restarting because of it?"}]}}),
        desc="This request explicitly targets sre-orchestrator, regardless of the `agent` variable. The default question is scenario 14, which completed in the recorded build. `message/stream` returns server-sent events as the agent works: status updates (delegated calls appear as function-call data parts), artifact updates with the answer, and a final status. In kagent 0.9.10 the controller cuts both `message/send` and `message/stream` at 180 seconds; streaming exposes progress but does not bypass that timeout. This request does not automatically save task/session IDs: for continuation, copy the latest result.taskId and result.contextId from the events into `task_id` and `session_id`.",
        headers={"Accept": "text/event-stream"},
        tests="pm.test('HTTP 2xx', () => pm.response.to.be.success);"),
    req("8 · message/send with A2A-Version 1.0", "POST", "/api/a2a/{{ns}}/{{agent}}/",
        a2a_message("How many nodes does this cluster have?"),
        desc="Same call, v1 wire format: the response uses `TASK_STATE_COMPLETED`-style enums.", headers={"A2A-Version": "1.0"},
        tests="pm.test('HTTP 2xx', () => pm.response.to.be.success);\nconsole.log(JSON.stringify(pm.response.json().result && pm.response.json().result.status));"),
]))

# 7 --------------------------------------------------------------- sessions
collection["item"].append(folder("7 · Sessions and tasks", "A session is a conversation with one agent; its id is the A2A `contextId`. The UI creates one per chat. handlers/sessions.go, handlers/tasks.go", [
    req("create a session", "POST", "/api/sessions?user_id={{user_id}}", {"agent_ref": "{{ns}}/{{agent}}", "name": "postman session"},
        desc="`agent_ref` is required. The returned `id` is used as `contextId` in A2A messages. The test script stores it.",
        tests="pm.test('HTTP 2xx', () => pm.response.to.be.success);\nconst d = pm.response.json().data || pm.response.json();\nif (d.id) pm.collectionVariables.set('session_id', d.id);"),
    req("message/send inside that session", "POST", "/api/a2a/{{ns}}/{{agent}}/",
        a2a_message("Summarise the state of namespace demo-broken in three lines.", {"contextId": "{{session_id}}"}), tests=A2A_TEST),
    req("list my sessions", "GET", "/api/sessions?user_id={{user_id}}", desc="Filtered by user. The UI's chats are here too, under `admin@kagent.dev`."),
    req("sessions of one agent", "GET", "/api/sessions/agent/{{ns}}/{{agent}}?user_id={{user_id}}"),
    req("session with its events", "GET", "/api/sessions/{{session_id}}?user_id={{user_id}}",
        desc="`{session, events: [...]}`. Each event's `data` is a JSON-encoded A2A message: user turns, tool calls, tool results, agent text."),
    req("tasks of the session", "GET", "/api/sessions/{{session_id}}/tasks?user_id={{user_id}}"),
    req("get a task", "GET", "/api/tasks/{{task_id}}?user_id={{user_id}}"),
    req("delete the session", "DELETE", "/api/sessions/{{session_id}}?user_id={{user_id}}"),
]))

# 8 ----------------------------------------------------- controller MCP
cm = dict(MCP_HEADERS, **{"Mcp-Session-Id": "{{mcp_session_id}}"})
collection["item"].append(folder("8 · The controller's own MCP endpoint (agents as tools)", "The controller serves an MCP server at `/mcp` on port 8083 with two tools: `list_agents` and `invoke_agent`. Any MCP client, or another agent, can use kagent agents as tools this way. internal/mcp/mcp_handler.go", [
    req("1 · initialize", "POST", "/mcp", rpc(1, "initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "postman", "version": "1.0"}}),
        desc="Server name is `kagent-agents`. Stateful unless the controller runs with KAGENT_MCP_STATELESS=true, so keep the session header.", headers=MCP_HEADERS, tests=SESSION_TEST % "mcp_session_id"),
    req("2 · notifications/initialized", "POST", "/mcp", {"jsonrpc": "2.0", "method": "notifications/initialized"}, headers=cm),
    req("3 · tools/list", "POST", "/mcp", rpc(2, "tools/list"), desc="Expect `list_agents` and `invoke_agent`.", headers=cm),
    req("4 · tools/call · list_agents", "POST", "/mcp", rpc(3, "tools/call", {"name": "list_agents", "arguments": {}}),
        desc="Only agents that are accepted and whose deployment is ready are listed.", headers=cm),
    req("5 · tools/call · invoke_agent", "POST", "/mcp", rpc(4, "tools/call", {"name": "invoke_agent", "arguments": {"agent": "{{ns}}/{{agent}}", "task": "How many nodes does this cluster have, and which version do they run?"}}),
        desc="Runs an A2A message/send behind the scenes and returns the agent's text plus `{agent, text, context_id}`.", headers=cm),
]))

# 9 ----------------------------------------------------------- feedback
collection["item"].append(folder("9 · Feedback", "Thumbs up/down on an agent message, as the UI does. handlers/feedback.go", [
    req("submit feedback", "POST", "/api/feedback?user_id={{user_id}}", {"is_positive": True, "feedback_text": "Found the ImagePullBackOff and quoted the event.", "issue_type": "factual"},
        desc="`feedback_text` is required; `issue_type` is one of instructions, factual, incomplete, tool."),
    req("list feedback", "GET", "/api/feedback?user_id={{user_id}}"),
]))

OUT.write_text(json.dumps(collection, indent=2, ensure_ascii=False) + "\n")
n = sum(len(f["item"]) for f in collection["item"])
print(f"wrote {OUT.name}: {len(collection['item'])} folders, {n} requests")
