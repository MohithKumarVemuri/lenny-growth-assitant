import React, { useMemo } from 'react';
import DOMPurify from 'dompurify';
import { ShieldCheck } from 'lucide-react';

interface SandboxedIframeProps {
  content: string;
  title: string;
}

export const SandboxedIframe: React.FC<SandboxedIframeProps> = ({ content, title }) => {
  // Sanitize markup prior to injecting into iframe srcDoc
  const cleanHtml = useMemo(() => {
    return DOMPurify.sanitize(content, {
      WHOLE_DOCUMENT: true,
      ADD_TAGS: ['style', 'link', 'script', 'input', 'button', 'form'],
      ADD_ATTR: ['target', 'id', 'class', 'style', 'type', 'value', 'min', 'max', 'oninput', 'onclick']
    });
  }, [content]);

  return (
    <div className="flex flex-col h-full bg-[#0b0f17] rounded-lg overflow-hidden border border-[#1c2638] shadow-inner">
      {/* Isolation Status Header */}
      <div className="bg-[#131b2a] border-b border-[#1c2638] px-3 py-1.5 flex items-center justify-between text-[11px]">
        <span className="text-slate-400 truncate max-w-[200px]">
          Target: <strong className="text-slate-200">{title}</strong>
        </span>
        <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800/40 font-medium">
          <ShieldCheck className="w-3 h-3" />
          Isolated (null origin sandbox)
        </span>
      </div>

      {/* Sandboxed Iframe Container */}
      <iframe
        title={title}
        srcDoc={cleanHtml}
        // Strict security isolation: allow scripts to run for interactivity,
        // but omit allow-same-origin to prevent access to parent cookies, local storage, and DOM.
        sandbox="allow-scripts"
        className="w-full flex-1 border-none bg-[#0f172a]"
      />
    </div>
  );
};
