import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import BrandIcon from '../components/BrandIcon';

const Login = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const initialEmail = queryParams.get('email') || queryParams.get('identifier') || '';

  const [email, setEmail] = useState(initialEmail);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState('');

  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleDemoLogin = async () => {
    setLocalError('');
    try {
      await login('demo@omniaid.ai', 'DemoUserPass123!');
      navigate('/dashboard');
    } catch {
      navigate('/dashboard');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLocalError('');

    if (!email.trim() || !email.includes('@')) {
      setLocalError('Please enter a valid email address.');
      return;
    }
    if (!password) {
      setLocalError('Please enter your password.');
      return;
    }

    try {
      await login(email.trim(), password);
      navigate('/dashboard');
    } catch (err) {
      setLocalError(err.message || 'Invalid email or password. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-[#EDF6F9] text-slate-800 flex flex-col font-sans antialiased sarvam-gradient-purple">
      <Navbar />

      <div className="flex-1 flex items-center justify-center px-4 py-8 sm:py-12">
        {/* Sarvam AI Style Split Card Modal */}
        <div className="w-full max-w-4xl bg-white border border-[#83C5BE]/40 rounded-[32px] shadow-2xl overflow-hidden grid grid-cols-1 md:grid-cols-12 min-h-[520px]">
          
          {/* Left Panel: Generative Theme Art Graphic */}
          <div className="md:col-span-5 relative bg-gradient-to-br from-[#003840] via-[#006D77] to-[#83C5BE] p-8 flex flex-col justify-between overflow-hidden text-white min-h-[220px] md:min-h-full">
            {/* Geometric Pixel Pattern Overlay */}
            <div className="absolute inset-0 opacity-15 pointer-events-none bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:16px_16px]" />

            {/* Glowing Center Emblem */}
            <div className="relative z-10 my-auto flex flex-col items-center justify-center text-center space-y-4 py-8">
              <div className="w-24 h-24 rounded-full bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center shadow-inner animate-pulse">
                <BrandIcon className="w-16 h-10 text-white drop-shadow-md" color="#FFFFFF" secondaryColor="#83C5BE" />
              </div>
              <div className="space-y-1">
                <h3 className="text-xl font-extrabold tracking-tight font-serif lowercase">sumscale</h3>
                <p className="text-[11px] text-[#83C5BE] uppercase tracking-widest font-bold">Multimodal AI Platform</p>
              </div>
            </div>

            {/* Bottom Tag */}
            <div className="relative z-10 text-[10px] text-white/70 font-semibold tracking-wider uppercase text-center">
              Password Protected Access
            </div>
          </div>

          {/* Right Panel: Password Sign In Form */}
          <div className="md:col-span-7 p-6 sm:p-10 flex flex-col justify-between space-y-6">
            <div className="space-y-6">
              {/* Header */}
              <div className="space-y-2">
                <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  Sign in to sumscale
                </h2>
                {/* Feature Bullet Points */}
                <div className="space-y-1.5 pt-1 text-xs text-slate-600 font-medium">
                  <div className="flex items-center space-x-2">
                    <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[10px] font-bold">✓</span>
                    <span>Multimodal AI Document, Speech & Fraud Intelligence</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[10px] font-bold">✓</span>
                    <span>Secure Password Protected Account Access</span>
                  </div>
                </div>
              </div>

              {localError && (
                <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium text-center space-y-1.5">
                  <div>{localError}</div>
                  {localError.toLowerCase().includes('no account') || localError.toLowerCase().includes('not found') ? (
                    <div>
                      <Link to={`/signup?email=${encodeURIComponent(email.trim())}`} className="inline-block font-bold text-[#006D77] bg-white px-3 py-1 rounded-full border border-[#83C5BE]/50 hover:bg-[#EDF6F9] transition-all shadow-2xs">
                        👉 Create a new account
                      </Link>
                    </div>
                  ) : null}
                </div>
              )}

              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">
                    Email Address
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="e.g. name@gmail.com"
                    className="w-full px-4 py-3 rounded-full bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-[#006D77] focus:ring-2 focus:ring-[#006D77]/20 transition-all font-medium"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-bold text-slate-700">
                      Password
                    </label>
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="text-[11px] font-medium text-[#006D77] hover:underline"
                    >
                      {showPassword ? 'Hide password' : 'Show password'}
                    </button>
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full px-4 py-3 rounded-full bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-[#006D77] focus:ring-2 focus:ring-[#006D77]/20 transition-all font-medium"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3.5 px-6 rounded-full bg-slate-900 hover:bg-[#006D77] text-white font-bold text-xs shadow-md transition-all disabled:opacity-50 flex items-center justify-center space-x-2 hover:scale-[1.02] active:scale-95 cursor-pointer"
                >
                  {loading ? <span>Signing In...</span> : <span>Sign In with Password →</span>}
                </button>
              </form>

              {/* Quick Demo Access */}
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-400">Testing platform features?</span>
                <button
                  type="button"
                  onClick={handleDemoLogin}
                  disabled={loading}
                  className="px-3.5 py-1.5 rounded-full bg-[#EDF6F9] hover:bg-[#83C5BE]/20 text-[#006D77] font-bold text-xs border border-[#83C5BE]/40 transition-all hover:scale-105 cursor-pointer"
                >
                  ⚡ Quick Demo Login
                </button>
              </div>
            </div>

            {/* Footer Navigation */}
            <div className="text-center text-xs text-slate-500 pt-4">
              Don't have an account?{' '}
              <Link to="/signup" className="text-[#006D77] hover:underline font-bold">
                Create Account
              </Link>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Login;
