import { useState } from "react";
import { X, ChevronRight, ChevronLeft, Check, Server, Shield, Cpu, Settings } from "lucide-react";

export default function OnboardingModal({ onClose, onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: "Welcome to Tactical Command",
      icon: <Shield className="text-primary" size={48} />,
      content: (
        <div className="space-y-4">
          <p className="text-foreground/90">
            Welcome to your Arma Reforger and Arma 4 Server Control Panel. This quick guide will help you get started.
          </p>
          <div className="bg-primary/10 border border-primary/30 rounded-sm p-4">
            <h4 className="font-secondary uppercase tracking-wider text-primary text-sm mb-2">Quick Overview</h4>
            <ul className="space-y-2 text-sm text-foreground/80">
              <li className="flex items-start gap-2">
                <Check size={16} className="text-primary mt-0.5 flex-shrink-0" />
                <span>Manage multiple Arma server instances</span>
              </li>
              <li className="flex items-start gap-2">
                <Check size={16} className="text-primary mt-0.5 flex-shrink-0" />
                <span>Monitor system resources in real-time</span>
              </li>
              <li className="flex items-start gap-2">
                <Check size={16} className="text-primary mt-0.5 flex-shrink-0" />
                <span>Configure server settings and mods</span>
              </li>
              <li className="flex items-start gap-2">
                <Check size={16} className="text-primary mt-0.5 flex-shrink-0" />
                <span>Create sub-admin accounts with granular permissions</span>
              </li>
            </ul>
          </div>
        </div>
      )
    },
    {
      title: "Installing SteamCMD",
      icon: <Server className="text-accent" size={48} />,
      content: (
        <div className="space-y-4">
          <p className="text-foreground/90">
            Before you can add server instances, you need to install <strong>SteamCMD</strong> on your system.
          </p>
          <div className="bg-card border border-border rounded-sm p-4 space-y-3">
            <h4 className="font-secondary uppercase tracking-wider text-accent text-sm">How to Install SteamCMD:</h4>
            <ol className="space-y-3 text-sm text-foreground/80 list-decimal list-inside">
              <li>Click the <strong>"Install SteamCMD"</strong> button in the top toolbar</li>
              <li>The panel will guide you through the installation process</li>
              <li>SteamCMD will be installed to <code className="bg-background px-1 rounded text-xs">/opt/steamcmd</code></li>
              <li>Once installed, you can use it to download Arma server files</li>
            </ol>
          </div>
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-sm p-3">
            <p className="text-xs text-yellow-200">
              <strong>Note:</strong> SteamCMD requires certain system libraries. The installer will handle dependencies automatically.
            </p>
          </div>
        </div>
      )
    },
    {
      title: "Adding Your First Server",
      icon: <Server className="text-primary" size={48} />,
      content: (
        <div className="space-y-4">
          <p className="text-foreground/90">
            Once SteamCMD is installed, you can create your first Arma server instance.
          </p>
          <div className="bg-card border border-border rounded-sm p-4 space-y-3">
            <h4 className="font-secondary uppercase tracking-wider text-primary text-sm">Steps to Add a Server:</h4>
            <ol className="space-y-3 text-sm text-foreground/80 list-decimal list-inside">
              <li>Click the <strong>"Add Server Instance"</strong> button</li>
              <li>Fill in the server details:
                <ul className="ml-6 mt-2 space-y-1 list-disc list-inside text-xs">
                  <li>Server name (e.g., "My Reforger Server")</li>
                  <li>Game type (Arma Reforger or Arma 4)</li>
                  <li>Port number (default: 2001)</li>
                  <li>Max players</li>
                  <li>Installation path (where server files will be stored)</li>
                </ul>
              </li>
              <li>Set resource allocations (CPU, RAM, storage, network)</li>
              <li>Click <strong>Create Server</strong></li>
            </ol>
          </div>
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-sm p-3">
            <p className="text-xs text-blue-200">
              <strong>Tip:</strong> Each server should use a unique port. Default Arma ports start at 2001.
            </p>
          </div>
        </div>
      )
    },
    {
      title: "Resource Management",
      icon: <Cpu className="text-accent" size={48} />,
      content: (
        <div className="space-y-4">
          <p className="text-foreground/90">
            Allocate system resources to each server instance to optimize performance.
          </p>
          <div className="bg-card border border-border rounded-sm p-4 space-y-3">
            <h4 className="font-secondary uppercase tracking-wider text-accent text-sm">Resource Controls:</h4>
            <div className="space-y-3 text-sm">
              <div>
                <strong className="text-primary">CPU Cores:</strong>
                <p className="text-foreground/80 text-xs mt-1">Assign dedicated CPU cores to your server (1-16 cores)</p>
              </div>
              <div>
                <strong className="text-accent">RAM:</strong>
                <p className="text-foreground/80 text-xs mt-1">Allocate memory for the server process (1-64 GB)</p>
              </div>
              <div>
                <strong className="text-primary">Storage:</strong>
                <p className="text-foreground/80 text-xs mt-1">Define disk space limits for server files and logs</p>
              </div>
              <div>
                <strong className="text-accent">Network Speed:</strong>
                <p className="text-foreground/80 text-xs mt-1">Set bandwidth limits to prevent network saturation</p>
              </div>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            Access resource management by clicking the <strong>"Resources"</strong> button on any server card.
          </p>
        </div>
      )
    },
    {
      title: "Sub-Admin Management",
      icon: <Shield className="text-primary" size={48} />,
      content: (
        <div className="space-y-4">
          <p className="text-foreground/90">
            Create sub-admin accounts and grant specific permissions for server management.
          </p>
          <div className="bg-card border border-border rounded-sm p-4 space-y-3">
            <h4 className="font-secondary uppercase tracking-wider text-primary text-sm">Sub-Admin Features:</h4>
            <ul className="space-y-2 text-sm text-foreground/80">
              <li className="flex items-start gap-2">
                <Check size={16} className="text-primary mt-0.5 flex-shrink-0" />
                <span>Create multiple sub-admin accounts</span>
              </li>
              <li className="flex items-start gap-2">
                <Check size={16} className="text-primary mt-0.5 flex-shrink-0" />
                <span>Assign permissions per server instance</span>
              </li>
              <li className="flex items-start gap-2">
                <Check size={16} className="text-primary mt-0.5 flex-shrink-0" />
                <span>Control start/stop/restart access</span>
              </li>
              <li className="flex items-start gap-2">
                <Check size={16} className="text-primary mt-0.5 flex-shrink-0" />
                <span>Manage config editing permissions</span>
              </li>
            </ul>
          </div>
          <p className="text-xs text-muted-foreground">
            Click the <strong>"Sub-Admins"</strong> button in the header to manage sub-admin accounts.
          </p>
        </div>
      )
    },
    {
      title: "Server Controls & Features",
      icon: <Settings className="text-accent" size={48} />,
      content: (
        <div className="space-y-4">
          <p className="text-foreground/90">
            Each server card provides quick access to essential management features.
          </p>
          <div className="bg-card border border-border rounded-sm p-4 space-y-3">
            <h4 className="font-secondary uppercase tracking-wider text-accent text-sm">Available Actions:</h4>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <strong className="text-primary text-xs">Start/Stop/Restart</strong>
                <p className="text-foreground/70 text-xs mt-1">Control server process</p>
              </div>
              <div>
                <strong className="text-accent text-xs">Config Editor</strong>
                <p className="text-foreground/70 text-xs mt-1">Edit server.cfg files</p>
              </div>
              <div>
                <strong className="text-primary text-xs">Mod Manager</strong>
                <p className="text-foreground/70 text-xs mt-1">Install and manage mods</p>
              </div>
              <div>
                <strong className="text-accent text-xs">Log Viewer</strong>
                <p className="text-foreground/70 text-xs mt-1">View server logs</p>
              </div>
            </div>
          </div>
          <div className="bg-primary/10 border border-primary/30 rounded-sm p-4 space-y-2">
            <h5 className="font-secondary uppercase tracking-wider text-primary text-xs">System Resources Monitor</h5>
            <p className="text-xs text-foreground/80">
              The top-right corner displays real-time system resource usage with visual charts. Monitor CPU, RAM, and disk usage at a glance.
            </p>
          </div>
        </div>
      )
    },
    {
      title: "You're All Set!",
      icon: <Check className="text-green-500" size={48} />,
      content: (
        <div className="space-y-4">
          <p className="text-foreground/90 text-center">
            You're ready to start managing your Arma servers!
          </p>
          <div className="bg-green-500/10 border border-green-500/30 rounded-sm p-4 space-y-3">
            <h4 className="font-secondary uppercase tracking-wider text-green-400 text-sm">Next Steps:</h4>
            <ol className="space-y-2 text-sm text-foreground/80 list-decimal list-inside">
              <li>Install SteamCMD if you haven't already</li>
              <li>Create your first server instance</li>
              <li>Configure server settings and mods</li>
              <li>Invite sub-admins if needed</li>
              <li>Start your server and monitor performance</li>
            </ol>
          </div>
          <div className="bg-card border border-border rounded-sm p-4">
            <h5 className="font-secondary uppercase tracking-wider text-primary text-xs mb-2">Need Help?</h5>
            <p className="text-xs text-foreground/80">
              Check the <strong>Updates & Fixes</strong> section in the login page footer for documentation and troubleshooting guides.
            </p>
          </div>
          <p className="text-xs text-center text-muted-foreground italic">
            You can re-launch this guide anytime from your profile menu.
          </p>
        </div>
      )
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleFinish();
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleFinish = () => {
    // Mark onboarding as complete in localStorage
    localStorage.setItem("onboarding_completed", "true");
    onComplete();
    onClose();
  };

  const handleSkip = () => {
    localStorage.setItem("onboarding_completed", "true");
    onClose();
  };

  const currentStepData = steps[currentStep];

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-md z-50 flex items-center justify-center p-6">
      <div className="bg-card/95 border border-border/50 rounded-sm w-full max-w-3xl tactical-corner max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border/30 flex-shrink-0">
          <div className="flex items-center gap-3">
            {currentStepData.icon}
            <div>
              <h2 className="font-secondary font-bold text-xl uppercase tracking-wider text-primary">
                {currentStepData.title}
              </h2>
              <p className="font-mono text-xs text-muted-foreground mt-1">
                Step {currentStep + 1} of {steps.length}
              </p>
            </div>
          </div>
          <button 
            onClick={handleSkip} 
            className="w-8 h-8 rounded-sm hover:bg-secondary/50 flex items-center justify-center transition-colors"
            aria-label="Skip onboarding"
          >
            <X size={20} />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 pt-4 flex-shrink-0">
          <div className="w-full bg-secondary/30 h-1 rounded-full overflow-hidden">
            <div 
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-1">
          {currentStepData.content}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-border/30 flex-shrink-0">
          <button
            onClick={handleSkip}
            className="font-mono text-sm text-muted-foreground hover:text-foreground transition-colors uppercase tracking-wider"
          >
            Skip Tour
          </button>

          <div className="flex gap-3">
            {currentStep > 0 && (
              <button
                onClick={handlePrev}
                className="h-10 px-6 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm transition-all active:scale-95 flex items-center gap-2"
              >
                <ChevronLeft size={16} />
                <span>Previous</span>
              </button>
            )}
            <button
              onClick={handleNext}
              className="h-10 px-6 bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm transition-all active:scale-95 flex items-center gap-2"
            >
              <span>{currentStep === steps.length - 1 ? "Get Started" : "Next"}</span>
              {currentStep === steps.length - 1 ? (
                <Check size={16} />
              ) : (
                <ChevronRight size={16} />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
