# Quickstart Guide: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Last Updated**: 2025-01-24
**Audience**: Developers setting up the Todo AI Chatbot for local development

## Overview

This guide will help you set up and run the Todo AI Chatbot locally. The chatbot enables users to manage todo tasks using natural language through a conversational AI interface.

**Architecture Highlights**:
- **Backend**: FastAPI with OpenAI Agents SDK
- **AI Agent**: Interprets natural language and selects appropriate MCP tools
- **MCP Tools**: Stateless task operations (add, list, complete, delete, update)
- **Database**: Neon PostgreSQL (all state persisted, no in-memory storage)
- **Frontend**: OpenAI ChatKit (hosted separately)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python**: 3.11 or higher
- **Git**: For cloning the repository
- **PostgreSQL Client**: For database access (psql or similar)
- **Code Editor**: VS Code recommended

**External Accounts Required**:
- [Neon](https://neon.tech/) account for PostgreSQL database
- [OpenAI](https://openai.com/) account for API access
- [Better Auth](https://www.betterauth.com/) account (or local auth setup)

## Setup Steps

### Step 1: Clone and Navigate to Repository

```bash
# Clone the repository (replace with actual repo URL when available)
git clone <repository-url>
cd Todo-Phase-III

# Switch to the feature branch
git checkout 001-todo-ai-chatbot
```

### Step 2: Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Install dependencies from pyproject.toml
pip install -e .

# Verify installation
pip list | grep -E "fastapi|openai|sqlmodel|mcp"
```

**Expected Packages**:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai` - OpenAI API and Agents SDK
- `sqlmodel` - ORM (SQLAlchemy + Pydantic)
- `psycopg2-binary` - PostgreSQL adapter
- `pydantic` - Data validation
- `pytest` - Testing framework
- `httpx` - Test client

### Step 4: Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@ep-xxx.aws.neon.tech/todo_db?sslmode=require

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxx

# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:8000

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
```

**Environment Variable Details**:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string | `postgresql://user:pass@ep-xxx.aws.neon.tech/dbname?sslmode=require` |
| `OPENAI_API_KEY` | Yes | OpenAI API key for agent access | `sk-proj-...` |
| `BETTER_AUTH_SECRET` | Yes | Secret key for JWT signing | Generate random string |
| `BETTER_AUTH_URL` | Yes | Base URL for auth callbacks | `http://localhost:8000` |
| `HOST` | No | Server host (default: 0.0.0.0) | `0.0.0.0` |
| `PORT` | No | Server port (default: 8000) | `8000` |
| `LOG_LEVEL` | No | Logging level (default: info) | `debug`, `info`, `warning`, `error` |

### Step 5: Set Up Database

#### Option A: Use Neon (Recommended for Development)

```bash
# Install Neon CLI
npm install -g neonctl

# Login to Neon
neonctl auth login

# Create a new Neon project
neonctl projects create --name todo-chatbot

# Get connection string
neonctl connection-string

# Copy the connection string to DATABASE_URL in .env
```

#### Option B: Use Local PostgreSQL (Alternative)

```bash
# Start PostgreSQL service (varies by OS)
# On macOS with Homebrew:
brew services start postgresql

# On Windows: Start PostgreSQL service from Services

# Create database
createdb todo_chatbot

# Update DATABASE_URL in .env:
# DATABASE_URL=postgresql://postgres@localhost:5432/todo_chatbot
```

### Step 6: Run Database Migrations

```bash
# Navigate to backend directory
cd backend

# Run initial schema migration
python -m migrations.migrate

# Verify tables created
python -c "
from sqlmodel import Session, create_engine, select
from src.models import User, Conversation, Message, Task

engine = create_engine(os.getenv('DATABASE_URL'))
print('Database connection successful!')
print('Tables: users, conversations, messages, tasks')
"
```

### Step 7: Start the Backend Server

```bash
# From backend directory
cd backend

# Start FastAPI server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify Server is Running**:

Open your browser to:
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/api/v1/health

### Step 8: Test the Chat Endpoint

#### Using cURL:

```bash
# Start a new conversation
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "message": "Add a task to buy groceries"
  }'

# Expected response:
# {
#   "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
#   "response": "I've created the task 'Buy groceries' for you.",
#   "role": "assistant",
#   "message_id": "223e4567-e89b-12d3-a456-426614174001",
#   "created_at": "2025-01-24T10:30:00Z"
# }

# Continue the conversation
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "message": "Show my tasks",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

#### Using Python:

```python
import requests

# Replace with your actual JWT token
headers = {"Authorization": "Bearer <your-jwt-token>"}

# Start new conversation
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={"message": "Add a task to buy groceries"},
    headers=headers
)
print(response.json())

# Continue conversation
conversation_id = response.json()["conversation_id"]
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "message": "Show my tasks",
        "conversation_id": conversation_id
    },
    headers=headers
)
print(response.json())
```

### Step 9: Run Tests

```bash
# From backend directory
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/integration/test_chat_endpoint.py

# Run with verbose output
pytest -v
```

**Expected Test Results**:
- All tests should pass (TDD approach: tests written before implementation)
- Coverage should be >80% for critical paths
- No warnings or errors

## Development Workflow

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests first** (TDD):
   ```bash
   # Create test file
   touch tests/unit/test_your_feature.py

   # Run tests (should fail)
   pytest tests/unit/test_your_feature.py
   ```

3. **Implement feature**:
   ```bash
   # Write code in src/
   # Run tests again (should pass)
   pytest tests/unit/test_your_feature.py
   ```

4. **Verify with integration tests**:
   ```bash
   pytest tests/integration/
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature"
   git push origin feature/your-feature-name
   ```

### Hot Reload

The server runs with `--reload` flag, so changes to Python files trigger automatic restart:

```bash
# Make a code change
# Save file
# Server automatically restarts
# Test your changes immediately
```

### Viewing Logs

```bash
# Server logs appear in terminal where uvicorn is running
# Example log output:
# INFO:     127.0.0.1:54321 - "POST /api/v1/chat HTTP/1.1" 200 OK
# INFO:     Loaded conversation 550e8400-e29b-41d4-a716-446655440000 (15 messages)
# INFO:     Agent selected tool: add_task
# INFO:     Task created: 123e4567-e89b-12d3-a456-426614174000
```

## Common Issues and Solutions

### Issue 1: Database Connection Error

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
- Verify `DATABASE_URL` is correct in `.env`
- Check Neon database is active (not paused)
- Ensure SSL mode is enabled: `?sslmode=require`
- Test connection: `psql $DATABASE_URL`

### Issue 2: OpenAI API Error

**Error**: `openai.error.AuthenticationError: No API key provided`

**Solutions**:
- Verify `OPENAI_API_KEY` is set in `.env`
- Check API key is valid and active
- Ensure you have API credits available

### Issue 3: Import Errors

**Error**: `ModuleNotFoundError: No module named 'sqlmodel'`

**Solutions**:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -e .`
- Check Python version: `python --version` (must be 3.11+)

### Issue 4: Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solutions**:
- Change port: `uvicorn main:app --port 8001`
- Kill existing process: `lsof -ti:8000 | xargs kill` (macOS/Linux)
- Kill existing process: `netstat -ano | findstr :8000` then `taskkill /PID <pid>` (Windows)

## Next Steps

1. **Explore the API Documentation**: http://localhost:8000/docs
2. **Review the Specification**: [specs/001-todo-ai-chatbot/spec.md](spec.md)
3. **Read the Implementation Plan**: [specs/001-todo-ai-chatbot/plan.md](plan.md)
4. **Understand the Data Model**: [specs/001-todo-ai-chatbot/data-model.md](data-model.md)
5. **Review MCP Tool Contracts**: [specs/001-todo-ai-chatbot/contracts/mcp-tools.yaml](contracts/mcp-tools.yaml)

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │ (OpenAI ChatKit - hosted separately)
│   (Browser)     │
└────────┬────────┘
         │ HTTP POST /api/v1/chat
         ▼
┌─────────────────────────────────┐
│      FastAPI Backend            │
│  ┌───────────────────────────┐  │
│  │   Authentication Layer    │  │ (Better Auth)
│  │   (extract user_id)       │  │
│  └───────────┬───────────────┘  │
│              │                  │
│  ┌───────────▼───────────────┐  │
│  │   Chat Endpoint          │  │
│  │   - Load conversation     │  │
│  │   - Invoke agent          │  │
│  └───────────┬───────────────┘  │
│              │                  │
│  ┌───────────▼───────────────┐  │
│  │   OpenAI Agents SDK       │  │
│  │   - Intent recognition    │  │
│  │   - Tool selection        │  │
│  └───────────┬───────────────┘  │
│              │                  │
│  ┌───────────▼───────────────┐  │
│  │   MCP Server              │  │
│  │   - add_task              │  │
│  │   - list_tasks            │  │
│  │   - complete_task         │  │
│  │   - delete_task           │  │
│  │   - update_task           │  │
│  └───────────┬───────────────┘  │
└──────────────┼──────────────────┘
               │
               ▼
      ┌─────────────────┐
      │  Neon PostgreSQL │
      │  - tasks        │
      │  - conversations │
      │  - messages     │
      └─────────────────┘
```

## Constitution Compliance

This implementation adheres to all constitutional principles:

- ✅ **Stateless Architecture**: No in-memory state, all data in PostgreSQL
- ✅ **MCP-First Design**: All task operations through MCP tools
- ✅ **Database as Single Source of Truth**: No caching layers
- ✅ **Test-First Development**: TDD workflow enforced
- ✅ **Natural Language Interface**: AI agent handles all command interpretation
- ✅ **Agentic Development Only**: Implementation via Claude Code
- ✅ **Conversation Continuity**: Conversations persist via conversation_id

## Getting Help

- **Documentation**: See [specs/001-todo-ai-chatbot/](.) directory
- **Issues**: Report bugs via GitHub Issues
- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)

## License

[Specify your license here]
