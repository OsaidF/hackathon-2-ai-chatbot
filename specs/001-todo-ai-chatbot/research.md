# Research: Todo AI Chatbot Architecture

**Feature**: 001-todo-ai-chatbot
**Date**: 2025-01-24
**Purpose**: Research and document technology decisions, best practices, and architectural patterns for implementation

## Overview

This document captures research findings and technology decisions for building a stateless AI chatbot with MCP tools. All decisions align with the constitutional principles and feature requirements.

## Decision 1: FastAPI with SQLModel for Backend

**Decision**: Use FastAPI as the web framework with SQLModel (built on Pydantic and SQLAlchemy) for ORM.

**Rationale**:
- FastAPI provides automatic OpenAPI documentation, async support, and type safety
- SQLModel combines Pydantic (validation) with SQLAlchemy (ORM) in a single model definition
- Both libraries have excellent TypeScript compatibility for future frontend integrations
- Strong community support and alignment with Python 3.11+ features
- Native support for dependency injection (useful for database sessions and authentication)

**Alternatives Considered**:
- **Django**: Too heavyweight, includes ORM we don't need (SQLModel preferred), more opinionated structure
- **Flask**: Requires more manual setup for async, OpenAPI, and validation
- **FastAPI + SQLAlchemy separately**: More boilerplate than SQLModel's unified approach

**Best Practices**:
- Use async endpoints for all database operations to support concurrency
- Leverage Pydantic models for request/response validation
- Implement dependency injection for database sessions (ensure per-request sessions)
- Use background tasks for operations that don't need to block the response

**Sources**:
- FastAPI official documentation: https://fastapi.tiangolo.com/
- SQLModel documentation: https://sqlmodel.tiangolo.com/

---

## Decision 2: MCP Server Architecture

**Decision**: Implement MCP server using Official MCP SDK with stdio transport for tool invocation.

**Rationale**:
- MCP SDK provides standard protocol implementation for tool discovery and invocation
- Stdio transport is simplest for local development and aligns with MCP specification
- Each tool operates independently as a stateless function
- Tools accept user_id parameter for multi-tenancy (per constitution)
- Structured JSON returns match contract standards

**Architecture Pattern**:
```
┌─────────────┐
│   Agent     │ (OpenAI Agents SDK)
└──────┬──────┘
       │ Tool invocation request
       ▼
┌─────────────┐
│ MCP Server  │ (stdio transport)
└──────┬──────┘
       │ Routes to appropriate tool
       ▼
┌─────────────────────────────────┐
│ MCP Tools (stateless functions) │
│ - add_task()                    │
│ - list_tasks()                  │
│ - complete_task()               │
│ - delete_task()                 │
│ - update_task()                 │
└─────────────────────────────────┘
       │ Direct DB query (no ORM layer)
       ▼
┌─────────────┐
│ PostgreSQL  │
└─────────────┘
```

**Alternatives Considered**:
- **SSE transport**: More complex, adds WebSocket-like overhead not needed for Phase III
- **HTTP-based MCP**: Adds network latency, stdio is sufficient for local agent-server communication

**Best Practices**:
- Each tool function must be pure (no side effects, no global state)
- Tools should handle database errors and return structured error responses
- Tool descriptions must be detailed for agent to understand capabilities
- Parameter validation happens at tool entry point

**Constitution Compliance**:
- ✅ Stateless: Each tool invocation is independent, queries DB directly
- ✅ MCP-First: All task operations go through MCP tools only
- ✅ Database as Single Source of Truth: Tools read/write PostgreSQL immediately

---

## Decision 3: Database Schema Design

**Decision**: Use separate tables for Tasks, Conversations, and Messages with foreign key relationships and user_id isolation.

**Schema Overview**:
```sql
-- Users table (simplified, managed by Better Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table (stores conversation metadata)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_conversations_user_id (user_id)
);

-- Messages table (stores individual messages)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_messages_conversation_id (conversation_id)
);

-- Tasks table (stores todo items)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tasks_user_id (user_id),
    INDEX idx_tasks_completed (user_id, completed)
);
```

**Rationale**:
- **UUID primary keys**: Prevents enumeration attacks, works well in distributed systems
- **Foreign key constraints**: Ensures data integrity (cascade deletes for orphaned records)
- **Indexes on user_id**: Optimizes queries filtering by user (most common query pattern)
- **Separation of concerns**: Tasks, Conversations, and Messages are distinct domains
- **Denormalization avoidance**: No redundant data, single source of truth

