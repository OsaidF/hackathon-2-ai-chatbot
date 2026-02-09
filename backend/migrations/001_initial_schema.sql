-- Migration: 001_initial_schema.sql
-- Purpose: Create initial database schema for Todo AI Chatbot
-- Entities: todo_users, todo_conversations, todo_messages, todo_tasks
-- Dependencies: None (initial schema)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Drop existing tables if they exist (for clean re-runs during development)
-- ============================================================================
-- Drop in reverse order of dependencies to avoid foreign key errors
DROP TABLE IF EXISTS todo_messages CASCADE;
DROP TABLE IF EXISTS todo_tasks CASCADE;
DROP TABLE IF EXISTS todo_conversations CASCADE;
DROP TABLE IF EXISTS todo_users CASCADE;

-- ============================================================================
-- Users Table
-- ============================================================================
-- Managed by Better Auth authentication system
-- Never directly accessed by MCP tools (only referenced via user_id)

CREATE TABLE todo_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ============================================================================
-- Conversations Table
-- ============================================================================
-- Represents a series of message exchanges between a user and the AI assistant
-- Enables conversation continuity across requests

CREATE TABLE todo_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Foreign key constraint added separately
    CONSTRAINT fk_todo_conversations_user_id
        FOREIGN KEY (user_id)
        REFERENCES todo_users(id)
        ON DELETE CASCADE
);

-- Index for filtering user's conversations
CREATE INDEX idx_todo_conversations_user_id ON todo_conversations(user_id);

-- ============================================================================
-- Messages Table
-- ============================================================================
-- Stores both user messages and assistant responses for conversation history

CREATE TABLE todo_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (LENGTH(TRIM(content)) > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Foreign key constraint added separately
    CONSTRAINT fk_todo_messages_conversation_id
        FOREIGN KEY (conversation_id)
        REFERENCES todo_conversations(id)
        ON DELETE CASCADE
);

-- Index for loading conversation history chronologically
CREATE INDEX idx_todo_messages_conversation_id_created_at ON todo_messages(conversation_id, created_at ASC);

-- ============================================================================
-- Tasks Table
-- ============================================================================
-- Represents a single todo item managed by users through natural language

CREATE TABLE todo_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    title TEXT NOT NULL CHECK (LENGTH(TRIM(title)) > 0 AND LENGTH(title) <= 500),
    completed BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Foreign key constraint added separately
    CONSTRAINT fk_todo_tasks_user_id
        FOREIGN KEY (user_id)
        REFERENCES todo_users(id)
        ON DELETE CASCADE
);

-- Index for filtering user's tasks
CREATE INDEX idx_todo_tasks_user_id ON todo_tasks(user_id);

-- Composite index for filtering active vs completed tasks
CREATE INDEX idx_todo_tasks_user_id_completed ON todo_tasks(user_id, completed);

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- All tables created with foreign key constraints and indexes
-- Cascade deletes configured for data integrity
