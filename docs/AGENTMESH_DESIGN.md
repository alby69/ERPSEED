# AgentMesh Integration Strategy for ERPSEED

## 1. Overview
The goal is to transform ERPSEED into a distributed agentic ERP. Each module (Sales, Inventory, etc.) becomes an "Agent" that exposes its functionality through "Capabilities" (Commands and Queries).

## 2. Core Concepts
- **Agent**: A self-contained functional module (e.g., `SalesAgent`, `WarehouseAgent`).
- **Capability**: A tool that an agent can execute. Maps 1:1 to a CQRS Command or Query.
- **Manifest**: A JSON schema describing all capabilities of an agent.
- **Mesh**: The communication layer (AgentMesh) that orchestrates these agents.

## 3. Implementation Path

### A. Capability Discovery
Instead of manually registering tools in `backend/modules/ai/service.py`, we will use a decentralized registry.
1. Modules register their commands/queries in a `CapabilityRegistry`.
2. A command class will include metadata for its "tool" representation (description, JSON schema).

### B. Agentification of Modules
Each module's `__init__.py` or a dedicated `agent.py` will:
1. Define the Agent's identity.
2. Register its capabilities.

### C. The Capability Manifesto (`/capabilities`)
A global endpoint that returns:
```json
{
  "agents": [
    {
      "name": "SalesAgent",
      "capabilities": [
        {
          "name": "create_order",
          "command": "CreateSalesOrderCommand",
          "schema": { ... }
        }
      ]
    }
  ]
}
```

### D. Governance & Security
- **Identity**: Agents use JWT/API keys for inter-agent communication.
- **Scoping**: AgentMesh policies define which agent can call which capability.

## 4. Strengths & Weaknesses

| Strength | Benefit |
|----------|---------|
| **CQRS Mapping** | Easy to turn business logic into tools without rewrite. |
| **Decoupling** | Agents can run on different nodes (ERPSEED Node architecture). |
| **Self-Documenting** | The manifest automatically updates as we add code. |

| Weakness | Mitigation |
|----------|------------|
| **Latency** | Use local caching of capabilities; optimize inter-agent bus. |
| **Consistency** | Use Sagas/Distributed Transactions via Event Bus for multi-agent workflows. |
| **Complexity** | Start with a "Local Mesh" (monolith) before full distribution. |

## 5. Next Steps
- Implement `CapabilityRegistry`.
- Decorate core commands with metadata.
- Expose the manifest API.
