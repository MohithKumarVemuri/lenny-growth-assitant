import { useState, useCallback } from 'react';
import { API_BASE, SourceCitation, Artifact, Message } from '../lib/api';

interface StreamState {
  isStreaming: boolean;
  statusText: string | null;
  currentSources: SourceCitation[];
}

export function useChatStream() {
  const [streamState, setStreamState] = useState<StreamState>({
    isStreaming: false,
    statusText: null,
    currentSources: []
  });

  const sendMessage = useCallback(async (
    sessionId: string,
    messageText: string,
    provider: string,
    mode: string,
    onToken: (token: string) => void,
    onSources: (sources: SourceCitation[]) => void,
    onArtifact: (artifact: Artifact) => void,
    onComplete: (fullText: string, sources: SourceCitation[], artifact?: Artifact) => void,
    onError: (err: string) => void
  ) => {
    setStreamState({
      isStreaming: true,
      statusText: 'Connecting to assistant...',
      currentSources: []
    });

    let fullResponse = '';
    let collectedSources: SourceCitation[] = [];
    let collectedArtifact: Artifact | undefined = undefined;

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: messageText,
          provider: provider,
          mode: mode
        })
      });

      if (!response.ok || !response.body) {
        throw new Error(`Chat request failed with status ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith('data: ')) continue;

          const dataContent = trimmed.substring(6).trim();
          if (dataContent === '[DONE]') {
            break;
          }

          try {
            const event = JSON.parse(dataContent);
            if (event.type === 'status') {
              setStreamState(prev => ({ ...prev, statusText: event.content }));
            } else if (event.type === 'sources') {
              collectedSources = event.sources || [];
              setStreamState(prev => ({ ...prev, currentSources: collectedSources }));
              onSources(collectedSources);
            } else if (event.type === 'token') {
              fullResponse += event.content;
              onToken(event.content);
            } else if (event.type === 'artifact') {
              collectedArtifact = event.artifact;
              onArtifact(event.artifact);
            }
          } catch (jsonErr) {
            console.error('Error parsing SSE event payload:', jsonErr, dataContent);
          }
        }
      }

      onComplete(fullResponse, collectedSources, collectedArtifact);
    } catch (err: any) {
      console.error('Streaming error:', err);
      onError(err.message || 'An error occurred while streaming response');
    } finally {
      setStreamState({
        isStreaming: false,
        statusText: null,
        currentSources: []
      });
    }
  }, []);

  return {
    isStreaming: streamState.isStreaming,
    statusText: streamState.statusText,
    currentSources: streamState.currentSources,
    sendMessage
  };
}
