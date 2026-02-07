# ADR-003: Data Architecture with SQLModel and Neon PostgreSQL

**Status**: Accepted  
**Date**: 2026-01-23

## Context

The system needs to persist task data durably to ensure it survives server restarts and is available consistently across sessions. The architecture must support user-level data isolation with efficient querying capabilities. The solution must integrate with FastAPI and support async operations.

## Decision

We will use SQLModel as the ORM with Neon Serverless PostgreSQL as the database. This combination provides async support needed for FastAPI, while offering the relationship mapping and query capabilities needed for the application.

The data architecture will:
- Use SQLModel as the ORM to provide both SQLAlchemy and Pydantic capabilities
- Use Neon Serverless PostgreSQL for automatic scaling and serverless benefits
- Implement proper connection pooling for efficient database access
- Define clear data models with appropriate indexes for performance
- Use UUIDs for primary keys to ensure global uniqueness

## Alternatives

- **Raw SQL queries**: Execute raw SQL directly without an ORM. Rejected because it would reduce maintainability and increase the risk of SQL injection.
- **Alternative ORMs**: Use SQLAlchemy Core, Peewee, or Tortoise ORM. Rejected because SQLModel provides both SQLAlchemy and Pydantic integration in one package.
- **Different database**: Use MongoDB, SQLite, or another database. Rejected because Neon PostgreSQL is specified in requirements and provides the ACID properties and relationship support needed.
- **Object storage**: Store data in JSON files or object storage. Rejected because it wouldn't provide the querying capabilities needed for user isolation and task management.

## Consequences

**Positive:**
- Strong typing with Pydantic integration
- Async support for FastAPI compatibility
- Automatic scaling with Neon Serverless
- Rich querying capabilities for complex operations
- ACID properties for data consistency

**Negative:**
- Learning curve for SQLModel if team is unfamiliar
- Potential cold start delays with serverless database
- Vendor lock-in with Neon-specific features

## References

- plan.md: Technical Context section on SQLModel and Neon PostgreSQL
- research.md: Database Connection Management decision
- data-model.md: Entity models and database schema
- spec.md: Requirements for data persistence