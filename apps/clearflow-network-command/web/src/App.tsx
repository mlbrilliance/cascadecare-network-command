import { AuthProvider, useAuth } from './hooks/useAuth';
import type { UiPathSDKConfig } from '@uipath/uipath-typescript/core';
import { Dashboard } from './components/Dashboard';

const authConfig: UiPathSDKConfig = {
  clientId: import.meta.env.VITE_UIPATH_CLIENT_ID,
  orgName: import.meta.env.VITE_UIPATH_ORG_NAME,
  tenantName: import.meta.env.VITE_UIPATH_TENANT_NAME,
  baseUrl: import.meta.env.VITE_UIPATH_BASE_URL,
  redirectUri: window.location.origin + window.location.pathname,
  scope: import.meta.env.VITE_UIPATH_SCOPE,
};

function AppContent() {
  const { isAuthenticated, isLoading, error, login, logout } = useAuth();

  if (isLoading) return <div className="min-h-screen bg-slate-950 p-8 text-slate-300">Loading...</div>;
  if (error) return <div className="min-h-screen bg-slate-950 p-8 text-red-400">Error: {error}</div>;

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="max-w-sm w-full bg-slate-900 border border-slate-800 rounded-lg shadow p-8 text-center">
          <h1 className="text-2xl font-semibold mb-2 text-slate-100">ClearFlow Network Command</h1>
          <p className="text-slate-400 mb-6">
            Sign in with your UiPath account to continue.
          </p>
          <button
            onClick={login}
            className="w-full py-2 px-4 bg-teal-600 text-white rounded hover:bg-teal-500"
          >
            Sign in with UiPath
          </button>
        </div>
      </div>
    );
  }

  return <Dashboard onLogout={logout} />;
}

function App() {
  return (
    <AuthProvider config={authConfig}>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
