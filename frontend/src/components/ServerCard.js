import { Play, Square, RotateCw, Trash2, Settings, Package, FileText } from "lucide-react";
import { useState } from "react";

export default function ServerCard({ server, onAction, onDelete, onOpenConfig, onOpenMods, onOpenLogs }) {
  const getStatusColor = (status) => {
    switch (status) {
      case "online":
        return "status-online";
      case "offline":
        return "status-offline";
      case "restarting":
        return "status-restarting";
      default:
        return "status-offline";
    }
  };

  const getBackgroundImage = (gameType) => {
    if (gameType === "arma_reforger") {
      return "https://images.unsplash.com/photo-1737363642262-8866f0903a1f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxBcm1hJTIwUmVmb3JnZXIlMjBzb2xkaWVyJTIwdGFjdGljYWx8ZW58MHx8fHwxNzY5NTQwNjE4fDA&ixlib=rb-4.1.0&q=85";
    } else if (gameType === "arma_4") {
      return "https://images.unsplash.com/photo-1752559342730-202893de3cf3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHxBcm1hJTIwUmVmb3JnZXIlMjBzb2xkaWVyJTIwdGFjdGljYWx8ZW58MHx8fHwxNzY5NTQwNjE4fDA&ixlib=rb-4.1.0&q=85";
    }
    return "https://images.unsplash.com/photo-1680992046626-418f7e910589?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1MDZ8MHwxfHNlYXJjaHw0fHxzZXJ2ZXIlMjByb29tJTIwZGFyayUyMG5lb24lMjBsaWdodHN8ZW58MHx8fHwxNzY5NTQwNjI4fDA&ixlib=rb-4.1.0&q=85";
  };

  return (
    <div
      data-testid={`server-card-${server.id}`}
      className="server-card-bg rounded-sm border border-border/50 overflow-hidden tactical-corner transition-all hover:border-primary/30"
      style={{ backgroundImage: `url(${getBackgroundImage(server.game_type)})` }}
    >
      <div className="server-card-content p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <div className={`h-2 w-2 rounded-full ${getStatusColor(server.status)}`} data-testid={`server-status-indicator-${server.id}`}></div>
              <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80">
                {server.status}
              </span>
            </div>
            <h3 className="font-secondary font-bold text-2xl tracking-tight uppercase text-foreground" data-testid={`server-name-${server.id}`}>
              {server.name}
            </h3>
            <p className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
              {server.game_type === "arma_reforger" ? "Arma Reforger" : "Arma 4"}
            </p>
          </div>
          <button
            data-testid={`delete-server-button-${server.id}`}
            onClick={() => onDelete(server.id)}
            className="text-muted-foreground hover:text-destructive transition-colors p-2"
            aria-label="Delete server"
          >
            <Trash2 size={16} />
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-3">
            <div className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 mb-1">
              Players
            </div>
            <div className="font-mono text-lg font-semibold text-foreground" data-testid={`server-players-${server.id}`}>
              {server.current_players} / {server.max_players}
            </div>
          </div>
          <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-sm p-3">
            <div className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 mb-1">
              Port
            </div>
            <div className="font-mono text-lg font-semibold text-foreground" data-testid={`server-port-${server.id}`}>
              {server.port}
            </div>
          </div>
        </div>

        {/* Install Path */}
        <div className="mb-4">
          <div className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 mb-1">
            Install Path
          </div>
          <div className="font-mono text-xs text-foreground/70 truncate" data-testid={`server-path-${server.id}`}>
            {server.install_path}
          </div>
        </div>

        {/* Control Buttons */}
        <div className="space-y-2">
          <div className="flex gap-2">
            {server.status === "offline" ? (
              <button
                data-testid={`start-server-button-${server.id}`}
                onClick={() => onAction(server.id, "start")}
                className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-9 flex items-center justify-center gap-2 text-sm"
              >
                <Play size={14} />
                <span>Start</span>
              </button>
            ) : (
              <button
                data-testid={`stop-server-button-${server.id}`}
                onClick={() => onAction(server.id, "stop")}
                disabled={server.status === "restarting"}
                className="flex-1 bg-destructive/10 hover:bg-destructive/20 text-destructive border border-destructive/50 font-secondary uppercase tracking-wider rounded-sm transition-all active:scale-95 h-9 flex items-center justify-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Square size={14} />
                <span>Stop</span>
              </button>
            )}
            <button
              data-testid={`restart-server-button-${server.id}`}
              onClick={() => onAction(server.id, "restart")}
              disabled={server.status === "restarting"}
              className="flex-1 bg-accent/10 hover:bg-accent/20 text-accent border border-accent/50 font-secondary uppercase tracking-wider rounded-sm transition-all active:scale-95 h-9 flex items-center justify-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RotateCw size={14} />
              <span>Restart</span>
            </button>
          </div>
          
          {/* Additional Actions */}
          <div className="flex gap-2">
            <button
              data-testid={`config-button-${server.id}`}
              onClick={() => onOpenConfig(server.id)}
              className="flex-1 bg-secondary/50 hover:bg-secondary/70 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm transition-all active:scale-95 h-9 flex items-center justify-center gap-2 text-xs"
              aria-label="Server configuration"
            >
              <Settings size={14} />
              <span>Config</span>
            </button>
            <button
              data-testid={`mods-button-${server.id}`}
              onClick={() => onOpenMods(server.id)}
              className="flex-1 bg-secondary/50 hover:bg-secondary/70 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm transition-all active:scale-95 h-9 flex items-center justify-center gap-2 text-xs"
              aria-label="Manage mods"
            >
              <Package size={14} />
              <span>Mods</span>
            </button>
            <button
              data-testid={`logs-button-${server.id}`}
              onClick={() => onOpenLogs(server.id)}
              className="flex-1 bg-secondary/50 hover:bg-secondary/70 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm transition-all active:scale-95 h-9 flex items-center justify-center gap-2 text-xs"
              aria-label="View logs"
            >
              <FileText size={14} />
              <span>Logs</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}