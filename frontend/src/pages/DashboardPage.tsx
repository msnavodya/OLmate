import { useAuth } from '../contexts/useAuth';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  CheckCircle2,
  Clock3,
  LogOut,
  MessageSquare,
  Settings,
  Sparkles,
  Target,
} from 'lucide-react';

const quickActions = [
  {
    title: 'Ask a Question',
    description: 'Get a clear answer with subject context and revision-friendly structure.',
    icon: MessageSquare,
    tone: 'bg-cyan-50 text-cyan-700',
    badge: 'Ready',
    path: '/chat',
  },
  {
    title: 'Practice Quizzes',
    description: 'Generate MCQs, answer them, and review explanations for each attempt.',
    icon: BookOpen,
    tone: 'bg-amber-50 text-amber-700',
    badge: 'Live',
    path: '/quiz',
  },
  {
    title: 'Profile Settings',
    description: 'Review your account details and manage access from one place.',
    icon: Settings,
    tone: 'bg-emerald-50 text-emerald-700',
    badge: 'Account',
    path: '/profile',
  },
];

const strengths = [
  ['Syllabus-Based', 'Answers aligned with the Sri Lankan O/L curriculum.'],
  ['Easy to Understand', 'Short explanations written for revision, not research papers.'],
  ['Subject Coverage', 'Support across 14 common O/L subjects.'],
  ['Always Available', 'Ask questions whenever your study session needs momentum.'],
];

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-slate-950 text-white">
              <Sparkles size={22} />
            </div>
            <div>
              <p className="text-sm font-semibold text-cyan-700">OL Mate</p>
              <h1 className="text-2xl font-bold text-slate-950">Welcome, {user?.name || 'Student'}</h1>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex w-fit items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-2 font-semibold text-red-700 transition hover:bg-red-100"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="rounded-lg bg-slate-950 p-6 text-white shadow-xl shadow-slate-200 sm:p-8">
          <div className="grid gap-8 lg:grid-cols-[1.4fr_0.6fr] lg:items-center">
            <div>
              <p className="mb-3 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-sm text-cyan-100">
                <Target size={16} />
                Today&apos;s study hub
              </p>
              <h2 className="max-w-3xl text-3xl font-bold leading-tight sm:text-4xl">
                Ask better questions, get clearer answers, keep revising.
              </h2>
              <p className="mt-4 max-w-2xl text-slate-300">
                Jump into chat for subject help, revisit explanations, and keep your O/L preparation organized.
              </p>
              <button
                onClick={() => navigate('/chat')}
                className="mt-6 inline-flex items-center gap-2 rounded-lg bg-cyan-500 px-5 py-3 font-bold text-white transition hover:bg-cyan-600"
              >
                Open chat
                <ArrowRight size={18} />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg border border-white/10 bg-white/10 p-4">
                <MessageSquare className="mb-3 text-cyan-300" size={24} />
                <p className="text-2xl font-bold">14</p>
                <p className="text-sm text-slate-300">Subjects</p>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/10 p-4">
                <Clock3 className="mb-3 text-amber-300" size={24} />
                <p className="text-2xl font-bold">24/7</p>
                <p className="text-sm text-slate-300">Study help</p>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-8">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-950">Quick actions</h2>
            <BarChart3 size={20} className="text-slate-400" />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <button
                  key={action.title}
                  onClick={() => action.path && navigate(action.path)}
                  className="group rounded-lg border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md disabled:cursor-default disabled:hover:translate-y-0"
                  disabled={!action.path}
                >
                  <div className="mb-5 flex items-center justify-between">
                    <span className={`flex h-11 w-11 items-center justify-center rounded-lg ${action.tone}`}>
                      <Icon size={22} />
                    </span>
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">
                      {action.badge}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-950">{action.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-500">{action.description}</p>
                  {action.path && (
                    <span className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-cyan-700">
                      Continue
                      <ArrowRight size={16} className="transition group-hover:translate-x-1" />
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </section>

        <section className="mt-8 rounded-lg border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <h2 className="text-xl font-bold text-slate-950">Why students use OL Mate</h2>
          <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
            {strengths.map(([title, description]) => (
              <div key={title} className="flex gap-4 rounded-lg bg-slate-50 p-4">
                <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                  <CheckCircle2 size={21} />
                </div>
                <div>
                  <h3 className="font-bold text-slate-950">{title}</h3>
                  <p className="mt-1 text-sm leading-6 text-slate-500">{description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
