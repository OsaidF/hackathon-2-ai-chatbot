import { useEffect } from 'react';
import styles from './ErrorModal.module.css';

interface ErrorModalProps {
  /**
   * Error message to display
   */
  error: string | null;

  /**
   * Callback to dismiss the error
   */
  onDismiss: () => void;

  /**
   * Optional retry callback
   * If provided, shows a retry button
   */
  onRetry?: () => void;

  /**
   * Whether the error is retryable
   * Shows retry button if true and onRetry is provided
   */
  isRetryable?: boolean;
}

/**
 * Error modal component for displaying error messages with retry option.
 *
 * Features:
 * - Displays error message in a modal overlay
 * - Dismiss button to close the modal
 * - Optional retry button for retryable errors
 * - Auto-focus management for accessibility
 * - Responsive design
 */
export default function ErrorModal({
  error,
  onDismiss,
  onRetry,
  isRetryable = true
}: ErrorModalProps) {
  // Auto-focus the modal when it opens for accessibility
  useEffect(() => {
    if (error) {
      // Prevent scrolling on the body when modal is open
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = '';
      };
    }
  }, [error]);

  if (!error) {
    return null;
  }

  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    }
  };

  return (
    <div
      className={styles.modalOverlay}
      onClick={onDismiss}
      role="dialog"
      aria-modal="true"
      aria-labelledby="error-title"
      aria-describedby="error-message"
    >
      <div
        className={styles.errorDialog}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Error Icon */}
        <div className={styles.errorIcon}>
          <svg
            width="48"
            height="48"
            viewBox="0 0 48 48"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="2" />
            <path
              d="M16 16L32 32M32 16L16 32"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>

        {/* Error Title */}
        <h2 id="error-title" className={styles.errorTitle}>
          Error
        </h2>

        {/* Error Message */}
        <p id="error-message" className={styles.errorMessage}>
          {error}
        </p>

        {/* Action Buttons */}
        <div className={styles.errorActions}>
          {/* Retry Button (if retryable) */}
          {isRetryable && onRetry && (
            <button
              type="button"
              onClick={handleRetry}
              className={styles.retryButton}
            >
              Try Again
            </button>
          )}

          {/* Dismiss Button */}
          <button
            type="button"
            onClick={onDismiss}
            className={styles.dismissButton}
          >
            {isRetryable && onRetry ? 'Cancel' : 'Close'}
          </button>
        </div>
      </div>
    </div>
  );
}
