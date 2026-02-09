import { useConversationContext } from '../contexts/ConversationContext';

/**
 * Hook to use conversation state
 * Convenience wrapper around ConversationContext
 */
export function useConversation() {
  const conversation = useConversationContext();

  return {
    conversationId: conversation.conversationId,
    messages: conversation.messages,
    isLoading: conversation.isLoading,
    error: conversation.error,
    isInitialized: conversation.isInitialized,
    sendMessage: conversation.sendMessage,
    clearConversation: conversation.clearConversation,
    loadConversation: conversation.loadConversation,
    setError: conversation.setError,
  };
}
