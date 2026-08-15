import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/useAuth';
import { useNavigate } from 'react-router-dom';
import { getErrorMessage } from '../utils/helpers';
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  KeyRound,
  Loader,
  LogOut,
  Mail,
  Save,
  Shield,
  User,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export default function ProfilePage() {
  const { user, logout, updateProfile, changePassword, refreshUser, isLoading } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [profileMessage, setProfileMessage] = useState('');
  const [passwordMessage, setPasswordMessage] = useState('');
  const [profileError, setProfileError] = useState('');
  const [passwordError, setPasswordError] = useState('');

  useEffect(() => {
    if (user) {
      setName(user.name);
      setEmail(user.email);
    }
  }, [user]);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleProfileSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setProfileError('');
    setProfileMessage('');

    if (name.trim().length < 2) {
      setProfileError('Name must be at least 2 characters.');
      return;
    }

    try {
      await updateProfile(name, email);
      setProfileMessage('Profile updated successfully.');
    } catch (error) {
      setProfileError(getErrorMessage(error, 'Could not update your profile.'));
    }
  };

  const handlePasswordSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setPasswordError('');
    setPasswordMessage('');

    if (newPassword.length < 6) {
      setPasswordError('New password must be at least 6 characters.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match.');
      return;
    }

    try {
      await changePassword(currentPassword, newPassword);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setPasswordMessage('Password changed successfully.');
    } catch (error) {
      setPasswordError(getErrorMessage(error, 'Could not change your password.'));
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-5 sm:px-6 lg:px-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-2 font-semibold text-slate-600 transition hover:bg-slate-100"
          >
            <ArrowLeft size={18} />
            Back
          </button>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-2 font-semibold text-red-700 transition hover:bg-red-100"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="rounded-lg bg-slate-950 p-6 text-white shadow-xl shadow-slate-200 sm:p-8">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-500 text-2xl font-bold">
                {(user?.name || 'S').charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="text-sm font-semibold text-cyan-200">Student profile</p>
                <h1 className="text-3xl font-bold">{user?.name || 'Student'}</h1>
                <p className="mt-1 text-sm text-slate-300">{user?.email || 'No email available'}</p>
              </div>
            </div>
            <div className="rounded-lg border border-white/10 bg-white/10 px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-slate-300">Role</p>
              <p className="mt-1 font-bold capitalize">{user?.role || 'student'}</p>
            </div>
          </div>
        </section>

        <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_0.9fr]">
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-50 text-cyan-700">
                <Shield size={20} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-950">Account details</h2>
                <p className="text-sm text-slate-500">Keep your student identity up to date.</p>
              </div>
            </div>

            <form onSubmit={handleProfileSubmit} className="space-y-4">
              <ProfileInput icon={User} label="Name" value={name} onChange={setName} autoComplete="name" />
              <ProfileInput icon={Mail} label="Email" type="email" value={email} onChange={setEmail} autoComplete="email" />

              {profileError && <StatusMessage tone="error" message={profileError} />}
              {profileMessage && <StatusMessage tone="success" message={profileMessage} />}

              <button
                type="submit"
                disabled={isLoading}
                className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-cyan-600 px-4 font-bold text-white transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {isLoading ? <Loader size={18} className="animate-spin" /> : <Save size={18} />}
                Save profile
              </button>
            </form>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                <KeyRound size={20} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-950">Password</h2>
                <p className="text-sm text-slate-500">Update your sign-in password securely.</p>
              </div>
            </div>

            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <ProfileInput
                icon={KeyRound}
                label="Current password"
                type="password"
                value={currentPassword}
                onChange={setCurrentPassword}
                autoComplete="current-password"
              />
              <ProfileInput
                icon={Shield}
                label="New password"
                type="password"
                value={newPassword}
                onChange={setNewPassword}
                autoComplete="new-password"
              />
              <ProfileInput
                icon={CheckCircle2}
                label="Confirm new password"
                type="password"
                value={confirmPassword}
                onChange={setConfirmPassword}
                autoComplete="new-password"
              />

              {passwordError && <StatusMessage tone="error" message={passwordError} />}
              {passwordMessage && <StatusMessage tone="success" message={passwordMessage} />}

              <button
                type="submit"
                disabled={isLoading}
                className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 font-bold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {isLoading ? <Loader size={18} className="animate-spin" /> : <KeyRound size={18} />}
                Change password
              </button>
            </form>
          </section>
        </div>
      </div>
    </main>
  );
}

function ProfileInput({
  icon: Icon,
  label,
  value,
  onChange,
  type = 'text',
  autoComplete,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  autoComplete?: string;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-semibold text-slate-700">{label}</span>
      <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 px-3">
        <Icon size={18} className="text-slate-400" />
        <input
          type={type}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          autoComplete={autoComplete}
          required
          className="w-full bg-transparent px-3 py-3 text-slate-900 placeholder:text-slate-400"
        />
      </div>
    </label>
  );
}

function StatusMessage({ tone, message }: { tone: 'success' | 'error'; message: string }) {
  const isSuccess = tone === 'success';
  const Icon = isSuccess ? CheckCircle2 : AlertCircle;
  return (
    <div className={`flex items-center gap-2 rounded-lg border px-4 py-3 text-sm font-semibold ${isSuccess ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-red-200 bg-red-50 text-red-700'}`}>
      <Icon size={17} />
      {message}
    </div>
  );
}
