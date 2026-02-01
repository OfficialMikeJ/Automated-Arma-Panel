import { useState, useEffect } from "react";
import { X, Plus, Edit, Trash2, Key, Shield } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function SubAdminManagementModal({ onClose }) {
  const [subAdmins, setSubAdmins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [servers, setServers] = useState([]);

  const [formData, setFormData] = useState({
    username: "",
    password: "",
    confirmPassword: "",
    serverPermissions: {}
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [subAdminsRes, serversRes] = await Promise.all([
        axios.get(`${API}/admin/sub-admins`, { headers }),
        axios.get(`${API}/servers`, { headers })
      ]);
      
      setSubAdmins(subAdminsRes.data);
      setServers(serversRes.data);
    } catch (error) {
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API}/admin/sub-admins`,
        {
          username: formData.username,
          password: formData.password,
          server_permissions: formData.serverPermissions
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success("Sub-admin created successfully");
      setShowCreateForm(false);
      setFormData({ username: "", password: "", confirmPassword: "", serverPermissions: {} });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create sub-admin");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this sub-admin?")) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/admin/sub-admins/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success("Sub-admin deleted");
      fetchData();
    } catch (error) {
      toast.error("Failed to delete sub-admin");
    }
  };

  const togglePermission = (serverId, permission) => {
    setFormData(prev => ({
      ...prev,
      serverPermissions: {
        ...prev.serverPermissions,
        [serverId]: {
          ...prev.serverPermissions[serverId],
          [permission]: !prev.serverPermissions[serverId]?.[permission]
        }
      }
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6">
      <div className="bg-card/95 border border-border/50 rounded-sm w-full max-w-4xl max-h-[80vh] flex flex-col tactical-corner">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
              <Shield className="text-primary" size={20} />
            </div>
            <div>
              <h2 className="font-secondary font-bold text-xl uppercase tracking-wider text-primary">
                Sub-Admin Management
              </h2>
              <p className="font-mono text-xs text-muted-foreground">Manage sub-admin users and permissions</p>
            </div>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-sm hover:bg-secondary/50 flex items-center justify-center transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {!showCreateForm && (
            <>
              <button
                onClick={() => setShowCreateForm(true)}
                className="w-full mb-4 bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm h-10 flex items-center justify-center gap-2 transition-all active:scale-95"
              >
                <Plus size={18} />
                Create Sub-Admin
              </button>

              {loading ? (
                <div className="text-center py-8 font-mono text-muted-foreground">Loading...</div>
              ) : subAdmins.length === 0 ? (
                <div className="text-center py-8 font-mono text-muted-foreground">No sub-admins created yet</div>
              ) : (
                <div className="space-y-3">
                  {subAdmins.map(subAdmin => (
                    <div key={subAdmin.id} className="bg-secondary/20 border border-border/30 rounded-sm p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-secondary font-semibold uppercase tracking-wider text-primary">{subAdmin.username}</h3>
                          <p className="font-mono text-xs text-muted-foreground mt-1">
                            {Object.keys(subAdmin.server_permissions || {}).length} servers assigned
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleDelete(subAdmin.id)}
                            className="p-2 hover:bg-destructive/20 rounded-sm transition-colors"
                          >
                            <Trash2 size={16} className="text-destructive" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {showCreateForm && (
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">Username</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full h-10 rounded-sm border border-input bg-background px-3 py-2 text-sm font-mono"
                  required
                />
              </div>

              <div>
                <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">Password</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full h-10 rounded-sm border border-input bg-background px-3 py-2 text-sm font-mono"
                  required
                />
              </div>

              <div>
                <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">Confirm Password</label>
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="w-full h-10 rounded-sm border border-input bg-background px-3 py-2 text-sm font-mono"
                  required
                />
              </div>

              <div>
                <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-3">Server Permissions</label>
                <div className="space-y-3">
                  {servers.map(server => (
                    <div key={server.id} className="bg-secondary/20 border border-border/30 rounded-sm p-3">
                      <h4 className="font-mono text-sm font-semibold mb-2">{server.name}</h4>
                      <div className="flex gap-3 flex-wrap">
                        {['view', 'edit', 'start', 'stop', 'restart'].map(perm => (
                          <label key={perm} className="flex items-center gap-2 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={formData.serverPermissions[server.id]?.[perm] || false}
                              onChange={() => togglePermission(server.id, perm)}
                              className="rounded"
                            />
                            <span className="font-mono text-xs uppercase">{perm}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false);
                    setFormData({ username: "", password: "", confirmPassword: "", serverPermissions: {} });
                  }}
                  className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm h-10"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm h-10"
                >
                  Create
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}