# Data Model: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2025-01-24
**Purpose**: Define entities, relationships, validation rules, and state transitions

## Entity Relationship Diagram

```
┌──────────────┐
│    User      │
│  (Auth Sys)  │
└──────┬───────┘
       │ 1
       │
       │ N
┌──────┴────────┐     ┌──────────────┐
│ Conversation  │     │    Task      │
├───────────────┤     ├──────────────┤
│ id (PK)       │     │ id (PK)      │
│ user_id (FK)  │     │ user_id (FK) │
│ created_at    │     │ title        │
└──────┬────────┘     │ completed    │
       │ 1             │ created_at   │
       │               │ updated_at   │
       │ N             └──────────────┘
┌──────┴────────┐
│    Message    │
├───────────────┤
│ id (PK)       │
│ conversation_id (FK) │
│ role          │
│ content       │
│ created_at    │
└───────────────┘
```

## Entities

### User

**Purpose**: Represents a person authenticated via Better Auth. Tasks and conversations are isolated by user_id.

**Attributes**:
- `id` (UUID, primary key): Unique user identifier
- `email` (string, unique): User email address
- `created_at` (timestamp): Account creation timestamp

**Relationships**:
- Has many Conversations (1:N)
- Has many Tasks (1:N)

**Notes**:
- Managed by Better Auth authentication system
- Never directly accessed by MCP tools (only referenced via user_id)
- Cascade deletes: When user deleted, all their conversations and tasks are deleted

**Validation Rules**:
- Email must be valid format (enforced by Better Auth)
- Email must be unique

---

### Conversation

**Purpose**: Represents a series of message exchanges between a user and the AI assistant. Enables conversation continuity across requests.

**Attributes**:
- `id` (UUID, primary key, auto-generated): Unique conversation identifier
- `user_id` (UUID, foreign key → User.id): Owner of this conversation
- `created_at` (timestamp, auto-generated): When conversation was created

**Relationships**:
- Belongs to User (N:1)
- Has many Messages (1:N)

**State Transitions**: None (conversation is a passive container for messages)

**Operations**:
- Create: Auto-created when conversation_id not provided in chat request
- Read: Retrieved by conversation_id and user_id (must match)
- Delete: Cascade deletes all associated messages

**Validation Rules**:
- `user_id` must be valid UUID
- `user_id` must reference existing user
- `conversation_id` must be provided for continuation
- Only owner (user_id match) can access conversation

