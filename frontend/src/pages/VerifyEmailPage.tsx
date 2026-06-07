import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { verifyEmail, resendVerification } from '../services/authService';

export default function VerifyEmailPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get('token');

  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'resend'>('loading');
  const [resendEmail, setResendEmail] = useState('');
  const [resendDone, setResendDone] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('resend');
      return;
    }
    verifyEmail(token)
      .then(() => setStatus('success'))
      .catch((err) => {
        setErrorMsg(
          err?.response?.data?.detail || 'Verification failed. The link may have expired.'
        );
        setStatus('error');
      });
  }, [token]);

  async function handleResend(e: React.FormEvent) {
    e.preventDefault();
    await resendVerification(resendEmail);
    setResendDone(true);
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-gray-500">Verifying your email…</p>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="bg-white rounded-2xl shadow-lg p-10 max-w-md w-full text-center">
          <div className="text-5xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Email verified!</h2>
          <p className="text-gray-500 text-sm mb-6">Your account is now active. You can log in and start finding deals.</p>
          <button
            onClick={() => navigate('/login')}
            className="bg-blue-600 text-white font-semibold px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Log In Now
          </button>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="bg-white rounded-2xl shadow-lg p-10 max-w-md w-full text-center">
          <div className="text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification failed</h2>
          <p className="text-gray-500 text-sm mb-6">{errorMsg}</p>
          <Link to="/verify-email" className="text-blue-600 hover:underline text-sm">
            Request a new verification link
          </Link>
        </div>
      </div>
    );
  }

  // resend form
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="bg-white rounded-2xl shadow-lg p-10 max-w-md w-full">
        <div className="text-center mb-6">
          <div className="text-5xl mb-3">📧</div>
          <h2 className="text-2xl font-bold text-gray-900">Resend verification email</h2>
          <p className="text-gray-500 text-sm mt-1">Enter your email and we'll send a new link.</p>
        </div>
        {resendDone ? (
          <p className="text-center text-green-600 font-medium">
            Verification email sent! Check your inbox.
          </p>
        ) : (
          <form onSubmit={handleResend} className="space-y-4">
            <input
              type="email"
              required
              value={resendEmail}
              onChange={(e) => setResendEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Send Verification Email
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
