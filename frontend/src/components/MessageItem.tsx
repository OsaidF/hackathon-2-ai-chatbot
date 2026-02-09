import { Message } from '../types/chat';
import { formatTimestamp } from '../utils/formatting';
import styles from './MessageItem.module.css';

/**
 * MessageItem Props
 */
interface MessageItemProps {
  message: Message;
}

/**
 * MessageItem Component
 * Displays individual message with role-based styling
 */
export default function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <div
      className={`${styles.messageItem} ${isUser ? styles.userMessage : styles.assistantMessage}`}
    >
      {/* Message Bubble */}
      <div className={styles.messageBubble}>
        {/* Message Content */}
        <div className={styles.messageContent}>
          {message.content.split('\n').map((line, index) => (
            <p key={index} className={styles.messageLine}>
              {line}
            </p>
          ))}
        </div>

        {/* Timestamp */}
        <div className={styles.messageMeta}>
          <time className={styles.timestamp} dateTime={message.created_at}>
            {formatTimestamp(message.created_at)}
          </time>
        </div>
      </div>
    </div>
  );
}
