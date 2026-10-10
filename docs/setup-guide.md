# Setup guide: multi-agent SRE workflows on Amazon EKS

This guide deploys seven agents: an orchestrator that uses six specialists as tools, including one custom incident reporter. kagent runs the declarative agents and supplies operational tools; kmcp deploys additional Model Context Protocol (MCP) servers. The tests cover diagnosis, delegated repair and human approval before changes.

The steps follow the dependencies of the committed manifests. They have been reconstructed from the final configuration and the 2026-10-07 build; this reordered procedure has not been rerun on a new cluster. The [build record](build-record.md) preserves every original command, output, screenshot and investigation. The [article](article.md) explains the workflow; the [runtime reference](runtime-and-protocols.md) explains the underlying interfaces.

The cluster is created from an `eksctl` file. Helm installs the platform and monitoring; `kubectl apply` creates model, agent and tool resources. No agent is created manually in the UI. The custom server and agent images are built locally and pushed to ECR.

AWS bills the control plane, nodes, NAT gateway, storage and image repositories while they exist. Model requests incur OpenRouter charges. The recorded model total was about 6 USD; no hourly AWS total or per-scenario model cost was measured. [Teardown](#teardown) removes the cluster and optionally the images.

![System overview: SRE, kagent controller, sre-orchestrator, six specialist agents, five MCP tool servers, demo-broken and monitoring targets, platform strip](diagrams/01-system-overview.jpg)

*The system. An SRE reaches the orchestrator through the kagent controller over A2A; the orchestrator delegates to six specialists, which use selected tools on five MCP servers; the tools act on the demo namespace and the monitoring stack. kmcp, PostgreSQL and kagent are the platform underneath.*

## Contents

- [Prerequisites and command conventions](#prerequisites-and-command-conventions)
- [0. Variables and credentials](#0-variables-and-credentials)
- [1. Create the EKS cluster](#1-create-the-eks-cluster)
- [2. Set the default StorageClass](#2-set-the-default-storageclass)
- [3. Create the model Secret](#3-create-the-model-secret)
- [4. Install Prometheus and Grafana](#4-install-prometheus-and-grafana)
- [5. Create the Grafana service-account token](#5-create-the-grafana-service-account-token)
- [6. Install kagent and bundled kmcp](#6-install-kagent-and-bundled-kmcp)
- [7. Deploy fetch and the broken workloads](#7-deploy-fetch-and-the-broken-workloads)
- [8. Build and deploy the custom MCP server](#8-build-and-deploy-the-custom-mcp-server)
- [9. Build the custom agent image](#9-build-the-custom-agent-image)
- [10. Apply model, prompt and agent resources](#10-apply-model-prompt-and-agent-resources)
- [11. Open local access and check tool discovery](#11-open-local-access-and-check-tool-discovery)
- [12. Test diagnosis, approval and orchestration](#12-test-diagnosis-approval-and-orchestration)
- [Troubleshooting](#troubleshooting)
- [Teardown](#teardown)

## Prerequisites and command conventions

You should be comfortable with Kubernetes resources, Helm and AWS credentials. MCP is the tool interface; A2A is the agent invocation interface. You do not need to implement either protocol to deploy the YAML agents.

| Requirement | Used for |
|---|---|
| AWS account and authenticated CLI | EKS, CloudFormation, EC2, IAM/Pod Identity and ECR operations |
| Eight spare standard on-demand vCPUs in `ap-south-1` | Two `t3.xlarge` workers |
| `aws`, `eksctl`, `kubectl`, `helm` | Provisioning and deployment |
| Docker with Buildx | Building Linux amd64 images |
| `kmcp` v0.3.0 | Building the custom MCP image |
| `uv` and Python 3.12 | Local MCP tests and optional agent development |
| `curl`, `jq`, Git; Python 3 for collection generation | API tests and repository tooling |
| OpenRouter API key and funded account | Model calls for the configured model IDs |
| A Grafana admin password of your choosing | Creating a Viewer service-account token |

Install these tools before continuing. kmcp v0.3.0 binaries are available from its [release](https://github.com/kagent-dev/kmcp/releases/tag/v0.3.0); the original machine used `kmcp-darwin-arm64`. The [version table](../README.md#versions) records the tested toolchain, including a development build of eksctl. This guide does not claim all newer tool versions are equivalent.

Command blocks contain commands only; outputs and success criteria are separate. Run commands from the repository root unless a subshell explicitly changes directory. Subshells such as `(cd ... && ...)` return to the root automatically. New terminals must load the variables from step 0. Names, IDs, IPs and ages in the build record will differ for you.

The manifests use `ap-south-1` and cluster name `kagent-sre-lab`. To use another region or name, update the cluster manifest and ECR image references as well as the shell variables. Source checkouts are optional for reproducing the source review; they are not needed to deploy the charts.

## 0. Variables and credentials

Start in the cloned repository. Copy the environment example once, then edit `.env` and replace both placeholders. Quote values containing spaces or shell metacharacters. Do not source the untouched example.

```bash
export REPO_ROOT="$PWD"
test -f "$REPO_ROOT/infra/eks/cluster.yaml"
test -f .env || cp .env.example .env
```

After editing `.env`, initialize the deployment shell:

```bash
export AWS_REGION=ap-south-1
export CLUSTER=kagent-sre-lab
mkdir -p "$REPO_ROOT/.kube"
export KUBECONFIG="$REPO_ROOT/.kube/config"
set -a
. "$REPO_ROOT/.env"
set +a
: "${OPENROUTER_API_KEY:?Set OPENROUTER_API_KEY in .env}"
: "${GRAFANA_ADMIN_PASSWORD:?Set GRAFANA_ADMIN_PASSWORD in .env}"
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
```

`.env` and `.kube/` are gitignored. The dedicated kubeconfig keeps these commands pointed at the lab cluster. Use the same absolute `KUBECONFIG` in every terminal used below.

Check authentication, versions and quota before provisioning:

```bash
aws sts get-caller-identity
aws --version
eksctl version
kubectl version --client
helm version --short
jq --version
docker buildx version
kmcp version
uv --version
aws service-quotas get-service-quota --service-code ec2 --quota-code L-1216C47A \
  --region "$AWS_REGION" --query 'Quota.Value' --output text
```

`L-1216C47A` is the standard on-demand EC2 vCPU quota. This build needs eight available vCPUs, not just a quota of eight if other instances already use it. The recorded quota was 32. Use fresh AWS credentials before cluster creation; an expired session interrupted the original eksctl command even though the submitted stacks continued in AWS.

## 1. Create the EKS cluster

[infra/eks/cluster.yaml](../infra/eks/cluster.yaml) provisions EKS 1.34, two private `t3.xlarge` workers in two availability zones and one NAT gateway. The nodes provide eight vCPUs and 32 GiB total, with a 50 GiB gp3 root volume per node. One NAT gateway is the lab's cost choice; it does not provide a gateway per zone.

The add-ons include the EBS CSI driver and EKS Pod Identity agent. `autoApplyPodIdentityAssociations: true` creates and associates the IAM role needed by the storage driver. The other add-ons are VPC CNI, CoreDNS, kube-proxy and metrics-server.

```bash
eksctl create cluster -f infra/eks/cluster.yaml --kubeconfig "$KUBECONFIG"
kubectl get nodes
aws eks list-addons --region "$AWS_REGION" --cluster-name "$CLUSTER" --output text
```

Continue when both nodes are Ready and all six add-ons are installed. The original cluster took approximately 15–20 minutes to finish. If the command returns `ExpiredToken`, use the [recorded recovery](build-record.md#3-eks-cluster): refresh credentials, inspect completed stacks, write the kubeconfig and add only missing add-ons. Do not assume the reported CLI failure means nothing was created.

## 2. Set the default StorageClass

PostgreSQL and Prometheus request storage without specifying a class. The cluster needs a default class that can provision their volumes.

```bash
kubectl apply -f infra/eks/storageclass-gp3.yaml
kubectl get sc
```

Success criterion: `gp3 (default)` uses `ebs.csi.aws.com`, with `Delete` reclaim policy and `WaitForFirstConsumer` binding. The original `gp2` class was present but was not default.

## 3. Create the model Secret

Every declarative model configuration references the same Secret. The custom agent receives its key from that Secret too. Create it before applying the agents.

```bash
kubectl create namespace kagent --dry-run=client -o yaml | kubectl apply -f -
kubectl -n kagent create secret generic kagent-openrouter \
  --from-literal=OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl -n kagent get secret kagent-openrouter
```

The final command confirms existence without printing the key. The model provider is `OpenAI` because OpenRouter exposes an OpenAI-compatible API; it does not mean every configured model is an OpenAI model.

## 4. Install Prometheus and Grafana

The [monitoring values](../infra/monitoring/values.yaml) set two-day Prometheus retention on a 10 GiB volume, disable Alertmanager and disable scrape targets for inaccessible EKS-managed control-plane components. Grafana persistence is off; its dashboards come from the chart.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update prometheus-community
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  --version 83.6.0 --namespace monitoring --create-namespace \
  -f infra/monitoring/values.yaml \
  --set-string grafana.adminPassword="$GRAFANA_ADMIN_PASSWORD" --wait --timeout 10m
kubectl -n monitoring get pods,pvc
```

Continue when the monitoring pods are Running/Ready and the Prometheus PVC is Bound. Chart 83.6.0 was used in the original build; chart 92.0.0 was available at that time but was not evaluated.

In-cluster endpoints are `http://prometheus-kube-prometheus-prometheus.monitoring:9090` and `http://prometheus-grafana.monitoring` on port 80.

## 5. Create the Grafana service-account token

The Grafana MCP server needs a Viewer service-account token. In a second terminal with the same `KUBECONFIG`, start this port-forward and leave it running:

```bash
kubectl -n monitoring port-forward svc/prometheus-grafana 3001:80
```

Once forwarding is ready, return to the deployment terminal. These commands capture the returned account ID rather than assuming it is `2`, as it was in the original run.

```bash
GRAFANA_SERVICE_ACCOUNT_ID=$(curl -fsS -u "admin:$GRAFANA_ADMIN_PASSWORD" \
  -H 'Content-Type: application/json' -X POST http://127.0.0.1:3001/api/serviceaccounts \
  -d '{"name":"kagent-grafana-mcp","role":"Viewer"}' | jq -er '.id')
export GRAFANA_MCP_TOKEN=$(curl -fsS -u "admin:$GRAFANA_ADMIN_PASSWORD" \
  -H 'Content-Type: application/json' \
  -X POST "http://127.0.0.1:3001/api/serviceaccounts/$GRAFANA_SERVICE_ACCOUNT_ID/tokens" \
  -d '{"name":"kagent-grafana-mcp"}' | jq -er '.key')
: "${GRAFANA_MCP_TOKEN:?Grafana token creation failed}"
```

Keep the token in the deployment shell. If you need to resume in another shell, store it as a quoted `GRAFANA_MCP_TOKEN` entry in your gitignored `.env` and reload that file. A service account with this name must not already exist for the create request; reuse its returned ID and issue a new token if resuming an existing deployment.

## 6. Install kagent and bundled kmcp

The committed [kagent values](../infra/kagent/values.yaml) enable Grafana MCP, so Grafana and its token now exist before installing kagent. They also enable bundled PostgreSQL with a 2 GiB volume, configure OpenRouter and disable the ten bundled agents.

```bash
helm upgrade --install kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds \
  --version 0.9.10 --namespace kagent --wait
helm upgrade --install kagent oci://ghcr.io/kagent-dev/kagent/helm/kagent \
  --version 0.9.10 --namespace kagent -f infra/kagent/values.yaml \
  --set-string grafana-mcp.grafana.serviceAccountToken="$GRAFANA_MCP_TOKEN" \
  --wait --timeout 10m
kubectl -n kagent get pods,pvc
kubectl -n kagent get modelconfig
kubectl -n kagent get remotemcpserver
```

The chart includes kmcp 0.3.0, kagent-tools 0.2.1, querydoc, Grafana MCP, the UI and controller. `default-model-config` should select `deepseek/deepseek-v4.1-flash`; PostgreSQL's PVC should be Bound. The Python agent runtime builds on Google ADK; the [reference](runtime-and-protocols.md#who-runs-what) identifies the pinned source.

The Grafana MCP values include `--allowed-hosts` for `kagent-grafana-mcp.kagent:8000` and `kagent-grafana-mcp.kagent`. Without this, the observed image rejected the controller's Service-name Host header. The image tag is `latest`, so its future behavior is not pinned by this guide.

If a server is Running but its `RemoteMCPServer` remains unaccepted after a startup discovery failure, trigger a new reconciliation:

```bash
kubectl -n kagent annotate remotemcpserver kagent-tool-server \
  docs/reconcile-nudge="$(date -u +%FT%TZ)" --overwrite
kubectl -n kagent annotate remotemcpserver kagent-grafana-mcp \
  docs/reconcile-nudge="$(date -u +%FT%TZ)" --overwrite
kubectl -n kagent get remotemcpserver
```

Wait for both to report Accepted. The original controller restarted twice because it started before PostgreSQL was listening; inspect logs and readiness rather than treating any startup restart as a persistent failure.

## 7. Deploy fetch and the broken workloads

`fetch` supplies URL/documentation retrieval. kmcp adapts its stdio package to HTTP through agentgateway. The demo namespace contains intentionally unhealthy workloads, so waiting for every demo pod to become Ready would be incorrect.

```bash
kubectl apply -f infra/kmcp/fetch-mcpserver.yaml -f infra/demo/broken-workloads.yaml
kubectl -n kagent rollout status deploy/fetch --timeout=300s
kubectl -n kagent get mcpserver fetch
kubectl -n demo-broken get pods
```

| Workload | Configured fault | Expected evidence |
|---|---|---|
| `api` | Nonexistent `nginx:1.99.99-does-not-exist` tag | ErrImagePull / ImagePullBackOff and the image error |
| `worker` | Prints a missing-config message and exits 1 | CrashLoopBackOff, exit status and log line |
| `cache` | Allocates 200 MiB under a 64 MiB limit | OOMKilled and increasing restart count |
| `checkout` Service / `web` pods | Selector `app: checkout`, pod labels `app: web` | Empty Service endpoints |
| `batch` | Requests 16 CPUs on 4-CPU nodes | Pending and Insufficient cpu |

These faults are the known answers for the diagnosis tests. Kubernetes status may vary between an immediate error and the later backoff state.

## 8. Build and deploy the custom MCP server

The four probe implementations are already in [byo/netprobe-mcp/](../byo/netprobe-mcp/). Use that directory; do not scaffold a second project for deployment. The original `kmcp init` command and generated-file details are preserved in the [build record](build-record.md#10-bring-your-own-mcp-server-scaffold-build-push-deploy).

First check the local implementation:

```bash
(cd "$REPO_ROOT/byo/netprobe-mcp" && uv sync && uv run pytest -q)
```

The original run passed ten tests with two warnings in 0.94 s. The [component README](../byo/netprobe-mcp/README.md) also describes running HTTP/stdio locally. Recorded direct MCP checks are in [results/raw/netprobe-local-mcp-test.txt](../results/raw/netprobe-local-mcp-test.txt).

For a new lab, create the ECR repository and authenticate Docker. If you retained it from a previous lab, reuse it and skip creation.

```bash
aws ecr create-repository --region "$AWS_REGION" --repository-name netprobe-mcp \
  --image-scanning-configuration scanOnPush=true
aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$ECR_REGISTRY"
(cd "$REPO_ROOT/byo/netprobe-mcp" && \
  kmcp build --platform linux/amd64 --tag "$ECR_REGISTRY/netprobe-mcp:0.1.0" --push)
sed "s/<ACCOUNT_ID>/$AWS_ACCOUNT_ID/" infra/kmcp/netprobe-mcpserver.yaml | kubectl apply -f -
kubectl -n kagent rollout status deploy/netprobe-mcp --timeout=300s
kubectl -n kagent get mcpserver netprobe-mcp
```

The platform flag produces x86_64 images for the workers, including when building on Apple Silicon. The original pushed image was 98 MB. The HTTP transport runs FastMCP directly at `http://netprobe-mcp.kagent:3000/mcp`; no agentgateway adapter is added. Its four tools are `dns_lookup`, `tcp_connect`, `http_check` and `tls_cert_expiry`.

![Two columns: the stdio fetch package behind an agentgateway adapter, and the custom HTTP netprobe-mcp image, both reconciled by kmcp and discovered by kagent](diagrams/04-kmcp-two-ways.jpg)

*What steps 7 and 8 created. `fetch` is a public stdio package adapted by agentgateway on kmcp's default image; `netprobe-mcp` is the custom HTTP image built in step 8. Both become a Deployment and a Service that kagent discovers.*

## 9. Build the custom agent image

Build the incident reporter before applying its Agent resource. The [Python implementation](../byo/incident-reporter-agent/src/) owns the tool-calling loop and uses the A2A SDK for its server; it does not depend on Google ADK.

```bash
aws ecr create-repository --region "$AWS_REGION" --repository-name incident-reporter-agent \
  --image-scanning-configuration scanOnPush=true
docker buildx build --platform linux/amd64 \
  -t "$ECR_REGISTRY/incident-reporter-agent:0.1.0" --push byo/incident-reporter-agent
```

Reuse an existing repository if resuming. The original image was 57 MB. Its deployment environment references the model Secret and the two MCP endpoints. The [local development commands](build-record.md#13-bring-your-own-agent-a-loop-an-a2a-server-a-container) and [container contract](runtime-and-protocols.md#the-custom-agent-boundary) are separate from the cluster deployment path.

## 10. Apply model, prompt and agent resources

The chart already created one model configuration. Apply the four additional configs, the orchestrator's prompt ConfigMap, then all seven agents. Substitute the AWS account ID in the BYO image reference.

```bash
kubectl apply -f infra/kagent/models/
kubectl apply -f infra/kagent/prompts/
for manifest in infra/kagent/agents/*.yaml; do
  sed "s/<ACCOUNT_ID>/$AWS_ACCOUNT_ID/" "$manifest" | kubectl apply -f -
done
kubectl -n kagent wait --for=condition=Ready agent --all --timeout=300s
kubectl -n kagent get agent -o wide
kubectl -n kagent get pods
```

Success criteria: all seven agents are Accepted and Ready, and their current pod rollouts are healthy. Six declarative agents use Python; `incident-reporter` is BYO. An Agent condition alone can be misleading during a failed rollout: the original Go-runtime attempt reported Ready while an old Python pod was still serving.

| Agent | Responsibility | Execution control |
|---|---|---|
| `cluster-troubleshooter` | Kubernetes diagnosis | Nine read-only tools |
| `observability-analyst` | Prometheus and Grafana analysis | Read-only tool selection |
| `runbook-assistant` | Diagnosis with documentation | Read-only tools and fetch |
| `release-manager` | Helm inspection and release operations | Upgrades, uninstalls and repository additions require approval |
| `incident-reporter` | Full namespace report and network evidence | Six Kubernetes tools and four probes; no mutating tools |
| `sre-operator` | Scaling, rollout and resource changes | All six exposed mutating tools require approval |
| `sre-orchestrator` | Select specialists and combine results | Six agent references; tested repair delegates to the approval-gated operator |

The orchestrator's prompt is in a ConfigMap. The manifest sets a 2 GiB memory limit after the recorded concurrent requests exceeded the original 1 GiB limit. The reference covers [tool selection and approval](runtime-and-protocols.md#agent-configuration-and-approval), including the difference between prompt restrictions and enforced execution controls.

## 11. Open local access and check tool discovery

Keep each needed port-forward running in its own terminal, with the same lab kubeconfig. Wait for its forwarding message before using the local endpoint.

| Purpose | Command | Local endpoint |
|---|---|---|
| Controller / A2A / REST | `kubectl -n kagent port-forward svc/kagent-controller 8083:8083` | `http://127.0.0.1:8083` |
| UI | `kubectl -n kagent port-forward svc/kagent-ui 8080:8080` | `http://127.0.0.1:8080` |
| Direct built-in MCP calls | `kubectl -n kagent port-forward svc/kagent-tools 8084:8084` | `http://127.0.0.1:8084/mcp` |
| Direct netprobe MCP calls | `kubectl -n kagent port-forward svc/netprobe-mcp 3002:3000` | `http://127.0.0.1:3002/mcp` |
| Grafana | Port-forward from step 5 | `http://127.0.0.1:3001` |

With the controller port-forward ready, check discovery:

```bash
curl -fsS http://127.0.0.1:8083/api/toolservers | \
  jq -r '.data[]|"\(.ref) \(.groupKind) tools=\(.discoveredTools|length)"'
```

The recorded result was five sources with 195 tools: built-in Kubernetes/Helm/etc. 124, Grafana 65, querydoc one, fetch one, netprobe four. The querydoc source is a labelled `Service`, not a `RemoteMCPServer`. The [source inventory](runtime-and-protocols.md#tool-sources-and-discovery) lists their in-cluster URLs and discovery rules.

For manual API inspection, generate/import [the Postman collection](../postman/kagent.postman_collection.json) and set its environment ports to match the table:

```bash
python3 postman/build_collection.py
```

The collection has ten folders and 62 requests, covering APIs, direct MCP calls and A2A invocation/approval. The original build exercised selected calls with curl; it did not execute the collection in Postman or validate every CRUD request. [Validation scope](runtime-and-protocols.md#api-collection-and-validation-scope).

## 12. Test diagnosis, approval and orchestration

Use new run IDs so a new demonstration keeps the committed evidence intact. Scripts save responses under `results/answers/<agent>/`.

### Start with a read-only diagnosis

```bash
./scripts/ask-agent.sh cluster-troubleshooter demo-s01 \
  "Why is the deployment api in namespace demo-broken not running?"
```

Check that the answer cites the nonexistent image tag and the actual pull event. Repeat with the questions in [scripts/scenarios.txt](../scripts/scenarios.txt) if you want the full evaluation. The original [results](article.md#results) contain the timings, tool counts and verdicts; completion alone is not correctness.

`scripts/run-scenarios.sh` sends all fourteen initial questions through non-streaming controller requests, including the known long-running scenario 13, and writes the original `s01`–`s14` filenames. Inspect that script before using it for a new comparison. Streaming does not bypass the controller timeout.

### Check direct approval and rejection

These commands request real changes to the lab's `web` deployment. The script supplies the approve/reject decision automatically to demonstrate the protocol.

```bash
kubectl -n demo-broken get deploy web -o jsonpath='{.spec.replicas}{"\n"}'
./scripts/approval-demo.sh approve \
  "Scale the deployment web in namespace demo-broken to 3 replicas." demo-approval
kubectl -n demo-broken get deploy web -o jsonpath='{.spec.replicas}{"\n"}'
./scripts/approval-demo.sh reject \
  "Scale the deployment web in namespace demo-broken down to 2 replicas." demo-reject
kubectl -n demo-broken get deploy web -o jsonpath='{.spec.replicas}{"\n"}'
```

For the original starting state, approval produced `2 → 3`; rejection left `3 → 3`. Inspect the saved pending call and task state as well as the replicas. For an interactive decision, use the UI or the collection's separate invocation and continuation requests.

### Exercise delegated diagnosis and repair

First ask the orchestrator to combine metrics and workload evidence:

```bash
./scripts/ask-agent-stream.sh sre-orchestrator demo-s14 \
  "Is the cluster under CPU or memory pressure right now, and is anything in demo-broken restarting because of it?"
```

The original run completed in 78 s and distinguished a container memory limit from node memory pressure. CPU/memory shares will differ on another cluster or day.

For the repair, use the UI or start a streamed task:

```bash
./scripts/ask-agent-stream.sh sre-orchestrator demo-s15 \
  "Fix the Service checkout in namespace demo-broken so that it has endpoints. Tell me what you intend to change before you do it."
```

Inspect the recorded events and extract the latest paused task/context:

```bash
jq -rs '[.[].result | select(.kind=="status-update" and .status.state=="input-required")] \
  | last | {taskId,contextId,message:.status.message}' \
  results/answers/sre-orchestrator/demo-s15.events.jsonl
```

Use those identifiers to answer the backend question. Replace the ID placeholders below and use the actual choice text returned by the question:

```bash
./scripts/orchestrator-continue.sh demo-s15 '<contextId>' '<taskId>' answer \
  'Yes, patch the selector to app=web'
```

Inspect the next `input-required` event. It should name the operator's proposed `k8s_patch_resource` call. Review the arguments, then send the execution decision using the latest task/context identifiers:

```bash
./scripts/orchestrator-continue.sh demo-s15 '<contextId>' '<taskId>' approve
kubectl -n demo-broken get svc checkout -o jsonpath='{.spec.selector}{"\n"}'
kubectl -n demo-broken get endpoints checkout
```

The original outcome was selector `{app: web}` and three endpoints after the earlier scale to three replicas. The first pause resolves intent; the second gates execution. Repairing the Service changes the original fault, so reapply the demo manifest before another baseline diagnosis run. It also resets `web` to the manifest's two replicas.

The continuation helper implements answering a question and approving a call; for rejecting a delegated call, use the UI or the A2A continuation format in the [reference](runtime-and-protocols.md#a2a-discovery-invocation-and-continuation).

### Long-running requests

In kagent 0.9.10, both controller `message/send` and `message/stream` paths are cut at 180 s. Some abandoned work continued in the pod; immediate retries overlapped and contributed to an OOMKill. Run orchestrator tests one at a time and inspect the previous execution before retrying.

A direct port-forward to the agent bypasses the controller's timeout:

```bash
kubectl -n kagent port-forward svc/sre-orchestrator 8090:8080
```

Send an A2A JSON-RPC body directly to `http://127.0.0.1:8090/` with the collection or curl. The existing `ask-agent-stream.sh` constructs a controller path; changing `KAGENT` alone does not turn it into a direct-Service client. The direct scenario 13 attempt was stopped on cost and never completed; bypassing this timeout is not evidence that the full request succeeds.

## Troubleshooting

| Symptom | First check / action | Original investigation |
|---|---|---|
| eksctl returns `ExpiredToken` | Refresh credentials; inspect existing stacks before recreating anything | [Cluster recovery](build-record.md#3-eks-cluster) |
| PVC remains Pending | Default StorageClass, CSI driver and Pod Identity association | [Storage setup](build-record.md#4-default-storageclass) |
| Running tool pod but unaccepted source | Endpoint readiness, then trigger reconciliation | [Startup discovery](build-record.md#5-kagent-and-kmcp) |
| Grafana MCP returns Forbidden | Service-name Host header and allowed-hosts arguments | [Host validation](build-record.md#9-the-grafana-mcp-server-that-ships-with-kagent) |
| querydoc reference rejected | Use `kind: Service` | [Agent acceptance](build-record.md#11-the-agents) |
| Agent says Ready but new pod cannot pull | Inspect the current Deployment rollout and image digest | [Go runtime attempt](build-record.md#the-go-runtime-tried-not-available) |
| Local TLS probe cannot verify issuer | Probe code uses a certifi trust bundle | [Local probe test](build-record.md#103-run-and-test-locally) |
| Prometheus tool rejects comparisons | Use supported queries such as `topk`, or Grafana's query path | [Tool behavior](runtime-and-protocols.md#tool-sources-and-discovery) |
| Orchestrator stream ends / pod restarts | Controller timeout, concurrent requests and memory state | [Orchestrator failures](build-record.md#16-the-orchestrator-over-messagestream) |

## Teardown

Stop the task's port-forwards with Ctrl-C in their terminals. Remove storage users and claims while the EBS CSI driver still exists, wait for volumes to disappear, then delete the cluster. The original teardown took about 14 minutes; its [full record](build-record.md#teardown) includes command outputs and follow-up checks.

```bash
helm uninstall prometheus -n monitoring
helm uninstall kagent -n kagent
kubectl delete pvc --all -n monitoring
kubectl delete pvc --all -n kagent
kubectl get pv
```

Wait until no lab PersistentVolumes remain. Check for orphaned volumes before deleting the cluster:

```bash
aws ec2 describe-volumes --region "$AWS_REGION" \
  --filters "Name=tag:kubernetes.io/cluster/$CLUSTER,Values=owned" --query 'Volumes[].VolumeId'
eksctl delete cluster --name "$CLUSTER" --region "$AWS_REGION" --wait
```

The cluster deletion removes its control plane, node group, add-ons and associated stacks, VPC and NAT gateway. Verify resources associated with this lab rather than assuming the AWS account contains no other clusters or repositories:

```bash
aws eks list-clusters --region "$AWS_REGION"
aws cloudformation list-stacks --region "$AWS_REGION" \
  --query "StackSummaries[?contains(StackName,'$CLUSTER') && StackStatus!='DELETE_COMPLETE'].[StackName,StackStatus]" \
  --output text
aws ec2 describe-volumes --region "$AWS_REGION" \
  --filters "Name=tag:kubernetes.io/cluster/$CLUSTER,Values=owned" --query 'Volumes[].VolumeId'
aws ecr describe-repositories --region "$AWS_REGION" \
  --query 'repositories[].repositoryName'
```

Expected: the lab cluster is absent, no non-deleted stacks for its name remain and the tagged volume list is empty. The original run also checked for remaining NAT gateways and instances. ECR repositories are independent of cluster deletion. The two retained images totaled about 155 MB in the original run; retaining them incurs ECR storage charges and allows rebuilding the cluster without rebuilding images.

If you want to delete the lab's images too:

```bash
aws ecr delete-repository --region "$AWS_REGION" --repository-name netprobe-mcp --force
aws ecr delete-repository --region "$AWS_REGION" --repository-name incident-reporter-agent --force
```

If you separately added the lab context to your default kubeconfig, remove that context explicitly from that file. The guide's normal commands used the repo-local kubeconfig.

```bash
kubectl --kubeconfig "$HOME/.kube/config" config delete-context kagent-sre-lab
```
