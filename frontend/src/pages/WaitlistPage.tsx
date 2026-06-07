import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

const WAITLIST_CLAIMED = 241;
const WAITLIST_TOTAL   = 500;

// Grain overlay component
function GrainOverlay() {
  return (
    <div className="pointer-events-none fixed inset-0 z-[999] opacity-[0.015]"
      style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='2.5' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
      }}
    />
  );
}

// ─── Feature cards ────────────────────────────────────────────────────────────
const FEATURES = [
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    title: 'Full analysis — instantly',
    body: 'Cash flow, net operating income, cap rate, CoC return, BRRRR exit, and 10-year appreciation — pre-calculated on every single listing the moment you open it.',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
    ),
    title: 'Section 8 rent data built in',
    body: 'We pull HUD Fair Market Rent tables for every ZIP code. See exactly what the government will pay — by bedroom count — before you make an offer.',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    title: 'BRRRR strategy calculator',
    body: 'Enter your rehab estimate and ARV. We instantly show your refi cash-out, infinite return potential, and remaining equity — all live as you type.',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
    ),
    title: 'Interactive map with filters',
    body: 'Visualize every deal on a live map. Filter by cash flow, cap rate, price, property type, and status. Only deals that meet your criteria make the cut.',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
          d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    title: 'Live assumption controls',
    body: 'Tweak down payment, interest rate, vacancy rate, management fee and more — every metric across every listing recalculates in real time.',
  },
];

// ─── How it works steps ───────────────────────────────────────────────────────
const STEPS = [
  {
    n: '01',
    title: 'Enter your market',
    body: 'Type any ZIP code. We pull every active listing and layer on Section 8 FMR rent data automatically.',
  },
  {
    n: '02',
    title: 'Set your criteria',
    body: 'Filter by minimum cash flow, cap rate, price range, and property type. Only deals that pencil show up.',
  },
  {
    n: '03',
    title: 'Analyze in seconds',
    body: 'Cash flow, BRRRR, appreciation — every number is waiting for you before you pick up the phone.',
  },
  {
    n: '04',
    title: 'Make confident offers',
    body: 'Go into negotiations knowing your exact numbers. No more guessing, no more spreadsheets, no more second-guessing yourself at closing.',
  },
];

