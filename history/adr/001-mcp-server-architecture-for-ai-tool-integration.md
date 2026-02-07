# ADR-001: MCP Server Architecture for AI Tool Integration

**Status**: Accepted  
**Date**: 2026-01-23

## Context

The system needs to expose task operations (add_task, list_tasks, complete_task, update_task, delete_task) as tools to AI agents. The architecture must support stateless operation while maintaining user-level data isolation. The solution must integrate with the OpenAI Agents SDK and follow the Model Context Protocol (MCP) specification.

## Decision

We will implement a dedicated MCP server using the official Python MCP SDK that exposes task operations as standardized tools. The server will be built with FastAPI and will handle authentication via JWT tokens passed with each tool call to ensure proper user isolation.

The MCP server will:
- Use the official python-mcp-sdk to register and serve tools
- Implement stateless operations that store all state in the database
- Authenticate each tool call using JWT tokens to identify the calling user
- Enforce user-level data isolation at the tool level
- Follow consistent input/output contracts defined via JSON Schema

## Alternatives

- **Custom AI tool protocol**: Build our own protocol for exposing tools to AI agents. Rejected because it would lack standardization and require more maintenance.
- **Direct API integration**: Have AI agents call our REST APIs directly instead of using MCP tools. Rejected because it doesn't follow the MCP standard and would complicate the architecture.
- **Server-side session state**: Store conversation context in server memory between AI requests. Rejected because it violates the stateless requirement and complicates scaling.

## Consequences

**Positive:**
- Standardized integration with AI agents via MCP protocol
- Stateless operation enables horizontal scaling
- Clear separation between AI layer and backend services
- Proper user data isolation at the tool level

**Negative:**
- Additional complexity of maintaining an MCP server
- Need to handle authentication within each tool call
- Potential latency overhead for tool operations

## References

- plan.md: Technical Context section on MCP SDK usage
- research.md: MCP SDK Integration decision
- spec.md: Requirements for MCP tools and user isolation