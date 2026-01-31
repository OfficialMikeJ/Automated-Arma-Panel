import { useState } from "react";
import { X } from "lucide-react";

export default function AddServerModal({ onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: "",
    game_type: "arma_reforger",
    port: 2001,
    max_players: 64,
    install_path: "/home/steamcmd/servers/",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm" data-testid="add-server-modal">
      <div className="bg-card border border-border/50 rounded-sm p-8 max-w-lg w-full tactical-corner">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-secondary font-bold text-2xl tracking-tight uppercase text-foreground">
            Add Server Instance
          </h2>
          <button
            data-testid="close-modal-button"
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
              Server Name
            </label>
            <input
              data-testid="server-name-input"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50 font-mono"
              placeholder="My Server"
              required
            />
          </div>

          <div>
            <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
              Game Type
            </label>
            <select
              data-testid="game-type-select"
              value={formData.game_type}
              onChange={(e) => setFormData({ ...formData, game_type: e.target.value })}
              className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50 font-mono"
            >
              <option value="arma_reforger">Arma Reforger</option>
              <option value="arma_4">Arma 4</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                Port
              </label>
              <input
                data-testid="port-input"
                type="number"
                value={formData.port}
                onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50 font-mono"
                required
              />
            </div>
            <div>
              <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
                Max Players
              </label>
              <input
                data-testid="max-players-input"
                type="number"
                value={formData.max_players}
                onChange={(e) => setFormData({ ...formData, max_players: parseInt(e.target.value) })}
                className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50 font-mono"
                required
              />
            </div>
          </div>

          <div>
            <label className="font-mono text-xs uppercase tracking-widest text-muted-foreground/80 block mb-2">
              Install Path
            </label>
            <input
              data-testid="install-path-input"
              type="text"
              value={formData.install_path}
              onChange={(e) => setFormData({ ...formData, install_path: e.target.value })}
              className="flex h-10 w-full rounded-sm border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50 font-mono"
              placeholder="/home/steamcmd/servers/"
              required
            />
          </div>

          <div className="flex gap-3 mt-6">
            <button
              type="button"
              data-testid="cancel-button"
              onClick={onClose}
              className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-secondary uppercase tracking-wider rounded-sm border border-border transition-all active:scale-95 h-10"
            >
              Cancel
            </button>
            <button
              type="submit"
              data-testid="submit-server-button"
              className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm shadow-sm transition-all active:scale-95 h-10 glow-primary"
            >
              Add Server
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}