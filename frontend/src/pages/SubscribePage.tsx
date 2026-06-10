import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCheckoutSession } from '../services/billingService';
import { useAuth } from '../contexts/AuthContext';

const FEATURES = [
  'Live MLS listings — Greater Cleveland metro area',
  'HUD Section 8 Fair Market Rents built-in',
  'Cash flow, cap rate & BRRRR analysis',
  'Find top deals instantly — filter by cash flow, cap rate & CoC return',
  'Appreciation projections & equity tracking',
  'Real-time metric recalculation',
];

export default function SubscribePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubscribe() {
    setError('');
    setLoading(true);
    const referralCode = localStorage.getItem('sec8_referral_code') || undefined;
    try {
      const url = await createCheckoutSession(referralCode);
      window.location.href = url;
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          'Could not start checkout. Please try again.'
      );
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-700 via-blue-600 to-indigo-700 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
          {/* Top banner */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6 text-white text-center">
            <div className="text-4xl mb-2">💕</div>
            <h1 className="text-2xl font-extrabold mb-1">SamePageDating</h1>
            <p className="text-blue-200 text-sm">Start your 30-day free trial today</p>
          </div>

          <div className="px-8 py-7">
            {/* Pricing */}
            <div className="text-center mb-6">
              <div className="flex items-end justify-center gap-1">
                <span className="text-5xl font-extrabold text-gray-900">$29</span>
                <span className="text-3xl font-bold text-gray-900">.99</span>
                <span className="text-gray-400 text-base mb-1">/month</span>
              </div>
              <div className="mt-1 inline-flex items-center gap-1.5 bg-green-50 border border-green-200 text-green-700 rounded-full px-3 py-1 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-green-400 inline-block" />
                30 days FREE — no charge until trial ends
              </div>
            </div>

            {/* Feature list */}
            <ul className="space-y-2.5 mb-7">
              {FEATURES.map((f) => (
                <li key={f} className="flex items-start gap-2.5 text-sm text-gray-700">
                  <span className="text-green-500 font-bold text-base leading-tight">✓</span>
                  {f}
                </li>
              ))}
            </ul>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              onClick={handleSubscribe}
              disabled={loading}
              className="w-full bg-blue-600 text-white font-bold text-lg py-4 rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-60 shadow-lg"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Redirecting to Stripe…
                </span>
              ) : (
                'Start Free Trial →'
              )}
            </button>

            <p className="text-center text-xs text-gray-400 mt-3">
              Cancel anytime. No charge for 30 days.
              <br />Powered by{' '}
              <span className="font-semibold text-gray-500">Stripe</span> — your card info is never stored on our servers.
            </p>
          </div>
        </div>

        {/* Signed in as + logout */}
        <div className="text-center mt-4 text-blue-200 text-xs">
          Signed in as <span className="font-semibold text-white">{user?.email}</span>
          {' · '}
          <button
            onClick={() => { logout(); navigate('/login'); }}
            className="underline hover:text-white"
          >
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}
