# Research: Todo AI Chatbot – MCP Server Tools

## Overview
This research document addresses the unknowns and technical decisions required for implementing the MCP server that exposes task operations as tools.

## Key Unknowns Resolved

### 1. MCP SDK Integration
**Decision**: Use the official Model Context Protocol (MCP) SDK for Python to implement the server
**Rationale**: The specification requires using the Official MCP SDK, which provides standardized interfaces for exposing tools to AI agents
**Alternatives considered**: 
- Building a custom protocol (rejected - reinventing the wheel, lacks standardization)
- Using alternative AI tool protocols (rejected - specification mandates MCP SDK)

### 2. Authentication Method for User Isolation
**Decision**: Implement JWT-based authentication to identify users calling MCP tools
**Rationale**: JWT tokens can be passed in tool requests to identify the calling user, enabling proper data isolation
**Alternatives considered**:
- Session-based authentication (rejected - MCP tools should be stateless)
- API keys per user (rejected - JWT is more standard for this use case)

### 3. Database Connection Management
**Decision**: Use SQLModel with Neon Serverless PostgreSQL for task persistence
**Rationale**: Specification mandates these technologies; they provide async support needed for FastAPI
**Alternatives considered**:
- Raw SQL queries (rejected - ORM provides better maintainability)
- Different database (rejected - specification mandates Neon PostgreSQL)

### 4. Tool Contract Definition Format
**Decision**: Define tool contracts using JSON Schema for input/output validation
**Rationale**: MCP SDK supports JSON Schema for defining tool parameters and responses
**Alternatives considered**:
- Custom validation (rejected - JSON Schema is standard for this purpose)
- No validation (rejected - would lead to unreliable tool usage)

### 5. Error Handling Strategy
**Decision**: Implement consistent error responses with appropriate HTTP-like status codes
**Rationale**: MCP tools need to communicate errors clearly to AI agents for proper handling
**Alternatives considered**:
- Generic error responses (rejected - insufficient information for AI agents)
- Exception propagation (rejected - would leak internal details)

## Technical Architecture

### MCP Server Structure
- FastAPI application serving as the MCP server
- Individual route handlers for each tool (add_task, list_tasks, etc.)
- Authentication middleware to identify calling user
- Database session management for each request
- JSON Schema validation for tool inputs/outputs

### Data Flow
1. AI client calls MCP tool with JWT token
2. Authentication middleware extracts user ID from token
3. Tool handler performs operation with user-scoped data access
4. Database operations are performed with user ID filter
5. Result is returned to AI client

### Security Considerations
- All tool calls must be authenticated
- User data access is filtered by user ID
- JWT tokens must be properly validated
- Rate limiting should be implemented to prevent abuse