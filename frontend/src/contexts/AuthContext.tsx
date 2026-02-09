import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authManager } from '../services/authManager';

/**
 * User interface
 */
interface User {
  id: string;
  token: string;
}

/**
 * Auth context interface
 */
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, userId: string) => Promise<void>;
  logout: () => void;
}

// Create context with undefined default value
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Auth Provider Props
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Auth Provider Component
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load token from storage on mount
  useEffect(() => {
    const loadAuth = () => {
      try {
        const token = authManager.getToken();
        const userId = authManager.getUserId();

        if (token && userId) {
          setUser({ id: userId, token });
        }
      } catch (error) {
        console.error('Failed to load auth state:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadAuth();
  }, []);

  /**
   * Login with token and user ID
   */
  const login = async (token: string, userId: string): Promise<void> => {
    try {
      authManager.setToken(token);
      authManager.setUserId(userId);
      setUser({ id: userId, token });
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  /**
   * Logout and clear auth state
   */
  const logout = () => {
    try {
      authManager.clearToken();
      authManager.clearUserId();
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use auth context
 */
export function useAuthContext(): AuthContextType {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }

  return context;
}
