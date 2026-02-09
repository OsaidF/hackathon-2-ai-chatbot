import { useState, FormEvent, KeyboardEvent } from 'react';
import { MAX_MESSAGE_LENGTH } from '../utils/constants';
import { getRemainingChars, validateMessage } from '../utils/validation';
import styles from './MessageInput.module.css';

/**
 * MessageInput Props
 */
interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

/**
 * MessageInput Component
 * Text input with validation and keyboard shortcuts
 */
export default function MessageInput({ onSend, disabled = false, placeholder = 'Type a message...' }: MessageInputProps) {
  const [message, setMessage] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  /**
   * Handle form submission
   */
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Validate message
    const validation = validateMessage(message);
    if (!validation.isValid) {
      setValidationError(validation.error || 'Invalid message');
      return;
    }

    // Clear validation error
    setValidationError(null);

    // Send message
    onSend(message);

    // Clear input
    setMessage('');
  };

  /**
   * Handle keyboard shortcuts
   * Enter to send, Shift+Enter for new line
   */
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      // Trigger form submission
      const form = e.currentTarget.closest('form');
      if (form) {
        form.requestSubmit();
      }
    }
  };

  /**
   * Handle input change
   */
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;

    // Enforce max length
    if (value.length <= MAX_MESSAGE_LENGTH) {
      setMessage(value);

      // Clear validation error if user is typing
      if (validationError && value.trim().length > 0) {
        setValidationError(null);
      }
    }
  };

  const remainingChars = getRemainingChars(message);
  const isNearLimit = remainingChars < 100;
  const isAtLimit = remainingChars === 0;

  return (
    <form className={styles.messageInputForm} onSubmit={handleSubmit}>
      <div className={`${styles.inputContainer} ${validationError ? styles.inputError : ''}`}>
        <textarea
          className={styles.messageTextarea}
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          aria-label="Message input"
          aria-invalid={!!validationError}
          aria-describedby={validationError ? 'error-message' : 'char-count'}
        />

        <div className={styles.inputActions}>
          {/* Character count */}
          <span
            id="char-count"
            className={`${styles.charCount} ${isNearLimit ? styles.charCountWarning : ''} ${isAtLimit ? styles.charCountLimit : ''}`}
          >
            {remainingChars}
          </span>

          {/* Send button */}
          <button
            type="submit"
            className={styles.sendButton}
            disabled={disabled || !message.trim()}
            aria-label="Send message"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 6 11 2 2"></polygon>
            </svg>
          </button>
        </div>
      </div>

      {/* Validation error */}
      {validationError && (
        <div id="error-message" className={styles.errorMessage} role="alert">
          {validationError}
        </div>
      )}

      {/* Keyboard hint */}
      {!validationError && (
        <div className={styles.keyboardHint}>
          Press <kbd>Enter</kbd> to send, <kbd>Shift + Enter</kbd> for new line
        </div>
      )}
    </form>
  );
}
