import React from 'react';
import { Cpu, Cloud, Zap, AlertCircle } from 'lucide-react';
import { HealthData } from '../../lib/api';

interface ModelSelectorProps {
  currentProvider: string;
  onSelectProvider: (provider: string) => void;
  health: HealthData | null;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  currentProvider,
  onSelectProvider,
  health
}) => {
  const ollamaOnline = health?.ollama_status?.online ?? false;
  const claudeConfigured = health?.cloud_configured?.anthropic ?? false;
  const openaiConfigured = health?.cloud_configured?.openai ?? false;

  return (
    <div className="flex items-center gap-1.5 bg-[#131b2a] border border-[#2a3850] rounded-lg p-1 text-xs shadow-sm">
      {/* Ollama Local */}
      <button
        onClick={() => onSelectProvider('ollama')}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md transition font-medium ${
          currentProvider === 'ollama'
            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
            : 'text-slate-400 hover:text-slate-200'
        }`}
        title={ollamaOnline ? 'Ollama running locally' : 'Ollama not detected locally (will fallback to simulated stream)'}
      >
        <Cpu className="w-3.5 h-3.5" />
        <span>Ollama (Local)</span>
        <span
          className={`w-1.5 h-1.5 rounded-full ${
            ollamaOnline ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
          }`}
        />
      </button>

      {/* Claude 3.5 Sonnet */}
      <button
        onClick={() => onSelectProvider('claude')}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md transition font-medium ${
          currentProvider === 'claude'
            ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
            : 'text-slate-400 hover:text-slate-200'
        }`}
        title={claudeConfigured ? 'Claude 3.5 Sonnet API Active' : 'ANTHROPIC_API_KEY required in .env'}
      >
        <Cloud className="w-3.5 h-3.5" />
        <span>Claude 3.5 Sonnet</span>
      </button>

      {/* OpenAI GPT-4o */}
      <button
        onClick={() => onSelectProvider('openai')}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md transition font-medium ${
          currentProvider === 'openai'
            ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
            : 'text-slate-400 hover:text-slate-200'
        }`}
        title={openaiConfigured ? 'OpenAI GPT-4o Active' : 'OPENAI_API_KEY required in .env'}
      >
        <Zap className="w-3.5 h-3.5" />
        <span>GPT-4o</span>
      </button>

      {/* Simulation Fallback */}
      <button
        onClick={() => onSelectProvider('sim')}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md transition font-medium ${
          currentProvider === 'sim'
            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
            : 'text-slate-400 hover:text-slate-200'
        }`}
        title="Deterministic test mode with zero dependencies"
      >
        <span>Demo Simulation</span>
      </button>
    </div>
  );
};
