import { Message } from './chat';

/**
 * Chat request payload
 */
export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

/**
 * Chat response from backend
 */
export interface ChatResponse {
  conversation_id: string;
  user_message: string;
  assistant_message: string;
  history: Message[];
}

/**
 * API error response
 */
export interface ApiErrorResponse {
  error: string;
  code: string;
  detail?: string;
}
