/**
 * Format task mentions in messages
 * Detects task-like patterns and formats them with checkboxes
 */
export function formatTaskMentions(text: string): string {
  // Pattern for completed tasks: ✅ task name or [x] task name
  const completedTaskPattern = /(\u2705|\[x\]|\[X\])\s+(.*?)(?=\n|$)/g;

  // Pattern for active tasks: ⬜ task name or [ ] task name
  const activeTaskPattern = /(\u25DC|\[\])\s+(.*?)(?=\n|$)/g;

  // Format completed tasks
  let formatted = text.replace(
    completedTaskPattern,
    '<span class="task-completed">✅ $2</span>'
  );

  // Format active tasks
  formatted = formatted.replace(
    activeTaskPattern,
    '<span class="task-active">⬜ $2</span>'
  );

  return formatted;
}

/**
 * Format message content with task highlighting
 */
export function formatMessageContent(content: string): string {
  // Escape HTML first to prevent XSS
  let escaped = escapeHtml(content);

  // Then format task mentions
  return formatTaskMentions(escaped);
}

/**
 * Escape HTML special characters
 */
export function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}

/**
 * Format timestamp
 */
export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) {
    return 'Just now';
  } else if (diffMins < 60) {
    return `${diffMins}m ago`;
  } else if (diffMins < 1440) {
    const hours = Math.floor(diffMins / 60);
    return `${hours}h ago`;
  } else if (diffMins < 10080) {
    const days = Math.floor(diffMins / 1440);
    return `${days}d ago`;
  } else {
    return date.toLocaleDateString();
  }
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - 3) + '...';
}

/**
 * Strip markdown formatting for plain text display
 */
export function stripMarkdown(text: string): string {
  return text
    .replace(/#{1,6}\s/g, '') // Headers
    .replace(/\*\*(.*?)\*\*/g, '$1') // Bold
    .replace(/\*(.*?)\*/g, '$1') // Italic
    .replace(/`(.*?)`/g, '$1') // Inline code
    .replace(/\n/g, ' '); // Newlines
}
