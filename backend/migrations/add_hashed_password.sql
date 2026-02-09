-- Migration: Add hashed_password column to todo_users table
-- Date: 2025-02-09
-- Description: Adds password storage for proper authentication

-- Add hashed_password column
ALTER TABLE todo_users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);

-- Add comment
COMMENT ON COLUMN todo_users.hashed_password IS 'Hashed password (bcrypt)';
