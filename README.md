# ocp5-first-look-lab

Red Hat OpenShift 5: First Look Lab

**Owners:** `openshiftkraft` (Jaafar Chraibi), `gmidha1` (Gaurav Midha)

---

## What this lab covers

A hands-on first look at the AI-driven operations features of OpenShift 5, on a fully
provisioned cluster. Each module runs against pre-deployed applications with
intentional issues.

### Module 1: Agentic Troubleshooting

OpenShift Lightspeed with the agentic operator, investigating and fixing application issues.

- **User-initiated investigation** in Lightspeed's troubleshooting mode: a timeout issue
  and a critical alert, with the AI correlating metrics, logs and resource state through MCP.
- **Inline Perses charts** generated during troubleshooting and exported to a dashboard.
- **Autonomous agentic runs**: the alerts adapter turns critical alerts into AgenticRuns,
  the agent proposes remediation plans, a human approves execution, and the agent verifies
  the fix (scenarios: `PaymentErrorRateHigh`, a bad `reporting-service` release;
  `PodDisruptionBudgetLimit`, a mistyped image tag).

### Module 2: MCP Server

The OpenShift MCP Server, used from an AI client (opencode, running in the cluster).

- **Core platform operations**: connecting a client, retrieving logs, creating resources,
  RBAC enforcement for a read-only user.
- **Observability and network diagnostics**: Prometheus queries, NetEdge OVN diagnostics.
- **Safety and access control**: warnings on destructive operations, read-only mode.
- **Service Mesh (Kiali/OSSM)**: mesh health, Istio config validation, traffic topology and
  latency, tracing, fault injection, creating and deleting an Istio Gateway, and a
  multi-tool investigation.

### Module 3: MCP Gateway

The MCP Gateway from Red Hat Connectivity Link, federating three mock MCP servers
(inventory, payments, accounts).

- **Federation**: one endpoint with prefix-based routing to 15 tools across 3 servers.
- **Security**: Keycloak OIDC authentication and team-based tool authorization from JWT claims.
- **Policy**: per-user rate limiting and policy hot-reload.
- **Operations**: OpenTelemetry tracing in Jaeger, graceful degradation when a server is down,
  and connecting an AI client (opencode) through the gateway.

### How the environment is deployed

Everything is installed by OpenShift GitOps (Argo CD) from `automation/gitops/`, through an
app-of-apps created by the `ocp5_ea` Ansible role (`automation/ansible/`). Main components:
OpenShift Lightspeed 1.1.5 and the agentic operator (with an agentic sandbox built in-cluster
for Red Hat MaaS), the OpenShift MCP Server, the MCP Gateway with its mock servers, the
`mcp-cli` opencode client, Service Mesh with Kiali, and the troubleshooting workloads used by
Module 1. Lab content is in `content/` (Antora/Showroom).
