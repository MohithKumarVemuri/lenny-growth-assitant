import React from 'react';
import { User, Sparkles, ExternalLink, Bot, ArrowRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Message, Artifact } from '../../lib/api';
import { SourceBadgeList } from './SourceBadge';
import { strip_artifact_tags } from './artifact_helpers';

interface MessageItemProps {
  message: Message;
  onOpenArtifact?: (artifact: Artifact) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message, onOpenArtifact }) => {
  const isUser = message.role === 'user';
  // Strip raw <artifact>...</artifact> tags from displayed conversational text
  const cleanContent = isUser ? message.content : strip_artifact_tags(message.content);
  const artifacts = message.artifacts || [];

  return (
    <div className={`py-4 px-4 md:px-8 flex gap-3.5 transition ${isUser ? 'bg-transparent' : 'bg-[#0e1420]/70 border-y border-[#1c2638]/40'}`}>
      {/* Avatar */}
      <div className="flex-shrink-0 mt-0.5">
        {isUser ? (
          <div className="w-8 h-8 rounded-full bg-slate-700/60 border border-slate-600 flex items-center justify-center text-slate-300">
            <User className="w-4 h-4" />
          </div>
        ) : (
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-amber-600 to-amber-400 border border-amber-300/30 flex items-center justify-center text-black font-bold shadow-md shadow-amber-500/10">
            <Bot className="w-4 h-4 fill-current" />
          </div>
        )}
      </div>

      {/* Content Region */}
      <div className="flex-1 overflow-hidden space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-200">
            {isUser ? 'You' : 'The Lenny Growth Assistant'}
          </span>
          {!isUser && message.model_provider && (
            <span className="text-[10px] text-slate-400 font-mono bg-[#131b2a] border border-[#2a3850] px-1.5 py-0.5 rounded">
              {message.model_provider}
            </span>
          )}
          {!isUser && message.mode && message.mode !== 'default' && (
            <span className="text-[10px] text-indigo-400 font-mono bg-indigo-950/40 border border-indigo-800/40 px-1.5 py-0.5 rounded">
              {message.mode === 'ship30' ? 'Ship 30 for 30' : 'Artifact Mode'}
            </span>
          )}
        </div>

        {/* Citations list for assistant response */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <SourceBadgeList sources={message.sources} />
        )}

        {/* Formatted Markdown Body */}
        <div className="prose-dark text-xs md:text-sm leading-relaxed break-words">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {cleanContent}
          </ReactMarkdown>
        </div>

        {/* Artifact Action Card */}
        {!isUser && artifacts.length > 0 && onOpenArtifact && (
          <div className="mt-3 pt-2">
            {artifacts.map((art, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 rounded-xl bg-gradient-to-r from-amber-950/20 via-[#131b2a] to-[#131b2a] border border-amber-500/30 hover:border-amber-400/50 shadow-md transition"
              >
                <div className="flex items-center gap-2.5 truncate pr-2">
                  <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <div className="truncate">
                    <div className="text-xs font-semibold text-white truncate">{art.title}</div>
                    <div className="text-[11px] text-amber-400/80 uppercase font-mono tracking-wider">
                      Interactive {art.type} Artifact Ready
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => onOpenArtifact(art)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-black text-xs font-semibold shadow transition flex-shrink-0"
                >
                  Open in Canvas
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
