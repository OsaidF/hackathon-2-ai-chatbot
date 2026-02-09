import React, { createContext, useContext, ReactNode } from 'react';

/**
 * ChatKit configuration interface
 */
interface ChatKitConfig {
  domainKey: string;
  apiUrl: string;
}

/**
 * ChatKit context interface
 */
interface ChatKitContextType {
  config: ChatKitConfig;
  isConfigured: boolean;
}

// Default configuration
const defaultConfig: ChatKitConfig = {
  domainKey: '',
  apiUrl: '',
};

// Create context with default value
const ChatKitContext = createContext<ChatKitContextType>({
  config: defaultConfig,
  isConfigured: false,
});

/**
 * ChatKit Provider Props
 */
interface ChatKitProviderProps {
  children: ReactNode;
  domainKey?: string;
  apiUrl?: string;
}

/**
 * ChatKit Provider Component
 * Wraps ChatKit SDK configuration
 */
export function ChatKitProvider({
  children,
  domainKey = '',
  apiUrl = '',
}: ChatKitProviderProps) {
  const config: ChatKitConfig = {
    domainKey: domainKey || import.meta.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || '',
    apiUrl: apiUrl || import.meta.env.VITE_API_BASE_URL || '',
  };

  const isConfigured = !!(config.domainKey && config.apiUrl);

  const value: ChatKitContextType = {
    config,
    isConfigured,
  };

  return <ChatKitContext.Provider value={value}>{children}</ChatKitContext.Provider>;
}

/**
 * Hook to use ChatKit context
 */
export function useChatKitContext(): ChatKitContextType {
  const context = useContext(ChatKitContext);

  if (context === undefined) {
    throw new Error('useChatKitContext must be used within a ChatKitProvider');
  }

  return context;
}

/**
 * Hook to use ChatKit (alias for convenience)
 */
export function useChatKit(): ChatKitContextType {
  return useChatKitContext();
}
