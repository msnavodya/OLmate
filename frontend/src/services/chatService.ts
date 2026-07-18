import apiClient, { API_BASE_URL } from './apiClient';

export interface ChatMessage {
  user_id: string;
  question: string;
  subject: string;
}

export interface ChatResponse {
  id: string;
  user_id: string;
  question: string;
  answer: string;
  subject: string;
  created_at: string;
}

export type ChatStreamEvent =
  | { type: 'chunk'; chunk: string }
  | { type: 'done'; message: ChatResponse }
  | { type: 'error'; error: string };

export const chatService = {
  async sendMessage(message: ChatMessage): Promise<ChatResponse> {
    const response = await apiClient.post('/chat/send', message);
    return response.data;
  },

  async getChatHistory(userId: string): Promise<ChatResponse[]> {
    const response = await apiClient.get(`/chat/history/${userId}`);
    return response.data;
  },

  async deleteChat(chatId: string): Promise<void> {
    await apiClient.delete(`/chat/history/${chatId}`);
  },

  async streamMessage(
    message: ChatMessage,
    onEvent: (event: ChatStreamEvent) => void
  ): Promise<void> {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(message),
    });

    if (!response.ok || !response.body) {
      throw new Error('Failed to start chat stream');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        onEvent(JSON.parse(trimmed) as ChatStreamEvent);
      }
    }

    if (buffer.trim()) {
      onEvent(JSON.parse(buffer.trim()) as ChatStreamEvent);
    }
  },
};
