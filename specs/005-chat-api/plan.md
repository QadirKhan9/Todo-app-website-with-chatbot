# Implementation Plan: Chat API & Orchestration Layer

**Branch**: `005-chat-api` | **Date**: January 23, 2026 | **Spec**: [link to spec]
**Input**: Feature specification from `/specs/005-chat-api/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a thin, stateless HTTP layer that connects the frontend UI with the AI Agent and MCP tools. The API will accept chat messages from the frontend, load and persist conversation context, invoke the AI agent with correct state, and relay agent responses back to the frontend while maintaining statelessness per request.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, OpenAI SDK, SQLModel, Neon PostgreSQL driver
**Storage**: Neon Serverless PostgreSQL
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: Web application
**Performance Goals**: Handle up to 1000 concurrent conversations with average response time under 3 seconds
**Constraints**: API must remain stateless per request while preserving conversation context; JSON-only HTTP API; no business logic inside controllers
**Scale/Scope**: Support 1000+ concurrent conversations with 99.5% success rate

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Stateless AI**: The API must rebuild all context per request, aligning with the principle of no server-side session state.
- **Tool-first design**: The API will facilitate AI agents acting through MCP tools for task operations.
- **Separation of concerns**: Clear isolation between agent logic, tools, and persistence will be maintained.
- **Reliability**: Conversation and message history must survive restarts through database persistence.
- **Security**: All chat actions will be user-scoped and authenticated.

## Project Structure

### Documentation (this feature)

```text
specs/005-chat-api/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── conversation_service.py
│   │   └── ai_agent_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat_router.py
│   │   └── dependencies.py
│   └── main.py
└── tests/
    ├── unit/
    │   └── test_conversation_service.py
    ├── integration/
    │   └── test_chat_api.py
    └── contract/
        └── test_api_contracts.py
```

**Structure Decision**: Selected web application structure with backend containing models, services, and API layers. The API will handle chat requests, the services will manage business logic, and models will represent data structures.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|