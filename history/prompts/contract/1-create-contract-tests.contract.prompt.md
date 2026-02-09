---
id: 1
title: Create Contract Tests for MCP Tools
stage: contract
date: 2026-01-26
surface: agent
model: claude-haiku-4-5-20251001
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: user
command: Create contract tests for all 5 MCP tools
labels: [mcp-tools, contract-tests, tdd, python]
links:
  spec: specs/001-todo-ai-chatbot/contracts/mcp-tools.yaml
  ticket: null
  adr: null
  pr: null
files:
  - backend/tests/contract/test_add_task.py
  - backend/tests/contract/test_list_tasks.py
  - backend/tests/contract/test_complete_task.py
  - backend/tests/contract/test_delete_task.py
  - backend/tests/contract/test_update_task.py
tests:
  - pytest tests/contract/test_add_task.py
  - pytest tests/contract/test_list_tasks.py
  - pytest tests/contract/test_complete_task.py
  - pytest tests/contract/test_delete_task.py
  - pytest tests/contract/test_update_task.py
---

## Prompt

Create contract tests for all 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) in backend/tests/contract/. Each test file should verify:
- Input validation (valid vs invalid parameters)
- Output format matches contract
- Error codes match specification
- Follow TDD: Tests should FAIL before implementation

Create these 5 test files based on the MCP tools contract specification:
1. tests/contract/test_add_task.py
2. tests/contract/test_list_tasks.py
3. tests/contract/test_complete_task.py
4. tests/contract/test_delete_task.py
5. tests/contract/test_update_task.py

Reference specs/001-todo-ai-chatbot/contracts/mcp-tools.yaml for contract details.

## Response snapshot

Created comprehensive contract tests for all 5 MCP tools following TDD principles. Each test file verifies:

**Test Coverage:**
- Input validation (UUID validation, required parameters, min/max length constraints)
- Output format compliance with contract specification
- Error code matching (INVALID_USER_ID, INVALID_TASK_ID, INVALID_TITLE, TASK_NOT_FOUND, DATABASE_ERROR)
- Edge cases and error scenarios

**Key Features:**
- All tests set to FAIL until implementation exists (raises NotImplementedError)
- Mock objects simulate database responses
- Comprehensive parameter validation testing
- Output schema verification for each tool
- Tests verify specific error codes and messages from contract

**Test Files Created:**
- backend/tests/contract/test_add_task.py - 15 test methods
- backend/tests/contract/test_list_tasks.py - 13 test methods
- backend/tests/contract/test_complete_task.py - 17 test methods
- backend/tests/contract/test_delete_task.py - 15 test methods
- backend/tests/contract/test_update_task.py - 17 test methods

**Verification:**
- Tests run successfully with pytest (installed via pip install -e ".[dev]")
- Tests fail as expected due to missing implementation
- Proper mock setup for database interactions

## Outcome

- ✅ Impact: Created comprehensive test suite ensuring MCP tools contract compliance before implementation
- 🧪 Tests: 77 total test methods across 5 files, all failing as expected per TDD
- 📁 Files: 5 contract test files added to backend/tests/contract/
- 🔁 Next prompts: Implementation of MCP tools to make tests pass, integration testing
- 🧠 Reflection: Tests properly mock database interactions and verify exact contract requirements including error codes and output schemas

## Evaluation notes (flywheel)

- Failure modes observed: Tests fail with NotImplementedError as expected, no import errors after fixing module paths
- Graders run and results (PASS/FAIL): All tests PASS in collection but FAIL individual execution as expected
- Prompt variant (if applicable): Standard contract test creation
- Next experiment (smallest change to try): Implement MCP server to pass one failing test at a time