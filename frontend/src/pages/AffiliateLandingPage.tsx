import React from 'react';
import { useNavigate } from 'react-router-dom';

const PERKS = [
  { icon: '💸', title: '30% Recurring Commission', desc: 'Earn 30% of every monthly payment your referrals make — not just the first one.' },
  { icon: '🔄', title: 'Monthly Payouts', desc: 'Commissions are held for 30 days then approved. Request your payout manually and get paid.' },
  { icon: '⚡', title: 'Instant Enrollment', desc: 'No approval process. Create a free affiliate account and your referral link is ready instantly.' },
  { icon: '📊', title: 'Full Dashboard', desc: 'Track clicks, conversions, commissions, and payout history — all inside the app.' },
  { icon: '🧾', title: 'Tax Ready', desc: 'W-9 form collection and YTD earnings tracking built in. 1099 preparation made easy.' },
  { icon: '🔗', title: '30-Day Cookie', desc: 'Your referral link tracks conversions for 30 days after the click.' },
];

const FAQ = [
  {
    q: 'How much do I earn?',
    a: '30% of each monthly payment your referred user makes. On the $19.99/month plan that\'s ~$6/month per active subscriber you referred — for as long as they stay subscribed.',
  },
  {
    q: 'When do I get paid?',
    a: 'Commissions are held for 30 days (chargeback window). Once cleared, they become "approved" and you can request a payout. Manual bank transfer or check.',
  },
  {
    q: 'Is there an approval process to join?',
    a: 'No. Create a free affiliate account at /affiliate-signup and your referral link is generated immediately after email verification.',
  },
  {
    q: 'How long does my referral link track?',
    a: 'Your referral code is saved in the browser for 30 days after someone clicks your link.',
  },
  {
    q: 'What counts as a conversion?',
    a: 'When someone signs up using your referral link and starts a paid subscription (even during the free trial — the commission is created on the first charge after trial ends).',
  },
  {
    q: 'Do I need a 1099?',
    a: 'If you earn over $600 in a calendar year, we\'ll need a W-9 from you. You can submit it inside the app. All earnings are tracked for easy 1099 generation.',
  },
];

export default function AffiliateLandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white font-sans">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur border-b border-gray-100 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <button onClick={() => navigate('/')} className="flex items-center gap-2">
            <span className="text-2xl">🏘️</span>
            <span className="font-bold text-gray-900 text-lg">FindBestRentals</span>
          </button>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/affiliate-login')}
              className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors px-4 py-2"
            >
              Log In
            </button>
            <button
              onClick={() => navigate('/affiliate-signup')}
              className="text-sm font-semibold bg-green-600 text-white px-5 py-2 rounded-lg hover:bg-green-700 transition-colors shadow"
            >
              Join Free
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-24 px-6 bg-gradient-to-br from-green-700 via-green-600 to-emerald-700 text-white text-center">
        <div className="max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-green-500/40 border border-green-400/50 rounded-full px-4 py-1.5 text-sm font-medium mb-6">
            <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
            Affiliate Program — Earn recurring commissions
          </div>
          <h1 className="text-5xl sm:text-6xl font-extrabold leading-tight mb-6">
            Earn <span className="text-yellow-300">30%</span><br />
            Every Month
          </h1>
          <p className="text-xl text-green-100 mb-10 max-w-xl mx-auto">
            Refer investors to FindBestRentals and earn 30% of their subscription every month they stay subscribed.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/affiliate-signup')}
              className="bg-yellow-400 text-gray-900 font-bold text-lg px-8 py-4 rounded-xl hover:bg-yellow-300 transition-colors shadow-lg"
            >
              Join the Affiliate Program →
            </button>
            <button
              onClick={() => navigate('/affiliate-login')}
              className="bg-white/10 border border-white/30 text-white font-semibold text-lg px-8 py-4 rounded-xl hover:bg-white/20 transition-colors"
            >
              Already a member? Log In
            </button>
          </div>
          <p className="mt-5 text-green-200 text-sm">Free to join &nbsp;·&nbsp; No approval needed &nbsp;·&nbsp; Instant enrollment</p>
        </div>
      </section>

      {/* How it works */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">How it works</h2>
            <p className="text-gray-500 text-lg">Three steps to start earning.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
            {[
              { num: '1', title: 'Create Free Account', desc: 'Sign up for a free affiliate account — no subscription required. Your referral link is generated instantly.' },
              { num: '2', title: 'Share Your Link', desc: 'Copy your unique referral link and share it anywhere — social, YouTube, email, blog, or real estate groups.' },
              { num: '3', title: 'Earn Every Month', desc: 'When someone subscribes through your link, you earn 30% of every payment they make — indefinitely.' },
            ].map((s) => (
              <div key={s.num} className="text-center bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
                <div className="w-14 h-14 rounded-2xl bg-green-600 text-white text-2xl font-extrabold flex items-center justify-center mx-auto mb-4 shadow-lg">
                  {s.num}
                </div>
                <h3 className="font-semibold text-gray-900 mb-2 text-lg">{s.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Perks */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Everything included</h2>
            <p className="text-gray-500 text-lg max-w-xl mx-auto">A clean, transparent program with no surprises.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {PERKS.map((p) => (
              <div key={p.title} className="bg-white rounded-2xl p-7 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <div className="text-4xl mb-4">{p.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{p.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{p.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Earnings calculator */}
      <section className="py-20 px-6 bg-gradient-to-r from-green-600 to-emerald-700 text-white text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-4xl font-bold mb-6">What could you earn?</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 mb-8">
            {[
              { referrals: 10, monthly: '$19.99', commission: '$6.00', total: '$60/mo' },
              { referrals: 25, monthly: '$19.99', commission: '$6.00', total: '$150/mo' },
              { referrals: 100, monthly: '$19.99', commission: '$6.00', total: '$600/mo' },
            ].map((row) => (
              <div key={row.referrals} className="bg-white/10 border border-white/20 rounded-2xl p-6">
                <div className="text-4xl font-extrabold text-yellow-300 mb-1">{row.total}</div>
                <div className="text-green-100 text-sm">{row.referrals} active referrals</div>
                <div className="text-green-200 text-xs mt-2">30% of {row.monthly} = {row.commission}/referral</div>
              </div>
            ))}
          </div>
          <p className="text-green-200 text-sm">Recurring — as long as your referrals stay subscribed.</p>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-4xl font-bold text-gray-900 text-center mb-14">Frequently asked questions</h2>
          <div className="space-y-6">
            {FAQ.map((item) => (
              <div key={item.q} className="bg-white rounded-2xl p-7 shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-900 mb-2">{item.q}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Ready to start earning?</h2>
          <p className="text-gray-500 text-lg mb-8">
            Create a free affiliate account and get your referral link in under 60 seconds.
          </p>
          <button
            onClick={() => navigate('/affiliate-signup')}
            className="bg-green-600 text-white font-bold text-xl px-10 py-5 rounded-2xl hover:bg-green-700 transition-colors shadow-lg"
          >
            Get Your Referral Link →
          </button>
          <p className="mt-4 text-gray-400 text-sm">Instant enrollment · No approval · 30% recurring</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-8 px-6 text-center text-gray-400 text-sm">
        © {new Date().getFullYear()} FindBestRentals ·{' '}
        <button onClick={() => navigate('/')} className="hover:text-gray-600 transition-colors">Home</button>
        {' '}·{' '}
        <button onClick={() => navigate('/affiliate-signup')} className="hover:text-gray-600 transition-colors">Join Affiliate</button>
      </footer>
    </div>
  );
}
