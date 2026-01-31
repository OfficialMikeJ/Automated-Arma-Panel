import { useState } from "react";
import { Eye, EyeOff, Shield } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";
import PasswordStrengthIndicator from "@/components/PasswordStrengthIndicator";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Predefined security questions
const SECURITY_QUESTIONS = [
  "What was the name of your first pet?",
  "In what city were you born?",
  "What is your mother's maiden name?",
  "What was the name of your elementary school?",
  "What street did you grow up on?",
  "What is your favorite book?",
  "What was your childhood nickname?",
  "What is the name of your favorite teacher?"
];

export default function FirstTimeSetupPage({ onComplete }) {
  const [step, setStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    confirmPassword: "",
    question1: SECURITY_QUESTIONS[0],
    answer1: "",
    question2: SECURITY_QUESTIONS[1],
    answer2: "",
    question3: SECURITY_QUESTIONS[2],
    answer3: "",
    question4: SECURITY_QUESTIONS[3],
    answer4: ""
  });

  const handleNext = () => {
    if (step === 1) {
      if (!formData.username || !formData.password || !formData.confirmPassword) {
        toast.error("Please fill in all fields");
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        toast.error("Passwords do not match");
        return;
      }
      if (formData.password.length < 6) {
        toast.error("Password must be at least 6 characters");
        return;
      }
    }
    setStep(step + 1);
  };

  const handleBack = () => {
    setStep(step - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate security answers
    if (!formData.answer1 || !formData.answer2 || !formData.answer3 || !formData.answer4) {
      toast.error("Please answer all security questions");
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/first-time-setup`, {
        username: formData.username,
        password: formData.password,
        security_questions: {
          question1: formData.answer1,
          question2: formData.answer2,
          question3: formData.answer3,
          question4: formData.answer4
        }
      });

      toast.success("Admin account created successfully!");
      onComplete(
        response.data.access_token, 
        response.data.username,
        response.data.requires_totp_setup || false,
        response.data.session_timeout_minutes || 60
      );
    } catch (error) {
      toast.error(error.response?.data?.detail || "Setup failed");
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
            <div className="inline-flex items-center justify-center w-20 h-20 bg-primary/10 rounded-full mb-4">
              <Shield className="text-primary" size={40} />
            </div>
            <h1 className="font-secondary font-bold text-4xl tracking-tight uppercase text-primary mb-2" data-testid="setup-title">
              First-Time Setup
            </h1>
            <p className="font-mono text-sm text-muted-foreground uppercase tracking-widest">
              Create Your Admin Account
            </p>
          </div>

          {/* Progress */}
          <div className="mb-8">
            <div className="flex items-center justify-center gap-4">
              <div className={`flex items-center gap-2 ${
                step >= 1 ? "text-primary" : "text-muted-foreground"
              }`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                  step >= 1 ? "border-primary bg-primary text-primary-foreground" : "border-muted-foreground"
                }`}>
                  1
                </div>
                <span className="font-mono text-xs uppercase">Account</span>
              </div>
              <div className={`h-0.5 w-16 ${
                step >= 2 ? "bg-primary" : "bg-muted-foreground/30"
              }`}></div>
              <div className={`flex items-center gap-2 ${
                step >= 2 ? "text-primary" : "text-muted-foreground"
              }`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                  step >= 2 ? "border-primary bg-primary text-primary-foreground" : "border-muted-foreground"
                }`}>
                  2
                </div>
                <span className="font-mono text-xs uppercase">Security</span>
              </div>
            </div>
          </div>

          {/* Form */}
          <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-sm p-8 tactical-corner">
            <form onSubmit={handleSubmit}>
              {step === 1 && (
                <div className="space-y-4">
                  <div>
                    <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                      Admin Username
                    </label>
                    <input
                      data-testid="username-input"
                      type="text"
                      value={formData.username}
                      onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                      className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary font-mono"
                      placeholder="admin"
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
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary font-mono pr-10"
                        placeholder="Enter password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-primary transition-colors"
                      >
                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                    {/* Password Strength Indicator */}
                    {formData.password && (
                      <div className="mt-3">
                        <PasswordStrengthIndicator password={formData.password} />
                      </div>
                    )}
                  </div>

                  <div>
                    <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                      Confirm Password
                    </label>
                    <div className="relative">
                      <input
                        data-testid="confirm-password-input"
                        type={showConfirmPassword ? "text" : "password"}
                        value={formData.confirmPassword}
                        onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                        className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary font-mono pr-10"
                        placeholder="Confirm password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-primary transition-colors"
                      >
                        {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>

                  <div className="pt-4">
                    <button
                      data-testid="next-button"
                      type="button"
                      onClick={handleNext}
                      className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-10 glow-primary"
                    >
                      Next: Security Questions
                    </button>
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-4">
                  <div className="mb-4">
                    <p className="font-mono text-xs text-muted-foreground">
                      These security questions will be used to reset your password if you forget it.
                    </p>
                  </div>

                  {[1, 2, 3, 4].map((num) => (
                    <div key={num}>
                      <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                        Question {num}
                      </label>
                      <select
                        data-testid={`question-${num}-select`}
                        value={formData[`question${num}`]}
                        onChange={(e) => setFormData({ ...formData, [`question${num}`]: e.target.value })}
                        className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary font-mono mb-2"
                      >
                        {SECURITY_QUESTIONS.map((q) => (
                          <option key={q} value={q}>{q}</option>
                        ))}
                      </select>
                      <input
                        data-testid={`answer-${num}-input`}
                        type="text"
                        value={formData[`answer${num}`]}
                        onChange={(e) => setFormData({ ...formData, [`answer${num}`]: e.target.value })}
                        className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary font-mono"
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
                      data-testid="complete-setup-button"
                      type="submit"
                      disabled={loading}
                      className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-10 disabled:opacity-50 disabled:cursor-not-allowed glow-primary"
                    >
                      {loading ? "CREATING..." : "Complete Setup"}
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