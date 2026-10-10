# netprobe-mcp: network checks for SRE agents

This MCP server runs HTTP, DNS, TCP and TLS checks from its own network location. Deployed inside the EKS cluster, it lets an agent test Service connectivity alongside Kubernetes resource state. The incident reporter uses these probes to gather evidence for its report.

The project was scaffolded with kmcp v0.3.0 and uses FastMCP 3.0.0. The four probe functions are the custom implementation; the scaffold supplies discovery, configuration, the entry point and container build. See the [article](../../docs/article.md#custom-mcp-tools-checking-the-network-from-inside-the-cluster) for its role in the workflow and the [setup guide](../../docs/setup-guide.md#8-build-and-deploy-the-custom-mcp-server) for ECR/Kubernetes deployment.

## Tools

| Tool | Arguments | Result |
|---|---|---|
| `http_check` | `url`, `timeout_seconds=5.0` | Success flag, HTTP status, latency, redirect target, server header, body length; error on failure |
| `dns_lookup` | `hostname` | Resolution flag, addresses and canonical name; error on failure |
| `tcp_connect` | `host`, `port`, `timeout_seconds=5.0` | Connection flag, connection time and peer; error on failure |
| `tls_cert_expiry` | `host`, `port=443`, `timeout_seconds=5.0` | Validity flag, days remaining, expiration time, issuer, subject, DNS names and TLS version; error on failure |

FastMCP derives the tool schemas from type hints and docstrings. The functions return structured evidence rather than performing repairs. Their read-only annotations describe their intended use; they do not enforce network access restrictions.

`http_check` accepts HTTP/HTTPS URLs and follows redirects. `tls_cert_expiry` uses certifi's CA bundle for certificate and hostname verification. An invalid or expired certificate can fail the handshake and return an error instead of expiration metadata. This is a connectivity/evidence tool, not a certificate-inspection tool that bypasses verification.

## Run locally

Run these commands from `byo/netprobe-mcp/`. Python 3.12 and uv are required.

```bash
uv sync
uv run pytest -q
```

The original run passed ten tests with two warnings in 0.94 s. Separate MCP client calls listed and exercised all four tools; the recorded output is in [results/raw/netprobe-local-mcp-test.txt](../../results/raw/netprobe-local-mcp-test.txt).

For streamable HTTP, leave this process running:

```bash
uv run python src/main.py --transport http --host 127.0.0.1 --port 3000
```

The MCP endpoint is `http://127.0.0.1:3000/mcp`. It is streamable HTTP, not a WebSocket endpoint. For a client that launches the server and communicates over stdin/stdout:

```bash
uv run python src/main.py --transport stdio
```

Stdio is the default transport. Other supported entry points are:

```bash
uv run dev       # HTTP, default host localhost and port 3000
uv run dev-http  # same as dev
uv run start    # stdio
```

The CLI accepts `--host` and `--port`; `HOST` and `PORT` set their defaults. `MCP_TRANSPORT_MODE` overrides the selected transport when set:

```bash
MCP_TRANSPORT_MODE=http uv run python src/main.py --host 127.0.0.1 --port 3000
```

## Build and run a container

From this project directory, build with an explicit image tag:

```bash
kmcp build --tag netprobe-mcp:0.1.0
```

For an HTTP server reachable through a local Docker port mapping:

```bash
docker run --rm -p 3000:3000 netprobe-mcp:0.1.0 \
  python src/main.py --transport http --host 0.0.0.0 --port 3000
```

For stdio:

```bash
docker run --rm -i netprobe-mcp:0.1.0
```

The EKS build uses `--platform linux/amd64`, an ECR tag and `--push`. The original image was 98 MB. Deployment uses the committed [MCPServer manifest](../../infra/kmcp/netprobe-mcpserver.yaml), with the account ID substituted before applying. This native HTTP server does not require the agentgateway stdio adapter. Full commands are in the setup guide.

## Project structure

```text
src/
├── tools/
│   ├── dns_lookup.py
│   ├── http_check.py
│   ├── tcp_connect.py
│   ├── tls_cert_expiry.py
│   └── __init__.py
├── core/
│   ├── server.py       dynamic module loading and FastMCP instance
│   ├── utils.py        YAML configuration and environment helpers
│   └── __init__.py
└── main.py             CLI and transport selection
kmcp.yaml               project configuration
tests/
├── test_discovery.py   loading and registration
└── test_tools.py       probe behavior with mocks
Dockerfile              two-stage uv build
pyproject.toml          runtime and development dependencies
```

The scaffold's echo example was removed. At startup, the loader imports each tool module under `src/tools/`; `@mcp.tool()` registers its function. Import/registration failures stop server startup rather than silently exposing an incomplete catalogue.

## Add a tool

The kmcp CLI can generate a new module:

```bash
kmcp add-tool my_tool
```

Implement the generated file using the existing probes as examples. Import `mcp` from `core.server`, decorate the function, type its parameters and explain its output in the docstring. Add behavior tests and restart the server so the loader imports the new module. Discovery registration alone does not establish correct tool behavior.

For a tool that needs configuration, the scaffold provides `get_tool_config` and `get_env_var` in `core.utils`. A custom tool can explicitly read a block such as:

```yaml
tools:
  my_tool:
    api_key_env: MY_TOOL_API_KEY
    timeout: 5
```

The existing probes take their arguments directly; adding a YAML setting does not automatically change their behavior. Environment loading uses dotenv during server initialization. The committed kmcp configuration does not require tool credentials.

After adding dependencies to `pyproject.toml`, run `uv sync` and rebuild the image. The development dependencies also provide these checks; their results are separate from the recorded pytest run:

```bash
uv run black --check .
uv run ruff check .
uv run mypy .
```

## Deployment and verification

kmcp turns the `MCPServer` into a Deployment and Service on port 3000. kagent discovers its tools at `http://netprobe-mcp.kagent:3000/mcp`. Check both the pod rollout and discovered tool list: kmcp 0.3.0 does not add readiness/liveness probes, so Deployment readiness alone does not verify an MCP request.

The four in-cluster direct calls are retained under [results/raw/](../../results/raw/); the [runtime reference](../../docs/runtime-and-protocols.md#kmcp-deployment-paths) explains discovery and the HTTP/stdio deployment distinction.
