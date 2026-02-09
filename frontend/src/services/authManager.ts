import { storageService } from './storage';
import { STORAGE_KEYS } from '../utils/constants';

/**
 * Auth Manager Service
 * Handles JWT token and user ID management
 */
export const authManager = {
  /**
   * Get authentication token
   */
  getToken(): string | null {
    return storageService.getAuthToken();
  },

  /**
   * Set authentication token
   */
  setToken(token: string): boolean {
    return storageService.setAuthToken(token);
  },

  /**
   * Clear authentication token
   */
  clearToken(): boolean {
    return storageService.removeAuthToken();
  },

  /**
   * Get user ID from storage
   */
  getUserId(): string | null {
    try {
      const userStr = window.localStorage.getItem('todo_chatbot_user_id');
      return userStr || null;
    } catch (error) {
      console.error('Failed to get user ID:', error);
      return null;
    }
  },

  /**
   * Set user ID
   */
  setUserId(userId: string): boolean {
    try {
      window.localStorage.setItem('todo_chatbot_user_id', userId);
      return true;
    } catch (error) {
      console.error('Failed to set user ID:', error);
      return false;
    }
  },

  /**
   * Clear user ID
   */
  clearUserId(): boolean {
    try {
      window.localStorage.removeItem('todo_chatbot_user_id');
      return true;
    } catch (error) {
      console.error('Failed to clear user ID:', error);
      return false;
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = this.getToken();
    const userId = this.getUserId();
    return !!(token && userId);
  },

  /**
   * Clear all auth data
   */
  clearAll(): boolean {
    this.clearToken();
    this.clearUserId();
    return true;
  },
};
