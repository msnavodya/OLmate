import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/useAuth';
import { useNavigate } from 'react-router-dom';
import { chatService, ChatResponse } from '../services/chatService';
import { OL_SUBJECTS } from '../utils/constants';
import { ArrowLeft, Bot, Copy, Loader, Send, Sparkles, Trash2, UserCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface Message {
  id?: string;
  question: string;
  answer: string;
  subject: string;
  timestamp?: string;
  isLoading?: boolean;
}

const samplePrompts = [
  'Explain photosynthesis for O/L Science',
  'Solve a quadratic equation step by step',
  'Summarize the causes of World War I',
];

export default function ChatPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [selectedSubject, setSelectedSubject] = useState(OL_SUBJECTS[0]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loadChatHistory = useCallback(async () => {
    try {
      if (user?.id) {
        const history = await chatService.getChatHistory(user.id);
        setMessages(history.map(mapChatResponseToMessage).reverse());
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  }, [user?.id]);

  useEffect(() => {
    if (user?.id) {
      loadChatHistory();
    }
  }, [user?.id, loadChatHistory]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || !user?.id) return;

    const pendingId = `pending-${Date.now()}`;

    const userMessage: Message = {
      id: pendingId,
      question,
      answer: '',
      subject: selectedSubject,
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      await chatService.streamMessage(
        {
          user_id: user.id,
          question,
          subject: selectedSubject,
        },
        (event) => {
          if (event.type === 'chunk' && event.chunk) {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === pendingId
                  ? { ...msg, answer: `${msg.answer}${event.chunk}`, isLoading: true }
                  : msg
              )
            );
            return;
          }

          if (event.type === 'done' && event.message) {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === pendingId
                  ? mapChatResponseToMessage(event.message)
                  : msg
              )
            );
            return;
          }

          if (event.type === 'error') {
            throw new Error(event.error || 'Chat stream failed');
          }
        }
      );
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to get response. Please try again.';
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === pendingId
            ? {
                ...msg,
                answer: `Error: ${errorMessage}`,
                isLoading: false,
              }
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
      setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
      await loadChatHistory();
    } catch (error) {
      console.error('Failed to delete chat:', error);
    }
  };

  const handleCopyResponse = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <main className="flex min-h-screen flex-col bg-slate-50 text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 text-slate-600 transition hover:bg-slate-100"
              title="Back to dashboard"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <p className="text-sm font-semibold text-cyan-700">OL Mate Chat</p>
              <h1 className="text-xl font-bold text-slate-950">Ask a syllabus question</h1>
            </div>
          </div>
          <label className="flex w-full items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 lg:w-auto">
            <span className="text-sm font-semibold text-slate-600">Subject</span>
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="min-w-0 flex-1 bg-transparent text-sm font-bold text-slate-950 lg:w-56"
            >
              {OL_SUBJECTS.map((subject) => (
                <option key={subject} value={subject}>
                  {subject}
                </option>
              ))}
            </select>
          </label>
        </div>
      </header>

      <div className="mx-auto grid w-full max-w-7xl flex-1 grid-cols-1 gap-5 px-4 py-5 sm:px-6 lg:grid-cols-[280px_1fr] lg:px-8">
        <aside className="hidden rounded-lg border border-slate-200 bg-white p-5 shadow-sm lg:block">
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-50 text-cyan-700">
              <Sparkles size={20} />
            </div>
            <div>
              <h2 className="font-bold text-slate-950">Prompt ideas</h2>
              <p className="text-xs text-slate-500">Click one to start</p>
            </div>
          </div>
          <div className="space-y-3">
            {samplePrompts.map((prompt) => (
              <button
                key={prompt}
                onClick={() => setInput(prompt)}
                className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-3 text-left text-sm leading-6 text-slate-600 transition hover:border-cyan-200 hover:bg-cyan-50 hover:text-cyan-800"
              >
                {prompt}
              </button>
            ))}
          </div>
        </aside>

        <section className="flex min-h-[calc(100vh-132px)] flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="flex-1 overflow-y-auto bg-slate-50 p-4 sm:p-6">
            {messages.length === 0 ? (
              <div className="flex h-full min-h-[420px] flex-col items-center justify-center text-center">
                <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-950 text-white">
                  <Bot size={32} />
                </div>
                <h2 className="text-2xl font-bold text-slate-950">Ready when you are.</h2>
                <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                  Pick a subject, ask your question, and OL Mate will answer in a revision-friendly way.
                </p>
                <div className="mt-6 grid w-full max-w-2xl grid-cols-1 gap-3 sm:grid-cols-3 lg:hidden">
                  {samplePrompts.map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => setInput(prompt)}
                      className="rounded-lg border border-slate-200 bg-white px-3 py-3 text-sm text-slate-600 shadow-sm transition hover:border-cyan-200 hover:bg-cyan-50"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <article key={message.id || `${message.question}-${index}`} className="space-y-3">
                    <div className="flex justify-end gap-3">
                      <div className="max-w-2xl rounded-lg bg-cyan-600 px-4 py-3 text-white shadow-sm">
                        <p className="text-sm leading-6">{message.question}</p>
                      </div>
                      <UserCircle size={28} className="mt-1 flex-shrink-0 text-cyan-700" />
                    </div>

                    <div className="flex justify-start gap-3">
                      <div className="mt-1 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-slate-950 text-white">
                        <Bot size={18} />
                      </div>
                      <div className="max-w-3xl rounded-lg border border-slate-200 bg-white px-4 py-3 shadow-sm">
                        {message.isLoading && !message.answer ? (
                          <div className="flex items-center gap-2 text-sm font-semibold text-slate-500">
                            <Loader size={18} className="animate-spin text-cyan-600" />
                            Thinking...
                          </div>
                        ) : (
                          <>
                            <div className="prose prose-sm max-w-none prose-slate">
                              <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                                {message.answer}
                              </ReactMarkdown>
                            </div>
                            <div className="mt-4 flex items-center justify-between gap-3 border-t border-slate-100 pt-3 text-xs text-slate-400">
                              <span className="inline-flex items-center gap-2">
                                {message.subject}
                                {message.isLoading && (
                                  <>
                                    <Loader size={13} className="animate-spin text-cyan-600" />
                                    Writing...
                                  </>
                                )}
                              </span>
                              <div className="flex gap-2">
                                <button
                                  onClick={() => handleCopyResponse(message.answer)}
                                  className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
                                  title="Copy answer"
                                >
                                  <Copy size={16} />
                                </button>
                                {message.id && (
                                  <button
                                    onClick={() => handleDeleteChat(message.id)}
                                    className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition hover:bg-red-50 hover:text-red-600"
                                    title="Delete chat"
                                  >
                                    <Trash2 size={16} />
                                  </button>
                                )}
                              </div>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-slate-200 bg-white p-4">
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={`Ask about ${selectedSubject}...`}
                className="min-w-0 flex-1 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 placeholder:text-slate-400"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-cyan-600 text-white transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:bg-slate-300"
                title="Send message"
              >
                <Send size={20} />
              </button>
            </form>
          </div>
        </section>
      </div>
    </main>
  );
}

function mapChatResponseToMessage(chat: ChatResponse): Message {
  return {
    id: chat.id,
    question: chat.question,
    answer: chat.answer,
    subject: chat.subject,
    timestamp: chat.created_at,
    isLoading: false,
  };
}
