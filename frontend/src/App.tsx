import { AuthProvider, useAuthContext } from './contexts/AuthContext';
import { ChatKitProvider } from './contexts/ChatKitContext';
import { ConversationProvider } from './contexts/ConversationContext';
import ChatView from './components/ChatView';
import LoginPage from './components/LoginPage';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingIndicator from './components/LoadingIndicator';
import './App.module.css';

function AppContent() {
  const { user, isAuthenticated, isLoading, logout } = useAuthContext();

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#f9fafb'
      }}>
        <LoadingIndicator />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <LoginPage
        onLoginSuccess={() => {
          // App will automatically re-render with authenticated state
        }}
      />
    );
  }

  // Get API URL from environment
  const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  const domainKey = import.meta.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || '';

  return (
    <ChatKitProvider domainKey={domainKey} apiUrl={apiUrl}>
      <ConversationProvider>
        <div className="app">
          <ChatView />
        </div>
      </ConversationProvider>
    </ChatKitProvider>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
