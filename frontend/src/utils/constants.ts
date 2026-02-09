/**
 * Application configuration constants
 */

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const CHAT_ENDPOINT = `${API_BASE_URL}/api/v1/chat`;

// Message Limits
export const MAX_MESSAGE_LENGTH = 10000;
export const MIN_MESSAGE_LENGTH = 1;

// Retry Configuration
export const MAX_RETRY_ATTEMPTS = 3;
export const RETRY_DELAYS = [1000, 2000, 4000]; // Exponential backoff: 1s, 2s, 4s

// Storage Keys
export const STORAGE_KEYS = {
  CONVERSATION_ID: 'todo_chatbot_conversation_id',
  AUTH_TOKEN: 'todo_chatbot_auth_token',
} as const;

// ChatKit Configuration
export const CHATKIT_CONFIG = {
  domainKey: import.meta.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || '',
} as const;

// UI Configuration
export const UI_CONFIG = {
  MAX_VISIBLE_MESSAGES: 100,
  AUTO_SCROLL_DELAY: 100,
  DEBOUNCE_DELAY: 300,
} as const;

// Development Mode
export const isDevMode = import.meta.env.VITE_DEV_MODE === 'true';
