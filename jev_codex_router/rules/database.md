# Database Domain Rules
- Use parameterized queries or ORM models; never format raw SQL strings.
- Explicitly define transactional boundaries and isolation levels.
- Always add indexes on foreign keys and frequently filtered columns.
- Ensure all migrations are reversible (up/down).
