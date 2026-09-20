import React, { useState, useEffect, useCallback } from 'react';
import { SessionSidebar } from './components/Sidebar/SessionSidebar';
import { ChatPane } from './components/Chat/ChatPane';
import { ArtifactViewer } from './components/Artifact/ArtifactViewer';
import {
  fetchHealth,
  fetchSessions,
  createSession,
  fetchSessionDetail,
  deleteSession,
  Session,
  Message,
  Artifact,
  SourceCitation,
  HealthData
} from './lib/api';
import { useChatStream } from './hooks/useChatStream';

export function App() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeSessionTitle, setActiveSessionTitle] = useState<string>('New Conversation');
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [currentProvider, setCurrentProvider] = useState<string>('ollama');

  // Streaming state from hook
  const { isStreaming, statusText, currentSources, sendMessage } = useChatStream();
  const [streamingToken, setStreamingToken] = useState<string>('');
  const [streamingSources, setStreamingSources] = useState<SourceCitation[]>([]);

  // Load health & sessions on boot
  useEffect(() => {
    async function init() {
      try {
        const h = await fetchHealth();
        setHealth(h);
        if (h.default_provider) {
          setCurrentProvider(h.default_provider);
        }
      } catch (err) {
        console.warn('Backend health check error:', err);
      }

      try {
        const list = await fetchSessions();
        setSessions(list);
        if (list.length > 0) {
          selectSession(list[0].id);
        } else {
          handleNewSession();
        }
      } catch (err) {
        console.warn('Failed to load sessions:', err);
        handleNewSession();
      }
    }
    init();
  }, []);

  const selectSession = useCallback(async (sessionId: string) => {
    setActiveSessionId(sessionId);
    setStreamingToken('');
    setStreamingSources([]);
    try {
      const detail = await fetchSessionDetail(sessionId);
      setActiveSessionTitle(detail.title);
      setMessages(detail.messages || []);
      // If session already has artifacts, load the latest
      if (detail.artifacts && detail.artifacts.length > 0) {
        setActiveArtifact(detail.artifacts[detail.artifacts.length - 1]);
      } else {
        setActiveArtifact(null);
      }
    } catch (err) {
      console.error('Error fetching session details:', err);
    }
  }, []);

  const handleNewSession = useCallback(async () => {
    try {
      const newSession = await createSession('New Conversation');
      setSessions(prev => [newSession, ...prev]);
      setActiveSessionId(newSession.id);
      setActiveSessionTitle('New Conversation');
      setMessages([]);
      setActiveArtifact(null);
      setStreamingToken('');
      setStreamingSources([]);
    } catch (err) {
      console.error('Failed to create new session:', err);
    }
  }, []);

  const handleDeleteSession = useCallback(async (sessionId: string) => {
    try {
      await deleteSession(sessionId);
      const remaining = sessions.filter(s => s.id !== sessionId);
      setSessions(remaining);
      if (activeSessionId === sessionId) {
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          handleNewSession();
        }
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  }, [sessions, activeSessionId, selectSession, handleNewSession]);

  const handleSendMessage = useCallback(async (text: string, mode: string) => {
    let currentId = activeSessionId;
    if (!currentId) {
      const newSession = await createSession(text.substring(0, 40));
      setSessions(prev => [newSession, ...prev]);
      currentId = newSession.id;
      setActiveSessionId(currentId);
      setActiveSessionTitle(newSession.title);
    }

    // Optimistically add user message
    const userMsg: Message = {
      id: `temp-${Date.now()}`,
      session_id: currentId,
      role: 'user',
      content: text,
      model_provider: currentProvider,
      mode: mode
    };
    setMessages(prev => [...prev, userMsg]);
    setStreamingToken('');
    setStreamingSources([]);

    await sendMessage(
      currentId,
      text,
      currentProvider,
      mode,
      // onToken
      (token) => {
        setStreamingToken(prev => prev + token);
      },
      // onSources
      (sources) => {
        setStreamingSources(sources);
      },
      // onArtifact
      (artifact) => {
        setActiveArtifact(artifact);
      },
      // onComplete
      async (fullText, sources, artifact) => {
        setStreamingToken('');
        setStreamingSources([]);
        if (artifact) {
          setActiveArtifact(artifact);
        }
        // Refresh session from database to persist verified message IDs
        if (currentId) {
          try {
            const detail = await fetchSessionDetail(currentId);
            setMessages(detail.messages || []);
            setActiveSessionTitle(detail.title);
            // Refresh sessions list in case title was updated
            const list = await fetchSessions();
            setSessions(list);
          } catch (e) {
            console.error('Error refreshing session:', e);
          }
        }
      },
      // onError
      (err) => {
        setStreamingToken('');
        setStreamingSources([]);
        const errorMsg: Message = {
          id: `err-${Date.now()}`,
          session_id: currentId!,
          role: 'assistant',
          content: `⚠️ **Error communicating with assistant:** ${err}`,
          model_provider: currentProvider,
          mode: mode
        };
        setMessages(prev => [...prev, errorMsg]);
      }
    );
  }, [activeSessionId, currentProvider, sendMessage]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0b0f17] text-slate-100 font-sans">
      {/* 1. Left Sidebar */}
      <SessionSidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={selectSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        health={health}
      />

      {/* 2. Center Chat Pane */}
      <div className="flex-1 flex min-w-0 h-full">
        <ChatPane
          sessionTitle={activeSessionTitle}
          messages={messages}
          isStreaming={isStreaming}
          streamingToken={streamingToken}
          streamingSources={streamingSources}
          statusText={statusText}
          currentProvider={currentProvider}
          onSelectProvider={setCurrentProvider}
          onSendMessage={handleSendMessage}
          onOpenArtifact={setActiveArtifact}
          health={health}
        />

        {/* 3. Claude-Style Sandboxed Artifact Viewer Drawer */}
        {activeArtifact && (
          <ArtifactViewer
            artifact={activeArtifact}
            onClose={() => setActiveArtifact(null)}
          />
        )}
      </div>
    </div>
  );
}

export default App;
