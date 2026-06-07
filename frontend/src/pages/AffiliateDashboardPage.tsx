import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  enrollAffiliate,
  getAffiliateDashboard,
  updatePayoutInfo,
  getStripeOnboardingLink,
  refreshStripeConnectStatus,
  formatCents,
  type AffiliateDashboard,
} from '../services/affiliateService';

export default function AffiliateDashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<AffiliateDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  // Payout info (deprecated but keeping for backward compatibility)
  const [payoutEmail, setPayoutEmail] = useState('');
  const [payoutSaving, setPayoutSaving] = useState(false);
  const [payoutMsg, setPayoutMsg] = useState('');

  // Stripe Connect
  const [stripeOnboarding, setStripeOnboarding] = useState(false);
  const [stripeRefreshing, setStripeRefreshing] = useState(false);
  const [stripeMsg, setStripeMsg] = useState('');
  const [settingsOpen, setSettingsOpen] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getAffiliateDashboard();
      setDashboard(data);
      setPayoutEmail(data.affiliate.payout_email || '');
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setEnrolling(true);
        try {
          await enrollAffiliate();
          // Load the dashboard after enrollment - user can manually set up Stripe Connect
          const data = await getAffiliateDashboard();
          setDashboard(data);
          setPayoutEmail(data.affiliate.payout_email || '');
        } catch {
          setError('Failed to enroll. Please try again.');
        } finally {
          setEnrolling(false);
        }
      } else if (err?.response?.status === 403) {
        setError('Please verify your email before accessing your affiliate dashboard.');
      } else {
        setError('Failed to load dashboard.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  function copyLink() {
    if (!dashboard?.referral_link) return;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(dashboard.referral_link);
    } else {
      // Fallback for non-HTTPS contexts
      const el = document.createElement('textarea');
      el.value = dashboard.referral_link;
      el.style.position = 'fixed';
      el.style.opacity = '0';
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function savePayoutInfo(e: React.FormEvent) {
    e.preventDefault();
    setPayoutSaving(true);
    setPayoutMsg('');
    try {
      const updated = await updatePayoutInfo(payoutEmail);
      setDashboard(prev => prev ? { ...prev, affiliate: updated } : prev);
      setPayoutMsg('Saved!');
    } catch {
      setPayoutMsg('Failed to save. Please try again.');
    } finally {
      setPayoutSaving(false);
      setTimeout(() => setPayoutMsg(''), 3000);
    }
  }

  async function startStripeOnboarding() {
    setStripeOnboarding(true);
    setStripeMsg('');
    try {
      const response = await getStripeOnboardingLink();
      if (response.onboarding_url) {
        window.location.href = response.onboarding_url;
      }
    } catch {
      setStripeMsg('Failed to generate onboarding link. Please try again.');
      setStripeOnboarding(false);
      setTimeout(() => setStripeMsg(''), 3000);
    }
  }

  async function checkStripeStatus() {
    setStripeRefreshing(true);
    setStripeMsg('');
    try {
      const response = await refreshStripeConnectStatus();
      // Reload dashboard to get updated affiliate info
      const data = await getAffiliateDashboard();
      setDashboard(data);
      if (response.payouts_enabled) {
        setStripeMsg('✓ Your Stripe account is fully activated!');
      } else {
        setStripeMsg('Your account is pending review. Check back soon.');
      }
    } catch {
      setStripeMsg('Failed to check status. Please try again.');
    } finally {
      setStripeRefreshing(false);
      setTimeout(() => setStripeMsg(''), 5000);
    }
  }

  const isSetupComplete = dashboard?.affiliate.payouts_enabled;
  const firstName = user?.full_name?.split(' ')[0];

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Nav */}
      <nav className="bg-white border-b border-gray-100 shadow-sm">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <button onClick={() => navigate('/affiliates')} className="flex items-center gap-2 text-gray-900 hover:text-green-700 transition-colors">
            <span className="text-2xl">🏨️</span>
            <span className="font-bold text-base">FindBestRentals</span>
            <span className="ml-2 text-xs bg-green-100 text-green-700 font-semibold px-2 py-0.5 rounded-full">Affiliate</span>
          </button>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500 hidden sm:block">{user?.email}</span>
            <button onClick={() => { logout(); navigate('/'); }} className="text-sm text-gray-500 hover:text-gray-800 transition-colors">Log Out</button>
          </div>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-6 py-10">
        {/* Loading */}
        {(loading || enrolling) && (
          <div className="flex items-center justify-center py-24">
            <div className="text-center">
              <div className="w-10 h-10 border-4 border-green-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-gray-500 text-sm">{enrolling ? 'Setting up your affiliate account…' : 'Loading…'}</p>
            </div>
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-6 text-center max-w-lg mx-auto mt-16">
            <p className="font-semibold mb-2">Something went wrong</p>
            <p className="text-sm mb-4">{error}</p>
            <button onClick={load} className="bg-red-600 text-white px-6 py-2 rounded-lg text-sm hover:bg-red-700 transition-colors">Try Again</button>
          </div>
        )}

        {!loading && !enrolling && dashboard && (
          <div className="space-y-6">

            {/* ─── SETUP MODE ─── */}
            {!isSetupComplete && (
              <>
                {/* Welcome */}
                <div className="text-center py-2">
                  <h1 className="text-3xl font-bold text-gray-900">
                    {firstName ? `Welcome, ${firstName}! 🎉` : 'Welcome! 🎉'}
                  </h1>
                  <p className="text-gray-500 mt-2">Complete Stripe Connect setup below to unlock your referral link and start earning.</p>
                </div>

                {/* Single-step progress indicator */}
                <div className="flex items-center justify-center gap-2 text-sm flex-wrap">
                  <div className={`flex items-center gap-1.5 px-4 py-2 rounded-full font-semibold transition-colors ${
                    dashboard.affiliate.payouts_enabled ? 'bg-green-100 text-green-700' : 'bg-gray-900 text-white'
                  }`}>
                    {dashboard.affiliate.payouts_enabled ? '✓' : '1'} Connect Stripe Account
                  </div>
                  <span className="text-gray-300 font-bold">→</span>
                  <div className="flex items-center gap-1.5 px-4 py-2 rounded-full font-semibold bg-yellow-100 text-yellow-700">
                    🔗 Your link
                  </div>
                </div>

                {/* Earning potential banner */}
                <div className="bg-gradient-to-r from-green-600 to-emerald-700 rounded-2xl p-6 text-white text-center">
                  <div className="text-5xl font-black mb-1">30%</div>
                  <div className="text-green-100 font-semibold text-lg">recurring commission</div>
                  <div className="text-green-200 text-sm mt-2 max-w-sm mx-auto">You earn every month your referral stays subscribed — not just a one-time bonus.</div>
                </div>

                {/* How it works */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                  <h2 className="font-semibold text-gray-900 mb-4">How it works</h2>
                  <div className="space-y-4">
                    {[
                      { n: '1', title: 'Share your unique link', desc: 'Anyone who clicks is tracked for 30 days.' },
                      { n: '2', title: 'They sign up and subscribe', desc: 'A commission is created for their first — and every — renewal.' },
                      { n: '3', title: 'Get paid', desc: 'After a short hold period, your commission is approved and paid directly to you.' },
                    ].map(s => (
                      <div key={s.n} className="flex gap-4">
                        <div className="w-8 h-8 rounded-full bg-green-100 text-green-700 font-bold flex items-center justify-center flex-shrink-0 text-sm">{s.n}</div>
                        <div>
                          <p className="font-medium text-gray-800 text-sm">{s.title}</p>
                          <p className="text-gray-500 text-xs mt-0.5">{s.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Stripe Connect Setup */}
                <div className={`bg-white rounded-2xl shadow-sm overflow-hidden border-2 ${
                  dashboard.affiliate.payouts_enabled ? 'border-green-300' : 'border-blue-300'
                }`}>
                  <div className={`px-6 py-4 flex items-center gap-3 ${
                    dashboard.affiliate.payouts_enabled ? 'bg-green-50 border-b border-green-100' : 'bg-blue-50 border-b border-blue-100'
                  }`}>
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 ${
                      dashboard.affiliate.payouts_enabled ? 'bg-green-500 text-white' : 'bg-blue-500 text-white'
                    }`}>
                      {dashboard.affiliate.payouts_enabled ? '✓' : '1'}
                    </div>
                    <div className="flex-1">
                      <h2 className="font-semibold text-gray-900">Connect your Stripe account</h2>
                      <p className="text-xs text-gray-500 mt-0.5">Stripe handles all tax info (1099s) and direct deposits</p>
                    </div>
                    {dashboard.affiliate.payouts_enabled && (
                      <span className="text-xs bg-green-100 text-green-700 font-semibold px-2.5 py-1 rounded-full">Active ✓</span>
                    )}
                  </div>
                  <div className="px-6 py-5">
                    {!dashboard.affiliate.stripe_onboarding_completed && (
                      <>
                        <div className="bg-gradient-to-br from-green-50 to-blue-50 border-2 border-green-300 rounded-lg p-5 mb-4">
                          <h3 className="text-base font-bold text-green-900 mb-3 flex items-center gap-2">
                            <span className="text-2xl">💰</span>
                            Complete Setup to Start Earning!
                          </h3>
                          <p className="text-sm text-gray-700 font-semibold mb-3">
                            You must connect your Stripe account to receive commission payments. No Stripe = No payouts.
                          </p>
                          <div className="bg-white rounded-md p-3 mb-3">
                            <p className="text-xs text-gray-600 font-medium mb-2">Here's what happens next:</p>
                            <ul className="text-xs text-gray-700 space-y-2">
                              <li className="flex items-start gap-2">
                                <span className="text-green-600 font-bold">→</span>
                                <span><strong>2 minutes:</strong> Stripe securely collects your bank & tax info</span>
                              </li>
                              <li className="flex items-start gap-2">
                                <span className="text-green-600 font-bold">→</span>
                                <span><strong>Instant access:</strong> Get your unique referral link immediately</span>
                              </li>
                              <li className="flex items-start gap-2">
                                <span className="text-green-600 font-bold">→</span>
                                <span><strong>Monthly payouts:</strong> Automatic deposits to your bank account</span>
                              </li>
                              <li className="flex items-start gap-2">
                                <span className="text-green-600 font-bold">→</span>
                                <span><strong>Tax-free hassle:</strong> Stripe handles all 1099 forms automatically</span>
                              </li>
                            </ul>
                          </div>
                          <p className="text-xs text-blue-900 font-semibold">
                            🔒 Your sensitive data never touches our servers — Stripe's bank-level security protects everything.
                          </p>
                        </div>

                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4">
                          <p className="text-xs text-amber-900">
                            By continuing, you agree to our <Link to="/affiliate-agreement" className="font-semibold underline hover:text-amber-700">Affiliate Agreement</Link>. 
                            Commissions are paid monthly via Stripe on the 1st of each month.
                          </p>
                        </div>

                        <button
                          onClick={startStripeOnboarding}
                          disabled={stripeOnboarding}
                          className="w-full bg-gradient-to-r from-green-600 to-blue-600 text-white font-bold py-4 rounded-xl text-base hover:from-green-700 hover:to-blue-700 disabled:opacity-60 transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                        >
                          {stripeOnboarding ? (
                            <>
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                              Redirecting to Stripe...
                            </>
                          ) : (
                            <>
                              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M13.976 9.15c-2.172-.806-3.356-1.426-3.356-2.409 0-.831.683-1.305 1.901-1.305 2.227 0 4.515.858 6.09 1.631l.89-5.494C18.252.975 15.697 0 12.165 0 9.667 0 7.589.654 6.104 1.872 4.56 3.147 3.757 4.992 3.757 7.218c0 4.039 2.467 5.76 6.476 7.219 2.585.92 3.445 1.574 3.445 2.583 0 .98-.84 1.545-2.354 1.545-1.875 0-4.965-.921-6.99-2.109l-.9 5.555C5.175 22.99 8.385 24 11.714 24c2.641 0 4.843-.624 6.328-1.813 1.664-1.305 2.525-3.236 2.525-5.732 0-4.128-2.524-5.851-6.591-7.305z"/>
                              </svg>
                              Complete Setup & Get Your Referral Link 🚀
                            </>
                          )}
                        </button>
                        {stripeMsg && (
                          <p className={`text-sm text-center mt-3 ${stripeMsg.includes('✓') ? 'text-green-600' : 'text-red-600'}`}>{stripeMsg}</p>
                        )}
                      </>
                    )}

                    {dashboard.affiliate.stripe_onboarding_completed && !dashboard.affiliate.payouts_enabled && (
                      <>
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                          <div className="flex items-start gap-3">
                            <div className="text-2xl">⏳</div>
                            <div>
                              <h3 className="text-sm font-semibold text-yellow-900 mb-1">Onboarding Complete - Pending Review</h3>
                              <p className="text-xs text-yellow-800">
                                Your Stripe account has been created and is under review. Stripe typically verifies accounts within 1-2 business days. 
                                Once approved, payouts will be enabled automatically.
                              </p>
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={checkStripeStatus}
                          disabled={stripeRefreshing}
                          className="w-full bg-yellow-600 text-white font-semibold py-2.5 rounded-lg text-sm hover:bg-yellow-700 disabled:opacity-60 transition-colors"
                        >
                          {stripeRefreshing ? 'Checking...' : 'Check Status Now'}
                        </button>
                        {stripeMsg && (
                          <p className={`text-sm text-center mt-3 ${stripeMsg.includes('✓') ? 'text-green-600' : 'text-gray-600'}`}>{stripeMsg}</p>
                        )}
                      </>
                    )}

                    {dashboard.affiliate.payouts_enabled && (
                      <>
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                          <div className="flex items-start gap-3">
                            <div className="text-2xl">✓</div>
                            <div>
                              <h3 className="text-sm font-semibold text-green-900 mb-1">Payouts Enabled!</h3>
                              <p className="text-xs text-green-800 mb-3">
                                Your Stripe Connect account is active. You'll receive monthly payouts on the 1st of each month for commissions over $100.
                              </p>
                              <div className="text-xs text-green-700 space-y-1">
                                <p><strong>Stripe Account ID:</strong> <span className="font-mono">{dashboard.affiliate.stripe_account_id}</span></p>
                                <p><strong>Payout Schedule:</strong> Monthly on the 1st</p>
                                <p><strong>Minimum Threshold:</strong> $100</p>
                                <p><strong>Hold Period:</strong> {dashboard.affiliate.hold_days} days</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                <p className="text-center text-xs text-gray-400 pb-4">
                  🔒 Your referral link unlocks automatically once Stripe Connect is active.
                </p>
              </>
            )}

            {/* ─── ACTIVE MODE ─── */}
            {isSetupComplete && (
              <>
                {/* Header */}
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">
                      {firstName ? `Hey ${firstName}! 👋` : 'Your Dashboard 👋'}
                    </h1>
                    <p className="text-gray-500 text-sm mt-1">
                      Code: <span className="font-mono font-semibold text-gray-700">{dashboard.affiliate.code}</span>
                      {' · '}30% recurring commission
                    </p>
                  </div>
                  <button
                    onClick={() => setSettingsOpen(!settingsOpen)}
                    className="flex-shrink-0 text-sm text-gray-500 hover:text-gray-800 border border-gray-200 rounded-lg px-3 py-1.5 transition-colors hover:bg-gray-50"
                  >
                    ⚙️ Settings
                  </button>
                </div>

                {/* Referral link */}
                <div className="bg-gradient-to-r from-green-600 to-emerald-700 rounded-2xl p-6 sm:p-8 text-white">
                  <p className="text-green-200 text-sm font-medium mb-2">Your Referral Link</p>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-white/10 border border-white/20 rounded-lg px-4 py-2.5 text-sm font-mono truncate">
                      {dashboard.referral_link}
                    </div>
                    <button onClick={copyLink} className="bg-yellow-400 hover:bg-yellow-300 text-gray-900 font-bold px-5 py-2.5 rounded-lg text-sm transition-colors whitespace-nowrap shadow">
                      {copied ? '✓ Copied!' : 'Copy Link'}
                    </button>
                  </div>
                  <p className="text-green-200 text-xs mt-3">30-day cookie · 30% recurring · {dashboard.affiliate.code}</p>
                </div>

                {/* User Conversion Metrics */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">User Conversion Funnel</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
                    {[
                      { 
                        label: 'Total Signups', 
                        value: dashboard.total_signups,
                        description: 'Users who signed up with your link',
                        icon: '👥'
                      },
                      { 
                        label: 'In Free Trial', 
                        value: dashboard.users_in_trial,
                        description: 'Currently in 30-day trial period',
                        icon: '🎁'
                      },
                      { 
                        label: 'Awaiting Approval', 
                        value: dashboard.users_paid_in_hold,
                        description: 'Paid users with commissions pending anti-fraud review',
                        icon: '🔒'
                      },
                      { 
                        label: 'Approved', 
                        value: dashboard.users_approved_current_cycle,
                        description: 'Commissions approved this cycle',
                        icon: '✅'
                      },
                      { 
                        label: 'All-Time Paid', 
                        value: dashboard.all_time_paid_users,
                        description: 'Total users who ever paid',
                        icon: '💰'
                      },
                    ].map((s) => (
                      <div key={s.label} className="text-center">
                        <div className="text-2xl mb-1">{s.icon}</div>
                        <div className="text-2xl font-extrabold text-gray-900">{s.value}</div>
                        <div className="text-xs font-medium text-gray-700 mt-1">{s.label}</div>
                        <div className="text-xs text-gray-400 mt-1.5 leading-tight">{s.description}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Commission Stats */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {[
                    { 
                      label: 'Pending', 
                      value: formatCents(dashboard.pending_amount_cents),
                      description: 'Commissions in anti-fraud hold period'
                    },
                    { 
                      label: 'Approved', 
                      value: formatCents(dashboard.approved_amount_cents),
                      description: 'Ready for payout after hold period'
                    },
                    { 
                      label: 'Total Earned', 
                      value: formatCents(dashboard.affiliate.total_earned_cents),
                      description: 'All-time commission earnings'
                    },
                    { 
                      label: 'Total Paid', 
                      value: formatCents(dashboard.affiliate.total_paid_cents),
                      description: 'Total commissions paid out'
                    },
                  ].map((s) => (
                    <div key={s.label} className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm text-center">
                      <div className="text-2xl font-extrabold text-gray-900">{s.value}</div>
                      <div className="text-xs font-medium text-gray-700 mt-1">{s.label}</div>
                      <div className="text-xs text-gray-400 mt-1.5 leading-tight">{s.description}</div>
                    </div>
                  ))}
                </div>

                {/* Commissions */}
                {dashboard.commissions.length > 0 ? (
                  <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-100">
                      <h2 className="font-semibold text-gray-900">Recent Commissions</h2>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                          <tr>
                            <th className="px-6 py-3 text-left">Date</th>
                            <th className="px-6 py-3 text-left">Amount</th>
                            <th className="px-6 py-3 text-left">Commission</th>
                            <th className="px-6 py-3 text-left">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                          {dashboard.commissions.slice(0, 20).map((c) => (
                            <tr key={c.id} className="hover:bg-gray-50">
                              <td className="px-6 py-3 text-gray-600">{new Date(c.created_at).toLocaleDateString()}</td>
                              <td className="px-6 py-3 text-gray-900">{formatCents(c.invoice_amount_cents)}</td>
                              <td className="px-6 py-3 text-green-700 font-medium">{formatCents(c.commission_amount_cents)}</td>
                              <td className="px-6 py-3">
                                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                                  c.status === 'approved' ? 'bg-green-100 text-green-700' :
                                  c.status === 'paid' ? 'bg-blue-100 text-blue-700' :
                                  c.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                                  'bg-gray-100 text-gray-600'
                                }`}>
                                  {c.status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 text-center">
                    <div className="text-3xl mb-3">🔗</div>
                    <p className="font-semibold text-gray-700">No commissions yet</p>
                    <p className="text-gray-400 text-sm mt-1">Share your link and you'll see earnings appear here.</p>
                    <button onClick={copyLink} className="mt-4 bg-green-600 text-white font-semibold px-6 py-2 rounded-lg text-sm hover:bg-green-700 transition-colors">
                      {copied ? '✓ Copied!' : 'Copy My Link'}
                    </button>
                  </div>
                )}

                {/* Account Settings accordion */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                  <button
                    onClick={() => setSettingsOpen(!settingsOpen)}
                    className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <span>⚙️</span>
                      <span className="font-semibold text-gray-900">Account Settings</span>
                      <span className="text-xs text-gray-400">Stripe Connect · Payout info</span>
                    </div>
                    <span className="text-gray-400 text-sm">{settingsOpen ? '▲' : '▼'}</span>
                  </button>
                  {settingsOpen && (
                    <div className="border-t border-gray-100 px-6 py-6 space-y-6">
                      {/* Stripe Connect Status */}
                      <div>
                        <h3 className="text-sm font-semibold text-gray-800 mb-3 flex items-center gap-2">
                          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M13.976 9.15c-2.172-.806-3.356-1.426-3.356-2.409 0-.831.683-1.305 1.901-1.305 2.227 0 4.515.858 6.09 1.631l.89-5.494C18.252.975 15.697 0 12.165 0 9.667 0 7.589.654 6.104 1.872 4.56 3.147 3.757 4.992 3.757 7.218c0 4.039 2.467 5.76 6.476 7.219 2.585.92 3.445 1.574 3.445 2.583 0 .98-.84 1.545-2.354 1.545-1.875 0-4.965-.921-6.99-2.109l-.9 5.555C5.175 22.99 8.385 24 11.714 24c2.641 0 4.843-.624 6.328-1.813 1.664-1.305 2.525-3.236 2.525-5.732 0-4.128-2.524-5.851-6.591-7.305z"/>
                          </svg>
                          Stripe Connect Status
                        </h3>
                        <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-xs">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Account ID:</span>
                            <span className="font-mono font-medium text-gray-900">{dashboard.affiliate.stripe_account_id || 'Not connected'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Onboarding Complete:</span>
                            <span className={`font-semibold ${dashboard.affiliate.stripe_onboarding_completed ? 'text-green-600' : 'text-yellow-600'}`}>
                              {dashboard.affiliate.stripe_onboarding_completed ? '✓ Yes' : '⏳ Pending'}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Payouts Enabled:</span>
                            <span className={`font-semibold ${dashboard.affiliate.payouts_enabled ? 'text-green-600' : 'text-yellow-600'}`}>
                              {dashboard.affiliate.payouts_enabled ? '✓ Active' : '⏳ Under Review'}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Hold Period:</span>
                            <span className="font-medium text-gray-900">{dashboard.affiliate.hold_days} days</span>
                          </div>
                        </div>
                        {!dashboard.affiliate.stripe_onboarding_completed && (
                          <button
                            onClick={startStripeOnboarding}
                            disabled={stripeOnboarding}
                            className="mt-3 w-full bg-blue-600 text-white font-semibold py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-60 transition-colors"
                          >
                            {stripeOnboarding ? 'Redirecting...' : 'Complete Stripe Onboarding'}
                          </button>
                        )}
                        {dashboard.affiliate.stripe_onboarding_completed && !dashboard.affiliate.payouts_enabled && (
                          <button
                            onClick={checkStripeStatus}
                            disabled={stripeRefreshing}
                            className="mt-3 w-full bg-yellow-600 text-white font-semibold py-2 rounded-lg text-sm hover:bg-yellow-700 disabled:opacity-60 transition-colors"
                          >
                            {stripeRefreshing ? 'Checking...' : 'Refresh Status'}
                          </button>
                        )}
                        {stripeMsg && (
                          <p className={`text-sm mt-2 ${stripeMsg.includes('✓') ? 'text-green-600' : 'text-gray-600'}`}>{stripeMsg}</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}

          </div>
        )}
      </div>
    </div>
  );
}
