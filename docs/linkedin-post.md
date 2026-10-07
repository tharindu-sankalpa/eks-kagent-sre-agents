I built seven SRE agents on Amazon EKS with kagent and kmcp, six of them in YAML only, and pointed them at a namespace with five deliberately broken workloads.

kagent installs a tool server with 124 Kubernetes, Helm and Prometheus tools before you write a single agent. An Agent resource is a model, a system prompt and a list of tool names. kmcp runs MCP servers as Kubernetes resources, including one I wrote with FastMCP (four network probes, about 100 lines) and built with its CLI.

The headline: a read-only troubleshooter with nine tools diagnosed all five faults (bad image tag, crash loop, OOMKilled, a Service selector that matched nothing, an unschedulable CPU request) in 5 to 52 seconds each, quoting the event or log line. Ten of twelve specialist answers were correct; one was incomplete and one listed a Pending pod as healthy. A completed task is not a correct answer.

The part I wanted to test was governance. The operator agent lists its mutating tools under requireApproval. Asked to scale a deployment, it paused with the exact call and arguments; I approved, and replicas went 2 to 3. I rejected the next one and nothing changed. Then an orchestrator agent, whose only tools are the other six agents, fixed a broken Service by asking the troubleshooter why, asking me which backend to use, and calling the operator, whose approval prompt surfaced one level up. Two decisions, one patch, three endpoints.

Then I hit the limits. The controller cuts every A2A call at 3 minutes, streaming included, and the task stays working forever. Requests it abandons keep running in the pod; a retry stacked three runs and OOM-killed the orchestrator. Most of the day's 6 USD of model spend was runs nobody was waiting for. The longest orchestrator question never completed.

Everything is reproducible: every command in order, the manifests, the raw A2A responses, a Postman collection for the kagent API and the tool servers, and the errors I hit.

Repo: <REPO_URL>
Article: <ARTICLE_URL>

#kagent #kmcp #Kubernetes #EKS #MCP #A2A #SRE #PlatformEngineering #AIAgents
