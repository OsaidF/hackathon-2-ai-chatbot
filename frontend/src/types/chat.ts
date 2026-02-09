/**
 * Message role types
 */
export type MessageRole = 'user' | 'assistant';

/**
 * Chat message interface
 */
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  created_at: string;
}

/**
 * Conversation state interface
 */
export interface Conversation {
  id: string;
  user_id: string;
  created_at: string;
  messages?: Message[];
}

/**
 * Conversation state for context provider
 */
export interface ConversationState {
  conversationId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  isInitialized: boolean;
}
