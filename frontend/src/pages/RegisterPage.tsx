import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/useAuth';
import { getErrorMessage } from '../utils/helpers';
import { ArrowRight, BookOpenCheck, CheckCircle2, Loader, Lock, Mail, ShieldCheck, User } from 'lucide-react';

const benefits = [
  'Personal study dashboard',
  'Subject-by-subject chat support',
  'Revision history saved securely',
];

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const { register, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    try {
      await register(name, email, password);
      navigate('/dashboard');
    } catch (error) {
      const message = getErrorMessage(error, 'Registration failed. Please check your details and try again.');
      setError(
        message === 'Email already registered'
          ? 'This email is already registered. Please log in instead.'
          : message
      );
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto grid min-h-screen w-full max-w-6xl grid-cols-1 lg:grid-cols-[0.95fr_1.05fr]">
        <section className="flex items-center justify-center bg-slate-50 px-6 py-10 text-slate-950 sm:px-10 lg:rounded-r-[2rem]">
          <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-xl shadow-slate-950/10 sm:p-8">
            <div className="mb-8">
              <p className="text-sm font-semibold uppercase tracking-wide text-emerald-600">Start learning</p>
              <h1 className="mt-2 text-3xl font-bold text-slate-950">Create your account</h1>
              <p className="mt-2 text-sm text-slate-500">Set up your OL Mate workspace in a minute.</p>
            </div>

            {error && (
              <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Full name</label>
                <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 px-3">
                  <User size={18} className="text-slate-400" />
                  <input
                    type="text"
                    name="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full bg-transparent px-3 py-3 text-slate-900 placeholder:text-slate-400"
                    placeholder="Your name"
                    autoComplete="name"
                    required
                  />
                </div>
              </div>

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
                    placeholder="Create a password"
                    autoComplete="new-password"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Confirm password</label>
                <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 px-3">
                  <ShieldCheck size={18} className="text-slate-400" />
                  <input
                    type="password"
                    name="confirmPassword"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full bg-transparent px-3 py-3 text-slate-900 placeholder:text-slate-400"
                    placeholder="Confirm your password"
                    autoComplete="new-password"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-3 font-bold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {isLoading ? (
                  <>
                    <Loader size={20} className="animate-spin" />
                    Creating account
                  </>
                ) : (
                  <>
                    Register
                    <ArrowRight size={18} />
                  </>
                )}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-slate-500">
              Already have an account?{' '}
              <button
                onClick={() => navigate('/login')}
                className="font-bold text-emerald-700 transition hover:text-emerald-900"
              >
                Login
              </button>
            </p>
          </div>
        </section>

        <section className="flex flex-col justify-between px-6 py-8 sm:px-10 lg:px-12">
          <div className="inline-flex w-fit items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm text-emerald-100">
            <BookOpenCheck size={18} />
            OL Mate
          </div>

          <div className="my-12 max-w-xl">
            <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-400/20">
              <CheckCircle2 size={28} />
            </div>
            <h2 className="text-4xl font-bold leading-tight sm:text-5xl">
              Keep your study help in one focused place.
            </h2>
            <p className="mt-5 text-lg leading-8 text-slate-300">
              Create an account to save questions, return to previous explanations, and organize revision by subject.
            </p>
            <div className="mt-8 space-y-3">
              {benefits.map((benefit) => (
                <div key={benefit} className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/10 px-4 py-3 text-sm text-slate-100">
                  <CheckCircle2 size={18} className="text-emerald-300" />
                  {benefit}
                </div>
              ))}
            </div>
          </div>

          <p className="text-sm text-slate-400">Designed for students who need fast, clear explanations while revising.</p>
        </section>
      </div>
    </main>
  );
}
