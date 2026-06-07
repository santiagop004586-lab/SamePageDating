import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../contexts/AuthContext';
import * as authService from '../services/authService';

type Step = 'credentials' | '2fa';

export default function LoginPage() {
  const { login, loginWithGoogle, finalizeLogin, appMode } = useAuth();
  const isWaitlistOrBeta = appMode !== 'production';
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as any)?.from?.pathname || '/app';

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
        navigate(from, { replace: true });
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
      navigate(from, { replace: true });
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
        navigate(from, { replace: true });
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Google sign-in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="text-5xl">🏘️</span>
          <div className="flex items-center justify-center gap-2 mt-3">
            <h1 className="text-2xl font-bold text-gray-900">Welcome back</h1>
            {isWaitlistOrBeta && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-300 uppercase tracking-wide">
                Beta
              </span>
            )}
          </div>
          <p className="text-gray-500 mt-1">Log in to your FindBestRentals account</p>
        </div>

        {isWaitlistOrBeta && (
          <div className="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-800">
            <p className="font-semibold mb-1">🚀 This app is currently in private beta.</p>
            <p>
              Access is currently controlled by app mode. If you don't have an account yet,{' '}
              <Link to="/waitlist" className="font-semibold underline hover:text-amber-900">
                join the waitlist
              </Link>{' '}
              to request access.
            </p>
          </div>
        )}

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
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="you@example.com"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-sm font-medium text-gray-700">Password</label>
                    <Link to="/forgot-password" className="text-xs text-blue-600 hover:underline">
                      Forgot password?
                    </Link>
                  </div>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="••••••••"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed mt-2"
                >
                  {loading ? 'Logging in…' : 'Log In'}
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
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm text-center tracking-[0.5em] font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="000000"
                />
              </div>

              <button
                type="submit"
                disabled={loading || totpCode.length !== 6}
                className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? 'Verifying…' : 'Verify & Log In'}
              </button>

              <button
                type="button"
                onClick={() => { setStep('credentials'); setTotpCode(''); setError(''); }}
                className="w-full text-sm text-gray-500 hover:text-gray-700"
              >
                ← Back to login
              </button>
            </form>
          )}
        </div>

        <p className="text-center text-sm text-gray-600 mt-6">
          {isWaitlistOrBeta ? (
            <>
              Want access?{' '}
              <Link to="/waitlist" className="text-blue-600 font-semibold hover:underline">
                Join the waitlist
              </Link>
            </>
          ) : (
            <>
              Don't have an account?{' '}
              <Link to="/signup" className="text-blue-600 font-semibold hover:underline">
                Sign up free
              </Link>
            </>
          )}
        </p>
      </div>
    </div>
  );
}

