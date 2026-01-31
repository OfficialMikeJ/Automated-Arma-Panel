import { useState, useEffect } from "react";
import { Shield, Copy, Check, X } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function TOTPSetupModal({ onComplete, onSkip }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [totpData, setTotpData] = useState(null);
  const [verificationCode, setVerificationCode] = useState("");
  const [copied, setCopied] = useState(false);

  const getAuthHeader = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  });

  useEffect(() => {
    setupTOTP();
  }, []);

  const setupTOTP = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/totp/setup`, {}, getAuthHeader());
      setTotpData(response.data);
    } catch (error) {
      toast.error("Failed to initialize 2FA setup");
    } finally {
      setLoading(false);
    }
  };

  const copySecret = () => {
    navigator.clipboard.writeText(totpData.secret);
    setCopied(true);
    toast.success("Secret copied to clipboard");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleVerify = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      toast.error("Please enter a valid 6-digit code");
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${API}/auth/totp/verify`,
        { totp_code: verificationCode },
        getAuthHeader()
      );
      toast.success("2FA enabled successfully!");
      onComplete();
    } catch (error) {
      toast.error("Invalid code. Please try again.");
      setVerificationCode("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm" data-testid="totp-setup-modal">
      <div className="bg-card border border-border/50 rounded-sm p-8 max-w-lg w-full tactical-corner">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
              <Shield className="text-primary" size={24} />
            </div>
            <div>
              <h2 className="font-secondary font-bold text-2xl tracking-tight uppercase text-foreground">
                Setup 2FA
              </h2>
              <p className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
                Secure Your Account
              </p>
            </div>
          </div>
          <button
            data-testid="skip-totp-button"
            onClick={onSkip}
            className="text-muted-foreground hover:text-foreground transition-colors"
            title="Skip for now"
          >
            <X size={24} />
          </button>
        </div>

        {loading && !totpData ? (
          <div className="text-center py-12">
            <div className="font-mono text-muted-foreground animate-pulse">INITIALIZING...</div>
          </div>
        ) : (
          <div className="space-y-6">
            {step === 1 && totpData && (
              <>
                <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-4">
                  <p className="font-mono text-xs text-muted-foreground mb-4">
                    Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
                  </p>
                  <div className="flex justify-center mb-4">
                    <img
                      src={`${API}${totpData.qr_code_url}`}
                      alt="TOTP QR Code"
                      className="w-64 h-64 bg-white p-2 rounded"
                      data-testid="totp-qr-code"
                    />
                  </div>
                  <div className="mt-4">
                    <p className="font-mono text-xs text-muted-foreground mb-2">
                      Or enter this secret key manually:
                    </p>
                    <div className="flex items-center gap-2">
                      <code className="flex-1 bg-background border border-input rounded-sm px-3 py-2 font-mono text-sm text-foreground">
                        {totpData.secret}
                      </code>
                      <button
                        onClick={copySecret}
                        className="p-2 bg-secondary hover:bg-secondary/80 text-secondary-foreground rounded-sm transition-colors"
                        title="Copy secret"
                      >
                        {copied ? <Check size={16} /> : <Copy size={16} />}
                      </button>
                    </div>
                  </div>
                </div>

                <button
                  data-testid="totp-continue-button"
                  onClick={() => setStep(2)}
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-10 glow-primary"
                >
                  Continue to Verification
                </button>
              </>
            )}

            {step === 2 && (
              <>
                <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-4">
                  <p className="font-mono text-xs text-muted-foreground mb-4">
                    Enter the 6-digit code from your authenticator app:
                  </p>
                  <input
                    data-testid="totp-verify-input"
                    type="text"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                    className="flex h-12 w-full rounded-sm border border-input bg-background px-3 py-2 text-center text-2xl font-mono ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary tracking-widest"
                    placeholder="000000"
                    maxLength={6}
                    autoFocus
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm border border-border transition-all active:scale-95 h-10"
                  >
                    Back
                  </button>
                  <button
                    data-testid="totp-verify-button"
                    onClick={handleVerify}
                    disabled={loading || verificationCode.length !== 6}
                    className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-10 disabled:opacity-50 disabled:cursor-not-allowed glow-primary"
                  >
                    {loading ? "VERIFYING..." : "Verify & Enable"}
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}