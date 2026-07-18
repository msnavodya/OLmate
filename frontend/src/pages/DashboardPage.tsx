import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { LogOut, MessageSquare, Settings, BookOpen } from 'lucide-react';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-12">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Welcome, {user?.name}!</h1>
            <p className="text-gray-600 mt-2">OL Mate - Your AI Learning Assistant</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Chat Card */}
          <div
            onClick={() => navigate('/chat')}
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl cursor-pointer transition transform hover:scale-105"
          >
            <div className="flex items-center justify-between mb-4">
              <MessageSquare size={32} className="text-blue-500" />
              <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
                New
              </span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Ask a Question</h2>
            <p className="text-gray-600">Get instant answers to your O/L syllabus questions</p>
          </div>

          {/* Quiz Card */}
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl cursor-pointer transition transform hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <BookOpen size={32} className="text-purple-500" />
              <span className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded-full">
                Coming Soon
              </span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Practice Quizzes</h2>
            <p className="text-gray-600">Test your knowledge with AI-generated MCQs</p>
          </div>

          {/* Profile Card */}
          <div
            onClick={() => navigate('/profile')}
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl cursor-pointer transition transform hover:scale-105"
          >
            <div className="flex items-center justify-between mb-4">
              <Settings size={32} className="text-green-500" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Profile Settings</h2>
            <p className="text-gray-600">Manage your account and preferences</p>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-12 bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Why Use OL Mate?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-bold">✓</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Syllabus-Based</h3>
                <p className="text-gray-600 text-sm">Answers aligned with Sri Lankan O/L curriculum</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-bold">✓</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">24/7 Available</h3>
                <p className="text-gray-600 text-sm">Get help anytime, anywhere</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-bold">✓</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Easy to Understand</h3>
                <p className="text-gray-600 text-sm">Simple language explanations for students</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-bold">✓</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Subject Coverage</h3>
                <p className="text-gray-600 text-sm">14 subjects covered with detailed support</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
