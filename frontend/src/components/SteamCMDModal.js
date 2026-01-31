import { useState, useEffect } from "react";
import { X, Download, CheckCircle, XCircle } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function SteamCMDModal({ onClose }) {
  const [status, setStatus] = useState(null);
  const [installing, setInstalling] = useState(false);
  const [loading, setLoading] = useState(true);

  const getAuthHeader = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  });

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API}/steamcmd/status`, getAuthHeader());
      setStatus(response.data);
    } catch (error) {
      toast.error("Failed to fetch SteamCMD status");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleInstall = async () => {
    setInstalling(true);
    try {
      const response = await axios.post(`${API}/steamcmd/install`, {}, getAuthHeader());
      toast.success(response.data.message);
      await fetchStatus();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Installation failed");
    } finally {
      setInstalling(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm" data-testid="steamcmd-modal">
      <div className="bg-card border border-border/50 rounded-sm p-8 max-w-lg w-full tactical-corner">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-secondary font-bold text-2xl tracking-tight uppercase text-foreground">
            SteamCMD Manager
          </h2>
          <button
            data-testid="close-steamcmd-modal-button"
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="font-mono text-muted-foreground animate-pulse">CHECKING STATUS...</div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Status */}
            <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80">
                  Installation Status
                </span>
                {status.installed ? (
                  <CheckCircle className="text-primary" size={20} data-testid="steamcmd-installed-icon" />
                ) : (
                  <XCircle className="text-muted-foreground" size={20} data-testid="steamcmd-not-installed-icon" />
                )}
              </div>
              <div className="font-secondary text-xl uppercase tracking-wider text-foreground">
                {status.installed ? "Installed" : "Not Installed"}
              </div>
            </div>

            {/* Details */}
            {status.installed && (
              <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-4">
                <div className="space-y-2">
                  <div>
                    <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80">
                      Install Path
                    </span>
                    <div className="font-mono text-sm text-foreground/70 mt-1" data-testid="steamcmd-path">
                      {status.path}
                    </div>
                  </div>
                  <div>
                    <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80">
                      Version
                    </span>
                    <div className="font-mono text-sm text-foreground/70 mt-1">
                      {status.version}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Info */}
            <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-4">
              <p className="font-mono text-xs text-muted-foreground leading-relaxed">
                SteamCMD is required to download and manage Arma Reforger and Arma 4 server files.
                The installation will download the Linux version from the official Steam servers.
              </p>
            </div>

            {/* Actions */}
            {!status.installed && (
              <button
                data-testid="install-steamcmd-button"
                onClick={handleInstall}
                disabled={installing}
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-10 disabled:opacity-50 disabled:cursor-not-allowed glow-primary flex items-center justify-center gap-2"
              >
                {installing ? (
                  <span>INSTALLING...</span>
                ) : (
                  <>
                    <Download size={16} />
                    <span>Install SteamCMD</span>
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}