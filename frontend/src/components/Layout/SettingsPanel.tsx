import React, { useState, useEffect, useCallback } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { useAuth } from '../../contexts/AuthContext';
import { updateProfile, changePassword, setup2fa, enable2fa, disable2fa } from '../../services/authService';
import { createPortalSession } from '../../services/billingService';
import {
  enrollAffiliate,
  getAffiliateDashboard,
  upsertTaxProfile,
  formatCents,
  type AffiliateDashboard,
  type TaxProfileUpsert,
} from '../../services/affiliateService';

interface Props {
  onClose: () => void;
}

type Tab = 'profile' | 'security' | 'billing';

export default function SettingsPanel({ onClose }: Props) {
  const { user, refreshUser, appMode } = useAuth();
  const [tab, setTab] = useState<Tab>('profile');
  const availableTabs: Tab[] = appMode === 'production' ? ['profile', 'security', 'billing'] : ['profile', 'security'];

  // Profile
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileMsg, setProfileMsg] = useState('');

  // Password
  const [currentPw, setCurrentPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [pwSaving, setPwSaving] = useState(false);
  const [pwMsg, setPwMsg] = useState('');
  const [pwError, setPwError] = useState('');

  // 2FA
  type TotpSetupStep = 'idle' | 'setup' | 'verify' | 'disabling';
  const [totpStep, setTotpStep] = useState<TotpSetupStep>('idle');
  const [totpSecret, setTotpSecret] = useState('');
  const [totpUri, setTotpUri] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [disablePw, setDisablePw] = useState('');
  const [totpMsg, setTotpMsg] = useState('');
  const [totpError, setTotpError] = useState('');
  const [totpLoading, setTotpLoading] = useState(false);

  async function startTotpSetup() {
    setTotpError(''); setTotpMsg(''); setTotpLoading(true);
    try {
      const res = await setup2fa();
      setTotpSecret(res.secret);
      setTotpUri(res.uri);
      setTotpStep('setup');
    } catch (e: any) {
      setTotpError(e?.response?.data?.detail || 'Failed to start 2FA setup.');
    } finally { setTotpLoading(false); }
  }

  async function confirmTotpEnable(e: React.FormEvent) {
    e.preventDefault();
    setTotpError(''); setTotpLoading(true);
    try {
      await enable2fa(totpCode);
      await refreshUser();
      setTotpStep('idle'); setTotpCode('');
      setTotpMsg('Two-factor authentication is now enabled.');
    } catch (err: any) {
      setTotpError(err?.response?.data?.detail || 'Invalid code.');
    } finally { setTotpLoading(false); }
  }

  async function confirmTotpDisable(e: React.FormEvent) {
    e.preventDefault();
    setTotpError(''); setTotpLoading(true);
    try {
      await disable2fa(disablePw);
      await refreshUser();
      setTotpStep('idle'); setDisablePw('');
      setTotpMsg('Two-factor authentication has been disabled.');
    } catch (err: any) {
      setTotpError(err?.response?.data?.detail || 'Incorrect password.');
    } finally { setTotpLoading(false); }
  }

  // Billing
  const [portalLoading, setPortalLoading] = useState(false);
  const [portalError, setPortalError] = useState('');

  // Referrals
  const [affDashboard, setAffDashboard] = useState<AffiliateDashboard | null>(null);
  const [affLoading, setAffLoading] = useState(false);
  const [affError, setAffError] = useState('');
  const [enrolling, setEnrolling] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showW9, setShowW9] = useState(false);
  const [taxForm, setTaxForm] = useState<TaxProfileUpsert>({});
  const [taxSaving, setTaxSaving] = useState(false);
  const [taxMsg, setTaxMsg] = useState('');
  const [showTin, setShowTin] = useState(false);

  function formatTin(digits: string): string {
    const d = digits.slice(0, 9);
    if (d.length > 5) return `${d.slice(0, 3)}-${d.slice(3, 5)}-${d.slice(5)}`;
    if (d.length > 3) return `${d.slice(0, 3)}-${d.slice(3)}`;
    return d;
  }

  function handleTinChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (!showTin) return; // masked mode is handled by onKeyDown
    const digits = e.target.value.replace(/\D/g, '');
    setTaxForm({ ...taxForm, tin: formatTin(digits) });
  }

  function handleTinKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (showTin) return; // visible mode: let onChange handle it normally
    const digits = (taxForm.tin || '').replace(/\D/g, '');
    if (e.key === 'Backspace') {
      e.preventDefault();
      setTaxForm({ ...taxForm, tin: formatTin(digits.slice(0, -1)) });
    } else if (/^\d$/.test(e.key) && digits.length < 9) {
      e.preventDefault();
      setTaxForm({ ...taxForm, tin: formatTin(digits + e.key) });
    } else if (e.key !== 'Tab') {
      e.preventDefault();
    }
  }

  const loadAffiliate = useCallback(async () => {
    setAffLoading(true);
    setAffError('');
    try {
      const data = await getAffiliateDashboard();
      setAffDashboard(data);
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setAffDashboard(null); // not enrolled yet
      } else {
        setAffError('Could not load affiliate data.');
      }
    } finally {
      setAffLoading(false);
    }
  }, []);

  async function handleEnroll() {
    setEnrolling(true);
    setAffError('');
    try {
      await enrollAffiliate();
      await loadAffiliate();
    } catch {
      setAffError('Enrollment failed. Please try again.');
    } finally {
      setEnrolling(false);
    }
  }

  function copyLink() {
    if (affDashboard?.referral_link) {
      navigator.clipboard.writeText(affDashboard.referral_link);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  async function saveTaxProfile(e: React.FormEvent) {
    e.preventDefault();
    setTaxSaving(true);
    setTaxMsg('');
    try {
      await upsertTaxProfile({
        ...taxForm,
        w9_collected: true,
        signature_text: taxForm.signature_text,
        perjury_acknowledged: taxForm.perjury_acknowledged,
        certification_confirmed: taxForm.certification_confirmed
      });
      setTaxMsg('Saved!');
      await loadAffiliate();
    } catch {
      setTaxMsg('Save failed.');
    } finally {
      setTaxSaving(false);
    }
  }

  async function openPortal() {
    setPortalError('');
    setPortalLoading(true);
    try {
      const url = await createPortalSession();
      window.location.href = url;
    } catch (err: any) {
      setPortalError(err?.response?.data?.detail || 'Could not open billing portal.');
      setPortalLoading(false);
    }
  }

  const STATUS_LABELS: Record<string, { label: string; color: string }> = {
    trialing: { label: 'Active (Trial)',  color: 'text-green-600 bg-green-50 border-green-200' },
    active:   { label: 'Active',          color: 'text-green-600 bg-green-50 border-green-200' },
    past_due: { label: 'Past Due',        color: 'text-yellow-700 bg-yellow-50 border-yellow-200' },
    canceled: { label: 'Canceled',        color: 'text-red-600 bg-red-50 border-red-200' },
    unpaid:   { label: 'Unpaid',          color: 'text-red-600 bg-red-50 border-red-200' },
  };
  const statusInfo = STATUS_LABELS[user?.subscription_status || ''] ?? {
    label: 'No subscription',
    color: 'text-gray-500 bg-gray-50 border-gray-200',
  };

  async function saveProfile(e: React.FormEvent) {
    e.preventDefault();
    setProfileSaving(true);
    setProfileMsg('');
    try {
      await updateProfile(fullName);
      await refreshUser();
      setProfileMsg('Profile updated!');
    } catch {
      setProfileMsg('Save failed. Please try again.');
    } finally {
      setProfileSaving(false);
    }
  }

  async function savePw(e: React.FormEvent) {
    e.preventDefault();
    setPwError('');
    setPwMsg('');
    if (newPw !== confirmPw) { setPwError('New passwords do not match.'); return; }
    if (newPw.length < 8) { setPwError('Password must be at least 8 characters.'); return; }
    setPwSaving(true);
    try {
      await changePassword(currentPw, newPw);
      setPwMsg('Password changed successfully!');
      setCurrentPw(''); setNewPw(''); setConfirmPw('');
    } catch (err: any) {
      setPwError(err?.response?.data?.detail || 'Change failed.');
    } finally {
      setPwSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-bold text-gray-900">Account Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-100 px-6">
          {availableTabs.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`py-3 px-4 text-sm font-medium border-b-2 transition-colors capitalize ${
                tab === t
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {tab === 'profile' && (
            <form onSubmit={saveProfile} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  disabled
                  value={user?.email || ''}
                  className="w-full border border-gray-200 bg-gray-50 rounded-lg px-4 py-2.5 text-sm text-gray-500 cursor-not-allowed"
                />
                <p className="text-xs text-gray-400 mt-1">Email cannot be changed.</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Your name"
                />
              </div>
              {profileMsg && (
                <p className={`text-sm ${profileMsg.includes('failed') ? 'text-red-600' : 'text-green-600'}`}>
                  {profileMsg}
                </p>
              )}
              <button
                type="submit"
                disabled={profileSaving}
                className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-60"
              >
                {profileSaving ? 'Saving…' : 'Save Profile'}
              </button>
            </form>
          )}

          {tab === 'security' && (
            <div className="space-y-8">
              {/* Change Password */}
              <form onSubmit={savePw} className="space-y-5">
                <h3 className="font-semibold text-gray-800">Change Password</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
                <input
                  type="password"
                  required
                  value={currentPw}
                  onChange={(e) => setCurrentPw(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="••••••••"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                <input
                  type="password"
                  required
                  value={newPw}
                  onChange={(e) => setNewPw(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Min 8 characters"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                <input
                  type="password"
                  required
                  value={confirmPw}
                  onChange={(e) => setConfirmPw(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Repeat new password"
                />
              </div>
              {pwError && <p className="text-sm text-red-600">{pwError}</p>}
              {pwMsg && <p className="text-sm text-green-600">{pwMsg}</p>}
              <button
                type="submit"
                disabled={pwSaving}
                className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-60"
              >
                {pwSaving ? 'Updating…' : 'Change Password'}
              </button>
            </form>

              {/* Two-Factor Authentication */}
              <div className="border-t border-gray-100 pt-6">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-800">Two-Factor Authentication</h3>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {user?.totp_enabled
                        ? 'Enabled — your account is protected with an authenticator app.'
                        : 'Add an extra layer of security with an authenticator app.'}
                    </p>
                  </div>
                  <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                    user?.totp_enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                  }`}>
                    {user?.totp_enabled ? 'ON' : 'OFF'}
                  </span>
                </div>

                {totpMsg && <p className="text-sm text-green-600 mb-3">{totpMsg}</p>}
                {totpError && <p className="text-sm text-red-600 mb-3">{totpError}</p>}

                {totpStep === 'idle' && !user?.totp_enabled && (
                  <button
                    onClick={startTotpSetup}
                    disabled={totpLoading}
                    className="w-full border border-blue-500 text-blue-600 font-semibold py-2.5 rounded-lg hover:bg-blue-50 transition disabled:opacity-60 text-sm"
                  >
                    {totpLoading ? 'Loading…' : 'Set Up Authenticator App'}
                  </button>
                )}

                {totpStep === 'setup' && (
                  <div className="space-y-4">
                    <p className="text-sm text-gray-600">
                      Scan the QR code below with your authenticator app (Google Authenticator, Authy, etc.),
                      or enter the secret key manually.
                    </p>
                    {/* QR code rendered locally — no external service needed */}
                    <div className="flex justify-center">
                      <QRCodeSVG
                        value={totpUri}
                        size={200}
                        level="M"
                        className="rounded-lg border border-gray-200 p-2 bg-white"
                      />
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-500 mb-1">Manual entry key:</p>
                      <code className="text-sm font-mono tracking-widest text-gray-800 select-all">{totpSecret}</code>
                    </div>
                    <button
                      onClick={() => setTotpStep('verify')}
                      className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 text-sm"
                    >
                      I've scanned it — enter code to confirm
                    </button>
                    <button
                      onClick={() => { setTotpStep('idle'); setTotpSecret(''); setTotpUri(''); }}
                      className="w-full text-sm text-gray-500 hover:text-gray-700"
                    >
                      Cancel
                    </button>
                  </div>
                )}

                {totpStep === 'verify' && (
                  <form onSubmit={confirmTotpEnable} className="space-y-4">
                    <p className="text-sm text-gray-600">
                      Enter the 6-digit code from your authenticator app to confirm setup.
                    </p>
                    <input
                      type="text"
                      inputMode="numeric"
                      pattern="\d{6}"
                      maxLength={6}
                      required
                      autoFocus
                      value={totpCode}
                      onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, ''))}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm text-center tracking-[0.5em] font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="000000"
                    />
                    <button
                      type="submit"
                      disabled={totpLoading || totpCode.length !== 6}
                      className="w-full bg-green-600 text-white font-semibold py-2.5 rounded-lg hover:bg-green-700 disabled:opacity-60 text-sm"
                    >
                      {totpLoading ? 'Verifying…' : 'Enable 2FA'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setTotpStep('setup')}
                      className="w-full text-sm text-gray-500 hover:text-gray-700"
                    >
                      ← Back
                    </button>
                  </form>
                )}

                {totpStep === 'idle' && user?.totp_enabled && (
                  <button
                    onClick={() => { setTotpStep('disabling'); setTotpError(''); setTotpMsg(''); }}
                    className="w-full border border-red-300 text-red-600 font-semibold py-2.5 rounded-lg hover:bg-red-50 transition text-sm"
                  >
                    Disable Two-Factor Authentication
                  </button>
                )}

                {totpStep === 'disabling' && (
                  <form onSubmit={confirmTotpDisable} className="space-y-4">
                    <p className="text-sm text-gray-600">
                      Enter your account password to disable 2FA.
                    </p>
                    <input
                      type="password"
                      required
                      autoFocus
                      value={disablePw}
                      onChange={(e) => setDisablePw(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
                      placeholder="Your password"
                    />
                    <button
                      type="submit"
                      disabled={totpLoading}
                      className="w-full bg-red-600 text-white font-semibold py-2.5 rounded-lg hover:bg-red-700 disabled:opacity-60 text-sm"
                    >
                      {totpLoading ? 'Disabling…' : 'Confirm — Disable 2FA'}
                    </button>
                    <button
                      type="button"
                      onClick={() => { setTotpStep('idle'); setDisablePw(''); }}
                      className="w-full text-sm text-gray-500 hover:text-gray-700"
                    >
                      Cancel
                    </button>
                  </form>
                )}
              </div>
            </div>
          )}

          {tab === 'billing' && (
            <div className="space-y-5">
              {/* Current status */}
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Subscription Status</p>
                <span className={`inline-flex items-center border rounded-full px-3 py-1 text-xs font-semibold ${statusInfo.color}`}>
                  {statusInfo.label}
                </span>
              </div>

              <div className="rounded-xl bg-blue-50 border border-blue-100 p-4 text-sm text-blue-800">
                <p className="font-semibold mb-1">Manage your subscription</p>
                <p className="text-blue-600 text-xs">
                  Update your payment method, view invoices, or cancel your plan — all through the secure Stripe portal.
                </p>
              </div>

              {portalError && (
                <p className="text-sm text-red-600">{portalError}</p>
              )}

              {user?.stripe_customer_id || ['trialing', 'active', 'past_due'].includes(user?.subscription_status || '') ? (
                <button
                  onClick={openPortal}
                  disabled={portalLoading}
                  className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-60 flex items-center justify-center gap-2"
                >
                  {portalLoading ? (
                    <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Opening portal…</>
                  ) : (
                    '💳 Manage Subscription →'
                  )}
                </button>
              ) : (
                <p className="text-sm text-gray-500">
                  No active subscription found.{' '}
                  <a href="/subscribe" className="text-blue-600 hover:underline">Subscribe now</a>
                </p>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