// ─── Root component ───────────────────────────────────────────────────────────
export default function WaitlistPage() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('/api/v1/waitlist/join', { email, name });
      setDone(true);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  if (done) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6" style={{ background: 'linear-gradient(135deg, #a7f3d0 0%, #99f6e4 20%, #ecfdf5 40%, #fef9c3 70%, #fbcfe8 100%)' }}>
        <GrainOverlay />
        <div className="relative z-10 text-center max-w-md animate-fadeInUp">
          <div className="mx-auto mb-8 w-20 h-20 rounded-full bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center shadow-2xl shadow-emerald-900/25">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-stone-900 mb-3">You're on the list.</h2>
          <p className="text-stone-500 mb-8 leading-relaxed">
            We'll reach out the moment your spot opens. Early members get locked-in pricing — you won't pay more than what's reserved for you today.
          </p>
          <Link to="/" className="inline-flex items-center gap-2 text-emerald-600 text-sm font-semibold hover:text-emerald-700 transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen text-stone-900 overflow-x-hidden font-sans" style={{ background: 'linear-gradient(135deg, #a7f3d0 0%, #99f6e4 20%, #ecfdf5 40%, #fef9c3 70%, #fbcfe8 100%)' }}>
      <GrainOverlay />

      {/* ── NAV ── */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl" style={{ background: 'rgba(255,255,255,0.85)' }}>
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-900/20 group-hover:shadow-emerald-900/30 transition-shadow">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </div>
            <span className="font-bold text-stone-900 text-base tracking-tight">FindBestRentals</span>
          </Link>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/login')}
              className="text-sm font-medium text-stone-500 hover:text-stone-900 transition-colors px-4 py-2"
            >
              Log In
            </button>
          </div>
        </div>
      </nav>

      {/* ── Floating organic blobs ── */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[10%] left-[5%] w-[450px] h-[450px] animate-float" style={{ background: 'radial-gradient(circle, rgba(167,243,208,0.15) 0%, transparent 60%)', borderRadius: '45% 55% 60% 40% / 50% 55% 45% 50%' }} />
        <div className="absolute top-[15%] right-[10%] w-[380px] h-[380px] animate-float-delayed" style={{ background: 'radial-gradient(circle, rgba(153,246,228,0.12) 0%, transparent 60%)', borderRadius: '60% 40% 50% 50% / 45% 60% 40% 55%' }} />
        <div className="absolute top-[50%] left-[50%] -translate-x-1/2 w-[420px] h-[420px] animate-float-slow" style={{ background: 'radial-gradient(circle, rgba(254,249,195,0.10) 0%, transparent 60%)', borderRadius: '50% 50% 55% 45% / 55% 45% 55% 45%' }} />
        <div className="absolute top-[40%] left-[30%] w-[350px] h-[350px] animate-float-slow" style={{ background: 'radial-gradient(circle, rgba(244,114,182,0.08) 0%, transparent 60%)', borderRadius: '40% 60% 55% 45% / 50% 50% 50% 50%' }} />
      </div>

      {/* ─────────────────────────────────────────────────────────────────────
          HERO
      ───────────────────────────────────────────────────────────────────── */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 pt-32 pb-20 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2.5 bg-white/80 backdrop-blur-sm border border-emerald-600/20 text-emerald-700 text-xs font-semibold tracking-widest uppercase px-5 py-2.5 rounded-full mb-8 shadow-lg shadow-emerald-900/10">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
          Private Beta · Limited Early Access
        </div>

        {/* Headline */}
        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black leading-[1.08] tracking-tight mb-6 text-stone-900" style={{ textShadow: '0 2px 40px rgba(0,0,0,0.03)' }}>
          Find the rentals<br />
          <span className="bg-gradient-to-r from-emerald-700 via-teal-600 to-cyan-600 bg-clip-text text-transparent">
            that actually pay.
          </span>
        </h1>

        {/* Sub-headline */}
        <p className="text-stone-600 text-lg sm:text-xl max-w-3xl mx-auto mb-12 leading-relaxed">
          FindBestRentals layers Section 8 HUD rent data and a full BRRRR calculator on top of every listing — so you see the real numbers before you spend a dollar.
        </p>

        {/* Waitlist form with name and email */}
        <form onSubmit={handleSubmit} id="hero-form" className="max-w-2xl mx-auto mb-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
            <input
              type="text"
              required
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Your name"
              className="w-full bg-white/95 backdrop-blur-md border border-stone-200 text-stone-900 placeholder-stone-400 rounded-xl px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all shadow-sm"
            />
            <input
              type="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="Your email"
              className="w-full bg-white/95 backdrop-blur-md border border-stone-200 text-stone-900 placeholder-stone-400 rounded-xl px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all shadow-sm"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 disabled:from-emerald-800 disabled:to-teal-800 text-white font-bold px-8 py-4 rounded-xl transition-all shadow-xl shadow-emerald-900/20 hover:shadow-2xl hover:shadow-emerald-900/30 hover:-translate-y-0.5 disabled:shadow-none disabled:translate-y-0"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Joining…
              </span>
            ) : 'Join the Waitlist →'}
          </button>
        </form>
        {error && (
          <p className="text-red-600 text-sm mb-4 font-medium">{error}</p>
        )}
        <p className="text-stone-500 text-xs">No credit card · No spam · Cancel anytime</p>

        {/* Waitlist progress bar */}
        <div className="mt-16 max-w-xl mx-auto bg-white/80 backdrop-blur-md rounded-2xl border border-stone-200 shadow-xl shadow-stone-900/5 p-8">
          <p className="text-xs font-bold text-emerald-700 uppercase tracking-widest mb-5">Private Beta · 500 spots total</p>
          <div className="relative h-3 bg-stone-100 rounded-full overflow-hidden mb-4">
            <div
              className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-emerald-600 to-teal-500 shadow-lg shadow-emerald-900/20"
              style={{ width: `${(WAITLIST_CLAIMED / WAITLIST_TOTAL) * 100}%` }}
            />
          </div>
          <div className="flex justify-between items-baseline">
            <span className="text-stone-900 font-black text-2xl tabular-nums">
              {WAITLIST_CLAIMED} <span className="text-stone-500 text-base font-normal">/ {WAITLIST_TOTAL} spots claimed</span>
            </span>
            <span className="text-emerald-700 text-sm font-bold tabular-nums">
              {WAITLIST_TOTAL - WAITLIST_CLAIMED} remaining
            </span>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────────────
          FEATURES
      ───────────────────────────────────────────────────────────────────── */}
      <section className="relative z-10 py-24 border-t border-white/40">
        <div className="absolute inset-0 pointer-events-none" style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(255,255,255,0.5) 0%, transparent 60%)' }} />
        
        <div className="relative max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-emerald-700 text-xs font-bold tracking-[0.2em] uppercase mb-4">Everything you need to invest</p>
            <h2 className="text-3xl sm:text-4xl font-black tracking-tight text-stone-900 mb-4">
              Built for serious investors.
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f, i) => (
              <div key={i}
                className="group relative bg-white/90 backdrop-blur-sm hover:bg-white border border-stone-200 hover:border-emerald-300 rounded-2xl p-7 transition-all duration-300 shadow-lg shadow-stone-900/5 hover:shadow-xl hover:shadow-emerald-900/10 hover:-translate-y-1"
              >
                <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center text-white mb-5 shadow-lg shadow-emerald-900/20">
                  {f.icon}
                </div>
                <h3 className="text-stone-900 font-bold text-base mb-2">{f.title}</h3>
                <p className="text-stone-600 text-sm leading-relaxed">{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────────────
          HOW IT WORKS
      ───────────────────────────────────────────────────────────────────── */}
      <section className="relative z-10 py-24 border-t border-white/40">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-emerald-700 text-xs font-bold tracking-[0.2em] uppercase mb-4">The process</p>
            <h2 className="text-3xl sm:text-4xl font-black tracking-tight text-stone-900">
              From zip code to offer<br />
              <span className="text-stone-600 font-normal">in under five minutes.</span>
            </h2>
          </div>

          <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-[19px] top-2 bottom-2 w-px bg-gradient-to-b from-emerald-600/40 via-emerald-600/20 to-transparent hidden sm:block" />

            <div className="space-y-10">
              {STEPS.map((s, i) => (
                <div key={i} className="flex gap-8 items-start">
                  {/* Step number */}
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-900/20">
                    <span className="text-white text-xs font-black tabular-nums">{s.n}</span>
                  </div>
                  <div className="pt-1.5 bg-white/70 backdrop-blur-sm rounded-xl p-5 flex-1 border border-stone-200 shadow-sm">
                    <h3 className="text-stone-900 font-bold text-lg mb-1">{s.title}</h3>
                    <p className="text-stone-600 leading-relaxed">{s.body}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────────────
          TESTIMONIAL
      ───────────────────────────────────────────────────────────────────── */}
      <section className="relative z-10 py-20 border-t border-white/40">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <div className="flex justify-center gap-1 mb-8">
            {[0,1,2,3,4].map(i => (
              <svg key={i} className="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            ))}
          </div>
          <blockquote className="text-xl sm:text-2xl font-normal text-stone-700 leading-relaxed mb-8">
            "I used to spend two hours running numbers on a single property. Now I filter 200 listings in ten minutes and only call on the ones that already pencil out. It's changed how I invest."
          </blockquote>
          <div className="flex items-center justify-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center text-white font-bold text-sm shadow-lg">M</div>
            <div className="text-left">
              <div className="text-stone-900 text-sm font-semibold">Marcus T.</div>
              <div className="text-stone-500 text-xs">Real estate investor · 12 doors · Cleveland, OH</div>
            </div>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────────────
          FINAL CTA
      ───────────────────────────────────────────────────────────────────── */}
      <section className="relative z-10 py-28 border-t border-white/40">
        <div className="absolute inset-0 pointer-events-none" style={{ background: 'radial-gradient(ellipse at 50% 100%, rgba(52,211,153,0.15) 0%, transparent 60%)' }} />
        
        <div className="relative max-w-xl mx-auto px-6 text-center">
          <p className="text-emerald-700 text-xs font-bold tracking-[0.2em] uppercase mb-4">Limited spots available</p>
          <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-stone-900 mb-5">
            Stop letting deals<br />slip past you.
          </h2>
          <p className="text-stone-600 mb-10 leading-relaxed">
            Early members get locked-in pricing and first access when we open doors. Takes five seconds to reserve your spot.
          </p>
          <form onSubmit={handleSubmit} className="max-w-md mx-auto mb-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
              <input
                type="text"
                required
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="Your name"
                className="w-full bg-white/95 backdrop-blur-md border border-stone-200 text-stone-900 placeholder-stone-400 rounded-xl px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all shadow-sm"
              />
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="Your email"
                className="w-full bg-white/95 backdrop-blur-md border border-stone-200 text-stone-900 placeholder-stone-400 rounded-xl px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all shadow-sm"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 disabled:from-emerald-800 disabled:to-teal-800 text-white font-bold px-8 py-4 rounded-xl transition-all shadow-xl shadow-emerald-900/20 hover:shadow-2xl hover:shadow-emerald-900/30 hover:-translate-y-0.5 disabled:shadow-none disabled:translate-y-0"
            >
              {loading ? 'Joining…' : 'Join the Waitlist →'}
            </button>
          </form>
          {error && <p className="text-red-600 text-sm mb-3 font-medium">{error}</p>}
          <p className="text-stone-500 text-xs">
            Already have an invite?{' '}
            <Link to="/signup" className="text-emerald-700 hover:text-emerald-800 font-semibold underline underline-offset-2 transition-colors">
              Sign up here
            </Link>
          </p>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="relative z-10 border-t border-white/40 py-8 bg-white/50 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <span className="text-stone-600 text-xs">© 2026 FindBestRentals. All rights reserved.</span>
          <div className="flex items-center gap-6 text-xs text-stone-600">
            <Link to="/privacy" className="hover:text-stone-900 transition-colors">Privacy</Link>
            <Link to="/terms" className="hover:text-stone-900 transition-colors">Terms</Link>
            <Link to="/login" className="hover:text-stone-900 transition-colors">Log in</Link>
          </div>
        </div>
      </footer>

    </div>
  );
}
