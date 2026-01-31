import { useState, useEffect } from "react";
import { X, Plus, Trash2, ToggleLeft, ToggleRight } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ModManagerModal({ serverId, onClose }) {
  const [mods, setMods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newMod, setNewMod] = useState({ workshop_id: "", name: "" });

  const getAuthHeader = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  });

  useEffect(() => {
    fetchMods();
  }, [serverId]);

  const fetchMods = async () => {
    try {
      const response = await axios.get(
        `${API}/servers/${serverId}/mods`,
        getAuthHeader()
      );
      setMods(response.data);
    } catch (error) {
      toast.error("Failed to load mods");
    } finally {
      setLoading(false);
    }
  };

  const handleAddMod = async () => {
    if (!newMod.workshop_id || !newMod.name) {
      toast.error("Please fill in all fields");
      return;
    }

    try {
      await axios.post(
        `${API}/servers/${serverId}/mods`,
        newMod,
        getAuthHeader()
      );
      toast.success("Mod added successfully");
      setNewMod({ workshop_id: "", name: "" });
      setShowAddForm(false);
      await fetchMods();
    } catch (error) {
      toast.error("Failed to add mod");
    }
  };

  const handleDeleteMod = async (modId) => {
    try {
      await axios.delete(
        `${API}/servers/${serverId}/mods/${modId}`,
        getAuthHeader()
      );
      toast.success("Mod deleted successfully");
      await fetchMods();
    } catch (error) {
      toast.error("Failed to delete mod");
    }
  };

  const handleToggleMod = async (modId) => {
    try {
      await axios.patch(
        `${API}/servers/${serverId}/mods/${modId}/toggle`,
        {},
        getAuthHeader()
      );
      await fetchMods();
    } catch (error) {
      toast.error("Failed to toggle mod");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm" data-testid="mod-manager-modal">
      <div className="bg-card border border-border/50 rounded-sm p-8 max-w-3xl w-full max-h-[90vh] flex flex-col tactical-corner">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-secondary font-bold text-2xl tracking-tight uppercase text-foreground">
            Mod Manager
          </h2>
          <button
            data-testid="close-mod-modal-button"
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="font-mono text-muted-foreground animate-pulse">LOADING MODS...</div>
          </div>
        ) : (
          <>
            {/* Add Mod Form */}
            {showAddForm ? (
              <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-4 mb-4">
                <div className="space-y-3">
                  <div>
                    <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                      Workshop ID
                    </label>
                    <input
                      data-testid="workshop-id-input"
                      type="text"
                      value={newMod.workshop_id}
                      onChange={(e) => setNewMod({ ...newMod, workshop_id: e.target.value })}
                      className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary font-mono"
                      placeholder="1234567890"
                    />
                  </div>
                  <div>
                    <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                      Mod Name
                    </label>
                    <input
                      data-testid="mod-name-input"
                      type="text"
                      value={newMod.name}
                      onChange={(e) => setNewMod({ ...newMod, name: e.target.value })}
                      className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary font-mono"
                      placeholder="My Awesome Mod"
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setShowAddForm(false)}
                      className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm border border-border transition-all active:scale-95 h-9 text-xs"
                    >
                      Cancel
                    </button>
                    <button
                      data-testid="add-mod-submit-button"
                      onClick={handleAddMod}
                      className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm transition-all active:scale-95 h-9 text-xs"
                    >
                      Add Mod
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <button
                data-testid="show-add-mod-button"
                onClick={() => setShowAddForm(true)}
                className="bg-primary/10 hover:bg-primary/20 text-primary border border-primary/50 font-secondary uppercase tracking-wider rounded-sm transition-all active:scale-95 h-10 mb-4 flex items-center justify-center gap-2"
              >
                <Plus size={16} />
                <span>Add Mod</span>
              </button>
            )}

            {/* Mods List */}
            <div className="flex-1 overflow-y-auto space-y-2">
              {mods.length === 0 ? (
                <div className="text-center py-12">
                  <p className="font-mono text-muted-foreground uppercase tracking-wider">
                    No mods installed
                  </p>
                  <p className="font-mono text-sm text-muted-foreground/60 mt-2">
                    Click "Add Mod" to get started
                  </p>
                </div>
              ) : (
                mods.map((mod) => (
                  <div
                    key={mod.id}
                    data-testid={`mod-item-${mod.id}`}
                    className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-4 flex items-center justify-between"
                  >
                    <div className="flex-1">
                      <div className="font-secondary text-lg uppercase tracking-wider text-foreground">
                        {mod.name}
                      </div>
                      <div className="font-mono text-xs text-muted-foreground">
                        Workshop ID: {mod.workshop_id}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        data-testid={`toggle-mod-button-${mod.id}`}
                        onClick={() => handleToggleMod(mod.id)}
                        className={`p-2 rounded-sm transition-colors ${
                          mod.enabled
                            ? "text-primary hover:text-primary/80"
                            : "text-muted-foreground hover:text-foreground"
                        }`}
                        aria-label="Toggle mod"
                      >
                        {mod.enabled ? <ToggleRight size={20} /> : <ToggleLeft size={20} />}
                      </button>
                      <button
                        data-testid={`delete-mod-button-${mod.id}`}
                        onClick={() => handleDeleteMod(mod.id)}
                        className="text-muted-foreground hover:text-destructive transition-colors p-2"
                        aria-label="Delete mod"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}