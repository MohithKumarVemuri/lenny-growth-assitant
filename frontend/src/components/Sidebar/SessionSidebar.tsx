import React from 'react';
import { Plus, MessageSquare, Trash2, Mic, Sparkles, Database } from 'lucide-react';
import { Session, HealthData } from '../../lib/api';

interface SessionSidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  health: HealthData | null;
}

export const SessionSidebar: React.FC<SessionSidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  health
}) => {
  return (
    <aside className="w-64 bg-[#070a0f] border-r border-[#1c2638] flex flex-col h-full flex-shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-[#1c2638]">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-amber-600 to-amber-400 flex items-center justify-center shadow-lg shadow-amber-500/20 text-black">
            <Mic className="w-5 h-5 fill-current" />
          </div>
          <div>
            <h1 className="font-semibold text-sm tracking-tight text-white flex items-center gap-1.5">
              Lenny Assistant
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                PRO
              </span>
            </h1>
            <p className="text-xs text-slate-400">Grounded Growth Strategy</p>
          </div>
        </div>

        {/* New Chat Button */}
        <button
          onClick={onNewSession}
          className="mt-4 w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-[#131b2a] hover:bg-[#1c2638] border border-[#2a3850] hover:border-amber-500/40 text-slate-200 hover:text-white transition text-xs font-medium shadow-sm group"
        >
          <Plus className="w-3.5 h-3.5 text-amber-400 group-hover:rotate-90 transition-transform" />
          New Conversation
        </button>
      </div>

      {/* Session History List */}
      <div className="flex-1 overflow-y-auto px-2 py-3 space-y-1">
        <div className="px-2 py-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Recent Conversations
        </div>

        {sessions.length === 0 ? (
          <div className="px-3 py-6 text-center text-xs text-slate-400">
            No past conversations yet.
          </div>
        ) : (
          sessions.map((s) => {
            const isActive = s.id === activeSessionId;
            return (
              <div
                key={s.id}
                onClick={() => onSelectSession(s.id)}
                className={`group flex items-center justify-between px-2.5 py-2 rounded-lg cursor-pointer text-xs transition ${
                  isActive
                    ? 'bg-[#131b2a] text-amber-400 border border-amber-500/30 font-medium'
                    : 'text-slate-300 hover:bg-[#131b2a]/60 hover:text-white border border-transparent'
                }`}
              >
                <div className="flex items-center gap-2 truncate pr-1">
                  <MessageSquare className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'text-amber-400' : 'text-slate-400'}`} />
                  <span className="truncate">{s.title || 'Conversation'}</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(s.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 rounded transition"
                  title="Delete chat"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Operational Diagnostic Footer */}
      <div className="p-3 border-t border-[#1c2638] bg-[#0b0f17] text-[11px] space-y-1.5">
        <div className="flex items-center justify-between text-slate-400">
          <span className="flex items-center gap-1.5">
            <Database className="w-3 h-3 text-slate-400" />
            Storage Mode:
          </span>
          <span className="text-slate-300 font-mono">
            {health?.database_mode === 'postgresql_pgvector' ? 'PostgreSQL (pgvector)' : 'SQLite Local'}
          </span>
        </div>
        <div className="flex items-center justify-between text-slate-400">
          <span className="flex items-center gap-1.5">
            <Sparkles className="w-3 h-3 text-amber-400" />
            Indexed Vectors:
          </span>
          <span className="text-amber-400 font-mono font-medium">
            {health?.vector_count ?? 20} chunks
          </span>
        </div>
      </div>
    </aside>
  );
};