**Indexes**:
- Primary key: `id`
- Foreign key index: `user_id` (for filtering user's conversations)

**Constitution Compliance**:
- ✅ Stateless: Conversation metadata persisted to database
- ✅ Database as Single Source of Truth: No in-memory storage

---

### Message

**Purpose**: Represents a single communication in a conversation. Stores both user messages and assistant responses for conversation history.

**Attributes**:
- `id` (UUID, primary key, auto-generated): Unique message identifier
- `conversation_id` (UUID, foreign key → Conversation.id): Which conversation this message belongs to
- `role` (enum: "user" | "assistant"): Who sent this message
- `content` (text): The message content
- `created_at` (timestamp, auto-generated): When message was created

**Relationships**:
- Belongs to Conversation (N:1)

**State Transitions**: None (messages are immutable once created)

**Operations**:
- Create: New message added to conversation (user or assistant role)
- Read: Retrieved as part of conversation history
- Delete: Cascade deleted when conversation deleted

**Validation Rules**:
- `conversation_id` must be valid UUID
- `conversation_id` must reference existing conversation
- `role` must be either "user" or "assistant"
- `content` cannot be empty or whitespace-only
- `content` maximum length: 10,000 characters (configurable)

**Indexes**:
- Primary key: `id`
- Foreign key index: `conversation_id` (for loading conversation history)
- Composite index: `(conversation_id, created_at)` (for chronological ordering)

**Constitution Compliance**:
- ✅ Conversation Continuity: All messages persisted, retrievable across restarts
- ✅ Stateless: No in-memory message storage

---

### Task

**Purpose**: Represents a single todo item managed by users through natural language commands.

**Attributes**:
- `id` (UUID, primary key, auto-generated): Unique task identifier
- `user_id` (UUID, foreign key → User.id): Owner of this task
- `title` (text): Task description (what the user needs to do)
- `completed` (boolean, default: false): Task completion status
- `created_at` (timestamp, auto-generated): When task was created
- `updated_at` (timestamp, auto-updated): When task was last modified

**Relationships**:
- Belongs to User (N:1)

**State Transitions**:
```
┌─────────┐     complete     ┌────────────┐
│ Created │ ───────────────> │ Completed  │
│(completed=false)          │(completed=true)│
└─────────┘                  └────────────┘
     ^                            │
     │                            │ recreate/uncomplete
     └────────────────────────────┘
```

**Operations**:
- Create (add_task): New task created with `completed=false`
- Read (list_tasks): Retrieve all tasks for a user (optionally filtered by status)
- Update (update_task): Modify task `title` field, `updated_at` auto-updates
- Complete (complete_task): Set `completed=true`, `updated_at` auto-updates
- Delete (delete_task): Remove task permanently

**Validation Rules**:
- `user_id` must be valid UUID and reference existing user
- `title` cannot be empty or whitespace-only
- `title` maximum length: 500 characters (configurable)
- `completed` must be boolean
- `updated_at` automatically updated on any modification

**Indexes**:
- Primary key: `id`
- Foreign key index: `user_id` (for filtering user's tasks)
- Composite index: `(user_id, completed)` (for filtering active vs completed tasks)

**Multi-Tenancy**:
- All queries MUST filter by `user_id`
- Users can only access their own tasks
- No cross-user task visibility

**Constitution Compliance**:
- ✅ Stateless: Task state persisted to database only
- ✅ MCP Tools: All task operations through MCP tools only
- ✅ Database as Single Source of Truth: No in-memory task storage

---

## Relationships Summary

| Entity | Related Entity | Relationship Type | Cardinality | Cascade Delete |
|--------|---------------|-------------------|-------------|----------------|
| User | Conversation | One-to-Many | 1 user → N conversations | Yes |
| User | Task | One-to-Many | 1 user → N tasks | Yes |
| Conversation | Message | One-to-Many | 1 conversation → N messages | Yes |

**Cascade Delete Behavior**:
- When User deleted: All their conversations and tasks are deleted
- When Conversation deleted: All associated messages are deleted
- When Task deleted: Task is permanently removed (no soft delete in Phase III)

---

## State Machines

### Task Lifecycle

```
                    ┌─────────────┐
                    │   Created   │
                    │ (completed: │
                    │    false)   │
                    └──────┬──────┘
                           │
                           │ complete_task()
                           │
                           ▼
                    ┌─────────────┐
                    │  Completed  │
                    │ (completed: │
                    │    true)    │
                    └─────────────┘

Allowed operations:
- Created state: update_task(), delete_task(), complete_task()
- Completed state: update_task(), delete_task()
```

### Message Lifecycle

```
┌─────────┐
│ Created │ (immutable after creation)
└─────────┘

No state transitions - messages are append-only logs
```

### Conversation Lifecycle

```
┌─────────┐
│ Created │ (passive container for messages)
└─────────┘

No state transitions - conversation exists if it has messages
```

---

## Data Integrity Constraints

### Database-Level Constraints

```sql
-- Foreign key constraints
ALTER TABLE conversations
ADD CONSTRAINT fk_conversations_user_id
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE messages
ADD CONSTRAINT fk_messages_conversation_id
FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;

ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_user_id
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Check constraints
ALTER TABLE messages
ADD CONSTRAINT chk_messages_role
CHECK (role IN ('user', 'assistant'));

ALTER TABLE tasks
ADD CONSTRAINT chk_tasks_title_not_empty
CHECK (LENGTH(TRIM(title)) > 0);
```

### Application-Level Validation

**Task Title Validation**:
- Strip leading/trailing whitespace
- Reject if empty after stripping
- Truncate if exceeds maximum length (with warning to user)

**User Access Control**:
- Every query MUST include `WHERE user_id = ?`
- MCP tools MUST verify user_id matches authenticated user
- Return 404 if resource exists but belongs to different user

**Message Content Validation**:
- Reject empty messages (after whitespace trimming)
- Preserve original formatting (no sanitization unless security risk)

---

## Performance Considerations

### Query Patterns

**Most Common Queries**:
1. Load conversation history: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC`
2. List user tasks: `SELECT * FROM tasks WHERE user_id = ?`
3. Filter by completion status: `SELECT * FROM tasks WHERE user_id = ? AND completed = ?`

**Index Optimization**:
- `messages(conversation_id, created_at)`: Covers conversation history queries
- `tasks(user_id)`: Covers task listing
- `tasks(user_id, completed)`: Covers status filtering

### N+1 Query Prevention

**Bad Pattern** (N+1 queries):
```python
# Don't do this - triggers N database queries
conversations = get_conversations(user_id)
for conv in conversations:
    conv.messages = get_messages(conv.id)  # N queries!
```

**Good Pattern** (single query with join):
```python
# Do this - single query with JOIN
conversations = get_conversations_with_messages(user_id)
# Or use SELECT IN for bulk loading
conversation_ids = [c.id for c in conversations]
messages = get_messages_for_conversations(conversation_ids)  # 1 query
```

---

## Migration Strategy

### Initial Schema Creation

**Order of Operations**:
1. Create `users` table (managed by Better Auth)
2. Create `conversations` table (depends on users)
3. Create `messages` table (depends on conversations)
4. Create `tasks` table (depends on users)

### Rollback Strategy

**If Migration Fails**:
- Transaction wraps all schema changes
- Rollback entire transaction on error
- No partial schema state possible

**If Rollback Required**:
- Drop tables in reverse order: tasks, messages, conversations, users
- Re-create from scratch or restore from backup

### Future Migrations

**Schema Evolution Principles**:
- Additive changes (new columns, tables) are safe
- Breaking changes require migration script:
  1. Add new column
  2. Backfill data
  3. Update application code
  4. Remove old column (in separate migration)

---

## Conformation Checklist

- ✅ All entities have clear purpose and attributes
- ✅ All relationships defined with cardinality
- ✅ Cascade delete behavior specified
- ✅ Validation rules documented (database and application level)
- ✅ State transitions defined (where applicable)
- ✅ Indexes specified for performance
- ✅ Multi-tenancy enforced via user_id
- ✅ Stateless architecture maintained (no in-memory state)
- ✅ Constitution compliance verified for all entities
- ✅ Migration strategy defined
