import { useEffect, useRef, useState } from 'react';
import { useConversation } from '../hooks/useConversation';
import { useAuth } from '../hooks/useAuth';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import Header from './Header';
import ErrorModal from './ErrorModal';
import styles from './ChatView.module.css';

/**
 * ChatView Component
 * Main chat container with responsive layout
 */
export default function ChatView() {
  const { messages, isLoading, error, sendMessage, setError } = useConversation();
  const { isAuthenticated } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isOnline, setIsOnline] = useState(true);

  // Auto-scroll to latest message when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Network status detection
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Set initial status
    setIsOnline(navigator.onLine);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Handle sending messages
  const handleSendMessage = async (message: string) => {
    if (!isAuthenticated) {
      setError('You must be logged in to send messages');
      return;
    }

    try {
      await sendMessage(message);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Error is already set in ConversationContext
    }
  };

  // Handle retrying failed messages
  const handleRetry = () => {
    // Clear error and let user try again
    setError(null);
  };

  return (
    <div className={styles.chatView}>
      {/* Header */}
      <Header />

      {/* Network Status Indicator */}
      {!isOnline && (
        <div className={styles.networkStatus}>
          <span className={styles.networkStatusText}>
            You are offline. Please check your internet connection.
          </span>
        </div>
      )}

      {/* Error Modal */}
      <ErrorModal
        error={error}
        onDismiss={() => setError(null)}
        onRetry={handleRetry}
        isRetryable={isOnline}
      />

      {/* Chat Container */}
      <div className={styles.chatContainer}>
        {/* Messages Area */}
        <div className={styles.messagesArea}>
          <MessageList messages={messages} isLoading={isLoading} />
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className={styles.inputArea}>
          <MessageInput
            onSend={handleSendMessage}
            disabled={isLoading || !isOnline}
            placeholder={isOnline ? "Type a message to manage your tasks..." : "Offline..."}
          />
        </div>
      </div>
    </div>
  );
}
