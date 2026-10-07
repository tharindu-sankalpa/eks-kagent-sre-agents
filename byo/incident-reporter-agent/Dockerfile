# Image for the bring-your-own agent. Same two-stage shape as the kmcp
# Python template: uv resolves the environment in the builder, the runtime
# image only carries the virtualenv and the source.
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml .python-version uv.loc[k] ./
RUN if [ -f uv.lock ]; then uv sync --frozen --no-dev --no-cache; else uv sync --no-dev --no-cache; fi
COPY src/ ./src/

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH=/app/src PYTHONUNBUFFERED=1 PORT=8080
RUN groupadd -r agent && useradd -r -g agent agent
USER agent
EXPOSE 8080
# kagent's readiness probe is GET /.well-known/agent-card.json on port 8080.
CMD ["python", "src/server.py"]
