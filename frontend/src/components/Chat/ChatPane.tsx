import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, BookOpen, Layers, Loader2, ArrowUpRight } from 'lucide-react';
import { Message, SourceCitation, Artifact, HealthData } from '../../lib/api';
import { MessageItem } from './MessageItem';
import { ModelSelector } from './ModelSelector';
import { SourceBadgeList } from './SourceBadge';

interface ChatPaneProps {
  sessionTitle: string;
  messages: Message[];
  isStreaming: boolean;
  streamingToken: string;
  streamingSources: SourceCitation[];
  statusText: string | null;
  currentProvider: string;
  onSelectProvider: (provider: string) => void;
  onSendMessage: (text: string, mode: string) => void;
  onOpenArtifact: (artifact: Artifact) => void;
  health: HealthData | null;
}

const PROMPT_SUGGESTIONS = [
  {
    title: "Brian Chesky on Founder Mode",
    desc: "Staying in details vs conventional manager delegation",
    prompt: "What is Founder Mode according to Brian Chesky on Lenny's Podcast, and how does it contrast with Manager Mode?",
    mode: "default"
  },
  {
    title: "Ship 30 for 30 Essay: Elena Verna",
    desc: "1,250-word executive essay on B2B PLG and Product-Led Sales",
    prompt: "Write a Ship 30 for 30 essay on Elena Verna's B2B Product-Led Growth playbook and why free users feed enterprise sales.",
    mode: "ship30"
  },
  {
    title: "Interactive Retention Widget",
    desc: "HTML/CSS cohort calculator with Gustaf Alströmer YC benchmarks",
    prompt: "Create an interactive retention cohort calculator artifact with sliders for Day 1, Day 7, Day 30 retention.",
    mode: "artifact"
  },
  {
    title: "Shreyas Doshi: High Agency & LNO",
    desc: "Bending reality and prioritizing 10x leverage tasks",
    prompt: "How does Shreyas Doshi define High Agency and how should a product manager apply the LNO Framework?",
    mode: "default"
  }
];

