import { useState, useEffect } from "react";
import { X, Save } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ConfigEditorModal({ serverId, onClose }) {
  const [config, setConfig] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const getAuthHeader = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  });

  useEffect(() => {
    fetchConfig();
  }, [serverId]);

  const fetchConfig = async () => {
    try {
      const response = await axios.get(
        `${API}/servers/${serverId}/config`,
        getAuthHeader()
      );
      setConfig(response.data.content);
    } catch (error) {
      toast.error("Failed to load configuration");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(
        `${API}/servers/${serverId}/config`,
        { content: config },
        getAuthHeader()
      );
      toast.success("Configuration saved successfully");
      onClose();
    } catch (error) {
      toast.error("Failed to save configuration");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm" data-testid="config-editor-modal">
      <div className="bg-card border border-border/50 rounded-sm p-8 max-w-4xl w-full max-h-[90vh] flex flex-col tactical-corner">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-secondary font-bold text-2xl tracking-tight uppercase text-foreground">
            Server Configuration
          </h2>
          <button
            data-testid="close-config-modal-button"
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="font-mono text-muted-foreground animate-pulse">LOADING CONFIGURATION...</div>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-hidden mb-4">
              <textarea
                data-testid="config-editor-textarea"
                value={config}
                onChange={(e) => setConfig(e.target.value)}
                className="w-full h-full font-mono text-sm bg-background border border-input rounded-sm p-4 text-foreground resize-none focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
                placeholder="Server configuration..."
              />
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                data-testid="cancel-config-button"
                onClick={onClose}
                className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm border border-border transition-all active:scale-95 h-10"
              >
                Cancel
              </button>
              <button
                data-testid="save-config-button"
                onClick={handleSave}
                disabled={saving}
                className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-10 glow-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? (
                  <span>SAVING...</span>
                ) : (
                  <>
                    <Save size={16} />
                    <span>Save Config</span>
                  </>
                )}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}