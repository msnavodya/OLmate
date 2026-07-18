import { useAuth } from '../contexts/useAuth';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Bell, CheckCircle2, KeyRound, LogOut, Mail, Shield, User } from 'lucide-react';

const upcomingFeatures = [
  { label: 'Edit profile information', icon: User },
  { label: 'Change password', icon: KeyRound },
  { label: 'Notification preferences', icon: Bell },
  { label: 'Study goals and preferences', icon: CheckCircle2 },
];

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
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

        <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_0.85fr]">
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-50 text-cyan-700">
                <Shield size={20} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-950">Account details</h2>
                <p className="text-sm text-slate-500">Your saved OL Mate identity.</p>
              </div>
            </div>

            <div className="space-y-4">
              <ProfileField icon={User} label="Name" value={user?.name || ''} />
              <ProfileField icon={Mail} label="Email" value={user?.email || ''} />
              <ProfileField icon={Shield} label="Role" value={user?.role || 'student'} capitalize />
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-bold text-slate-950">Coming soon</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              These account tools are prepared for the next version of the student workspace.
            </p>
            <div className="mt-6 space-y-3">
              {upcomingFeatures.map((feature) => {
                const Icon = feature.icon;
                return (
                  <div key={feature.label} className="flex items-center gap-3 rounded-lg bg-slate-50 p-3">
                    <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                      <Icon size={18} />
                    </span>
                    <span className="text-sm font-semibold text-slate-600">{feature.label}</span>
                  </div>
                );
              })}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}

function ProfileField({
  icon: Icon,
  label,
  value,
  capitalize = false,
}: {
  icon: typeof User;
  label: string;
  value: string;
  capitalize?: boolean;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-semibold text-slate-700">{label}</span>
      <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 px-3">
        <Icon size={18} className="text-slate-400" />
        <input
          type="text"
          value={value}
          disabled
          className={`w-full bg-transparent px-3 py-3 text-slate-600 ${capitalize ? 'capitalize' : ''}`}
        />
      </div>
    </label>
  );
}
