# ADR-002: Authentication and Data Isolation Strategy

**Status**: Accepted  
**Date**: 2026-01-23

## Context

The system must ensure that each user can only access their own tasks through the MCP tools. The architecture must be stateless, meaning no server-side session state should be maintained between requests. This is critical for security and scalability.

## Decision

We will implement JWT-based authentication for all MCP tool calls. Each tool call will include a JWT token in the request headers that identifies the calling user. The token will be validated on each request, and all data access will be filtered by the authenticated user's ID.

The authentication system will:
- Use JWT tokens with HS256 encryption
- Include user ID in the "sub" claim of the token
- Validate tokens in each tool handler before performing operations
- Enforce user-level data isolation by filtering database queries by user ID
- Use python-jose for token handling and passlib for password hashing

## Alternatives

- **Session-based authentication**: Store session information server-side. Rejected because it violates the stateless requirement and complicates horizontal scaling.
- **API keys per user**: Use static API keys for authentication. Rejected because JWT tokens provide more flexibility and include user identity in the token itself.
- **OAuth 2.0**: Implement full OAuth flow. Rejected because it's overly complex for this use case and the system doesn't need third-party integrations.

## Consequences

**Positive:**
- Stateless operation supporting horizontal scaling
- Built-in user identification in tokens
- Fine-grained access control at the data level
- Standard authentication approach familiar to developers

**Negative:**
- Need to validate tokens on each tool call
- Larger request payloads due to token inclusion
- Token expiration and refresh considerations

## References

- plan.md: Security section on user-scoped authentication
- research.md: Authentication Method for User Isolation decision
- spec.md: Requirements for user-level data isolation