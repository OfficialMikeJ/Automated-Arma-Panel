import { useState } from "react";
import { Eye, EyeOff, Info } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";
import UpdatesModal from "@/components/UpdatesModal";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function LoginPage({ onLogin, onForgotPassword }) {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [requiresTOTP, setRequiresTOTP] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showUpdates, setShowUpdates] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const endpoint = isLogin ? "/auth/login" : "/auth/register";
      const payload = {
        username,
        password,
      };
      
      // Add TOTP code if required
      if (isLogin && totpCode) {
        payload.totp_code = totpCode;
      }
      
      const response = await axios.post(`${API}${endpoint}`, payload);

      toast.success(isLogin ? "Login successful" : "Registration successful");
      onLogin(
        response.data.access_token, 
        response.data.username,
        response.data.requires_totp_setup,
        response.data.session_timeout_minutes
      );
    } catch (error) {
      const errorMsg = error.response?.data?.detail || "Authentication failed";
      
      // Check if TOTP is required
      if (errorMsg.includes("2FA code required")) {
        setRequiresTOTP(true);
        toast.error("Please enter your 2FA code");
      } else {
        toast.error(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Image with Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1545915345-3c135498d3dc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHw0fHxBcm1hJTIwUmVmb3JnZXIlMjBzb2xkaWVyJTIwdGFjdGljYWx8ZW58MHx8fHwxNzY5NTQwNjE4fDA&ixlib=rb-4.1.0&q=85')`
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-background/95 via-background/85 to-background/95"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          {/* Logo/Header */}
          <div className="text-center mb-8">
            <h1 className="font-secondary font-bold text-5xl tracking-tight uppercase text-primary mb-2" data-testid="login-title">
              TACTICAL COMMAND
            </h1>
            <p className="font-mono text-sm text-muted-foreground uppercase tracking-widest">
              Arma Server Management Panel
            </p>
          </div>

          {/* Login Form */}
          <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-sm p-8 tactical-corner">
            <div className="flex gap-2 mb-6">
              <button
                data-testid="login-tab-button"
                onClick={() => setIsLogin(true)}
                className={`flex-1 py-2 px-4 font-secondary uppercase tracking-wider text-sm rounded-sm transition-all ${
                  isLogin
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary/50 text-muted-foreground hover:bg-secondary/70"
                }`}
              >
                Login
              </button>
              <button
                data-testid="register-tab-button"
                onClick={() => setIsLogin(false)}
                className={`flex-1 py-2 px-4 font-secondary uppercase tracking-wider text-sm rounded-sm transition-all ${
                  !isLogin
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary/50 text-muted-foreground hover:bg-secondary/70"
                }`}
              >
                Register
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                  Username
                </label>
                <input
                  data-testid="username-input"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50 font-mono"
                  placeholder="Enter username"
                  required
                />
              </div>

              <div>
                <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    data-testid="password-input"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50 font-mono pr-10"
                    placeholder="Enter password"
                    required
                  />
                  <button
                    data-testid="toggle-password-button"
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-primary transition-colors"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              {isLogin && requiresTOTP && (
                <div>
                  <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                    2FA Code
                  </label>
                  <input
                    data-testid="totp-code-input"
                    type="text"
                    value={totpCode}
                    onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                    className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary font-mono tracking-widest text-center"
                    placeholder="000000"
                    maxLength={6}
                    autoFocus
                  />
                </div>
              )}

              <button
                data-testid="submit-button"
                type="submit"
                disabled={loading}
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-10 disabled:opacity-50 disabled:cursor-not-allowed glow-primary"
              >
                {loading ? "PROCESSING..." : isLogin ? "LOGIN" : "REGISTER"}
              </button>

              {isLogin && (
                <div className="text-center mt-4">
                  <button
                    type="button"
                    data-testid="forgot-password-button"
                    onClick={onForgotPassword}
                    className="font-mono text-xs text-accent hover:text-accent/80 transition-colors"
                  >
                    Forgot Password?
                  </button>
                </div>
              )}
            </form>
          </div>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="font-mono text-xs text-muted-foreground">
              Secure • Lightweight • Fast
            </p>
          </div>
        </div>

        {/* Updates & Fixes Button */}
        <div className="mt-4">
          <button
            onClick={() => setShowUpdates(true)}
            className="w-full flex items-center justify-center gap-2 py-2 text-muted-foreground hover:text-primary transition-colors font-mono text-xs uppercase tracking-wider"
          >
            <Info size={14} />
            Updates & Fixes
          </button>
        </div>
      </div>

      {/* Updates Modal */}
      {showUpdates && <UpdatesModal onClose={() => setShowUpdates(false)} />}
    </div>
  );
}