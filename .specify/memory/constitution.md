<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: Initial → 1.0.0 (MAJOR: Initial constitution ratification)

Modified Principles:
  - N/A (initial version)

Added Sections:
  - All 7 Core Principles (I-VII)
  - Technology Constraints section
  - MCP Tool Contract Standards section
  - Development Workflow section
  - Quality Gates section
  - Deployment Requirements section
  - Deliverables Standard section
  - Governance section

Removed Sections:
  - N/A (initial version)

Templates Status:
  ✅ plan-template.md - Reviewed, constitution check section compatible
  ✅ spec-template.md - Reviewed, user story structure aligned with TDD principle
  ✅ tasks-template.md - Reviewed, test-first approach aligned
  ⚠ README.md - Not found (needs creation per deliverables standard)

Follow-up TODOs:
  - README.md must be created with setup steps, environment variables,
    deployment guide, and testing instructions (per Deliverables Standard)
  - Database migrations directory must be created per Repository Structure
  - API documentation for chat endpoint must be generated
  - MCP tool specifications must be documented with examples

================================================================================
-->

# Todo AI Chatbot Constitution

## Core Principles

### I. Stateless Architecture (NON-NEGOTIABLE)

Every backend component MUST be stateless. All state MUST persist to the database. Server instances MUST hold no conversation or task state in memory. Any request MUST be handleable by any server instance.

**Rationale**: This enables horizontal scaling, resilience to restarts, and simplified deployment. Statelessness is foundational to the architecture and cannot be compromised.

### II. MCP-First Tool Design

All task operations MUST be exposed as MCP tools using the Official MCP SDK. Tools are the single source of truth for task operations. MCP tools MUST be stateless - they MUST query/modify the database directly. Agent interactions MUST flow through the MCP server only. No direct database access from agent logic.

**Rationale**: MCP tools provide a clean contract boundary, ensure statelessness, and enable proper separation of concerns between agent intelligence and data operations.

### III. Database as Single Source of Truth

All persistent state (tasks, conversations, messages) MUST be stored in Neon PostgreSQL. Every request MUST read current state from the database. Every action MUST write results to the database immediately. Conversation history MUST be reconstructed from the database on each request. No caching layers in Phase III.

**Rationale**: Ensures consistency across requests, enables conversation continuity, and simplifies reasoning about system state.

### IV. Test-First Development (NON-NEGOTIABLE)

TDD is mandatory for all components: MCP tools, API endpoints, and database operations. Tests MUST be written first → User MUST approve → Tests MUST fail → Implementation begins. Red-Green-Refactor cycle MUST be strictly enforced. Integration tests REQUIRED for: MCP tool contracts, chat endpoint flow, agent-tool interactions, and database operations.

**Rationale**: Test-first development ensures quality, provides executable specification, and prevents regression. This is non-negotiable for maintaining system reliability.

### V. Natural Language Interface

AI agent MUST handle all command interpretation via OpenAI Agents SDK. Users MUST interact purely through conversational language - no command syntax required. Agent MUST understand intent variations (e.g., "add task", "remember to", "create todo"). Tool selection and parameter extraction MUST be handled by agent intelligence.

**Rationale**: Natural language interface reduces user cognitive load and makes the system accessible to non-technical users.

### VI. Agentic Development Only

Zero manual coding - all implementation MUST be via Claude Code with Spec-Kit Plus. Workflow: Write spec → Generate plan → Break into tasks → Implement. Every feature MUST have a spec file before development. Prompts and iterations MUST be documented for review. Human role is limited to specification, review, and approval.

**Rationale**: Ensures consistent development process, maintains traceability, and enables review of AI-assisted development decisions.

### VII. Conversation Continuity

Conversations MUST persist across server restarts. Each request MUST include conversation_id to retrieve history. Agent MUST receive full conversation context (history + new message). New conversations MUST be auto-created when conversation_id is not provided. Messages MUST be stored with role (user/assistant) and timestamp.

**Rationale**: Users expect conversations to resume seamlessly regardless of server state. This principle ensures natural user experience.

## Technology Constraints

### Required Stack

**Frontend**: OpenAI ChatKit (hosted with domain allowlist configuration)
**Backend**: Python FastAPI
**AI Framework**: OpenAI Agents SDK
**MCP**: Official MCP SDK
**ORM**: SQLModel
**Database**: Neon Serverless PostgreSQL
**Auth**: Better Auth

**No substitutions allowed**. This stack is chosen for learning objectives and architectural alignment.

## MCP Tool Contract Standards

Every MCP tool MUST:
- Accept `user_id` as a required parameter for multi-tenancy
- Return structured JSON in the format `{task_id, status, title}` or `{tasks: [...]}` for list operations
- Include error responses in the format `{error: string, code: string}`
- Use standardized status values: `"created"`, `"updated"`, `"completed"`, `"deleted"`
- Be documented with purpose, parameters, returns, and examples

## Development Workflow

### Specification Phase

1. Write detailed spec file in `/specs` directory
2. Include: purpose, inputs, outputs, examples, edge cases
3. Get user approval before proceeding
4. Spec becomes contract for tests

### Implementation Phase

1. Generate implementation plan via Claude Code
2. Break plan into discrete tasks
3. Write tests first (must fail initially)
4. Implement via Claude Code until tests pass
5. Document prompts and iterations used
6. No manual code editing allowed

## Quality Gates

- All MCP tools MUST have unit tests
- Chat endpoint MUST have integration tests
- Database operations MUST have transaction tests
- Agent behavior MUST have conversation flow tests
- Tests MUST pass before merge
- Code review focuses on spec compliance, not implementation details

## Deployment Requirements

- Frontend deployed with production URL (Vercel/GitHub Pages/custom)
- Domain added to OpenAI allowlist before ChatKit usage
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` configured
- Database migrations applied before server start
- Environment variables documented in README

## Deliverables Standard

### Repository Structure

```
/frontend     # ChatKit UI
/backend      # FastAPI + Agents SDK + MCP
/specs        # All specification files
/tests        # Test suites
/migrations   # Database migration scripts
README.md     # Setup instructions
```

### Chatbot Capabilities (Acceptance Criteria)

✅ Manage all Basic Level task operations via natural language
✅ Maintain conversation context across requests
✅ Provide confirmation messages for all actions
✅ Handle errors gracefully with user-friendly messages
✅ Resume conversations after server restart
✅ Support concurrent users via user_id isolation

### Documentation Requirements

README MUST include:
- Setup steps
- Environment variables
- Deployment guide
- Testing instructions

Additional documentation:
- API documentation for chat endpoint
- MCP tool specifications with examples
- Database schema documentation
- Agent behavior specification

## Governance

This constitution supersedes all implementation preferences. When conflicts arise between developer preference and constitutional principles, the constitution wins.

**Amendment Procedure**:
1. Document rationale for the amendment
2. Obtain user approval
3. Provide migration plan for existing code

**Complexity Principle**: Complexity MUST be justified - YAGNI (You Aren't Gonna Need It) principles apply. All development reviews MUST verify:

- Stateless architecture is maintained
- MCP tools properly implement contracts
- Database is the single source of truth
- Tests are written before implementation
- Agentic development process is followed

**Version**: 1.0.0 | **Ratified**: 2025-01-24 | **Last Amended**: 2025-01-24
