import MessageItem from './MessageItem';
import { Message } from '../types/chat';
import styles from './MessageList.module.css';

/**
 * MessageList Props
 */
interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

/**
 * MessageList Component
 * Scrollable display of chat messages
 */
export default function MessageList({ messages, isLoading }: MessageListProps) {
  if (messages.length === 0 && !isLoading) {
    return (
      <div className={styles.emptyState}>
        <p className={styles.emptyText}>
          Start managing your tasks with natural language!
        </p>
        <p className={styles.emptyHint}>
          Try: "Add task buy groceries" or "Show my tasks"
        </p>
      </div>
    );
  }

  return (
    <div className={styles.messageList}>
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}

      {isLoading && (
        <div className={styles.loadingState}>
          <div className={styles.loadingIndicator} />
          <span className={styles.loadingText}>AI is thinking...</span>
        </div>
      )}
    </div>
  );
}
