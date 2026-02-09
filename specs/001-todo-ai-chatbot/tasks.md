# Tasks: Todo AI Chatbot with Natural Language Interface

**Input**: Design documents from `/specs/001-todo-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/

**Tests**: TDD approach is MANDATORY per constitution. Tests are written for all components following Red-Green-Refactor cycle.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web application**: `backend/src/`, `frontend/src/`
- Paths shown below reflect the project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per implementation plan (backend/src/{models,services,api,mcp,agent,db}, tests/{contract,integration,unit}, migrations)
- [x] T002 Initialize Python project with pyproject.toml including FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel, pytest, pytest-asyncio, httpx, psycopg2-binary
- [x] T003 [P] Create .env.example template in backend/ with DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET, BETTER_AUTH_URL
- [x] T004 [P] Create .gitignore file in repository root for Python (venv, __pycache__, *.pyc, .env)
- [x] T005 [P] Create README.md in repository root with project overview, architecture diagram, and link to quickstart.md
- [x] T006 [P] Create frontend directory structure for OpenAI ChatKit configuration (frontend/.env, frontend/config/)
- [x] T007 [P] Create domain allowlist configuration in frontend/config/domain-allowlist.json for ChatKit

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Setup

- [x] T008 Create database session management in backend/src/db/session.py with async engine factory from SQLModel
- [x] T009 Create database initialization module in backend/src/db/init.py with engine creation and session dependency
- [x] T010 [P] Write contract test in tests/unit/test_db_session.py for database session creation and cleanup

### Data Models

- [x] T011 [P] Create User model in backend/src/models/user.py with id, email, created_at fields (managed by Better Auth)
- [x] T012 [P] Create Task model in backend/src/models/task.py with id, user_id, title, completed, created_at, updated_at fields
- [x] T013 [P] Create Conversation model in backend/src/models/conversation.py with id, user_id, created_at fields
- [x] T014 [P] Create Message model in backend/src/models/message.py with id, conversation_id, role, content, created_at fields
- [x] T015 [P] Write unit tests in tests/unit/test_models.py for all four models with validation rules

### Database Migrations

- [x] T016 Create initial schema migration in backend/migrations/001_initial_schema.sql with users, conversations, messages, tasks tables
- [x] T017 [P] Add foreign key constraints to migrations (user_id references, conversation_id references with CASCADE DELETE)
- [x] T018 [P] Add indexes to migrations (conversations.user_id, messages.conversation_id+created_at, tasks.user_id+completed)
- [x] T019 [P] Add check constraints to migrations (messages.role IN ('user','assistant'), tasks.title not empty)
- [x] T020 [P] Create migration runner script in backend/migrations/run.py to execute SQL migrations
- [x] T021 [P] Write integration test in tests/integration/test_migrations.py for schema creation and constraint enforcement

### MCP Server Infrastructure

- [x] T022 Create MCP server setup in backend/src/mcp/server.py with stdio transport and tool registry
- [x] T023 [P] Write contract test in tests/contract/test_mcp_server.py for MCP server startup and tool discovery

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Manage Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Enable users to manage their personal todo list by chatting with the system using everyday language

**Independent Test**: User can send natural language messages to add, list, complete, delete, and update tasks, and the system correctly interprets and executes operations without command syntax

### Tests for User Story 1 (TDD - MANDATORY) ⚠️

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T024 [P] [US1] Write contract test in tests/contract/test_add_task.py for add_task MCP tool (input validation, output format, error codes)
- [x] T025 [P] [US1] Write contract test in tests/contract/test_list_tasks.py for list_tasks MCP tool (filter by completed status, output format)
- [x] T026 [P] [US1] Write contract test in tests/contract/test_complete_task.py for complete_task MCP tool (idempotency, error handling)
- [x] T027 [P] [US1] Write contract test in tests/contract/test_delete_task.py for delete_task MCP tool (ownership verification, error handling)
- [x] T028 [P] [US1] Write contract test in tests/contract/test_update_task.py for update_task MCP tool (title validation, ownership verification)
- [x] T029 [P] [US1] Write integration test in tests/integration/test_task_operations.py for complete user journey (create → list → complete → delete)
- [x] T030 [P] [US1] Write integration test in tests/integration/test_natural_language_variations.py for 10+ variations of "create task" intent

### MCP Tool Implementations for User Story 1

- [x] T031 [P] [US1] Implement add_task tool in backend/src/mcp/tools/add_task.py with user_id validation, title validation, database insert
- [x] T032 [P] [US1] Implement list_tasks tool in backend/src/mcp/tools/list_tasks.py with user_id filtering, optional completed filter
- [x] T033 [P] [US1] Implement complete_task tool in backend/src/mcp/tools/complete_task.py with ownership verification, idempotency
- [x] T034 [P] [US1] Implement delete_task tool in backend/src/mcp/tools/delete_task.py with ownership verification, cascade delete
- [x] T035 [P] [US1] Implement update_task tool in backend/src/mcp/tools/update_task.py with title validation, ownership verification
- [x] T036 [US1] Register all 5 MCP tools in backend/src/mcp/server.py tool registry with proper schemas

### Service Layer for User Story 1

- [x] T037 [US1] Implement TaskService in backend/src/services/task_service.py with create, list, complete, delete, update methods (stateless, queries DB directly)
- [x] T038 [P] [US1] Write unit tests in tests/unit/test_task_service.py for TaskService with mocked database

**Checkpoint**: At this point, User Story 1 should be fully functional and independently testable via MCP tools

---

## Phase 4: User Story 2 - Conversation Continuity Across Sessions (Priority: P2)

**Goal**: Users can continue their conversation where they left off, even if the system restarts or they switch devices

**Independent Test**: User creates tasks in a conversation, reconnects with conversation_id, and verifies conversation history and task context are preserved

### Tests for User Story 2 (TDD - MANDATORY) ⚠️

- [x] T039 [P] [US2] Write contract test in tests/contract/test_conversation_create.py for conversation creation (auto-generate conversation_id)
- [x] T040 [P] [US2] Write contract test in tests/contract/test_conversation_retrieve.py for conversation history retrieval by conversation_id
- [x] T041 [P] [US2] Write integration test in tests/integration/test_conversation_continuity.py for persistence across server restart
- [x] T042 [P] [US2] Write integration test in tests/integration/test_conversation_isolation.py for separate conversations (no cross-contamination)

### Database Operations for User Story 2

- [x] T043 [P] [US2] Create ConversationService in backend/src/services/chat_service.py with create_conversation, get_conversation methods
- [x] T044 [P] [US2] Implement message persistence in backend/src/services/chat_service.py with save_message, get_conversation_history methods
- [x] T045 [P] [US2] Write unit tests in tests/unit/test_chat_service.py for ConversationService and MessageService with mocked database

### Chat Endpoint for User Story 2

- [x] T046 [US2] Create chat endpoint in backend/src/api/chat.py with POST /api/v1/chat accepting message and optional conversation_id
- [x] T047 [US2] Implement conversation loading logic in chat endpoint (load history if conversation_id provided, create new if not)
- [x] T048 [US2] Implement message persistence logic in chat endpoint (save both user message and assistant response)
- [x] T049 [US2] Add Better Auth integration to chat endpoint for user_id extraction from JWT
- [x] T050 [P] [US2] Write integration test in tests/integration/test_chat_endpoint.py for full request/response cycle

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Multi-User Task Isolation (Priority: P3)

**Goal**: Multiple users can use the system simultaneously without seeing each other's tasks or conversations

**Independent Test**: Two users create tasks with same titles simultaneously, each user only sees and manages their own tasks with no data leakage

### Tests for User Story 3 (TDD - MANDATORY) ⚠️

- [x] T051 [P] [US3] Write integration test in tests/integration/test_multi_user_isolation.py for concurrent task operations (no cross-user visibility)
- [x] T052 [P] [US3] Write integration test in tests/integration/test_cross_user_access_attempts.py for unauthorized access prevention (404 when user_id mismatch)
- [x] T053 [P] [US3] Write integration test in tests/integration/test_concurrent_users.py for 10+ simultaneous users (no data mixing)

### Multi-Tenancy Enforcement for User Story 3

- [x] T054 [US3] Add user_id verification to all MCP tools (reject operations on resources owned by different user)
- [x] T055 [US3] Add user_id filtering to all database queries in TaskService (WHERE user_id = ? on every query)
- [x] T056 [US3] Add user_id filtering to all database queries in ChatService (WHERE user_id = ? on conversation/message queries)
- [x] T057 [US3] Add ownership check in chat endpoint (verify conversation belongs to user before loading history)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: AI Agent Integration

**Purpose**: Integrate OpenAI Agents SDK to interpret natural language and select appropriate MCP tools

### Tests for Agent Integration (TDD - MANDATORY) ⚠️

- [x] T058 [P] Write contract test in tests/contract/test_agent_intent_recognition.py for intent variations (10+ "create task" phrases)
- [x] T059 [P] Write integration test in tests/integration/test_agent_tool_selection.py for correct tool selection based on user input
- [x] T060 [P] Write integration test in tests/integration/test_agent_tool_invocation.py for end-to-end agent→tool→DB flow

### Agent Implementation

- [x] T061 Create agent configuration in backend/src/agent/agent.py with OpenAI Agents SDK setup and function calling
- [x] T062 [P] Register MCP tools as functions in agent configuration (add_task, list_tasks, complete_task, delete_task, update_task)
- [x] T063 [P] Create system prompt in backend/src/agent/prompts.py with task management instructions and tool descriptions
- [x] T064 Integrate agent invocation into chat endpoint (pass conversation history and new message to agent)
- [x] T065 Handle agent responses in chat endpoint (extract tool calls, invoke MCP tools, generate natural language confirmation)
- [x] T066 [P] Write integration test in tests/integration/test_agent_error_handling.py for graceful error messages when operations fail

---

## Phase 7: API Health Check and Monitoring

**Purpose**: Add health check endpoint and basic monitoring

- [x] T067 [P] Create health endpoint in backend/src/api/health.py with GET /api/v1/health
- [x] T068 [P] Add database connectivity check to health endpoint
- [x] T069 [P] Add MCP server availability check to health endpoint
- [x] T070 [P] Write integration test in tests/integration/test_health_endpoint.py for health status reporting

---

## Phase 8: FastAPI Application Setup

**Purpose**: Wire together all components into a running FastAPI application

- [x] T071 Create FastAPI application entry point in backend/main.py with app initialization
- [x] T072 Register chat and health endpoints in FastAPI app (include routers)
- [x] T073 Add CORS middleware for frontend communication
- [x] T074 Add Better Auth middleware for JWT validation
- [x] T075 [P] Create startup event in FastAPI app for database connection validation
- [x] T076 [P] Create shutdown event in FastAPI app for database connection cleanup
- [x] T077 [P] Write integration test in tests/integration/test_fastapi_app.py for application startup and endpoint registration

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T078 [P] Add structured logging to all MCP tools (operation, user_id, result)
- [ ] T079 [P] Add structured logging to chat endpoint (conversation_id, user_id, message counts)
- [ ] T080 [P] Add error handlers for common exceptions (validation, database, authentication)
- [ ] T081 [P] Add request validation with Pydantic models for chat endpoint
- [ ] T082 [P] Add response validation with Pydantic models for chat endpoint
- [ ] T083 [P] Run all tests with coverage reporting (pytest --cov=src --cov-report=html)
- [ ] T084 [P] Update README.md with API documentation link and setup instructions
- [ ] T085 [P] Create OpenAPI specification documentation in backend/openapi.json
- [ ] T086 Document all 5 MCP tools in backend/docs/mcp-tools.md with examples
- [ ] T087 Create database schema documentation in backend/docs/schema.md
- [ ] T088 Run quickstart.md validation (follow setup steps, verify all commands work)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **AI Agent Integration (Phase 6)**: Depends on User Story 1 (MCP tools) and User Story 2 (chat endpoint)
- **API Setup (Phase 7-8)**: Depends on all user stories complete
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US1 and US2 with multi-user enforcement

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD mandatory)
- Models before services
- Services before endpoints/tools
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- MCP tools within US1 marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write tests first):
Task: "Contract test in tests/contract/test_add_task.py"
Task: "Contract test in tests/contract/test_list_tasks.py"
Task: "Contract test in tests/contract/test_complete_task.py"
Task: "Contract test in tests/contract/test_delete_task.py"
Task: "Contract test in tests/contract/test_update_task.py"
Task: "Integration test in tests/integration/test_task_operations.py"
Task: "Integration test in tests/integration/test_natural_language_variations.py"

# After tests are written and failing, launch all MCP tools in parallel:
Task: "Implement add_task tool in backend/src/mcp/tools/add_task.py"
Task: "Implement list_tasks tool in backend/src/mcp/tools/list_tasks.py"
Task: "Implement complete_task tool in backend/src/mcp/tools/complete_task.py"
Task: "Implement delete_task tool in backend/src/mcp/tools/delete_task.py"
Task: "Implement update_task tool in backend/src/mcp/tools/update_task.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (P1)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**MVP Deliverables**:
- Users can create, list, complete, delete, and update tasks via MCP tools
- Natural language variations understood (10+ intents for "create task")
- All contract tests pass
- All integration tests pass
- Coverage >80% for MCP tools and TaskService

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add AI Agent Integration (Phase 6) → Deploy/Demo
6. Add Polish (Phase 9) → Final release

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (MCP tools + TaskService)
   - Developer B: User Story 2 (ChatService + chat endpoint)
   - Developer C: User Story 3 (Multi-user enforcement)
3. Stories complete and integrate independently
4. Team integrates AI Agent (Phase 6) together
5. Team completes Polish (Phase 9) together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD is NON-NEGOTIABLE**: Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Constitution Compliance**: All tasks maintain stateless architecture, MCP-first design, database as single source of truth
- **Agentic Development**: All implementation via Claude Code, no manual coding
- **Test Categories**:
  - Contract tests: Verify MCP tool interfaces
  - Integration tests: Verify end-to-end flows
  - Unit tests: Verify business logic in isolation
