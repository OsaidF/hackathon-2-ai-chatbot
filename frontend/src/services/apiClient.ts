import { ChatRequest, ChatResponse, ApiErrorResponse } from '../types/api';
import { ApiError } from '../types/errors';
import { CHAT_ENDPOINT, MAX_RETRY_ATTEMPTS, RETRY_DELAYS } from '../utils/constants';
import { authManager } from './authManager';

/**
 * API Client Service
 * Handles HTTP requests with retry logic, error handling, and authentication
 */

/**
 * Delay function for retry backoff
 */
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * API Client class
 */
class ApiClient {
  private baseUrl: string;

  constructor() {
    // Extract base URL from chat endpoint
    this.baseUrl = CHAT_ENDPOINT.replace('/api/v1/chat', '');
  }

  /**
   * Get auth headers
   */
  private getAuthHeaders(): Record<string, string> {
    const token = authManager.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  /**
   * Send chat message with retry logic
   */
  async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    return this.withRetry(async () => {
      const response = await fetch(CHAT_ENDPOINT, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
        } as ChatRequest),
      });

      if (!response.ok) {
        const errorData: ApiErrorResponse = await response.json().catch(() => ({
          error: 'Unknown error',
          code: 'UNKNOWN_ERROR',
        }));

        throw new ApiError(response.status, errorData);
      }

      return response.json() as Promise<ChatResponse>;
    });
  }

  /**
   * Generic request with exponential backoff retry logic
   */
  private async withRetry<T>(
    fn: () => Promise<T>,
    maxAttempts: number = MAX_RETRY_ATTEMPTS
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;

        // If this is the last attempt, throw the error
        if (attempt === maxAttempts) {
          throw error;
        }

        // Calculate delay for this attempt (exponential backoff)
        const delayMs = RETRY_DELAYS[attempt - 1] || RETRY_DELAYS[RETRY_DELAYS.length - 1];

        console.warn(`Request failed (attempt ${attempt}/${maxAttempts}), retrying in ${delayMs}ms...`);

        // Wait before retrying
        await delay(delayMs);
      }
    }

    // Should never reach here, but TypeScript needs it
    throw lastError || new Error('Retry failed');
  }

  /**
   * Check if network is available
   */
  isNetworkAvailable(): boolean {
    return navigator.onLine;
  }

  /**
   * Get current network status
   */
  getNetworkStatus(): 'online' | 'offline' {
    return navigator.onLine ? 'online' : 'offline';
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
