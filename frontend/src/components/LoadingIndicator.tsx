import styles from './LoadingIndicator.module.css';

interface LoadingIndicatorProps {
  /**
   * Size of the loading indicator
   * @default 'medium'
   */
  size?: 'small' | 'medium' | 'large';

  /**
   * Optional message to display below the spinner
   */
  message?: string;
}

/**
 * Loading indicator component with spinner and optional message.
 *
 * Features:
 * - Animated spinner
 * - Optional loading message
 * - Multiple size variants
 * - Accessible with proper ARIA attributes
 */
export default function LoadingIndicator({ size = 'medium', message }: LoadingIndicatorProps) {
  return (
    <div className={styles.loadingContainer}>
      <div className={`${styles.spinner} ${styles[size]}`} role="status" aria-live="polite">
        <svg
          className={styles.spinnerSvg}
          viewBox="0 0 50 50"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <circle
            className={styles.spinnerCircle}
            cx="25"
            cy="25"
            r="20"
            fill="none"
            strokeWidth="5"
          />
        </svg>
      </div>
      {message && <p className={styles.loadingMessage}>{message}</p>}
      <span className={styles.visuallyHidden}>Loading...</span>
    </div>
  );
}
