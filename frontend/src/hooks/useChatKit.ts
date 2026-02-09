import { useChatKitContext } from '../contexts/ChatKitContext';

/**
 * Hook to use ChatKit configuration
 * Convenience wrapper around ChatKitContext
 */
export function useChatKit() {
  const chatkit = useChatKitContext();

  return {
    config: chatkit.config,
    isConfigured: chatkit.isConfigured,
  };
}
