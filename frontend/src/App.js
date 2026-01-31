import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import FirstTimeSetupPage from "./pages/FirstTimeSetupPage";
import PasswordResetPage from "./pages/PasswordResetPage";
import { Toaster } from "@/components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isFirstRun, setIsFirstRun] = useState(false);
  const [showPasswordReset, setShowPasswordReset] = useState(false);

  useEffect(() => {
    checkFirstRun();
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const checkFirstRun = async () => {
    try {
      const response = await axios.get(`${API}/auth/check-first-run`);
      setIsFirstRun(response.data.is_first_run);
    } catch (error) {
      console.error("Failed to check first run:", error);
    }
  };

  const handleLogin = (token, username) => {
    localStorage.setItem('token', token);
    localStorage.setItem('username', username);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setIsAuthenticated(false);
  };

  const handleFirstTimeSetup = (token, username) => {
    setIsFirstRun(false);
    handleLogin(token, username);
  };

  const handlePasswordResetSuccess = () => {
    setShowPasswordReset(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-primary font-mono">LOADING...</div>
      </div>
    );
  }

  // Show first-time setup if no admin exists
  if (isFirstRun) {
    return (
      <>
        <FirstTimeSetupPage onComplete={handleFirstTimeSetup} />
        <Toaster position="top-right" richColors />
      </>
    );
  }

  // Show password reset modal
  if (showPasswordReset) {
    return (
      <>
        <PasswordResetPage 
          onCancel={() => setShowPasswordReset(false)}
          onSuccess={handlePasswordResetSuccess}
        />
        <Toaster position="top-right" richColors />
      </>
    );
  }

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route 
            path="/login" 
            element={
              isAuthenticated ? 
                <Navigate to="/" replace /> : 
                <LoginPage 
                  onLogin={handleLogin}
                  onForgotPassword={() => setShowPasswordReset(true)}
                />
            } 
          />
          <Route 
            path="/" 
            element={
              isAuthenticated ? 
                <DashboardPage onLogout={handleLogout} /> : 
                <Navigate to="/login" replace />
            } 
          />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </>
  );
}

export default App;