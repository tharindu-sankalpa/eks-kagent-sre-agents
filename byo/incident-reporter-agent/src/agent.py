"""The agent: a plain while loop, no framework.

One turn of the loop:
  1. send the conversation to the model (OpenRouter, OpenAI-compatible API)
  2. if the model asked for tool calls, run them against the MCP servers and
     append the results to the conversation
  3. otherwise the model's text is the answer; stop

The tools come from two MCP servers over streamable HTTP:
  - kagent's built-in tool server (read-only Kubernetes tools)
  - the netprobe server from byo/netprobe-mcp (network checks)
Every MCP tool is offered to the model as an OpenAI "function" tool with the
server's own input schema; nothing is hand-written per tool.
"""

from __future__ import annotations

import json
import os
from contextlib import AsyncExitStack
from dataclasses import dataclass, field

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from openai import AsyncOpenAI

SYSTEM_PROMPT = """You are an incident reporter for one Kubernetes cluster.

Given a namespace, produce an incident report with these sections:
1. Summary: one sentence per unhealthy workload, or "nothing is wrong" if all is healthy.
2. Evidence: the exact event message, log line or probe result that shows each problem.
3. Root cause: the most likely cause for each problem.
4. Fix: the kubectl command or manifest change that resolves it.

Rules:
- Call tools before stating any fact. Start with k8s_get_resources for pods in
  the namespace (output "wide"), then events, then describe or logs for each
  unhealthy pod. Use the netprobe tools (dns_lookup, tcp_connect, http_check)
  to check Services from inside the cluster.
- Stop calling tools once the evidence explains every problem.
- Never invent names, counts or messages. Quote tool output.
- You cannot change the cluster.
"""

# The only allow-list in this agent: which tools of each server the model may see.
KAGENT_TOOLS = {
    "k8s_get_resources", "k8s_describe_resource", "k8s_get_events", "k8s_get_pod_logs",
    "k8s_get_resource_yaml", "k8s_check_service_connectivity",
}
NETPROBE_TOOLS = {"dns_lookup", "tcp_connect", "http_check", "tls_cert_expiry"}


@dataclass
class McpServer:
    name: str
    url: str
    allowed: set[str]
    session: ClientSession | None = None
    tools: list[dict] = field(default_factory=list)  # OpenAI tool definitions


class IncidentReporter:
    def __init__(self) -> None:
        self.model = os.environ.get("MODEL", "deepseek/deepseek-v4.1-flash")
        self.max_turns = int(os.environ.get("MAX_TURNS", "20"))
        self.llm = AsyncOpenAI(
            base_url=os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.environ["OPENROUTER_API_KEY"],
        )
        self.servers = [
            McpServer("kagent-tools", os.environ.get("KAGENT_TOOLS_URL", "http://kagent-tools.kagent:8084/mcp"), KAGENT_TOOLS),
            McpServer("netprobe", os.environ.get("NETPROBE_URL", "http://netprobe-mcp.kagent:3000/mcp"), NETPROBE_TOOLS),
        ]
        self._stack: AsyncExitStack | None = None
        self._tool_owner: dict[str, McpServer] = {}

    # -- MCP --------------------------------------------------------------
    async def connect(self) -> None:
        """Open one MCP session per server and collect the allowed tools."""
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()
        for srv in self.servers:
            read, write, _ = await self._stack.enter_async_context(streamablehttp_client(srv.url))
            srv.session = await self._stack.enter_async_context(ClientSession(read, write))
            await srv.session.initialize()
            listed = await srv.session.list_tools()
            for t in listed.tools:
                if t.name not in srv.allowed:
                    continue
                srv.tools.append({
                    "type": "function",
                    "function": {"name": t.name, "description": t.description or "", "parameters": t.inputSchema},
                })
                self._tool_owner[t.name] = srv

    async def close(self) -> None:
        if self._stack:
            await self._stack.aclose()

    async def call_tool(self, name: str, arguments: dict) -> str:
        srv = self._tool_owner.get(name)
        if srv is None or srv.session is None:
            return f"error: unknown tool {name}"
        result = await srv.session.call_tool(name, arguments)
        text = "\n".join(c.text for c in result.content if getattr(c, "text", None))
        return text[:12000]  # keep one tool result from flooding the context

    # -- the loop ---------------------------------------------------------
    async def run(self, user_text: str, on_step=None) -> str:
        """Run the ReAct loop for one request and return the final text.

        on_step(kind, detail) is called for each tool call and result so the
        A2A server can stream progress; it is optional.
        """
        tools = [t for s in self.servers for t in s.tools]
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_text}]

        for turn in range(self.max_turns):
            resp = await self.llm.chat.completions.create(model=self.model, messages=messages, tools=tools, tool_choice="auto")
            msg = resp.choices[0].message

            if not msg.tool_calls:
                return msg.content or "(the model returned no text)"

            # The model wants tools. Record its request, run each call, append results.
            messages.append({"role": "assistant", "content": msg.content,
                             "tool_calls": [tc.model_dump() for tc in msg.tool_calls]})
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                if on_step:
                    await on_step("call", f"{tc.function.name}({json.dumps(args)})")
                output = await self.call_tool(tc.function.name, args)
                if on_step:
                    await on_step("result", f"{tc.function.name}: {output[:200]}")
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": output})

        return f"Stopped after {self.max_turns} turns without a final answer."
