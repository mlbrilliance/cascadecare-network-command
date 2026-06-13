import type { ReactNode } from 'react';
import { motion } from 'motion/react';
import { AuthProvider, useAuth } from './hooks/useAuth';
import type { UiPathSDKConfig } from '@uipath/uipath-typescript/core';
import { Dashboard } from './components/Dashboard';
import logoUrl from './assets/clearflow-logo.svg';

const authConfig: UiPathSDKConfig = {
  clientId: import.meta.env.VITE_UIPATH_CLIENT_ID,
  orgName: import.meta.env.VITE_UIPATH_ORG_NAME,
  tenantName: import.meta.env.VITE_UIPATH_TENANT_NAME,
  baseUrl: import.meta.env.VITE_UIPATH_BASE_URL,
  redirectUri: window.location.origin + window.location.pathname,
  scope: import.meta.env.VITE_UIPATH_SCOPE,
};

function Splash({ children }: { children: ReactNode }) {
  return <div className="min-h-screen flex items-center justify-center bg-radial-command p-6">{children}</div>;
}

function AppContent() {
  const { isAuthenticated, isLoading, error, login, logout } = useAuth();

  if (isLoading) {
    return (
      <Splash>
        <div className="flex items-center gap-3 text-slate-400">
          <span className="w-2.5 h-2.5 rounded-full bg-accent animate-pulse-glow" />
          Establishing secure session…
        </div>
      </Splash>
    );
  }

  if (!isAuthenticated) {
    return (
      <Splash>
        <motion.div
          initial={{ opacity: 0, y: 16, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="relative max-w-md w-full rounded-2xl border border-ink-700/70 bg-ink-850/70 backdrop-blur-xl shadow-panel p-8 text-center overflow-hidden"
        >
          <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-accent/60 to-transparent" />
          <img src={logoUrl} alt="" className="w-16 h-16 mx-auto mb-5 animate-float" />
          <h1 className="text-2xl font-bold text-slate-50">
            ClearFlow <span className="text-accent text-glow">Network Command</span>
          </h1>
          <p className="text-slate-400 mt-2 mb-7 text-sm leading-relaxed">
            Cyber Crisis Operations console. Sign in with your UiPath account to enter the command center.
          </p>
          {error && (
            <p className="text-sm text-rose-300 bg-rose-500/10 border border-rose-500/30 rounded-lg p-3 mb-4 break-words">
              {error}
            </p>
          )}
          <button
            onClick={login}
            className="w-full py-2.5 px-4 rounded-lg bg-accent text-ink-950 font-semibold hover:bg-accent-glow shadow-glow-sm transition-all"
          >
            Sign in with UiPath
          </button>
        </motion.div>
      </Splash>
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
