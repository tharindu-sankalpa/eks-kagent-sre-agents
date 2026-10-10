I built and tested multi-agent orchestration for SRE workflows on Amazon EKS using kagent and kmcp. An orchestrator uses specialist agents as tools to diagnose Kubernetes faults and coordinate repairs, with human approval preserved across delegated calls.

Six of the seven agents are YAML configurations: a model, system instructions and allowed tools. kagent deploys them, runs them through its Google Agent Development Kit (ADK)-based Python runtime and supplies built-in tools for Kubernetes, Helm and Prometheus. kmcp deploys the additional MCP servers.

I added an in-cluster network-probe server and a custom incident reporter with its own Python tool-calling loop, exposed over the Agent-to-Agent (A2A) protocol. The orchestrator can call that custom agent through the same interface as its declarative specialists.

The test namespace had five deliberate faults. The read-only troubleshooter diagnosed all five individually in 5–52 seconds each. Of twelve specialist answers, ten were correct, one incomplete and one partly wrong.

The repair test exercised the entire delegation path: the troubleshooter identified a Service selector mismatch; the orchestrator asked which backend to use; the operator paused on the exact patch for approval. After approval, kubectl confirmed three endpoints. A separate rejection test left the replica count unchanged.

Testing also exposed the limits. The controller cut requests at three minutes, streaming included. Abandoned work overlapped with retries and the orchestrator was OOMKilled at its default memory limit. Its longest diagnostic task never completed.

The repository includes the manifests, custom code, setup procedure, original build record, API collection and raw responses used to check the results.

Repo: <REPO_URL>
Article: <ARTICLE_URL>

#kagent #kmcp #Kubernetes #EKS #MCP #A2A #SRE #MultiAgent #PlatformEngineering
