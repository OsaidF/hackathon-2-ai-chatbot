-- Migration: Add priority, due_date, and tags to todo_tasks table
-- Date: 2025-02-09
-- Description: Adds task priority, due dates, and tags/categories

-- Add priority column
ALTER TABLE todo_tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium';

-- Add due date column
ALTER TABLE todo_tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP;

-- Add tags column
ALTER TABLE todo_tasks ADD COLUMN IF NOT EXISTS tags VARCHAR(500);

-- Add indexes for new fields
CREATE INDEX IF NOT EXISTS idx_todo_tasks_priority ON todo_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_todo_tasks_due_date ON todo_tasks(due_date);

-- Add comments
COMMENT ON COLUMN todo_tasks.priority IS 'Task priority level (low, medium, high)';
COMMENT ON COLUMN todo_tasks.due_date IS 'Task due date (optional)';
COMMENT ON COLUMN todo_tasks.tags IS 'Task tags/categories (comma-separated)';
