import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import BrandIcon from '../components/BrandIcon';

const Signup = () => {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const initialEmail = queryParams.get('email') || queryParams.get('identifier') || '';

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState(initialEmail);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState('');

  const { register, loading } = useAuth();
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setLocalError('');

    if (!fullName.trim()) {
      setLocalError('Please enter your full name.');
      return;
    }
    if (!email.trim() || !email.includes('@')) {
      setLocalError('Please enter a valid email address.');
      return;
    }
    if (!password || password.length < 8) {
      setLocalError('Password must be at least 8 characters long.');
      return;
    }
    if (password !== confirmPassword) {
      setLocalError('Passwords do not match. Please re-enter your password.');
      return;
    }

    try {
      await register(email.trim(), password, fullName.trim());
      navigate('/dashboard');
    } catch (err) {
      setLocalError(err.message || 'Registration failed. Please try again.');
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
              Password Protected Sign Up
            </div>
          </div>

          {/* Right Panel: Password Sign Up Form */}
          <div className="md:col-span-7 p-6 sm:p-10 flex flex-col justify-between space-y-6">
            <div className="space-y-5">
              {/* Header */}
              <div className="space-y-1.5">
                <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  Create sumscale Account
                </h2>
                {/* Feature Bullet Points */}
                <div className="space-y-1 pt-0.5 text-xs text-slate-600 font-medium">
                  <div className="flex items-center space-x-2">
                    <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[10px] font-bold">✓</span>
                    <span>Instant access to AI Copilot & Document Agents</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[10px] font-bold">✓</span>
                    <span>Secure Password Protected Authentication</span>
                  </div>
                </div>
              </div>

              {localError && (
                <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium text-center space-y-1.5">
                  <div>{localError}</div>
                  {localError.toLowerCase().includes('already exists') || localError.toLowerCase().includes('sign in') ? (
                    <div>
                      <Link to={`/login?email=${encodeURIComponent(email.trim())}`} className="inline-block font-bold text-[#006D77] bg-white px-3 py-1 rounded-full border border-[#83C5BE]/50 hover:bg-[#EDF6F9] transition-all shadow-2xs">
                        👉 Sign In to your Account
                      </Link>
                    </div>
                  ) : null}
                </div>
              )}

              <form onSubmit={handleSignup} className="space-y-3.5">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Anand Kosuru"
                    className="w-full px-4 py-2.5 rounded-full bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-[#006D77] focus:ring-2 focus:ring-[#006D77]/20 transition-all font-medium"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="e.g. name@gmail.com"
                    className="w-full px-4 py-2.5 rounded-full bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-[#006D77] focus:ring-2 focus:ring-[#006D77]/20 transition-all font-medium"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
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
                    minLength={8}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Create a strong password (min 8 chars)"
                    className="w-full px-4 py-2.5 rounded-full bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-[#006D77] focus:ring-2 focus:ring-[#006D77]/20 transition-all font-medium"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Confirm Password
                  </label>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    minLength={8}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter your password"
                    className="w-full px-4 py-2.5 rounded-full bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-[#006D77] focus:ring-2 focus:ring-[#006D77]/20 transition-all font-medium"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 px-6 rounded-full bg-slate-900 hover:bg-[#006D77] text-white font-bold text-xs shadow-md transition-all disabled:opacity-50 flex items-center justify-center space-x-2 hover:scale-[1.02] active:scale-95 cursor-pointer mt-2"
                >
                  {loading ? <span>Creating Account...</span> : <span>Create Account →</span>}
                </button>
              </form>
            </div>

            {/* Footer Navigation */}
            <div className="text-center text-xs text-slate-500 pt-2">
              Already have an account?{' '}
              <Link to="/login" className="text-[#006D77] hover:underline font-bold">
                Sign In
              </Link>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Signup;
