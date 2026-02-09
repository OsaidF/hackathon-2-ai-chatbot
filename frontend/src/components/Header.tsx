import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useConversation } from '../hooks/useConversation';
import TaskManagerModal from './TaskManagerModal';
import styles from './Header.module.css';

interface HeaderProps {
  /**
   * Application title to display in header
   */
  title?: string;
}

/**
 * Header component with logo, user controls, and conversation management.
 *
 * Features:
 * - Displays application title/logo
 * - Dark mode toggle
 * - Manage tasks button (opens task manager modal)
 * - Clear conversation button with confirmation dialog
 * - Logout button
 * - Responsive design for mobile/tablet/desktop
 */
export default function Header({ title = 'Todo AI Chatbot' }: HeaderProps) {
  const { isAuthenticated, logout } = useAuth();
  const { messages, clearConversation } = useConversation();
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [showTaskManager, setShowTaskManager] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Initialize dark mode from localStorage or system preference
  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialDarkMode = savedDarkMode !== null ? savedDarkMode : prefersDark;
    setIsDarkMode(initialDarkMode);
    if (initialDarkMode) {
      document.documentElement.classList.add('dark-mode');
    }
  }, []);

  /**
   * Toggle dark mode
   */
  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    localStorage.setItem('darkMode', String(newDarkMode));
    if (newDarkMode) {
      document.documentElement.classList.add('dark-mode');
    } else {
      document.documentElement.classList.remove('dark-mode');
    }
  };

  /**
   * Handle clear conversation with confirmation
   */
  const handleClearConversation = () => {
    // Only show confirmation if there are messages
    if (messages.length > 0) {
      setShowClearConfirm(true);
    } else {
      clearConversation();
    }
  };

  /**
   * Confirm and clear conversation
   */
  const confirmClearConversation = () => {
    clearConversation();
    setShowClearConfirm(false);
  };

  /**
   * Handle logout and clear conversation state
   */
  const handleLogout = () => {
    // Clear conversation state before logout
    clearConversation();
    // Then logout (clears auth tokens)
    logout();
  };

  return (
    <header className={styles.header}>
      <div className={styles.headerContainer}>
        {/* Logo/Title */}
        <div className={styles.logo}>
          <h1 className={styles.title}>{title}</h1>
        </div>

        {/* User Controls */}
        {isAuthenticated && (
          <div className={styles.controls}>
            {/* Dark Mode Toggle */}
            <button
              type="button"
              onClick={toggleDarkMode}
              className={styles.iconButton}
              aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDarkMode ? (
                // Sun icon for light mode
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M10 2L10 4M10 16L10 18M18 10L16 10M4 10L2 10M15.6569 4.34315L14.2426 5.75736M5.75736 14.2426L4.34315 15.6569M15.6569 15.6569L14.2426 14.2426M5.75736 5.75736L4.34315 4.34315M10 14C12.2091 14 14 12.2091 14 10C14 7.79086 12.2091 6 10 6C7.79086 6 6 7.79086 6 10C6 12.2091 7.79086 14 10 14Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              ) : (
                // Moon icon for dark mode
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M17.293 13.293C17.6047 12.3941 17.7266 11.4393 17.6505 10.4889C17.5744 9.53844 17.3018 8.61379 16.8503 7.77044C16.3987 6.92709 15.7777 6.18333 15.0252 5.58747C14.2727 4.99162 13.4047 4.55623 12.4766 4.30927C11.5486 4.06231 10.5808 4.0095 9.63169 4.15431C8.68256 4.29912 7.77354 4.6383 6.95937 5.15099C6.1452 5.66369 5.44437 6.33833 4.90256 7.13621C4.36075 7.9341 3.99038 8.83778 3.8148 9.78665C4.77049 9.66309 5.74057 9.73523 6.66663 10.00024C7.47514 10.2333 8.22415 10.6383 8.86639 11.1865C9.50862 11.7347 10.0292 12.4132 10.3915 13.1773C10.7538 13.9415 10.9492 14.7739 10.9642 15.618C12.2625 15.4768 13.4655 14.8899 14.3744 13.9556C15.2834 13.0213 15.8369 11.7986 15.9432 10.4969C16.4614 11.4263 16.7482 12.4681 16.7785 13.5341L17.293 13.293Z" fill="currentColor"/>
                </svg>
              )}
            </button>

            {/* Manage Tasks Button */}
            <button
              type="button"
              onClick={() => setShowTaskManager(true)}
              className={styles.iconButton}
              aria-label="Manage tasks"
              title="Manage tasks"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  d="M9 2H4C2.89543 2 2 2.89543 2 4V9M9 2H16C17.1046 2 18 2.89543 18 4V9M9 2V9M18 9V16C18 17.1046 17.1046 18 16 18H11M18 9H11M11 18V9M11 9L9 11M11 9L13 11"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <span className={styles.buttonText}>Tasks</span>
            </button>

            {/* Clear Conversation Button */}
            <button
              type="button"
              onClick={handleClearConversation}
              className={styles.clearButton}
              aria-label="Clear conversation"
              title={messages.length > 0 ? 'Clear conversation history' : 'No messages to clear'}
              disabled={messages.length === 0}
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  d="M4 4H16M4 8H16M4 12H12M4 16H8"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
              <span className={styles.buttonText}>Clear</span>
            </button>

            {/* Logout Button */}
            <button
              type="button"
              onClick={handleLogout}
              className={styles.logoutButton}
              aria-label="Logout"
              title="Logout"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  d="M7 17L2 12M2 12L7 7M2 12H14M14 12C14 13.0609 14.4214 14.0783 15.1716 14.8284C15.9217 15.5786 16.9391 16 18 16"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <span className={styles.buttonText}>Logout</span>
            </button>
          </div>
        )}
      </div>

      {/* Confirmation Dialog */}
      {showClearConfirm && (
        <div className={styles.modalOverlay} onClick={() => setShowClearConfirm(false)}>
          <div
            className={styles.confirmDialog}
            onClick={(e) => e.stopPropagation()}
            role="alertdialog"
            aria-labelledby="clear-confirm-title"
            aria-describedby="clear-confirm-desc"
          >
            <h2 id="clear-confirm-title" className={styles.confirmTitle}>
              Clear Conversation?
            </h2>
            <p id="clear-confirm-desc" className={styles.confirmDesc}>
              This will permanently delete all messages in this conversation. This action cannot be undone.
            </p>
            <div className={styles.confirmActions}>
              <button
                type="button"
                onClick={() => setShowClearConfirm(false)}
                className={styles.cancelButton}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={confirmClearConversation}
                className={styles.confirmButton}
              >
                Clear Conversation
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Task Manager Modal */}
      {showTaskManager && (
        <TaskManagerModal onClose={() => setShowTaskManager(false)} />
      )}
    </header>
  );
}
