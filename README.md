# Todo AI Chatbot with Natural Language Interface

A conversational AI chatbot that enables users to manage personal todo lists using natural language, without learning command syntax.

## 🎯 Features

- **Natural Language Interface**: Manage tasks through everyday conversation (no command syntax)
- **Stateless Architecture**: All state persisted to PostgreSQL, enabling horizontal scaling
- **MCP-First Design**: All task operations exposed as Model Context Protocol (MCP) tools
- **Conversation Continuity**: Conversations persist across server restarts
- **Multi-User Support**: Data isolation between concurrent users

## 🏗️ Architecture

```
Frontend (OpenAI ChatKit)
    ↓
FastAPI Backend
    ↓
OpenAI Agents SDK (Natural Language Understanding)
    ↓
MCP Server (Task Operations)
    ↓
Neon PostgreSQL (Tasks, Conversations, Messages)
```

## 📋 Tech Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **AI Framework**: OpenAI SDK with Gemini model
- **MCP**: Official MCP SDK
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Auth**: Better Auth
- **Testing**: pytest (TDD approach)

### Frontend
- **Framework**: React 18.2+ with TypeScript
- **Build Tool**: Vite 5.0
- **UI**: Custom components (CSS Modules)
- **State**: React Context API
- **HTTP**: Axios with retry logic
- **Testing**: React Testing Library + Vitest

## 🚀 Quick Start

### Prerequisites

**Backend:**
- Python 3.11 or higher
- Neon PostgreSQL account
- OpenAI API key

**Frontend:**
- Node.js 18+ and npm/yarn/pnpm

### Backend Setup

1. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -e .
   pip install -e ".[dev]"  # For development
   ```

3. **Configure environment**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Set environment variable for development mode**
   ```bash
   # Add to backend/.env
   ENVIRONMENT=development
   ```

5. **Start the server**
   ```bash
   cd backend
   python main.py
   # Or: uvicorn main:app --reload
   ```

6. **Test the API**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   cd frontend
   cp .env.example .env
   # Edit .env if needed (defaults work for local development)
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open the app**
   Navigate to `http://localhost:3000`

### Full Stack Development

To run both backend and frontend:

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

## 📖 Documentation

### Backend
- [Quickstart Guide](specs/001-todo-ai-chatbot/quickstart.md) - Detailed setup instructions
- [Feature Specification](specs/001-todo-ai-chatbot/spec.md) - Requirements and user stories
- [Implementation Plan](specs/001-todo-ai-chatbot/plan.md) - Architecture and technical decisions
- [Data Model](specs/001-todo-ai-chatbot/data-model.md) - Entity definitions
- [MCP Tools Contract](specs/001-todo-ai-chatbot/contracts/mcp-tools.yaml) - Tool specifications

### Frontend
- [Frontend README](frontend/README.md) - Frontend development guide
- [Frontend Specification](specs/002-frontend-chatkit/spec.md) - Frontend requirements
- [Frontend Tasks](specs/002-frontend-chatkit/tasks.md) - Implementation tasks

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/contract/test_add_task.py
```

## 📝 Development Workflow

This project follows **Test-Driven Development (TDD)**:

1. Write test (must fail)
2. Get user approval
3. Implement code (test passes)
4. Refactor (tests still pass)

## 🏛️ Constitutional Principles

All development adheres to the [project constitution](.specify/memory/constitution.md):

1. **Stateless Architecture** (NON-NEGOTIABLE)
2. **MCP-First Tool Design**
3. **Database as Single Source of Truth**
4. **Test-First Development** (NON-NEGOTIABLE)
5. **Natural Language Interface**
6. **Agentic Development Only**
7. **Conversation Continuity**

## 📄 License

[Specify your license here]

## 🤝 Contributing

[Specify contribution guidelines here]
