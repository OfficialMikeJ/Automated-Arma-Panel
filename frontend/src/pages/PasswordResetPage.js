import { useState } from "react";
import { Eye, EyeOff, KeyRound } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function PasswordResetPage({ onCancel, onSuccess }) {
  const [step, setStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    username: "",
    answer1: "",
    answer2: "",
    answer3: "",
    answer4: "",
    newPassword: "",
    confirmPassword: ""
  });

  const handleNext = async () => {
    if (step === 1) {
      if (!formData.username) {
        toast.error("Please enter your username");
        return;
      }
      setLoading(true);
      try {
        await axios.get(`${API}/auth/security-questions/${formData.username}`);
        setStep(2);
      } catch (error) {
        toast.error("User not found or security questions not set");
      } finally {
        setLoading(false);
      }
    } else if (step === 2) {
      if (!formData.answer1 || !formData.answer2 || !formData.answer3 || !formData.answer4) {
        toast.error("Please answer all security questions");
        return;
      }
      setStep(3);
    }
  };

  const handleBack = () => {
    setStep(step - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.newPassword || !formData.confirmPassword) {
      toast.error("Please fill in all fields");
      return;
    }
    
    if (formData.newPassword !== formData.confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }
    
    if (formData.newPassword.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API}/auth/reset-password`, {
        username: formData.username,
        answer1: formData.answer1,
        answer2: formData.answer2,
        answer3: formData.answer3,
        answer4: formData.answer4,
        new_password: formData.newPassword
      });

      toast.success("Password reset successfully!");
      onSuccess();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Password reset failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background */}
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
        <div className="w-full max-w-2xl">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-accent/10 rounded-full mb-4">
              <KeyRound className="text-accent" size={40} />
            </div>
            <h1 className="font-secondary font-bold text-4xl tracking-tight uppercase text-foreground mb-2" data-testid="reset-title">
              Password Reset
            </h1>
            <p className="font-mono text-sm text-muted-foreground uppercase tracking-widest">
              Recover Your Account Access
            </p>
          </div>

          {/* Progress */}
          <div className="mb-8">
            <div className="flex items-center justify-center gap-2">
              {[1, 2, 3].map((num) => (
                <div key={num} className="flex items-center gap-2">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                    step >= num ? "border-accent bg-accent text-accent-foreground" : "border-muted-foreground text-muted-foreground"
                  }`}>
                    {num}
                  </div>
                  {num < 3 && (
                    <div className={`h-0.5 w-8 ${
                      step > num ? "bg-accent" : "bg-muted-foreground/30"
                    }`}></div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Form */}
          <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-sm p-8 tactical-corner">
            <form onSubmit={handleSubmit}>
              {step === 1 && (
                <div className="space-y-4">
                  <div>
                    <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                      Username
                    </label>
                    <input
                      data-testid="reset-username-input"
                      type="text"
                      value={formData.username}
                      onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                      className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-accent font-mono"
                      placeholder="Enter your username"
                      required
                    />
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      type="button"
                      onClick={onCancel}
                      className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm border border-border transition-all active:scale-95 h-10"
                    >
                      Cancel
                    </button>
                    <button
                      data-testid="reset-next-button"
                      type="button"
                      onClick={handleNext}
                      disabled={loading}
                      className="flex-1 bg-accent hover:bg-accent/90 text-accent-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-10 disabled:opacity-50 disabled:cursor-not-allowed glow-accent"
                    >
                      {loading ? "CHECKING..." : "Next"}
                    </button>
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-4">
                  <div className="mb-4">
                    <p className="font-mono text-xs text-muted-foreground">
                      Answer your security questions to verify your identity.
                    </p>
                  </div>

                  {[1, 2, 3, 4].map((num) => (
                    <div key={num}>
                      <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                        Security Question {num}
                      </label>
                      <input
                        data-testid={`reset-answer-${num}-input`}
                        type="text"
                        value={formData[`answer${num}`]}
                        onChange={(e) => setFormData({ ...formData, [`answer${num}`]: e.target.value })}
                        className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-accent font-mono"
                        placeholder="Your answer"
                        required
                      />
                    </div>
                  ))}

                  <div className="flex gap-3 pt-4">
                    <button
                      type="button"
                      onClick={handleBack}
                      className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm border border-border transition-all active:scale-95 h-10"
                    >
                      Back
                    </button>
                    <button
                      data-testid="verify-answers-button"
                      type="button"
                      onClick={handleNext}
                      className="flex-1 bg-accent hover:bg-accent/90 text-accent-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-10 glow-accent"
                    >
                      Verify Answers
                    </button>
                  </div>
                </div>
              )}

              {step === 3 && (
                <div className="space-y-4">
                  <div>
                    <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                      New Password
                    </label>
                    <div className="relative">
                      <input
                        data-testid="new-password-input"
                        type={showPassword ? "text" : "password"}
                        value={formData.newPassword}
                        onChange={(e) => setFormData({ ...formData, newPassword: e.target.value })}
                        className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-accent font-mono pr-10"
                        placeholder="Enter new password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-accent transition-colors"
                      >
                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                      Confirm New Password
                    </label>
                    <div className="relative">
                      <input
                        data-testid="confirm-new-password-input"
                        type={showConfirmPassword ? "text" : "password"}
                        value={formData.confirmPassword}
                        onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                        className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-accent font-mono pr-10"
                        placeholder="Confirm new password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-accent transition-colors"
                      >
                        {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      type="button"
                      onClick={handleBack}
                      className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm border border-border transition-all active:scale-95 h-10"
                    >
                      Back
                    </button>
                    <button
                      data-testid="reset-password-button"
                      type="submit"
                      disabled={loading}
                      className="flex-1 bg-accent hover:bg-accent/90 text-accent-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-10 disabled:opacity-50 disabled:cursor-not-allowed glow-accent"
                    >
                      {loading ? "RESETTING..." : "Reset Password"}
                    </button>
                  </div>
                </div>
              )}
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}