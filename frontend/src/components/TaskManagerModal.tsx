import { useState, useEffect } from 'react';
import { Task, TaskUpdateInput, TaskFilter } from '../types/task';
import { authManager } from '../services/authManager';
import styles from './TaskManagerModal.module.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

interface TaskManagerModalProps {
  onClose: () => void;
}

/**
 * TaskManagerModal Component
 * Modal for managing all tasks with inline editing
 */
export default function TaskManagerModal({ onClose }: TaskManagerModalProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState<TaskFilter>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<TaskUpdateInput>({});

  useEffect(() => {
    loadTasks();
  }, [filter]);

  const loadTasks = async () => {
    setIsLoading(true);
    try {
      const token = authManager.getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      // Build query params for filter
      const params = new URLSearchParams();
      if (filter === 'completed') {
        params.append('filter_completed', 'true');
      } else if (filter === 'uncompleted') {
        params.append('filter_completed', 'false');
      }

      const queryString = params.toString();
      const url = `${API_BASE_URL}/api/v1/tasks${queryString ? `?${queryString}` : ''}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to load tasks: ${response.statusText}`);
      }

      const data = await response.json();

      // Transform the response to match our Task interface
      const transformedTasks: Task[] = data.tasks.map((task: any) => ({
        task_id: task.id,
        title: task.title,
        completed: task.completed,
        priority: task.priority,
        due_date: task.due_date,
        tags: task.tags,
        created_at: task.created_at,
        updated_at: task.updated_at,
      }));

      setTasks(transformedTasks);
    } catch (error) {
      console.error('Failed to load tasks:', error);
      setTasks([]);
    } finally {
      setIsLoading(false);
    }
  };

  const startEdit = (task: Task) => {
    setEditingTaskId(task.task_id);
    setEditForm({
      title: task.title,
      completed: task.completed,
      priority: task.priority,
      due_date: task.due_date || undefined,
      tags: task.tags || undefined,
    });
  };

  const cancelEdit = () => {
    setEditingTaskId(null);
    setEditForm({});
  };

  const saveEdit = async (taskId: string) => {
    try {
      // Send update via chat interface
      await saveTaskViaChat(taskId, editForm);
      await loadTasks();
      cancelEdit();
    } catch (error) {
      console.error('Failed to update task:', error);
      alert('Failed to update task. Please try again.');
    }
  };

  const deleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      // Send delete via chat interface
      await deleteTaskViaChat(taskId);
      await loadTasks();
    } catch (error) {
      console.error('Failed to delete task:', error);
      alert('Failed to delete task. Please try again.');
    }
  };

  const toggleComplete = async (task: Task) => {
    try {
      const newStatus = !task.completed;
      await saveTaskViaChat(task.task_id, { completed: newStatus });
      await loadTasks();
    } catch (error) {
      console.error('Failed to toggle task completion:', error);
    }
  };

  const saveTaskViaChat = async (taskId: string, updates: TaskUpdateInput) => {
    const token = authManager.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    // Build update body with only provided fields
    const body: any = {};
    if (updates.title !== undefined) body.title = updates.title;
    if (updates.completed !== undefined) body.completed = updates.completed;
    if (updates.priority !== undefined) body.priority = updates.priority;
    if (updates.due_date !== undefined) body.due_date = updates.due_date;
    if (updates.tags !== undefined) body.tags = updates.tags;

    const response = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Failed to update task: ${response.statusText}`);
    }
  };

  const deleteTaskViaChat = async (taskId: string) => {
    const token = authManager.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to delete task: ${response.statusText}`);
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'completed') return task.completed;
    if (filter === 'uncompleted') return !task.completed;
    return true;
  });

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Manage Tasks</h2>
          <button
            type="button"
            onClick={onClose}
            className={styles.closeButton}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Filter Controls */}
        <div className={styles.filterControls}>
          <span className={styles.filterLabel}>Filter:</span>
          <button
            type="button"
            className={`${styles.filterButton} ${filter === 'all' ? styles.active : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            type="button"
            className={`${styles.filterButton} ${filter === 'uncompleted' ? styles.active : ''}`}
            onClick={() => setFilter('uncompleted')}
          >
            Active
          </button>
          <button
            type="button"
            className={`${styles.filterButton} ${filter === 'completed' ? styles.active : ''}`}
            onClick={() => setFilter('completed')}
          >
            Completed
          </button>
        </div>

        {/* Task List */}
        <div className={styles.taskList}>
          {isLoading ? (
            <div className={styles.loading}>Loading tasks...</div>
          ) : filteredTasks.length === 0 ? (
            <div className={styles.emptyState}>
              <p>No tasks found. Use the chat to create tasks!</p>
            </div>
          ) : (
            filteredTasks.map(task => (
              <div
                key={task.task_id}
                className={`${styles.taskItem} ${task.completed ? styles.completed : ''}`}
              >
                {editingTaskId === task.task_id ? (
                  // Edit Mode
                  <div className={styles.editForm}>
                    <input
                      type="text"
                      value={editForm.title || ''}
                      onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                      className={styles.titleInput}
                      placeholder="Task title"
                    />

                    <div className={styles.editFields}>
                      <select
                        value={editForm.priority || 'medium'}
                        onChange={(e) => setEditForm({
                          ...editForm,
                          priority: e.target.value as 'low' | 'medium' | 'high'
                        })}
                        className={styles.selectInput}
                      >
                        <option value="low">Low Priority</option>
                        <option value="medium">Medium Priority</option>
                        <option value="high">High Priority</option>
                      </select>

                      <input
                        type="date"
                        value={editForm.due_date ? editForm.due_date.split('T')[0] : ''}
                        onChange={(e) => setEditForm({ ...editForm, due_date: e.target.value || undefined })}
                        className={styles.dateInput}
                      />

                      <input
                        type="text"
                        value={editForm.tags || ''}
                        onChange={(e) => setEditForm({ ...editForm, tags: e.target.value || undefined })}
                        className={styles.tagsInput}
                        placeholder="Tags (comma-separated)"
                      />
                    </div>

                    <div className={styles.editActions}>
                      <button
                        type="button"
                        onClick={cancelEdit}
                        className={styles.cancelButton}
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        onClick={() => saveEdit(task.task_id)}
                        className={styles.saveButton}
                      >
                        Save
                      </button>
                    </div>
                  </div>
                ) : (
                  // View Mode
                  <>
                    <div className={styles.taskMain}>
                      <button
                        type="button"
                        onClick={() => toggleComplete(task)}
                        className={styles.checkbox}
                        aria-label={task.completed ? 'Mark as uncompleted' : 'Mark as completed'}
                      >
                        {task.completed ? '✓' : '○'}
                      </button>

                      <div className={styles.taskContent}>
                        <h3 className={styles.taskTitle}>{task.title}</h3>

                        <div className={styles.taskMeta}>
                          {task.priority !== 'medium' && (
                            <span className={`${styles.priority} ${styles[task.priority]}`}>
                              {task.priority}
                            </span>
                          )}

                          {task.due_date && (
                            <span className={styles.dueDate}>
                              Due: {new Date(task.due_date).toLocaleDateString()}
                            </span>
                          )}

                          {task.tags && (
                            <span className={styles.tags}>
                              {task.tags.split(',').map((tag, i) => (
                                <span key={i} className={styles.tag}>
                                  {tag.trim()}
                                </span>
                              ))}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className={styles.taskActions}>
                      <button
                        type="button"
                        onClick={() => startEdit(task)}
                        className={styles.editButton}
                        aria-label="Edit task"
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => deleteTask(task.task_id)}
                        className={styles.deleteButton}
                        aria-label="Delete task"
                      >
                        Delete
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
