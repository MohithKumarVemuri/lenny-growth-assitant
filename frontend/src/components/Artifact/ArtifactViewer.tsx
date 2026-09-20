import React, { useState } from 'react';
import { X, Copy, Check, Download, Code, Eye, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { SandboxedIframe } from './SandboxedIframe';
import { Artifact } from '../../lib/api';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({ artifact, onClose }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(artifact.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error('Failed to copy code:', e);
    }
  };

  const handleDownload = () => {
    const ext = artifact.type === 'html' ? 'html' : 'md';
    const blob = new Blob([artifact.content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${artifact.title.toLowerCase().replace(/[^a-z0-9]/g, '_')}.${ext}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <aside className="w-full lg:w-[540px] xl:w-[620px] bg-[#070a0f] border-l border-[#1c2638] flex flex-col h-full z-20 shadow-2xl transition-all">
      {/* Artifact Header */}
      <div className="p-4 border-b border-[#1c2638] flex items-center justify-between bg-[#0b0f17]">
        <div className="flex items-center gap-2 truncate pr-2">
          <div className="w-7 h-7 rounded bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 flex-shrink-0">
            <Sparkles className="w-4 h-4" />
          </div>
          <div className="truncate">
            <h2 className="text-xs font-semibold text-white truncate">{artifact.title}</h2>
            <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">
              Artifact • {artifact.type.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Header Actions */}
        <div className="flex items-center gap-1.5 flex-shrink-0">
          {/* Tab Switcher */}
          <div className="flex bg-[#131b2a] border border-[#2a3850] rounded-lg p-0.5 text-xs mr-1">
            <button
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition ${
                activeTab === 'preview'
                  ? 'bg-amber-500/20 text-amber-300 font-medium'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Eye className="w-3 h-3" />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition ${
                activeTab === 'code'
                  ? 'bg-amber-500/20 text-amber-300 font-medium'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code className="w-3 h-3" />
              <span>Source</span>
            </button>
          </div>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg bg-[#131b2a] hover:bg-[#1c2638] border border-[#2a3850] text-slate-300 hover:text-white transition"
            title="Copy Source"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>

          {/* Download Button */}
          <button
            onClick={handleDownload}
            className="p-1.5 rounded-lg bg-[#131b2a] hover:bg-[#1c2638] border border-[#2a3850] text-slate-300 hover:text-white transition"
            title="Download Artifact"
          >
            <Download className="w-3.5 h-3.5" />
          </button>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-[#131b2a] hover:bg-[#1c2638] border border-[#2a3850] text-slate-400 hover:text-rose-400 transition"
            title="Close Canvas"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Artifact Body */}
      <div className="flex-1 overflow-hidden p-4">
        {activeTab === 'preview' ? (
          artifact.type === 'html' ? (
            <SandboxedIframe content={artifact.content} title={artifact.title} />
          ) : (
            <div className="h-full overflow-y-auto bg-[#0b0f17] p-4 rounded-lg border border-[#1c2638] prose-dark text-xs">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {artifact.content}
              </ReactMarkdown>
            </div>
          )
        ) : (
          <div className="h-full flex flex-col bg-[#070a0f] rounded-lg border border-[#1c2638] overflow-hidden">
            <div className="bg-[#131b2a] px-3 py-1.5 border-b border-[#1c2638] text-[10px] text-slate-400 font-mono flex items-center justify-between">
              <span>{artifact.title}.{artifact.type === 'html' ? 'html' : 'md'}</span>
              <span>{artifact.content.length} characters</span>
            </div>
            <pre className="flex-1 p-3 font-mono text-xs text-slate-300 overflow-auto whitespace-pre-wrap select-all">
              <code>{artifact.content}</code>
            </pre>
          </div>
        )}
      </div>
    </aside>
  );
};
