import { Check, X, AlertCircle } from "lucide-react";
import { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function PasswordStrengthIndicator({ password }) {
  const [config, setConfig] = useState(null);
  const [checks, setChecks] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    numbers: false,
    special: false
  });

  useEffect(() => {
    fetchConfig();
  }, []);

  useEffect(() => {
    if (config) {
      validatePassword();
    }
  }, [password, config]);

  const fetchConfig = async () => {
    try {
      const response = await axios.get(`${API}/auth/password-config`);
      setConfig(response.data);
    } catch (error) {
      console.error("Failed to fetch password config");
    }
  };

  const validatePassword = () => {
    setChecks({
      length: password.length >= config.min_length,
      uppercase: !config.require_uppercase || /[A-Z]/.test(password),
      lowercase: !config.require_lowercase || /[a-z]/.test(password),
      numbers: !config.require_numbers || /[0-9]/.test(password),
      special: !config.require_special || /[!@#$%^&*(),.?":{}|<>]/.test(password)
    });
  };

  if (!config) return null;

  const allPassed = Object.values(checks).every(v => v);
  const strength = Object.values(checks).filter(v => v).length;
  const total = Object.values(checks).length;

  const getStrengthColor = () => {
    const percentage = (strength / total) * 100;
    if (percentage === 100) return "text-primary";
    if (percentage >= 60) return "text-accent";
    return "text-destructive";
  };

  const getStrengthLabel = () => {
    const percentage = (strength / total) * 100;
    if (percentage === 100) return "Strong";
    if (percentage >= 60) return "Medium";
    return "Weak";
  };

  return (
    <div className="space-y-2" data-testid="password-strength-indicator">
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
          Password Strength
        </span>
        <span className={`font-mono text-xs font-semibold uppercase ${getStrengthColor()}`}>
          {getStrengthLabel()}
        </span>
      </div>
      
      <div className="h-1 bg-secondary rounded-full overflow-hidden">
        <div 
          className={`h-full transition-all duration-300 ${allPassed ? 'bg-primary' : 'bg-accent'}`}
          style={{ width: `${(strength / total) * 100}%` }}
        ></div>
      </div>

      <div className="space-y-1 pt-2">
        <RequirementCheck 
          met={checks.length} 
          label={`At least ${config.min_length} characters`}
        />
        {config.require_uppercase && (
          <RequirementCheck 
            met={checks.uppercase} 
            label="One uppercase letter"
          />
        )}
        {config.require_lowercase && (
          <RequirementCheck 
            met={checks.lowercase} 
            label="One lowercase letter"
          />
        )}
        {config.require_numbers && (
          <RequirementCheck 
            met={checks.numbers} 
            label="One number"
          />
        )}
        {config.require_special && (
          <RequirementCheck 
            met={checks.special} 
            label="One special character (!@#$%^&*...)"
          />
        )}
      </div>
    </div>
  );
}

function RequirementCheck({ met, label }) {
  return (
    <div className="flex items-center gap-2">
      {met ? (
        <Check size={14} className="text-primary" />
      ) : (
        <X size={14} className="text-muted-foreground" />
      )}
      <span className={`font-mono text-xs ${
        met ? "text-foreground" : "text-muted-foreground"
      }`}>
        {label}
      </span>
    </div>
  );
}