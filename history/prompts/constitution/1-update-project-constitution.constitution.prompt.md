---
id: 1
title: Update Project Constitution
stage: constitution
date_iso: 2026-01-22
surface: agent
model: Qwen Code
feature: todo-ai-chatbot
branch: main
user: qwen
command: /sp.constitution
labels:
  - constitution
  - todo-ai-chatbot
  - phase-3
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - .specify/memory/constitution.md
tests_yaml: []
---

# Update Project Constitution

## User Input

```
Project: Todo AI Chatbot – Phase 3

Core principles:
- Stateless AI: No server-side session state; all context rebuilt per request
- Tool-first design: AI agents act only through MCP tools for task operations
- Separation of concerns: Agent logic, tools, and persistence are clearly isolated
- Reliability: Conversation and task state must survive restarts
- Security: All chat actions are user-scoped and authenticated

Key standards:
- Chat API must be stateless and idempotent
- Conversation and message history must be persisted in the database
- AI agents must select MCP tools based on user intent
- MCP tools must be stateless and store state only in the database
- Tool results must be translated into clear, user-friendly responses
- Errors must be handled gracefully without exposing internals

Constraints:
- AI framework: OpenAI Agents SDK
- MCP server: Official MCP SDK
- Backend: FastAPI + SQLModel
- Database: Neon Serverless PostgreSQL
- Frontend: OpenAI ChatKit
- No manual coding; spec-driven development only

Success criteria:
- Users manage todos via natural language
- Conversations resume after server restarts
- AI reliably calls correct MCP tools
- Task data remains consistent and user-isolated
- System operates correctly under stateless execution
```

## Response Summary

Updated the project constitution at `.specify/memory/constitution.md` to reflect the new principles for the Todo AI Chatbot – Phase 3 project. The updated constitution includes:

- Core principles: Stateless AI, Tool-first design, Separation of concerns, Reliability, and Security
- Additional constraints covering technology stack and development approach
- Development workflow guidelines
- Success criteria for the project
- Governance section outlining compliance requirements

Version was incremented from 1.1.0 to 1.2.0 to reflect the material changes in project direction.

## Outcome

The constitution has been successfully updated to align with the Todo AI Chatbot – Phase 3 project requirements. All principles from the user input have been incorporated, and the document follows the required format and structure.