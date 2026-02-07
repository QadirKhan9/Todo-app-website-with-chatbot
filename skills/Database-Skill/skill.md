# Database Skill – Create Tables, Migrations, Schema Design

**Description:** Design and manage database schemas, create tables, and handle migrations efficiently.

---

## Instructions

### 1. Schema Design
- Define entities and relationships clearly
- Normalize tables to reduce redundancy
- Use meaningful table and column names

### 2. Table Creation
- Use appropriate data types for each column
- Set primary keys and unique constraints
- Define foreign keys for relationships

### 3. Migrations
- Use migration files to track schema changes
- Apply migrations consistently across environments
- Rollback migrations safely if needed

---

## Best Practices
- Keep table names singular and descriptive  
- Avoid storing calculated or derived data  
- Index frequently queried columns for performance  
- Document schema changes for team reference  

---

## Example Structure

```sql
-- Users Table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posts Table
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  title VARCHAR(200) NOT NULL,
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
