import { STORAGE_KEYS } from '../utils/constants';

/**
 * Storage service for localStorage operations
 * Provides type-safe wrapper around localStorage with error handling
 */

/**
 * Get item from localStorage
 */
export function getItem<T>(key: string): T | null {
  try {
    const item = window.localStorage.getItem(key);
    if (item === null) {
      return null;
    }
    return JSON.parse(item) as T;
  } catch (error) {
    console.error(`Failed to get item "${key}" from localStorage:`, error);
    return null;
  }
}

/**
 * Set item in localStorage
 */
export function setItem<T>(key: string, value: T): boolean {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error(`Failed to set item "${key}" in localStorage:`, error);
    return false;
  }
}

/**
 * Remove item from localStorage
 */
export function removeItem(key: string): boolean {
  try {
    window.localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error(`Failed to remove item "${key}" from localStorage:`, error);
    return false;
  }
}

/**
 * Clear all items from localStorage
 */
export function clearAll(): boolean {
  try {
    window.localStorage.clear();
    return true;
  } catch (error) {
    console.error('Failed to clear localStorage:', error);
    return false;
  }
}

/**
 * Storage service for conversation management
 */
export const storageService = {
  /**
   * Get conversation ID from storage
   */
  getConversationId(): string | null {
    return getItem<string>(STORAGE_KEYS.CONVERSATION_ID);
  },

  /**
   * Save conversation ID to storage
   */
  setConversationId(conversationId: string): boolean {
    return setItem(STORAGE_KEYS.CONVERSATION_ID, conversationId);
  },

  /**
   * Remove conversation ID from storage
   */
  removeConversationId(): boolean {
    return removeItem(STORAGE_KEYS.CONVERSATION_ID);
  },

  /**
   * Get auth token from storage
   */
  getAuthToken(): string | null {
    return getItem<string>(STORAGE_KEYS.AUTH_TOKEN);
  },

  /**
   * Save auth token to storage
   */
  setAuthToken(token: string): boolean {
    return setItem(STORAGE_KEYS.AUTH_TOKEN, token);
  },

  /**
   * Remove auth token from storage
   */
  removeAuthToken(): boolean {
    return removeItem(STORAGE_KEYS.AUTH_TOKEN);
  },

  /**
   * Clear all app data from storage
   */
  clearAll(): boolean {
    return clearAll();
  },
};
