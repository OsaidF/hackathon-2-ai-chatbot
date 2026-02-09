import { useAuthContext } from '../contexts/AuthContext';

/**
 * Hook to use authentication state
 * Convenience wrapper around AuthContext
 */
export function useAuth() {
  const auth = useAuthContext();

  return {
    user: auth.user,
    isAuthenticated: auth.isAuthenticated,
    isLoading: auth.isLoading,
    login: auth.login,
    logout: auth.logout,
  };
}
