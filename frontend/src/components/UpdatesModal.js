import { useState, useEffect } from "react";
import { X, AlertCircle, CheckCircle, Info } from "lucide-react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function UpdatesModal({ onClose }) {
  const [loading, setLoading] = useState(true);
  const [changelog, setChangelog] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchChangelog();
  }, []);

  const fetchChangelog = async () => {
    try {
      const response = await axios.get(`${API}/changelog`);
      setChangelog(response.data.content);
    } catch (err) {
      setError("Failed to load updates");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6">
      <div className="bg-card/95 border border-border/50 rounded-sm w-full max-w-3xl max-h-[80vh] flex flex-col tactical-corner">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
              <Info className="text-primary" size={20} />
            </div>
            <div>
              <h2 className="font-secondary font-bold text-xl uppercase tracking-wider text-primary">
                Updates & Fixes
              </h2>
              <p className="font-mono text-xs text-muted-foreground">Latest changes and improvements</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-sm hover:bg-secondary/50 flex items-center justify-center transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="text-primary font-mono">Loading updates...</div>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-3 p-4 bg-destructive/10 border border-destructive/30 rounded-sm">
              <AlertCircle className="text-destructive" size={20} />
              <span className="font-mono text-sm text-destructive">{error}</span>
            </div>
          )}

          {!loading && !error && (
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown
                components={{
                  h1: ({ children }) => (
                    <h1 className="font-secondary text-2xl font-bold text-primary uppercase tracking-wider mb-4">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="font-secondary text-xl font-bold text-primary uppercase tracking-wide mb-3 mt-6">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="font-secondary text-lg font-semibold text-accent uppercase tracking-wide mb-2 mt-4">
                      {children}
                    </h3>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc list-inside space-y-1 font-mono text-sm text-foreground/90">
                      {children}
                    </ul>
                  ),
                  li: ({ children }) => (
                    <li className="flex items-start gap-2">
                      <CheckCircle size={16} className="text-primary mt-0.5 flex-shrink-0" />
                      <span>{children}</span>
                    </li>
                  ),
                  p: ({ children }) => (
                    <p className="font-mono text-sm text-muted-foreground mb-3">{children}</p>
                  ),
                  code: ({ children }) => (
                    <code className="bg-secondary/50 px-1.5 py-0.5 rounded text-primary font-mono text-xs">
                      {children}
                    </code>
                  ),
                }}
              >
                {changelog}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-border/30">
          <button
            onClick={onClose}
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-secondary uppercase tracking-wider rounded-sm h-10 transition-all active:scale-95"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}