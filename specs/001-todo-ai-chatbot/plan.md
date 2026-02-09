# Implementation Plan: Todo AI Chatbot with Natural Language Interface

**Branch**: `001-todo-ai-chatbot` | **Date**: 2025-01-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-todo-ai-chatbot/spec.md`

## Summary

Build a conversational AI chatbot that enables users to manage personal todo lists using natural language, without learning command syntax. The system demonstrates stateless architecture with MCP (Model Context Protocol) tools as the single source of truth for task operations. All state persists to Neon PostgreSQL, enabling conversation continuity across server restarts and horizontal scalability. The AI agent interprets varied natural language expressions for task management (create, read, update, delete, complete) while maintaining multi-user data isolation.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (web framework), OpenAI Agents SDK (AI agent orchestration), Official MCP SDK (tool protocol), SQLModel (ORM), Better Auth (authentication)
**Storage**: Neon Serverless PostgreSQL (tasks, conversations, messages)
**Testing**: pytest (test framework), pytest-asyncio (async test support), pytest-cov (coverage)
**Target Platform**: Linux server (backend), web browsers (frontend via OpenAI ChatKit)
**Project Type**: Web application (backend + frontend separation)
**Performance Goals**: Task creation within 5 seconds (95%), task retrieval within 3 seconds (99%), support 50 concurrent users with response time under 5 seconds
**Constraints**: Stateless architecture (no in-memory state), MCP tools must query database directly, no caching layers in Phase III, TDD mandatory (tests before implementation)
**Scale/Scope**: 50 concurrent users, 5 basic task operations, unlimited conversation history within practical storage limits, English language only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Stateless Architecture (NON-NEGOTIABLE) - ✅ PASS
- **Requirement**: All backend components stateless, all state to database
- **Plan Impact**: No in-memory conversation or task state. Every request reads from DB, writes immediately to DB.
- **Compliance**: MCP tools will query PostgreSQL directly. Chat endpoint loads conversation history from DB on each request. Server can restart without data loss.

### II. MCP-First Tool Design - ✅ PASS
- **Requirement**: All task operations as MCP tools using Official MCP SDK
- **Plan Impact**: Task operations (add, list, complete, delete, update) exposed exclusively as MCP tools. Agent interacts only through MCP server.
- **Compliance**: MCP tools will be stateless, accepting user_id and returning structured JSON per contract standards.

### III. Database as Single Source of Truth - ✅ PASS
- **Requirement**: All persistent state in Neon PostgreSQL, no caching layers
- **Plan Impact**: Tasks, conversations, and messages stored in PostgreSQL. No Redis or in-memory caches.
- **Compliance**: Every request reads current state. Conversation history reconstructed from DB on each request.

### IV. Test-First Development (NON-NEGOTIABLE) - ✅ PASS
- **Requirement**: TDD mandatory, Red-Green-Refactor cycle, integration tests for MCP tools, chat endpoint, agent-tool interactions, database operations
- **Plan Impact**: Tests written before any implementation. User approval required before implementation begins.
- **Compliance**: Implementation phase cannot start until tests are written, approved, and failing.

### V. Natural Language Interface - ✅ PASS
- **Requirement**: AI agent handles command interpretation via OpenAI Agents SDK, no command syntax required
- **Plan Impact**: OpenAI Agents SDK configured for intent recognition and tool selection. Varied phrasing supported.
- **Compliance**: Chat endpoint passes messages to agent, agent selects appropriate MCP tool, extracts parameters automatically.

### VI. Agentic Development Only - ✅ PASS
- **Requirement**: Zero manual coding, all via Claude Code with Spec-Kit Plus
- **Plan Impact**: No manual code editing. All implementation through agentic workflow.
- **Compliance**: Workflow: spec → plan → tasks → implement via Claude Code. All prompts documented.

### VII. Conversation Continuity - ✅ PASS
- **Requirement**: Conversations persist across restarts via conversation_id, messages with role/timestamp
- **Plan Impact**: Messages table stores full history. Chat endpoint accepts conversation_id, retrieves history.
- **Compliance**: New conversations auto-created when conversation_id not provided. History passed to agent with each request.

**Overall Gate Status**: ✅ ALL GATES PASSED - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-ai-chatbot/
├── spec.md              # Feature specification (already complete)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technology research and decisions
├── data-model.md        # Phase 1: Entity definitions and relationships
├── quickstart.md        # Phase 1: Developer onboarding guide
├── contracts/           # Phase 1: API and MCP tool contracts
│   ├── mcp-tools.yaml   # MCP tool specifications
│   └── chat-api.yaml    # Chat endpoint OpenAPI spec
└── tasks.md             # Phase 2: Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/                      # FastAPI application
├── src/
│   ├── models/              # SQLModel database models
│   │   ├── task.py          # Task entity
│   │   ├── conversation.py  # Conversation entity
│   │   ├── message.py       # Message entity
│   │   └── user.py          # User entity (auth reference)
│   ├── services/            # Business logic (stateless)
│   │   ├── task_service.py  # Task operations logic
│   │   └── chat_service.py  # Chat/conversation logic
│   ├── api/                 # FastAPI endpoints
│   │   ├── chat.py          # Chat endpoint
│   │   └── health.py        # Health check endpoint
│   ├── mcp/                 # MCP server implementation
│   │   ├── server.py        # MCP server setup
│   │   └── tools/           # MCP tool implementations
│   │       ├── add_task.py
│   │       ├── list_tasks.py
│   │       ├── complete_task.py
│   │       ├── delete_task.py
│   │       └── update_task.py
│   ├── agent/               # OpenAI Agents SDK integration
│   │   ├── agent.py         # Agent configuration
│   │   └── prompts.py       # System prompts
│   └── db/                  # Database setup
│       ├── session.py       # Database session management
│       └── init.py          # DB initialization
├── tests/                   # Test suite (TDD approach)
│   ├── contract/            # MCP tool contract tests
│   ├── integration/         # Chat endpoint and flow tests
│   └── unit/                # Unit tests for services
├── migrations/              # Database migration scripts
│   ├── 001_initial_schema.sql
│   └── 002_seed_data.sql
├── pyproject.toml           # Python dependencies
└── main.py                  # FastAPI application entry point

frontend/                    # OpenAI ChatKit (hosted separately)
├── .env                     # Environment variables
├── public/                  # Static assets (if any)
└── config/                  # ChatKit configuration
    └── domain-allowlist.json

README.md                    # Setup, deployment, testing guide
```

**Structure Decision**: Web application structure selected per Constitution Required Stack. Backend contains all business logic, API endpoints, MCP server, and agent integration. Frontend is OpenAI ChatKit (hosted separately) configured to connect to backend chat endpoint. Tests follow TDD principles with contract, integration, and unit test separation.

## Complexity Tracking

> **No constitutional violations requiring justification**

This implementation adheres to all constitutional principles without requiring exceptions or complexity justifications.
