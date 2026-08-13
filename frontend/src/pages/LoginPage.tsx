import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/useAuth';
import { authService } from '../services/authService';
import { ArrowRight, BookOpenCheck, Check, Loader, Lock, Mail, Sparkles } from 'lucide-react';

const highlights = ['Syllabus-aware answers', 'Saved chat history', 'Built for O/L revision'];

export default function LoginPage() {
  const rememberedEmail = authService.getRememberedEmail();
  const [email, setEmail] = useState(rememberedEmail);
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(Boolean(rememberedEmail));
  const [error, setError] = useState('');
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
      if (rememberMe) {
        authService.setRememberedEmail(email);
      } else {
        authService.clearRememberedEmail();
      }
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid email or password');
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto grid min-h-screen w-full max-w-6xl grid-cols-1 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="flex flex-col justify-between px-6 py-8 sm:px-10 lg:px-12">
          <div className="inline-flex w-fit items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm text-cyan-100">
            <BookOpenCheck size={18} />
            OL Mate
          </div>

          <div className="my-12 max-w-xl">
            <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-400 text-slate-950 shadow-lg shadow-amber-400/20">
              <Sparkles size={28} />
            </div>
            <h1 className="text-4xl font-bold leading-tight sm:text-5xl">
              Study smarter for Sri Lankan O/Ls.
            </h1>
            <p className="mt-5 text-lg leading-8 text-slate-300">
              Ask subject questions, keep your revision conversations organized, and get clear explanations when you need them.
            </p>
            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              {highlights.map((item) => (
                <div key={item} className="rounded-lg border border-white/10 bg-white/10 px-4 py-3 text-sm text-slate-100">
                  {item}
                </div>
              ))}
            </div>
          </div>

          <p className="text-sm text-slate-400">Focused learning for Mathematics, Science, ICT, Commerce, History, and more.</p>
        </section>

        <section className="flex items-center justify-center bg-slate-50 px-6 py-10 text-slate-950 sm:px-10 lg:rounded-l-[2rem]">
          <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-xl shadow-slate-950/10 sm:p-8">
            <div className="mb-8">
              <p className="text-sm font-semibold uppercase tracking-wide text-cyan-600">Welcome back</p>
              <h2 className="mt-2 text-3xl font-bold text-slate-950">Log in to continue</h2>
              <p className="mt-2 text-sm text-slate-500">Your study dashboard is waiting.</p>
            </div>

            {error && (
              <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Email</label>
                <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 px-3">
                  <Mail size={18} className="text-slate-400" />
                  <input
                    type="email"
                    name="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-transparent px-3 py-3 text-slate-900 placeholder:text-slate-400"
                    placeholder="you@example.com"
                    autoComplete="username"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Password</label>
                <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 px-3">
                  <Lock size={18} className="text-slate-400" />
                  <input
                    type="password"
                    name="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-transparent px-3 py-3 text-slate-900 placeholder:text-slate-400"
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    required
                  />
                </div>
              </div>

              <label className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-3 text-sm text-slate-600">
                <span className="font-semibold">Remember my email</span>
                <span className="relative inline-flex h-6 w-11 flex-shrink-0 items-center">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="peer sr-only"
                  />
                  <span className="absolute inset-0 rounded-full bg-slate-300 transition peer-checked:bg-cyan-600" />
                  <span className="relative ml-1 flex h-4 w-4 items-center justify-center rounded-full bg-white text-cyan-600 transition peer-checked:translate-x-5">
                    {rememberMe && <Check size={11} strokeWidth={3} />}
                  </span>
                </span>
              </label>

              <button
                type="submit"
                disabled={isLoading}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-cyan-600 px-4 py-3 font-bold text-white transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {isLoading ? (
                  <>
                    <Loader size={20} className="animate-spin" />
                    Logging in
                  </>
                ) : (
                  <>
                    Login
                    <ArrowRight size={18} />
                  </>
                )}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-slate-500">
              New to OL Mate?{' '}
              <button
                onClick={() => navigate('/register')}
                className="font-bold text-cyan-700 transition hover:text-cyan-900"
              >
                Create an account
              </button>
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
