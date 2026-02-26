# Database Migration Guide

This guide explains how to manage database migrations using **Alembic** in this project.

## Quick Start

### Creating a New Migration

**Option 1: Using Makefile**
```bash
# Format
make migration CAT='<category>' DESC='<description>'

# Example: Add a new table
make migration CAT='020-user' DESC='create_notifications_table'
```

**Option 2: Using CLI directly**
```bash
# Format
uv run alembic revision -m "<category>_<description>"

# Example
uv run alembic revision -m "020_user_add_phone_to_profiles"
```

### Running Migrations

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Rollback last migration
uv run alembic downgrade -1
```

## Category Prefixes

We use a categorized naming convention for migrations to keep the history organized:

| Prefix | Purpose | Examples |
|--------|---------|----------|
| `000-infra` | Infrastructure | Schemas, extensions, triggers, functions |
| `020-user` | User/App Data | Testimonials, profiles, preferences |
| `060-checkpoint` | LangGraph | Checkpoints, storage permissions |
| `070-view` | Views | Materialized views, reports |

## Current Migrations

1. **`000-infra`**: Creates the `mengantar_test` schema and enables `uuid-ossp`/`pgcrypto` extensions.
2. **`020-user`**: Creates the `testimonials` table.
3. **`060-checkpoint`**: Sets up permissions for LangGraph's internal tables.

## Best Practices

- **Schema Specificity**: Always specify the schema `mengantar_test` when creating tables or indexes.
- **Idempotency**: Use `IF NOT EXISTS` or check for table existence if necessary.
- **LangGraph Checkpoints**: Avoid creating LangGraph's internal tables (`checkpoints`, etc.) manually. LangGraph manages these via `AsyncPostgresSaver.setup()`. Use migrations only for permissions or custom extensions related to checkpoints.
- **Startup Automation**: The Docker container automatically runs `alembic upgrade head` on startup via `entrypoint.sh`.
