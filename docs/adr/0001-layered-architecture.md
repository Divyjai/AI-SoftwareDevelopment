# ADR 1: Layered Architecture and Independence from Orchestration Framework

## Context
The platform aims to build an autonomous software engineering pipeline. To prevent deep coupling with specific orchestration frameworks (like Google ADK), we must isolate the business logic.

## Decision
1. **Layered Architecture:** The platform is separated into Domain, Application, Interfaces, Infrastructure, Shared, and Presentation layers.
2. **Framework as Infrastructure:** Google ADK is relegated to the `infrastructure` layer. It acts as an adapter, implementing the core `interfaces`.
3. **Event & Artifact Driven:** Agents do not directly invoke each other. They produce artifacts and emit events which managers react to.
4. **Dependency Injection:** Dependencies are injected (e.g., in Managers) rather than hardcoded instantiations.

## Status
Accepted

## Consequences
- The platform logic is completely independent of the orchestration runner.
- Changing frameworks (e.g., migrating from ADK) only requires a new Infrastructure Adapter.
- Testing is much easier because we can mock the interfaces.