**Alternatives Considered**:
- **Integer auto-increment IDs**: Simpler but predictable (security concern)
- **Single table for tasks and messages**: Would violate single responsibility principle
- **Adding conversation_id to tasks**: Unnecessary coupling, tasks can exist without conversation context

**Best Practices**:
- Use database-level constraints for validation (not just application-level)
- Cascade deletes maintain referential integrity when user/conversation deleted
- Index foreign keys for query performance
- Store timestamps in UTC to avoid timezone issues

---

## Decision 4: OpenAI Agents SDK Integration

**Decision**: Use OpenAI Agents SDK with function calling (MCP tools) for natural language understanding and tool selection.

**Architecture Pattern**:
```
User Message (natural language)
       │
       ▼
┌─────────────────────────────┐
│ Chat Endpoint (FastAPI)     │
│ - Load conversation history │
│ - Extract user_id           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Agent (OpenAI Agents SDK)   │
│ - Context: conversation     │
│ - Tools: MCP tool schemas   │
└──────────┬──────────────────┘
           │ Intent recognition
           │ Parameter extraction
           ▼
┌─────────────────────────────┐
│ MCP Tool Invocation         │
│ - add_task()                │
│ - list_tasks()              │
│ - complete_task()           │
│ - delete_task()             │
│ - update_task()             │
└──────────┬──────────────────┘
           │ Tool result
           ▼
┌─────────────────────────────┐
│ Agent Response Generation   │
│ - Natural language response │
│ - Confirmation message      │
└──────────┬──────────────────┘
           │
           ▼
     Save to Messages table
           │
           ▼
    Return to User
```

**Rationale**:
- OpenAI Agents SDK handles intent recognition automatically
- Function calling is more reliable than prompt-based tool selection
- Agent receives full conversation context for multi-turn understanding
- System prompt can guide agent to confirm actions and handle errors gracefully

**Alternatives Considered**:
- **Prompt-based parsing**: More fragile, requires extensive testing for edge cases
- **Intent classification models**: Overkill for basic CRUD, adds complexity
- **Custom NLP pipeline**: Reimplementing what OpenAI Agents SDK provides

**Best Practices**:
- Provide clear tool descriptions so agent understands when to use each tool
- Include example interactions in system prompt
- Handle ambiguous requests by asking clarifying questions
- Confirm destructive operations (delete, complete) before executing
- Store both user message and agent response in messages table

---

## Decision 5: Stateless Chat Endpoint

**Decision**: Chat endpoint loads conversation history from database on each request, maintains no in-memory state.

**Request Flow**:
```python
# Pseudocode for chat endpoint
async def chat_endpoint(
    message: str,
    user_id: UUID,
    conversation_id: Optional[UUID] = None
):
    # 1. Load or create conversation
    if conversation_id is None:
        conversation = create_conversation(user_id)
    else:
        conversation = get_conversation(conversation_id, user_id)

    # 2. Load conversation history
    messages = load_messages(conversation.id)

    # 3. Add new user message
    user_message = create_message(conversation.id, "user", message)
    messages.append(user_message)

    # 4. Invoke agent with context
    agent_response = agent.invoke(
        messages=messages,
        tools=mcp_tools
    )

    # 5. Save assistant response
    assistant_message = create_message(
        conversation.id,
        "assistant",
        agent_response.content
    )

    # 6. Return response
    return {
        "conversation_id": conversation.id,
        "response": agent_response.content
    }
```

**Rationale**:
- Every request is independent (can be handled by any server instance)
- Server restart doesn't lose conversation context (history in DB)
- Horizontal scaling enabled (no sticky sessions required)
- Aligns with Constitution Principle I (Stateless Architecture)

**Alternatives Considered**:
- **In-memory conversation cache**: Faster but violates stateless principle, loses data on restart
- **Redis for conversation storage**: Adds complexity, unnecessary for Phase III scope

**Best Practices**:
- Use database transactions for message creation to ensure consistency
- Return conversation_id in response so frontend can maintain context
- Handle missing conversation_id gracefully (create new conversation)
- Implement pagination for conversation history if it grows large

---

## Decision 6: Testing Strategy (TDD)

**Decision**: Three-layer testing approach following Red-Green-Refactor cycle: contract tests → integration tests → unit tests.

