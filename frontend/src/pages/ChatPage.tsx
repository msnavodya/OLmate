import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { chatService } from '../services/chatService';
import { OL_SUBJECTS } from '../utils/constants';
import { Send, ArrowLeft, Copy, Trash2, Loader } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Message {
  id?: string;
  question: string;
  answer: string;
  subject: string;
  timestamp?: string;
  isLoading?: boolean;
}

export default function ChatPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [selectedSubject, setSelectedSubject] = useState(OL_SUBJECTS[0]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (user?.id) {
      loadChatHistory();
    }
  }, [user?.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      if (user?.id) {
        await chatService.getChatHistory(user.id);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !user?.id) return;

    const userMessage: Message = {
      question: input,
      answer: '',
      subject: selectedSubject,
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage({
        user_id: user.id,
        question: input,
        subject: selectedSubject,
      });

      setMessages((prev) =>
        prev.map((msg) =>
          msg.question === input
            ? { ...msg, ...response, id: response.id }
            : msg
        )
      );
      await loadChatHistory();
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.question === input
            ? { ...msg, answer: 'Error: Failed to get response. Please try again.' }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteChat = async (messageId?: string) => {
    if (!messageId) return;
    try {
      await chatService.deleteChat(messageId);
      setMessages(messages.filter((msg) => msg.id !== messageId));
      await loadChatHistory();
    } catch (error) {
      console.error('Failed to delete chat:', error);
    }
  };

  const handleCopyResponse = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-blue-600 hover:text-blue-800"
          >
            <ArrowLeft size={24} />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">OL Mate Chat</h1>
        </div>
        <select
          value={selectedSubject}
          onChange={(e) => setSelectedSubject(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          {OL_SUBJECTS.map((subject) => (
            <option key={subject} value={subject}>
              {subject}
            </option>
          ))}
        </select>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <p className="text-lg">No messages yet. Start by asking a question!</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className="space-y-3">
              {/* User Message */}
              <div className="flex justify-end">
                <div className="bg-blue-500 text-white rounded-lg px-4 py-3 max-w-md">
                  {message.question}
                </div>
              </div>

              {/* AI Response */}
              <div className="flex justify-start">
                <div className="bg-white rounded-lg shadow px-4 py-3 max-w-md">
                  {message.isLoading ? (
                    <div className="flex items-center gap-2">
                      <Loader size={20} className="animate-spin text-blue-500" />
                      <span>Thinking...</span>
                    </div>
                  ) : (
                    <>
                      <div className="prose prose-sm max-w-none">
                        <ReactMarkdown>{message.answer}</ReactMarkdown>
                      </div>
                      <div className="flex gap-2 mt-3 text-gray-500">
                        <button
                          onClick={() => handleCopyResponse(message.answer)}
                          className="hover:text-gray-700"
                          title="Copy"
                        >
                          <Copy size={18} />
                        </button>
                        {message.id && (
                          <button
                            onClick={() => handleDeleteChat(message.id)}
                            className="hover:text-red-500"
                            title="Delete"
                          >
                            <Trash2 size={18} />
                          </button>
                        )}
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-300 p-4">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about {selectedSubject}..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition flex items-center gap-2"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}
