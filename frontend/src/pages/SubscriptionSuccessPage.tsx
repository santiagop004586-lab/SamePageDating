import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { syncFromSession } from '../services/billingService';

export default function SubscriptionSuccessPage() {
  const { refreshUser } = useAuth();
  const navigate = useNavigate();

  // Sync subscription from Stripe (webhook fallback for local dev), then enter app
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sessionId = params.get('session_id');

    // Safety net: sync subscription from Stripe directly using the session_id
    // Stripe returns in the success URL. In production, webhooks fire before the
    // user lands here so this is redundant but harmless. In local dev, webhooks
    // can't reach localhost so this is what actually activates the subscription.
    const sync = sessionId ? syncFromSession(sessionId) : Promise.resolve();
    sync
      .catch(() => {/* non-fatal — webhook may have already fired in production */})
      .then(() => refreshUser())
      .then(() => setTimeout(() => navigate('/app', { replace: true }), 2500));
  }, [refreshUser, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg p-12 max-w-md w-full text-center">
        <div className="text-6xl mb-4">🎉</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">You're all set!</h1>
        <p className="text-gray-500 text-sm mb-1">
          Your 30-day free trial has started.
        </p>
        <p className="text-gray-400 text-xs mb-6">Redirecting you to the app…</p>
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
      </div>
    </div>
  );
}