**Test Layers**:

1. **Contract Tests** (MCP Tools):
   - Verify each tool accepts correct parameters
   - Validate return format matches contract standards
   - Test error responses for invalid inputs
   - Example: `test_add_task_returns_correct_format()`

2. **Integration Tests** (Chat Endpoint):
   - Test full flow: user message → agent → tool → database → response
   - Verify conversation persistence and retrieval
   - Test multi-user isolation (no data leakage)
   - Example: `test_conversation_persists_across_requests()`

3. **Unit Tests** (Services):
   - Test business logic in isolation
   - Mock database and external dependencies
   - Test edge cases and error handling
   - Example: `test_task_service_filters_by_user_id()`

**TDD Workflow** (Per Constitution):
```
1. Write test (RED)
   → Test must fail initially

2. Get user approval
   → Review test for correctness

3. Implement (GREEN)
   → Write minimum code to pass test

4. Refactor
   → Improve code without breaking tests
```

**Testing Tools**:
- **pytest**: Test framework and runner
- **pytest-asyncio**: Async test support for FastAPI
- **pytest-cov**: Code coverage reporting
- **httpx**: Test client for FastAPI endpoints
- **pytest-mock**: Mocking for unit tests

**Constitution Compliance**:
- ✅ Tests written before implementation
- ✅ Red-Green-Refactor cycle enforced
- ✅ Integration tests for MCP tools, chat endpoint, agent-tool interactions, database operations
- ✅ User approval required before implementation

**Alternatives Considered**:
- ** unittest framework**: Less pytest features, more boilerplate
- **Skipping contract tests**: Risk of MCP tool violations

---

## Decision 7: Error Handling Strategy

**Decision**: Structured error responses with user-friendly messages and appropriate HTTP status codes.

**Error Response Format**:
```json
{
  "error": "Task not found",
  "code": "TASK_NOT_FOUND",
  "details": "No task with ID '123' exists for this user"
}
```

**Error Categories**:

1. **Validation Errors** (400 Bad Request):
   - Missing required parameters (user_id, conversation_id)
   - Invalid task title (empty, too long)
   - Invalid UUID format

2. **Not Found Errors** (404 Not Found):
   - Task doesn't exist or belongs to different user
   - Conversation doesn't exist or belongs to different user

3. **Database Errors** (500 Internal Server Error):
   - Connection failures
   - Constraint violations
   - Transaction deadlocks

4. **Agent Errors** (500 Internal Server Error):
   - Tool invocation failures
   - Invalid agent responses
   - OpenAI API errors

**Best Practices**:
- Never expose database errors directly to users
- Log technical errors for debugging
- Return actionable error messages (what went wrong + how to fix)
- Use error codes for programmatic handling
- Test error paths in integration tests

---

## Decision 8: Performance Optimization

**Decision**: Focus on database query optimization and async operations rather than caching.

**Optimization Strategies**:

1. **Database Indexing**:
   - Index foreign keys (user_id, conversation_id)
   - Index frequently filtered columns (completed status)
   - Use `EXPLAIN ANALYZE` to verify query plans

2. **Async Operations**:
   - Use `async/await` for all database queries
   - Parallelize independent operations where possible
   - Use connection pooling for database connections

3. **Query Optimization**:
   - Select only required columns (avoid `SELECT *`)
   - Use joins efficiently (avoid N+1 queries)
   - Limit conversation history loaded per request

4. **Monitoring**:
   - Track query performance with database logs
   - Monitor endpoint response times
   - Alert on performance degradation

**Rationale**:
- Caching adds complexity and violates stateless principle for Phase III
- Database optimization is sufficient for 50 concurrent users
- Performance goals (3-5 seconds) are achievable without caching

**Alternatives Considered**:
- **Redis caching**: Faster but adds infrastructure complexity, violates "no caching in Phase III"
- **Read replicas**: Overkill for current scale, adds operational overhead

---

## Summary

All research decisions align with constitutional principles and feature requirements. No NEEDS CLARIFICATION items remain. The architecture is straightforward, stateless, and ready for Phase 1 (Design & Contracts).

**Next Steps**:
1. Create data-model.md with entity definitions
2. Create contracts/ with MCP tool and API specifications
3. Create quickstart.md for developer onboarding
4. Proceed to task generation via `/sp.tasks`

**Constitution Re-Check**: ✅ All principles still satisfied with researched architecture
