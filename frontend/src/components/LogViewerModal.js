import { useState, useEffect } from "react";
import { X, RefreshCw } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function LogViewerModal({ serverId, onClose }) {
  const [logs, setLogs] = useState("");
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const getAuthHeader = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  });

  const fetchLogs = async () => {
    try {
      const response = await axios.get(
        `${API}/servers/${serverId}/logs?lines=100`,
        getAuthHeader()
      );
      setLogs(response.data.logs);
      setLoading(false);
    } catch (error) {
      toast.error("Failed to load logs");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [serverId]);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchLogs, 3000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, serverId]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm" data-testid="log-viewer-modal">
      <div className="bg-card border border-border/50 rounded-sm p-8 max-w-6xl w-full max-h-[90vh] flex flex-col tactical-corner">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-secondary font-bold text-2xl tracking-tight uppercase text-foreground">
            Server Logs
          </h2>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                data-testid="auto-refresh-checkbox"
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="w-4 h-4 rounded border-input bg-background"
              />
              <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                Auto Refresh
              </span>
            </label>
            <button
              data-testid="refresh-logs-button"
              onClick={fetchLogs}
              className="text-muted-foreground hover:text-primary transition-colors p-2"
              aria-label="Refresh logs"
            >
              <RefreshCw size={20} />
            </button>
            <button
              data-testid="close-logs-modal-button"
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="font-mono text-muted-foreground animate-pulse">LOADING LOGS...</div>
          </div>
        ) : (
          <div className="flex-1 overflow-hidden">
            <pre
              data-testid="log-viewer-content"
              className="w-full h-full font-mono text-xs bg-background border border-input rounded-sm p-4 text-foreground overflow-auto"
            >
              {logs || "No logs available"}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}