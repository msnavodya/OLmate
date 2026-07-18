import apiClient from './apiClient';

interface ChatMessage {
  user_id: string;
  question: string;
  subject: string;
}

interface ChatResponse {
  id: string;
  user_id: string;
  question: string;
  answer: string;
  subject: string;
  created_at: string;
}

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
};
