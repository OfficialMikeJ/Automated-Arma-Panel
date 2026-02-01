import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { LogOut, Plus, RefreshCw, Server, Activity, HardDrive, Shield } from "lucide-react";
import ServerCard from "../components/ServerCard";
import SystemResources from "../components/SystemResources";
import AddServerModal from "../components/AddServerModal";
import SteamCMDModal from "../components/SteamCMDModal";
import ConfigEditorModal from "../components/ConfigEditorModal";
import ModManagerModal from "../components/ModManagerModal";
import LogViewerModal from "../components/LogViewerModal";
import SubAdminManagementModal from "../components/SubAdminManagementModal";
import ResourceManagementModal from "../components/ResourceManagementModal";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function DashboardPage({ onLogout }) {
  const [servers, setServers] = useState([]);
  const [resources, setResources] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showSteamCMDModal, setShowSteamCMDModal] = useState(false);
  const [selectedServerId, setSelectedServerId] = useState(null);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showModsModal, setShowModsModal] = useState(false);
  const [showLogsModal, setShowLogsModal] = useState(false);
  const [showSubAdminManagement, setShowSubAdminManagement] = useState(false);
  const [showResourceManagement, setShowResourceManagement] = useState(false);
  const [selectedServerForResources, setSelectedServerForResources] = useState(null);
  const username = localStorage.getItem("username");

  const getAuthHeader = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  });

  const fetchServers = async () => {
    try {
      const response = await axios.get(`${API}/servers`, getAuthHeader());
      setServers(response.data);
    } catch (error) {
      if (error.response?.status === 401) {
        toast.error("Session expired. Please login again.");
        onLogout();
      } else {
        toast.error("Failed to fetch servers");
      }
    }
  };

  const fetchResources = async () => {
    try {
      const response = await axios.get(`${API}/system/resources`, getAuthHeader());
      setResources(response.data);
    } catch (error) {
      console.error("Failed to fetch resources", error);
    }
  };

  useEffect(() => {
    const init = async () => {
      await Promise.all([fetchServers(), fetchResources()]);
      setLoading(false);
    };
    init();

    // Refresh resources every 5 seconds
    const interval = setInterval(fetchResources, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    await Promise.all([fetchServers(), fetchResources()]);
    toast.success("Dashboard refreshed");
  };

  const handleServerAction = async (serverId, action) => {
    try {
      await axios.post(`${API}/servers/${serverId}/${action}`, {}, getAuthHeader());
      toast.success(`Server ${action} successful`);
      await fetchServers();
    } catch (error) {
      toast.error(`Failed to ${action} server`);
    }
  };

  const handleAddServer = async (serverData) => {
    try {
      await axios.post(`${API}/servers`, serverData, getAuthHeader());
      toast.success("Server added successfully");
      setShowAddModal(false);
      await fetchServers();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to add server");
    }
  };

  const handleDeleteServer = async (serverId) => {
    try {
      await axios.delete(`${API}/servers/${serverId}`, getAuthHeader());
      toast.success("Server deleted successfully");
      await fetchServers();
    } catch (error) {
      toast.error("Failed to delete server");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-primary font-mono animate-pulse">LOADING TACTICAL INTERFACE...</div>
      </div>
    );
  }

  const totalPlayers = servers.reduce((sum, s) => sum + s.current_players, 0);
  const totalMaxPlayers = servers.reduce((sum, s) => sum + s.max_players, 0);
  const onlineServers = servers.filter(s => s.status === "online").length;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/30 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Server className="text-primary" size={32} />
              <div>
                <h1 className="font-secondary font-bold text-2xl tracking-tight uppercase text-primary">
                  TACTICAL COMMAND
                </h1>
                <p className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
                  Operator: {username}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                data-testid="sub-admins-button"
                onClick={() => setShowSubAdminManagement(true)}
                className="h-10 px-4 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/30 font-secondary uppercase tracking-wider rounded-sm transition-all active:scale-95 flex items-center gap-2"
              >
                <Shield size={16} />
                <span>Sub-Admins</span>
              </button>
              <button
                data-testid="refresh-button"
                onClick={handleRefresh}
                className="h-10 px-4 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm border border-border transition-all active:scale-95 flex items-center gap-2"
              >
                <RefreshCw size={16} />
                <span>Refresh</span>
              </button>
              <button
                data-testid="logout-button"
                onClick={onLogout}
                className="h-10 px-4 bg-destructive/10 hover:bg-destructive/20 text-destructive border border-destructive/50 font-secondary uppercase tracking-wider rounded-sm transition-all active:scale-95 flex items-center gap-2"
              >
                <LogOut size={16} />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-sm p-6 tactical-corner">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80">
                Total Servers
              </span>
              <Server className="text-primary" size={20} />
            </div>
            <div className="font-secondary font-bold text-4xl text-foreground" data-testid="total-servers-stat">
              {servers.length}
            </div>
          </div>

          <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-sm p-6 tactical-corner">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80">
                Online Servers
              </span>
              <Activity className="text-primary" size={20} />
            </div>
            <div className="font-secondary font-bold text-4xl text-primary" data-testid="online-servers-stat">
              {onlineServers}
            </div>
          </div>

          <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-sm p-6 tactical-corner">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80">
                Active Players
              </span>
              <Activity className="text-accent" size={20} />
            </div>
            <div className="font-secondary font-bold text-4xl text-foreground" data-testid="total-players-stat">
              {totalPlayers}<span className="text-2xl text-muted-foreground">/{totalMaxPlayers}</span>
            </div>
          </div>

          <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-sm p-6 tactical-corner">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80">
                System Load
              </span>
              <HardDrive className="text-accent" size={20} />
            </div>
            <div className="font-secondary font-bold text-4xl text-foreground" data-testid="cpu-load-stat">
              {resources?.cpu_percent?.toFixed(0) || 0}<span className="text-2xl text-muted-foreground">%</span>
            </div>
          </div>
        </div>

        {/* System Resources */}
        {resources && <SystemResources resources={resources} />}

        {/* Action Buttons */}
        <div className="flex gap-3 mb-6 mt-8">
          <button
            data-testid="add-server-button"
            onClick={() => setShowAddModal(true)}
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 px-6 py-3 flex items-center gap-2 glow-primary"
          >
            <Plus size={20} />
            <span>Add Server Instance</span>
          </button>
          <button
            data-testid="steamcmd-button"
            onClick={() => setShowSteamCMDModal(true)}
            className="bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm border border-border transition-all active:scale-95 px-6 py-3 flex items-center gap-2"
          >
            <HardDrive size={20} />
            <span>SteamCMD Manager</span>
          </button>
        </div>

        {/* Server Instances */}
        <div>
          <h2 className="font-secondary font-bold text-2xl tracking-tight uppercase text-foreground mb-6">
            Server Instances
          </h2>
          {servers.length === 0 ? (
            <div className="bg-card/30 backdrop-blur-sm border border-border/50 rounded-sm p-12 text-center">
              <Server className="text-muted-foreground mx-auto mb-4" size={48} />
              <p className="font-mono text-muted-foreground uppercase tracking-wider">
                No server instances configured
              </p>
              <p className="font-mono text-sm text-muted-foreground/60 mt-2">
                Click "Add Server Instance" to get started
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {servers.map((server) => (
                <ServerCard
                  key={server.id}
                  server={server}
                  onAction={handleServerAction}
                  onDelete={handleDeleteServer}
                  onOpenConfig={(serverId) => {
                    setSelectedServerId(serverId);
                    setShowConfigModal(true);
                  }}
                  onOpenMods={(serverId) => {
                    setSelectedServerId(serverId);
                    setShowModsModal(true);
                  }}
                  onOpenLogs={(serverId) => {
                    setSelectedServerId(serverId);
                    setShowLogsModal(true);
                  }}
                  onOpenResources={(server) => {
                    setSelectedServerForResources(server);
                    setShowResourceManagement(true);
                  }}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Modals */}
      {showAddModal && (
        <AddServerModal
          onClose={() => setShowAddModal(false)}
          onSubmit={handleAddServer}
        />
      )}
      {showSteamCMDModal && (
        <SteamCMDModal onClose={() => setShowSteamCMDModal(false)} />
      )}
      {showConfigModal && selectedServerId && (
        <ConfigEditorModal
          serverId={selectedServerId}
          onClose={() => {
            setShowConfigModal(false);
            setSelectedServerId(null);
          }}
        />
      )}
      {showModsModal && selectedServerId && (
        <ModManagerModal
          serverId={selectedServerId}
          onClose={() => {
            setShowModsModal(false);
            setSelectedServerId(null);
          }}
        />
      )}
      {showLogsModal && selectedServerId && (
        <LogViewerModal
          serverId={selectedServerId}
          onClose={() => {
            setShowLogsModal(false);
            setSelectedServerId(null);
          }}
        />
      )}

      {showSubAdminManagement && (
        <SubAdminManagementModal onClose={() => setShowSubAdminManagement(false)} />
      )}

      {showResourceManagement && selectedServerForResources && (
        <ResourceManagementModal
          server={selectedServerForResources}
          onClose={() => {
            setShowResourceManagement(false);
            setSelectedServerForResources(null);
          }}
          onUpdate={() => {
            fetchServers();
            fetchResources();
          }}
        />
      )}
    </div>
  );
}