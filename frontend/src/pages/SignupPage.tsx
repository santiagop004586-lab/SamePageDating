import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

export default function SignupPage() {
  const { register, appMode } = useAuth();
  const requiresAccessCode = appMode !== 'production';
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  // Invite token can come from URL param or from user manually entering it
  const [inviteToken, setInviteToken] = useState(searchParams.get('invite') || '');
  const [inviteInput, setInviteInput] = useState('');
  const [inviteChecked, setInviteChecked] = useState(
    !requiresAccessCode || !!searchParams.get('invite')
  );
  const [inviteChecking, setInviteChecking] = useState(false);
  const [inviteError, setInviteError] = useState('');

  // Capture referral code from URL param and persist in localStorage
  useEffect(() => {
    const ref = searchParams.get('ref');
    if (ref) {
      localStorage.setItem('sec8_referral_code', ref);
    }
  }, [searchParams]);

  // Validate invite token from URL on mount (only if pre-supplied and access code is required)
  useEffect(() => {
    if (!requiresAccessCode) return; // Skip validation when app mode is production
    const tokenFromUrl = searchParams.get('invite');
    if (!tokenFromUrl) return; // user will enter manually
    async function checkInvite() {
      setInviteChecking(true);
      try {
        const { data } = await api.get(`/api/v1/waitlist/check-invite?token=${encodeURIComponent(tokenFromUrl!)}`);
        if (!data.valid) {
          setInviteToken('');
          setInviteChecked(false);
          setInviteError('This invite link is invalid or has already been used.');
        } else {
          if (data.email) setEmail(data.email);
          setInviteToken(tokenFromUrl!);
          setInviteChecked(true);
        }
      } catch {
        setInviteToken('');
        setInviteChecked(false);
        setInviteError('Could not validate invite. Please enter your code below.');
      } finally {
        setInviteChecking(false);
      }
    }
    checkInvite();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requiresAccessCode, searchParams]);

  async function handleInviteSubmit(e: React.FormEvent) {
    e.preventDefault();
    setInviteError('');
    setInviteChecking(true);
    try {
      const { data } = await api.get(`/api/v1/waitlist/check-invite?token=${encodeURIComponent(inviteInput.trim())}`);
      if (!data.valid) {
        setInviteError('Invalid or expired invite code. Check your email and try again.');
      } else {
        if (data.email) setEmail(data.email);
        setInviteToken(inviteInput.trim());
        setInviteChecked(true);
      }
    } catch {
      setInviteError('Could not validate invite. Please try again.');
    } finally {
      setInviteChecking(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    setLoading(true);
    const referralCode = localStorage.getItem('sec8_referral_code') || undefined;
    try {
      await register(email, password, fullName || undefined, referralCode, inviteToken || undefined);
      setDone(true);
    } catch (err: any) {
      const msg =
        err?.response?.data?.detail ||
        'Registration failed. Please try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  if (inviteChecking && !inviteChecked) {
    return null; // briefly blank while validating URL token
  }

  // ── Invite code entry screen ───────────────────────────────────────────────
  if (!inviteChecked) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <span className="text-5xl">🏘️</span>
            <h1 className="text-2xl font-bold text-gray-900 mt-3">Enter your invite code</h1>
            <p className="text-gray-500 mt-1">
              This app is in private beta. Check your email for an invite code.
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-8">
            {inviteError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
                {inviteError}
              </div>
            )}

            <form onSubmit={handleInviteSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Invite Code</label>
                <input
                  type="text"
                  required
                  autoFocus
                  value={inviteInput}
                  onChange={(e) => setInviteInput(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Paste your invite code here"
                />
              </div>

              <button
                type="submit"
                disabled={inviteChecking || !inviteInput.trim()}
                className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {inviteChecking ? 'Checking…' : 'Continue'}
              </button>
            </form>
          </div>

          <p className="text-center text-sm text-gray-600 mt-6">
            Don't have a code?{' '}
            <Link to="/waitlist" className="text-blue-600 font-semibold hover:underline">
              Join the waitlist
            </Link>
          </p>
          <p className="text-center text-sm text-gray-600 mt-2">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-600 font-semibold hover:underline">
              Log in
            </Link>
          </p>
        </div>
      </div>
    );
  }

  if (done) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-lg p-10 max-w-md w-full text-center">
          <div className="text-5xl mb-4">📧</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Check your email</h2>
          <p className="text-gray-500 text-sm mb-3">
            We sent a verification link to <strong>{email}</strong>.
            Click the link to activate your account.
          </p>
          <p className="text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-4 py-2 text-xs mb-6">
            ⚠️ Don't see it? Check your <strong>spam or junk folder</strong>. The email comes from <span className="font-mono">noreply@send.findbestrentals.com</span>
          </p>
          <button
            onClick={() => navigate('/login')}
            className="bg-blue-600 text-white font-semibold px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="text-5xl">🏘️</span>
          <h1 className="text-2xl font-bold text-gray-900 mt-3">Create your account</h1>
          <p className="text-gray-500 mt-1">30-day free trial · $19.99/month after · Cancel anytime</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name <span className="text-gray-400">(optional)</span>
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Jane Investor"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Min 8 characters"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
              <input
                type="password"
                required
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Repeat your password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed mt-2"
            >
              {loading ? 'Creating account…' : 'Create Account'}
            </button>
          </form>
        </div>

        <p className="text-center text-sm text-gray-600 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-600 font-semibold hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
