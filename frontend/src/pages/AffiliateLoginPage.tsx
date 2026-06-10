import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../contexts/AuthContext';
import * as authService from '../services/authService';

type Step = 'credentials' | '2fa';

export default function AffiliateLoginPage() {
  const { login, loginWithGoogle, finalizeLogin } = useAuth();
  const navigate = useNavigate();

  // credentials step
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  // 2FA step
  const [step, setStep] = useState<Step>('credentials');
  const [partialToken, setPartialToken] = useState('');
  const [totpCode, setTotpCode] = useState('');

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleCredentials(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await login(email, password);
      if (authService.isPartialToken(result)) {
        setPartialToken(result.partial_token);
        setStep('2fa');
      } else {
        navigate('/affiliate-dashboard', { replace: true });
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Login failed. Check your credentials and try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleTotpSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await authService.verify2fa(partialToken, totpCode);
      finalizeLogin(result.user);
      navigate('/affiliate-dashboard', { replace: true });
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Invalid code. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSuccess(credentialResponse: { credential?: string }) {
    if (!credentialResponse.credential) return;
    setError('');
    setLoading(true);
    try {
      const result = await loginWithGoogle(credentialResponse.credential);
      if (authService.isPartialToken(result)) {
        setPartialToken(result.partial_token);
        setStep('2fa');
      } else {
        navigate('/affiliate-dashboard', { replace: true });
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Google sign-in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <button onClick={() => navigate('/affiliates')} className="flex items-center gap-2 mx-auto mb-4 text-green-700 hover:text-green-800 transition-colors">
            <span className="text-3xl">💕</span>
            <span className="font-bold text-lg">SamePageDating</span>
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Affiliate Login</h1>
          <p className="text-gray-500 mt-1">Access your affiliate dashboard</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          {step === 'credentials' ? (
            <>
              {/* Google Sign-In */}
              <div className="flex justify-center mb-5">
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={() => setError('Google sign-in was cancelled or failed.')}
                  useOneTap={false}
                  theme="outline"
                  shape="rectangular"
                  text="signin_with"
                  width="320"
                />
              </div>

              <div className="relative mb-5">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200" />
                </div>
                <div className="relative flex justify-center text-xs text-gray-400">
                  <span className="bg-white px-3">or continue with email</span>
                </div>
              </div>

              <form onSubmit={handleCredentials} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="you@example.com"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-sm font-medium text-gray-700">Password</label>
                    <Link to="/forgot-password" className="text-xs text-green-600 hover:underline">
                      Forgot password?
                    </Link>
                  </div>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="••••••••"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-green-600 text-white font-semibold py-3 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed mt-2"
                >
                  {loading ? 'Logging in…' : 'Log In to Affiliate Dashboard'}
                </button>
              </form>
            </>
          ) : (
            /* ── 2FA step ─────────────────────────────────────────────── */
            <form onSubmit={handleTotpSubmit} className="space-y-5">
              <div className="text-center mb-2">
                <div className="text-3xl">🔐</div>
                <h2 className="text-lg font-semibold text-gray-900 mt-2">Two-Factor Authentication</h2>
                <p className="text-sm text-gray-500 mt-1">
                  Enter the 6-digit code from your authenticator app.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Authentication Code
                </label>
                <input
                  type="text"
                  inputMode="numeric"
                  pattern="\d{6}"
                  maxLength={6}
                  required
                  autoFocus
                  value={totpCode}
                  onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, ''))}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-center text-2xl font-mono tracking-widest focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="000000"
                />
              </div>

              <button
                type="submit"
                disabled={loading || totpCode.length !== 6}
                className="w-full bg-green-600 text-white font-semibold py-3 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? 'Verifying…' : 'Verify & Log In'}
              </button>

              <button
                type="button"
                onClick={() => { setStep('credentials'); setTotpCode(''); setPartialToken(''); }}
                className="w-full text-sm text-gray-500 hover:text-gray-700"
              >
                ← Back to login
              </button>
            </form>
          )}
        </div>

        <p className="text-center text-sm text-gray-600 mt-6">
          Don't have an affiliate account?{' '}
          <Link to="/affiliate-signup" className="text-green-600 font-medium hover:underline">
            Sign up free
          </Link>
        </p>
        <p className="text-center text-xs text-gray-400 mt-2">
          Want the full app?{' '}
          <Link to="/login" className="text-blue-600 hover:underline">Log in here</Link>
        </p>
      </div>
    </div>
  );
}
