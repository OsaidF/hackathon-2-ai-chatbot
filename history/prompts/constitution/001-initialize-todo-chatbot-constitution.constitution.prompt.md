---
id: 001
title: Initialize Todo AI Chatbot Constitution
stage: constitution
date: 2025-01-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: architect
command: /sp.constitution
labels: ["constitution", "setup", "initialization"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - No tests for constitution update
---

## Prompt

Todo AI Chatbot Constitution
Core Principles
I. Stateless Architecture (NON-NEGOTIABLE)
Every backend component must be stateless; all state persists to database. Server instances hold no conversation or task state in memory. Any request can be handled by any server instance. This enables horizontal scaling, resilience to restarts, and simplified deployment.
II. MCP-First Tool Design
All task operations exposed as MCP tools using Official MCP SDK. Tools are the single source of truth for task operations. MCP tools must be stateless - query/modify database directly. Agent interactions flow through MCP server only. No direct database access from agent logic.
III. Database as Single Source of Truth
All persistent state (tasks, conversations, messages) stored in Neon PostgreSQL. Every request reads current state from database. Every action writes results to database immediately. Conversation history reconstructed from database on each request. No caching layers in Phase III.
IV. Test-First Development (NON-NEGOTIABLE)
TDD mandatory for all components: MCP tools, API endpoints, database operations. Tests written → User approved → Tests fail → Implementation begins. Red-Green-Refactor cycle strictly enforced. Integration tests required for: MCP tool contracts, chat endpoint flow, agent-tool interactions, database operations.
V. Natural Language Interface
AI agent handles all command interpretation via OpenAI Agents SDK. Users interact purely through conversational language - no command syntax required. Agent must understand intent variations ("add task", "remember to", "create todo"). Tool selection and parameter extraction handled by agent intelligence.
VI. Agentic Development Only
Zero manual coding - all implementation via Claude Code with Spec-Kit Plus. Workflow: Write spec → Generate plan → Break into tasks → Implement. Every feature must have spec file before development. Prompts and iterations documented for review. Human role limited to specification, review, and approval.
VII. Conversation Continuity
Conversations persist across server restarts. Each request includes conversation_id to retrieve history. Agent receives full conversation context (history + new message). New conversations auto-created when conversation_id not provided. Messages stored with role (user/assistant) and timestamp.
Technology Constraints
Required Stack

Frontend: OpenAI ChatKit (hosted with domain allowlist configuration)
Backend: Python FastAPI
AI Framework: OpenAI Agents SDK
MCP: Official MCP SDK
ORM: SQLModel
Database: Neon Serverless PostgreSQL
Auth: Better Auth

No substitutions allowed. Stack chosen for learning objectives and architectural alignment.
MCP Tool Contract Standards
Every MCP tool must accept user_id as required parameter for multi-tenancy. Tools return structured JSON: {task_id, status, title} or {tasks: [...]} for list operations. Error responses include: {error: string, code: string}. Status values standardized: "created", "updated", "completed", "deleted". All tools documented with purpose, parameters, returns, examples.
Development Workflow
Specification Phase

Write detailed spec file in /specs directory
Include: purpose, inputs, outputs, examples, edge cases
Get user approval before proceeding
Spec becomes contract for tests

Implementation Phase

Generate implementation plan via Claude Code
Break plan into discrete tasks
Write tests first (must fail initially)
Implement via Claude Code until tests pass
Document prompts and iterations used
No manual code editing allowed

Quality Gates

All MCP tools must have unit tests
Chat endpoint must have integration tests
Database operations must have transaction tests
Agent behavior must have conversation flow tests
Tests must pass before merge
Code review focuses on spec compliance, not implementation details

Deployment Requirements

Frontend deployed with production URL (Vercel/GitHub Pages/custom)
Domain added to OpenAI allowlist before ChatKit usage
NEXT_PUBLIC_OPENAI_DOMAIN_KEY configured
Database migrations applied before server start
Environment variables documented in README

Deliverables Standard
Repository Structure
/frontend     # ChatKit UI
/backend      # FastAPI + Agents SDK + MCP
/specs        # All specification files
/tests        # Test suites
/migrations   # Database migration scripts
README.md     # Setup instructions
Chatbot Capabilities (Acceptance Criteria)

✅ Manage all Basic Level task operations via natural language
✅ Maintain conversation context across requests
✅ Provide confirmation messages for all actions
✅ Handle errors gracefully with user-friendly messages
✅ Resume conversations after server restart
✅ Support concurrent users via user_id isolation

Documentation Requirements

README with: setup steps, environment variables, deployment guide, testing instructions
API documentation for chat endpoint
MCP tool specifications with examples
Database schema documentation
Agent behavior specification

Governance
This constitution supersedes all implementation preferences. When conflicts arise between developer preference and constitutional principles, constitution wins. Amendments require: documentation of rationale, user approval, migration plan for existing code. Complexity must be justified - YAGNI principles apply.
All development reviews verify:

Stateless architecture maintained
MCP tools properly implement contracts
Database is single source of truth
Tests written before implementation
Agentic development process followed

Version: 1.0.0 | Ratified: 2025-01-24 | Last Amended: 2025-01-24

## Response snapshot

Successfully created Todo AI Chatbot Constitution version 1.0.0. The constitution establishes seven core principles:

1. **Stateless Architecture (NON-NEGOTIABLE)**: All state persists to database, enabling horizontal scaling
2. **MCP-First Tool Design**: All operations through MCP tools using Official MCP SDK
3. **Database as Single Source of Truth**: Neon PostgreSQL with no caching in Phase III
4. **Test-First Development (NON-NEGOTIABLE)**: TDD mandatory with Red-Green-Refactor cycle
5. **Natural Language Interface**: AI agent interprets all commands via OpenAI Agents SDK
6. **Agentic Development Only**: Zero manual coding, all via Claude Code with Spec-Kit Plus
7. **Conversation Continuity**: Conversations persist across server restarts

The constitution also defines:
- Technology constraints (FastAPI, OpenAI Agents SDK, SQLModel, Neon PostgreSQL, Better Auth)
- MCP tool contract standards with multi-tenancy support
- Development workflow (spec → plan → tasks → implement)
- Quality gates requiring comprehensive testing
- Deployment requirements for ChatKit frontend
- Repository structure and documentation requirements

## Outcome

- ✅ Impact: Foundation established for Todo AI Chatbot project with clear architectural principles
- 🧪 Tests: N/A (constitution update)
- 📁 Files: Created `.specify/memory/constitution.md` with complete constitution including sync impact report
- 🔁 Next prompts: Create README.md per deliverables standard, begin feature specification
- 🧠 Reflection: Constitution provides strong guardrails for development. Two principles marked NON-NEGOTIABLE (stateless architecture, test-first development) will require strict enforcement. Template compatibility verified across plan, spec, and tasks templates.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution successfully created with all placeholders filled
- Graders run and results (PASS/FAIL): N/A - constitution establishment phase
- Prompt variant (if applicable): Initial constitution ratification
- Next experiment (smallest change to try): Create README.md to satisfy deliverables standard, then begin first feature specification following the defined workflow
