# Research: Chat API & Orchestration Layer

## Overview
This document outlines the research findings for implementing the Chat API & Orchestration Layer. It addresses unknowns from the technical context and provides information about dependencies and integrations.

## Decision: AI Agent Integration Approach
**Rationale**: The system needs to integrate with an AI agent that can process user messages and potentially call external tools. The OpenAI Agents SDK is the most appropriate choice based on the constitution's constraint of using the OpenAI Agents SDK.

**Alternatives considered**: 
- Building a custom AI agent framework
- Using LangChain or similar libraries
- Using the OpenAI Assistants API directly

## Decision: Conversation Context Management
**Rationale**: To maintain statelessness per request while preserving conversation context, we'll load the conversation history from the database for each request and pass it to the AI agent. This aligns with the "Stateless AI" principle from the constitution.

**Alternatives considered**:
- Server-side session storage (violates statelessness)
- Client-side context passing (security and complexity concerns)

## Decision: Database Schema Design
**Rationale**: Using Neon Serverless PostgreSQL with SQLModel ORM to store conversation and message data. This aligns with the constitution's constraints and provides the necessary scalability.

**Alternatives considered**:
- NoSQL databases (would complicate the architecture)
- In-memory storage (doesn't meet reliability requirements)

## Decision: API Contract Design
**Rationale**: Designing a RESTful JSON-only API that accepts chat messages and returns structured responses. The API will be stateless and idempotent as required by the constitution.

**Alternatives considered**:
- WebSocket connections (adds complexity without clear benefits)
- GraphQL (overkill for this use case)

## Decision: Tool Call Handling
**Rationale**: The API will intercept tool calls from the AI agent, forward them to the MCP server, receive results, and continue the agent execution. This provides transparency to the frontend while maintaining proper separation of concerns.

**Alternatives considered**:
- Exposing tool calls directly to the frontend (violates the requirement for transparency)
- Blocking tool calls entirely (limits AI agent capabilities)

## Decision: Authentication and User Isolation
**Rationale**: Using JWT-based authentication to ensure all chat actions are user-scoped and authenticated, as required by the constitution's security principle.

**Alternatives considered**:
- Session-based authentication (violates statelessness)
- No authentication (violates security requirements)