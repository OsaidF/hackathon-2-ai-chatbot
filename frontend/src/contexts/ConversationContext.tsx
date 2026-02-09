import React, { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { Message, ConversationState } from '../types/chat';
import { apiClient } from '../services/apiClient';
import { storageService } from '../services/storage';
import { v4 as uuidv4 } from 'uuid';

/**
 * Conversation context interface
 */
interface ConversationContextType extends ConversationState {
  sendMessage: (message: string) => Promise<void>;
  clearConversation: () => void;
  loadConversation: (conversationId: string) => Promise<void>;
  setError: (error: string | null) => void;
}

// Create context with undefined default value
const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

/**
 * Conversation Provider Props
 */
interface ConversationProviderProps {
  children: ReactNode;
}

/**
 * Conversation Provider Component
 */
export function ConversationProvider({ children }: ConversationProviderProps) {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Load conversation ID from storage on mount
  useEffect(() => {
    const loadStoredConversation = () => {
      try {
        const storedId = storageService.getConversationId();
        if (storedId) {
          setConversationId(storedId);
          console.log('Loaded conversation ID from storage:', storedId);
          // Note: History will be loaded when user sends their first message
          // This is because the chat endpoint requires a message to process
        }
      } catch (error) {
        console.error('Failed to load conversation from storage:', error);
      } finally {
        setIsInitialized(true);
      }
    };

    loadStoredConversation();
  }, []);

  /**
   * Send message to backend
   */
  const sendMessage = useCallback(async (message: string): Promise<void> => {
    if (isLoading) {
      console.warn('Already sending a message, ignoring');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Optimistic UI: Add user message immediately
      const userMessage: Message = {
        id: uuidv4(),
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
      };

      setMessages(prev => [...prev, userMessage]);

      // Send to backend
      const response = await apiClient.sendMessage(message, conversationId || undefined);

      // Update conversation ID
      if (response.conversation_id && response.conversation_id !== conversationId) {
        setConversationId(response.conversation_id);
        storageService.setConversationId(response.conversation_id);
      }

      // Update messages with full history from backend
      setMessages(response.history || []);
    } catch (error) {
      console.error('Failed to send message:', error);

      // Rollback optimistic update on error
      setMessages(prev => prev.filter(msg => msg.role !== 'user' || msg.content !== message));

      // Set error message
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, isLoading]);

  /**
   * Clear conversation and start fresh
   */
  const clearConversation = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setError(null);
    storageService.removeConversationId();
  }, []);

  /**
   * Load conversation by ID
   */
  const loadConversation = useCallback(async (id: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // TODO: Implement loading conversation history from backend
      setConversationId(id);
      storageService.setConversationId(id);
      console.log('Loading conversation:', id);
    } catch (error) {
      console.error('Failed to load conversation:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to load conversation';
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const value: ConversationContextType = {
    conversationId,
    messages,
    isLoading,
    error,
    isInitialized,
    sendMessage,
    clearConversation,
    loadConversation,
    setError,
  };

  return <ConversationContext.Provider value={value}>{children}</ConversationContext.Provider>;
}

/**
 * Hook to use conversation context
 */
export function useConversationContext(): ConversationContextType {
  const context = useContext(ConversationContext);

  if (context === undefined) {
    throw new Error('useConversationContext must be used within a ConversationProvider');
  }

  return context;
}
