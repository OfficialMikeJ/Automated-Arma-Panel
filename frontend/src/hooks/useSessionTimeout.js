import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SESSION_WARNING_MINUTES = 5; // Show warning 5 minutes before expiry

export function useSessionTimeout({ onTimeout }) {
  const [sessionTimeout, setSessionTimeout] = useState(null);
  const [showWarning, setShowWarning] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(null);

  useEffect(() => {
    // Get session timeout from token response
    const timeout = localStorage.getItem('session_timeout');
    if (timeout) {
      setSessionTimeout(parseInt(timeout));
    }
  }, []);

  useEffect(() => {
    if (!sessionTimeout) return;

    const loginTime = localStorage.getItem('login_time');
    if (!loginTime) {
      localStorage.setItem('login_time', Date.now().toString());
      return;
    }

    const checkSession = () => {
      const elapsed = Date.now() - parseInt(loginTime);
      const remaining = (sessionTimeout * 60 * 1000) - elapsed;
      const remainingMinutes = Math.floor(remaining / 60000);

      setTimeRemaining(remainingMinutes);

      if (remaining <= 0) {
        // Session expired
        handleSessionExpired();
      } else if (remaining <= SESSION_WARNING_MINUTES * 60 * 1000 && !showWarning) {
        // Show warning
        setShowWarning(true);
        toast.warning(
          `Your session will expire in ${remainingMinutes} minute(s)`,
          { duration: 10000 }
        );
      }
    };

    // Check immediately
    checkSession();

    // Check every minute
    const interval = setInterval(checkSession, 60000);

    return () => clearInterval(interval);
  }, [sessionTimeout, showWarning]);

  const handleSessionExpired = useCallback(() => {
    toast.error("Your session has expired. Please log in again.");
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('login_time');
    localStorage.removeItem('session_timeout');
    if (onTimeout) {
      onTimeout();
    }
  }, [onTimeout]);

  const refreshSession = useCallback(() => {
    // Reset login time
    localStorage.setItem('login_time', Date.now().toString());
    setShowWarning(false);
    toast.success("Session refreshed");
  }, []);

  return {
    showWarning,
    timeRemaining,
    refreshSession,
    sessionTimeout
  };
}

export function SessionTimeoutWarning({ timeRemaining, onRefresh, onLogout }) {
  if (!timeRemaining || timeRemaining > SESSION_WARNING_MINUTES) return null;

  return (
    <div 
      className="fixed bottom-6 right-6 z-50 bg-accent/10 border border-accent rounded-sm p-4 backdrop-blur-sm tactical-corner max-w-sm"
      data-testid="session-timeout-warning"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 bg-accent/20 rounded-full flex items-center justify-center">
          <span className="text-accent font-mono text-sm font-bold">
            {timeRemaining}
          </span>
        </div>
        <div className="flex-1">
          <h3 className="font-secondary font-semibold text-sm uppercase tracking-wider text-foreground mb-1">
            Session Expiring Soon
          </h3>
          <p className="font-mono text-xs text-muted-foreground mb-3">
            Your session will expire in {timeRemaining} minute{timeRemaining !== 1 ? 's' : ''}. Save your work.
          </p>
          <div className="flex gap-2">
            <button
              onClick={onRefresh}
              className="flex-1 bg-accent hover:bg-accent/90 text-accent-foreground font-secondary uppercase tracking-wider rounded-sm text-xs py-1.5 px-3 transition-all active:scale-95"
              data-testid="refresh-session-button"
            >
              Refresh
            </button>
            <button
              onClick={onLogout}
              className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm text-xs py-1.5 px-3 transition-all active:scale-95 border border-border"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}