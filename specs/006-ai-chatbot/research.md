# Research Findings: Todo AI Chatbot

## Overview
This document captures research findings and decisions made during the planning phase for the Todo AI Chatbot feature. All previously identified "NEEDS CLARIFICATION" items have been resolved through research and analysis.

## Key Decisions

### 1. OpenAI Agent Configuration
- **Decision**: Use OpenAI Assistant API with GPT-4 Turbo for optimal balance of intelligence and cost
- **Rationale**: GPT-4 Turbo offers improved reasoning capabilities needed for understanding complex natural language todo requests while maintaining reasonable response times and costs
- **Alternatives considered**: 
  - GPT-3.5 Turbo (faster and cheaper but less capable for complex reasoning)
  - GPT-4 (more capable but slower and more expensive)
  - Alternative AI providers (would complicate integration and require different skill sets)

### 2. Conversation Context Reconstruction Strategy
- **Decision**: Implement hybrid approach using conversation history + vector embeddings for context
- **Rationale**: Pure history can become too long and exceed token limits; pure embeddings might lose important details. Combining both ensures context preservation while managing token usage
- **Alternatives considered**:
  - Full history approach (would eventually exceed token limits)
  - Summarization approach (risk of losing important details)
  - Vector embeddings only (might miss important contextual details)

### 3. MCP Tool Integration Pattern
- **Decision**: Implement a tool router pattern that maps AI agent decisions to specific MCP tools
- **Rationale**: Maintains clear separation of concerns while allowing the AI to trigger appropriate operations without directly implementing them
- **Alternatives considered**:
  - Direct integration (violates separation of concerns principle)
  - Generic tool wrapper (might not handle specific tool requirements well)

### 4. Frontend Integration Approach
- **Decision**: Use OpenAI ChatKit with custom backend API for conversation management
- **Rationale**: ChatKit provides robust UI components while our backend handles conversation persistence and AI processing
- **Alternatives considered**:
  - Building custom chat UI (would require significant effort)
  - Other chat frameworks (would require different skill sets)

### 5. Authentication and User Isolation
- **Decision**: Leverage existing Better Auth JWT implementation for user identification and isolation
- **Rationale**: Aligns with existing architecture and security practices in the codebase
- **Alternatives considered**:
  - Separate authentication system (would create inconsistency)
  - Session-based authentication (violates stateless principle)

## Technical Research Findings

### OpenAI Assistant API Integration
- The Assistant API maintains its own thread state, but for our stateless architecture, we'll need to recreate threads for each request
- We can attach file-based knowledge to assistants for domain-specific understanding
- Tool calling capabilities allow us to extend the assistant's functionality with custom tools

### Conversation Persistence Strategy
- Need to maintain conversation history in our own database to ensure persistence across server restarts
- Will implement a synchronization mechanism between ChatKit frontend, our backend, and OpenAI's thread system
- Each conversation will have a unique ID that connects the frontend session, backend records, and OpenAI thread

### Performance Considerations
- OpenAI API calls typically take 1-3 seconds depending on complexity
- Need to implement proper loading states in the UI to manage user expectations
- Rate limiting considerations for production deployment

## Architecture Patterns Identified

### Service Layer Pattern
- Clear separation between API layer, business logic (services), and data models
- Allows for easy testing and maintenance of individual components

### Repository Pattern
- Abstracts data access logic for conversations, messages, and todos
- Enables easier testing and potential future database changes

### Event-Driven Updates
- Use WebSocket connections or server-sent events for real-time updates between chat and todo list
- Ensures consistency between the AI conversation and the visual todo interface