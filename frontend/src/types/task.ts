/**
 * Task types for Todo AI Chatbot
 */

export interface Task {
  task_id: string;
  title: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  due_date: string | null;
  tags: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskListResponse {
  tasks: Task[];
  count: number;
}

export interface TaskCreateInput {
  title: string;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
  tags?: string;
}

export interface TaskUpdateInput {
  title?: string;
  completed?: boolean;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
  tags?: string;
}

export type TaskFilter = 'all' | 'completed' | 'uncompleted';