export const ChatPane: React.FC<ChatPaneProps> = ({
  sessionTitle,
  messages,
  isStreaming,
  streamingToken,
  streamingSources,
  statusText,
  currentProvider,
  onSelectProvider,
  onSendMessage,
  onOpenArtifact,
  health
}) => {
  const [inputText, setInputText] = useState('');
  const [activeMode, setActiveMode] = useState<'default' | 'ship30' | 'artifact'>('default');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingToken, isStreaming]);

  const handleSend = () => {
    if (!inputText.trim() || isStreaming) return;
    onSendMessage(inputText.trim(), activeMode);
    setInputText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 180)}px`;
  };

  return (
    <main className="flex-1 flex flex-col h-full bg-[#0b0f17] overflow-hidden">
      {/* Top Navbar */}
      <header className="p-3 md:px-6 border-b border-[#1c2638] flex flex-wrap items-center justify-between gap-3 bg-[#0b0f17]/90 backdrop-blur z-10">
        <div className="truncate max-w-[280px] md:max-w-md">
          <h2 className="text-xs md:text-sm font-semibold text-white truncate">
            {sessionTitle || 'New Conversation'}
          </h2>
          <span className="text-[10px] text-slate-400 font-mono">
            Grounding Engine: <strong className="text-amber-400 font-normal">Lenny's Podcast Transcripts</strong>
          </span>
        </div>

        {/* Runtime Model Selector */}
        <ModelSelector
          currentProvider={currentProvider}
          onSelectProvider={onSelectProvider}
          health={health}
        />
      </header>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 && !isStreaming ? (
          /* Empty State / Welcome Screen */
          <div className="max-w-2xl mx-auto px-4 py-12 flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-600 to-amber-400 text-black flex items-center justify-center shadow-xl shadow-amber-500/20 mb-4">
              <Sparkles className="w-6 h-6 fill-current" />
            </div>
            <h1 className="text-xl md:text-2xl font-bold text-white tracking-tight">
              The Lenny Growth Assistant
            </h1>
            <p className="mt-2 text-xs md:text-sm text-slate-400 max-w-lg leading-relaxed">
              Synthesize tactical wisdom from 200+ hours of Lenny's Podcast. Ask product questions,
              generate Ship 30 for 30 executive essays, or build live interactive artifacts.
            </p>

            {/* Prompt Starter Pills */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-3 w-full text-left">
              {PROMPT_SUGGESTIONS.map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => {
                    setActiveMode(item.mode as any);
                    onSendMessage(item.prompt, item.mode);
                  }}
                  className="p-3.5 rounded-xl bg-[#131b2a]/80 hover:bg-[#1c2638] border border-[#2a3850] hover:border-amber-500/40 cursor-pointer transition shadow-sm group"
                >
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-200 group-hover:text-amber-300">
                    <span>{item.title}</span>
                    <ArrowUpRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-amber-400 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                  </div>
                  <div className="mt-1 text-[11px] text-slate-400 leading-snug">
                    {item.desc}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Message Stream */
          <div className="divide-y divide-[#1c2638]/40">
            {messages.map((m) => (
              <MessageItem
                key={m.id}
                message={m}
                onOpenArtifact={onOpenArtifact}
              />
            ))}

            {/* Live Streaming Response Bubble */}
            {isStreaming && (
              <div className="py-4 px-4 md:px-8 flex gap-3.5 bg-[#0e1420]/70 border-y border-[#1c2638]/40">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-amber-600 to-amber-400 flex items-center justify-center text-black font-bold shadow-md">
                  <Sparkles className="w-4 h-4 fill-current animate-spin" />
                </div>
                <div className="flex-1 overflow-hidden space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-white">The Lenny Growth Assistant</span>
                    <span className="text-[10px] text-amber-400 font-mono bg-[#131b2a] px-2 py-0.5 rounded border border-amber-500/20 animate-pulse">
                      Generating...
                    </span>
                  </div>

                  {/* Status Banner */}
                  {statusText && (
                    <div className="text-xs text-slate-400 italic flex items-center gap-1.5 py-1">
                      <Loader2 className="w-3 h-3 animate-spin text-amber-400" />
                      {statusText}
                    </div>
                  )}

                  {/* Streaming Sources */}
                  {streamingSources.length > 0 && (
                    <SourceBadgeList sources={streamingSources} />
                  )}

                  {/* Tokens */}
                  {streamingToken && (
                    <div className="prose-dark text-xs md:text-sm leading-relaxed whitespace-pre-wrap">
                      {streamingToken}
                      <span className="inline-block w-1.5 h-3.5 bg-amber-400 ml-1 animate-pulse" />
                    </div>
                  )}
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Dock */}
      <footer className="p-3 md:p-5 border-t border-[#1c2638] bg-[#070a0f]">
        <div className="max-w-3xl mx-auto space-y-2">
          {/* Mode Selector Chips */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-[11px] text-slate-400 font-medium mr-1">Mode:</span>
            <button
              onClick={() => setActiveMode('default')}
              className={`px-2.5 py-0.5 rounded-full transition text-[11px] font-medium ${
                activeMode === 'default'
                  ? 'bg-amber-500 text-black shadow-sm'
                  : 'bg-[#131b2a] text-slate-300 hover:bg-[#1c2638] border border-[#2a3850]'
              }`}
            >
              🎙️ Grounded Q&A
            </button>
            <button
              onClick={() => setActiveMode('ship30')}
              className={`px-2.5 py-0.5 rounded-full transition text-[11px] font-medium flex items-center gap-1 ${
                activeMode === 'ship30'
                  ? 'bg-indigo-500 text-white shadow-sm'
                  : 'bg-[#131b2a] text-slate-300 hover:bg-[#1c2638] border border-[#2a3850]'
              }`}
            >
              <BookOpen className="w-3 h-3" />
              Ship 30 for 30 Essay (~1,250 words)
            </button>
            <button
              onClick={() => setActiveMode('artifact')}
              className={`px-2.5 py-0.5 rounded-full transition text-[11px] font-medium flex items-center gap-1 ${
                activeMode === 'artifact'
                  ? 'bg-sky-500 text-white shadow-sm'
                  : 'bg-[#131b2a] text-slate-300 hover:bg-[#1c2638] border border-[#2a3850]'
              }`}
            >
              <Layers className="w-3 h-3" />
              Artifact Generator
            </button>
          </div>

          {/* Textarea Input Container */}
          <div className="relative flex items-end bg-[#131b2a] border border-[#2a3850] focus-within:border-amber-500/60 focus-within:ring-1 focus-within:ring-amber-500/20 rounded-xl p-2 transition shadow-lg">
            <textarea
              ref={textareaRef}
              value={inputText}
              onChange={handleTextareaInput}
              onKeyDown={handleKeyDown}
              disabled={isStreaming}
              placeholder={
                activeMode === 'ship30'
                  ? 'Enter topic for a Ship 30 for 30 essay (e.g. Elena Verna on B2B PLG)...'
                  : activeMode === 'artifact'
                  ? 'Describe the interactive tool or document to build (e.g. Day 30 retention calculator)...'
                  : "Ask a product or growth question grounded in Lenny's podcast..."
              }
              rows={1}
              className="flex-1 bg-transparent text-xs md:text-sm text-white placeholder-slate-500 focus:outline-none resize-none px-2 py-1 max-h-40"
            />

            <button
              onClick={handleSend}
              disabled={!inputText.trim() || isStreaming}
              className={`p-2 rounded-lg transition flex-shrink-0 ${
                inputText.trim() && !isStreaming
                  ? 'bg-amber-500 hover:bg-amber-400 text-black shadow'
                  : 'bg-[#1c2638] text-slate-500 cursor-not-allowed'
              }`}
            >
              {isStreaming ? (
                <Loader2 className="w-4 h-4 animate-spin text-slate-400" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
          <div className="text-center text-[10px] text-slate-400">
            Answers are strictly retrieved and attributed from Lenny’s Podcast transcripts. Press Enter to send, Shift+Enter for new line.
          </div>
        </div>
      </footer>
    </main>
  );
};
