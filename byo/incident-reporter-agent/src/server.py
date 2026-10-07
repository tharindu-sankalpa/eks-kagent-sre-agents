"""A2A server around the agent, using the A2A Python SDK (0.3 line, which is
what kagent 0.9.10 speaks to a BYO agent).

kagent expects a BYO container to:
  - listen on port 8080
  - serve the agent card at /.well-known/agent-card.json
  - accept A2A JSON-RPC (message/send, message/stream, ...) at /

The SDK's A2AStarletteApplication does all three. Our only code is the
AgentExecutor: it takes the user's message, runs the loop, and publishes the
answer as a task artifact.
"""

from __future__ import annotations

import os

import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, Part, TaskState, TextPart
from a2a.utils import new_task

from agent import IncidentReporter


class IncidentReporterExecutor(AgentExecutor):
    def __init__(self, reporter: IncidentReporter) -> None:
        self.reporter = reporter

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task or new_task(context.message)
        if context.current_task is None:
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.start_work()

        async def on_step(kind: str, detail: str) -> None:
            # Progress for streaming clients (message/stream): one working-state update per tool step.
            await updater.update_status(
                TaskState.working,
                message=updater.new_agent_message([Part(root=TextPart(text=f"{kind}: {detail}"))]),
            )

        try:
            answer = await self.reporter.run(context.get_user_input(), on_step=on_step)
        except Exception as e:  # report failures as a failed task, not a crash
            await updater.failed(updater.new_agent_message([Part(root=TextPart(text=f"error: {type(e).__name__}: {e}"))]))
            return
        await updater.add_artifact([Part(root=TextPart(text=answer))], name="incident-report")
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("cancel is not supported")


def build_app(reporter: IncidentReporter):
    public_url = os.environ.get("PUBLIC_URL", "http://localhost:8080/")
    card = AgentCard(
        name="incident_reporter",
        description="Bring-your-own agent: a while-loop ReAct agent that writes an incident report for a namespace from live cluster state and in-cluster network probes.",
        url=public_url,
        version="0.1.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[AgentSkill(
            id="incident-report",
            name="Incident report",
            description="Summary, evidence, root cause and fix for every unhealthy workload in a namespace.",
            tags=["kubernetes", "incident", "report", "read-only"],
            examples=["Write an incident report for namespace demo-broken."],
        )],
    )
    handler = DefaultRequestHandler(agent_executor=IncidentReporterExecutor(reporter), task_store=InMemoryTaskStore())
    return A2AStarletteApplication(agent_card=card, http_handler=handler)


async def main() -> None:
    reporter = IncidentReporter()
    await reporter.connect()
    app = build_app(reporter).build()
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), log_level="info")
    try:
        await uvicorn.Server(config).serve()
    finally:
        await reporter.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
