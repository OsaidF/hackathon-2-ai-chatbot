/**
 * Task Service for Todo AI Chatbot
 * Handles API calls for task management
 */

import { authManager } from './authManager';
import { Task, TaskListResponse, TaskCreateInput, TaskUpdateInput, TaskFilter } from '../types/task';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class TaskService {
  /**
   * Get all tasks for the current user
   */
  async getTasks(filter?: TaskFilter): Promise<Task[]> {
    const token = authManager.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    // We use the chat endpoint to interact with tasks
    // For getting tasks, we send a "show my tasks" message
    const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        message: filter === 'completed' ? 'Show me completed tasks' :
                 filter === 'uncompleted' ? 'Show me uncompleted tasks' :
                 'Show me all tasks',
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to get tasks: ${response.statusText}`);
    }

    // The chat endpoint returns a response with message text
    // We need to parse the task list from the response
    const data = await response.json();

    // Since we're using natural language interface, we'll need to parse
    // the response or add a dedicated endpoint
    // For now, return empty array - this will need a dedicated API endpoint
    return [];
  }

  /**
   * Create a new task
   */
  async createTask(input: TaskCreateInput): Promise<Task> {
    const token = authManager.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const message = this.buildCreateTaskMessage(input);

    const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create task: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  }

  /**
   * Update a task
   */
  async updateTask(taskId: string, input: TaskUpdateInput): Promise<Task> {
    const token = authManager.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const message = this.buildUpdateTaskMessage(taskId, input);

    const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Failed to update task: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  }

  /**
   * Delete a task
   */
  async deleteTask(taskId: string): Promise<void> {
    const token = authManager.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const message = `Delete task ${taskId}`;

    const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Failed to delete task: ${response.statusText}`);
    }
  }

  /**
   * Build a natural language message for creating a task
   */
  private buildCreateTaskMessage(input: TaskCreateInput): string {
    let message = `Add a task: ${input.title}`;

    if (input.priority && input.priority !== 'medium') {
      message += ` with ${input.priority} priority`;
    }

    if (input.due_date) {
      const date = new Date(input.due_date);
      message += ` due by ${date.toLocaleDateString()}`;
    }

    if (input.tags) {
      message += ` tagged as ${input.tags}`;
    }

    return message;
  }

  /**
   * Build a natural language message for updating a task
   */
  private buildUpdateTaskMessage(taskId: string, input: TaskUpdateInput): string {
    let message = `Update task ${taskId}:`;

    if (input.title !== undefined) {
      message += ` change title to "${input.title}"`;
    }

    if (input.completed !== undefined) {
      message += input.completed ? ' mark as completed' : ' mark as uncompleted';
    }

    if (input.priority) {
      message += ` set priority to ${input.priority}`;
    }

    if (input.due_date) {
      const date = new Date(input.due_date);
      message += ` set due date to ${date.toISOString()}`;
    }

    if (input.tags !== undefined) {
      message += input.tags ? ` set tags to ${input.tags}` : ' clear tags';
    }

    return message;
  }
}

export const taskService = new TaskService();
