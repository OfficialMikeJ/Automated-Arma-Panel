import { useState } from "react";
import { X, Cpu, HardDrive, Network, Save } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ResourceManagementModal({ server, onClose, onUpdate }) {
  const [formData, setFormData] = useState({
    cpu_cores: server.cpu_cores || 2,
    ram_gb: server.ram_gb || 4,
    storage_gb: server.storage_gb || 50,
    network_speed_mbps: server.network_speed_mbps || 100
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.patch(
        `${API}/servers/${server.id}`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success("Resource allocation updated");
      onUpdate();
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update resources");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6">
      <div className="bg-card/95 border border-border/50 rounded-sm w-full max-w-2xl tactical-corner">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border/30">
          <div>
            <h2 className="font-secondary font-bold text-xl uppercase tracking-wider text-primary">
              Resource Management
            </h2>
            <p className="font-mono text-xs text-muted-foreground mt-1">{server.name}</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-sm hover:bg-secondary/50 flex items-center justify-center transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* CPU Cores */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Cpu size={18} className="text-primary" />
              <label className="font-mono text-sm uppercase tracking-wider text-foreground">CPU Cores</label>
            </div>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="1"
                max="16"
                value={formData.cpu_cores}
                onChange={(e) => setFormData({ ...formData, cpu_cores: parseInt(e.target.value) })}
                className="flex-1"
              />
              <input
                type="number"
                min="1"
                max="16"
                value={formData.cpu_cores}
                onChange={(e) => setFormData({ ...formData, cpu_cores: parseInt(e.target.value) })}
                className="w-20 h-10 rounded-sm border border-input bg-background px-3 py-2 text-sm font-mono text-center"
              />
              <span className="font-mono text-xs text-muted-foreground w-12">Cores</span>
            </div>
          </div>

          {/* RAM */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <HardDrive size={18} className="text-accent" />
              <label className="font-mono text-sm uppercase tracking-wider text-foreground">RAM</label>
            </div>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="1"
                max="64"
                value={formData.ram_gb}
                onChange={(e) => setFormData({ ...formData, ram_gb: parseInt(e.target.value) })}
                className="flex-1"
              />
              <input
                type="number"
                min="1"
                max="64"
                value={formData.ram_gb}
                onChange={(e) => setFormData({ ...formData, ram_gb: parseInt(e.target.value) })}
                className="w-20 h-10 rounded-sm border border-input bg-background px-3 py-2 text-sm font-mono text-center"
              />
              <span className="font-mono text-xs text-muted-foreground w-12">GB</span>
            </div>
          </div>

          {/* Storage */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <HardDrive size={18} className="text-primary" />
              <label className="font-mono text-sm uppercase tracking-wider text-foreground">Storage</label>
            </div>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="10"
                max="500"
                step="10"
                value={formData.storage_gb}
                onChange={(e) => setFormData({ ...formData, storage_gb: parseInt(e.target.value) })}
                className="flex-1"
              />
              <input
                type="number"
                min="10"
                max="500"
                step="10"
                value={formData.storage_gb}
                onChange={(e) => setFormData({ ...formData, storage_gb: parseInt(e.target.value) })}
                className="w-20 h-10 rounded-sm border border-input bg-background px-3 py-2 text-sm font-mono text-center"
              />
              <span className="font-mono text-xs text-muted-foreground w-12">GB</span>
            </div>
          </div>

          {/* Network Speed */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Network size={18} className="text-accent" />
              <label className="font-mono text-sm uppercase tracking-wider text-foreground">Network Speed</label>
            </div>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="10"
                max="1000"
                step="10"
                value={formData.network_speed_mbps}
                onChange={(e) => setFormData({ ...formData, network_speed_mbps: parseInt(e.target.value) })}
                className="flex-1"
              />
              <input
                type="number"
                min="10"
                max="1000"
                step="10"
                value={formData.network_speed_mbps}
                onChange={(e) => setFormData({ ...formData, network_speed_mbps: parseInt(e.target.value) })}
                className="w-20 h-10 rounded-sm border border-input bg-background px-3 py-2 text-sm font-mono text-center"
              />
              <span className="font-mono text-xs text-muted-foreground w-12">Mbps</span>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-secondary/20 border border-border/30 rounded-sm p-4">
            <h3 className="font-mono text-xs uppercase tracking-wider text-muted-foreground mb-3">Resource Summary</h3>
            <div className="grid grid-cols-2 gap-3 font-mono text-sm">
              <div>
                <span className="text-muted-foreground">CPU:</span>
                <span className="text-foreground ml-2">{formData.cpu_cores} Cores</span>
              </div>
              <div>
                <span className="text-muted-foreground">RAM:</span>
                <span className="text-foreground ml-2">{formData.ram_gb} GB</span>
              </div>
              <div>
                <span className="text-muted-foreground">Storage:</span>
                <span className="text-foreground ml-2">{formData.storage_gb} GB</span>
              </div>
              <div>
                <span className="text-muted-foreground">Network:</span>
                <span className="text-foreground ml-2">{formData.network_speed_mbps} Mbps</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-border/30 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm h-10 transition-all active:scale-95"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm h-10 transition-all active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Save size={18} />
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  );
}