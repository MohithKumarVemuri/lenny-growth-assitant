import React, { useState } from 'react';
import { Mic, ChevronDown, ChevronUp, ExternalLink, Award } from 'lucide-react';
import { SourceCitation } from '../../lib/api';

interface SourceBadgeProps {
  sources: SourceCitation[];
}

export const SourceBadgeList: React.FC<SourceBadgeProps> = ({ sources }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mb-3 space-y-1.5">
      <div className="flex items-center gap-1.5 text-[11px] font-semibold tracking-wide uppercase text-amber-400">
        <Award className="w-3.5 h-3.5" />
        Verified Grounding Sources ({sources.length}):
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {sources.map((s, idx) => {
          const isExpanded = expandedIndex === idx;
          return (
            <div
              key={idx}
              className="bg-[#131b2a] border border-[#2a3850] hover:border-amber-500/40 rounded-lg p-2.5 transition text-xs shadow-sm"
            >
              <div
                className="flex items-start justify-between cursor-pointer gap-2"
                onClick={() => setExpandedIndex(isExpanded ? null : idx)}
              >
                <div className="flex items-start gap-2 truncate">
                  <div className="p-1 rounded bg-amber-500/10 text-amber-400 mt-0.5 flex-shrink-0">
                    <Mic className="w-3 h-3" />
                  </div>
                  <div className="truncate">
                    <div className="font-medium text-slate-200 truncate">{s.episode}</div>
                    <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
                      <span>Guest: <strong className="text-slate-300 font-medium">{s.guest}</strong></span>
                      {s.timestamp && (
                        <>
                          <span>•</span>
                          <span className="font-mono text-amber-400/80">{s.timestamp}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-1 text-slate-400">
                  <span className="text-[10px] font-mono bg-[#1c2638] px-1.5 py-0.5 rounded text-amber-400/90">
                    {Math.round(s.score * 100)}% match
                  </span>
                  {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </div>
              </div>

              {/* Expandable Verbatim Transcript Excerpt */}
              {isExpanded && (
                <div className="mt-2 pt-2 border-t border-[#1c2638] text-[11px] text-slate-300 leading-relaxed font-sans bg-[#0b0f17] p-2 rounded border border-[#1c2638]">
                  <div className="text-[10px] text-slate-400 uppercase font-semibold mb-1">
                    Retrieved Transcript Excerpt:
                  </div>
                  <p className="italic">"{s.text}"</p>
                  {s.url && (
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 mt-2 text-[11px] text-sky-400 hover:underline font-medium"
                    >
                      Search Episode Online <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
