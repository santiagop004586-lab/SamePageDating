import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { formatCents, type PayoutBatchOut } from '../services/affiliateService';
import {
  listAdminAffiliates,
  listAdminPayouts,
  approveDueCommissions,
  createPayoutBatch,
  markBatchPaid,
  paySelectedCommissions,
  getAffiliateTin,
  listWaitlist,
  deleteWaitlistEntry,
  listInvites,
  createInvites,
  revokeInvite,
  listBetaUsers,
  revokeBetaAccess,
  reviewCommissions,
  type AdminAffiliateRow,
  type WaitlistEntry,
  type InviteEntry,
  type BetaUser,
  type AdminCommissionReviewRow,
} from '../services/adminService';

type Tab = 'taxes' | 'payouts' | 'beta';
type ModalType = 'payout' | 'markpaid' | 'tin' | null;

interface PayoutModal {
  affiliate: AdminAffiliateRow;
}

interface MarkPaidModal {
  batchId: number;
  amount: number;
  affiliateEmail: string;
  payoutEmail: string | null;
}

interface TinModal {
  affiliateId: number;
  tin: string | null;
  legalName: string | null;
  taxClass: string | null;
  loading: boolean;
}

export default function AdminPage() {
  const { user, logout, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<Tab>('taxes');

  // ── Affiliates tab state ──────────────────────────────────────────────────
  const [affiliates, setAffiliates] = useState<AdminAffiliateRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [approveMsg, setApproveMsg] = useState('');
  const [approving, setApproving] = useState(false);

  // Modal state
  const [modal, setModal] = useState<ModalType>(null);
  const [payoutModal, setPayoutModal] = useState<PayoutModal | null>(null);
  const [markPaidModal, setMarkPaidModal] = useState<MarkPaidModal | null>(null);
  const [tinModal, setTinModal] = useState<TinModal | null>(null);

  // Payout form
  const [payoutSaving, setPayoutSaving] = useState(false);
  const [payoutError, setPayoutError] = useState('');
  const [createdBatchId, setCreatedBatchId] = useState<number | null>(null);

  // Mark paid form
  const [payoutRef, setPayoutRef] = useState('');
  const [markPaidSaving, setMarkPaidSaving] = useState(false);
  const [markPaidError, setMarkPaidError] = useState('');

  // ── Beta tab state ────────────────────────────────────────────────────────
  const [waitlist, setWaitlist] = useState<WaitlistEntry[]>([]);
  const [invites, setInvites] = useState<InviteEntry[]>([]);
  const [betaUsers, setBetaUsers] = useState<BetaUser[]>([]);
  const [betaLoading, setBetaLoading] = useState(false);
  const [betaError, setBetaError] = useState('');
  const [betaMsg, setBetaMsg] = useState('');
  // ── Payouts tab state ─────────────────────────────────────────────────────
  const [payouts, setPayouts] = useState<PayoutBatchOut[]>([]);
  const [payoutsLoading, setPayoutsLoading] = useState(false);
  const [approvedCommissions, setApprovedCommissions] = useState<AdminCommissionReviewRow[]>([]);
  const [selectedCommissions, setSelectedCommissions] = useState<Record<number, Set<number>>>({});
  const [payoutReferences, setPayoutReferences] = useState<Record<number, string>>({});
  const [paying, setPaying] = useState<Record<number, boolean>>({});
  
  // Commission review state
  const [commissions, setCommissions] = useState<AdminCommissionReviewRow[]>([]);
  const [commissionsLoading, setCommissionsLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  // Invite creation form
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteCount, setInviteCount] = useState(1);
  const [inviteDays, setInviteDays] = useState('');
  const [inviteCreating, setInviteCreating] = useState(false);
  const [newLinks, setNewLinks] = useState<InviteEntry[]>([]);
  
  // Debounce search for commission review
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);
  // Which waitlist rows are selected
  const [selectedWaitlist, setSelectedWaitlist] = useState<Set<number>>(new Set());
  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const rows = await listAdminAffiliates();
      setAffiliates(rows);
    } catch (err: any) {
      if (err?.response?.status === 403) {
        setError('Access denied — admin only.');
      } else {
        setError('Failed to load affiliates.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const loadBeta = useCallback(async () => {
    setBetaLoading(true);
    setBetaError('');
    try {
      const [w, inv, bu] = await Promise.all([listWaitlist(), listInvites(), listBetaUsers()]);
      setWaitlist(w);
      setInvites(inv);
      setBetaUsers(bu);
    } catch {
      setBetaError('Failed to load beta data.');
    } finally {
      setBetaLoading(false);
    }
  }, []);

  const loadPayouts = useCallback(async () => {
    setPayoutsLoading(true);
    try {
      const [rows, batches, approved] = await Promise.all([
        listAdminAffiliates(),
        listAdminPayouts(),
        reviewCommissions({ status: 'approved' }),
      ]);
      setAffiliates(rows);
      setPayouts(batches);
      setApprovedCommissions(approved);
      
      // Initialize selected commissions - all checked by default
      const selectedByAffiliate: Record<number, Set<number>> = {};
      approved.forEach(comm => {
        if (!selectedByAffiliate[comm.affiliate_id]) {
          selectedByAffiliate[comm.affiliate_id] = new Set();
        }
        selectedByAffiliate[comm.affiliate_id].add(comm.commission_id);
      });
      setSelectedCommissions(selectedByAffiliate);
    } catch {
      // silent — affiliates already shown in affiliates tab
    } finally {
      setPayoutsLoading(false);
    }
  }, []);
  
  const loadCommissions = useCallback(async () => {
    setCommissionsLoading(true);
    try {
      const data = await reviewCommissions({
        status: statusFilter || undefined,
        search: debouncedSearch || undefined,
      });
      setCommissions(data);
    } catch {
      // silent
    } finally {
      setCommissionsLoading(false);
    }
  }, [statusFilter, debouncedSearch]);

  useEffect(() => {
    if (authLoading) return;
    if (!user?.is_admin) {
      navigate('/', { replace: true });
      return;
    }
    load();
  }, [user, authLoading, navigate, load]);

  useEffect(() => {
    if (activeTab === 'beta' && user?.is_admin) loadBeta();
  }, [activeTab, user, loadBeta]);

  useEffect(() => {
    if (activeTab === 'payouts' && user?.is_admin) loadPayouts();
  }, [activeTab, user, loadPayouts]);
  
  useEffect(() => {
    if (activeTab === 'payouts' && user?.is_admin) loadCommissions();
  }, [activeTab, user, loadCommissions]);

  // ── Beta tab handlers ─────────────────────────────────────────────────────
  async function handleDeleteWaitlist(id: number) {
    await deleteWaitlistEntry(id);
    setWaitlist((w: WaitlistEntry[]) => w.filter((x: WaitlistEntry) => x.id !== id));
    setSelectedWaitlist((s: Set<number>) => { const n = new Set(s); n.delete(id); return n; });
  }

  async function handleSendInvite(email: string) {
    setInviteCreating(true);
    setBetaMsg('');
    try {
      const links = await createInvites(email, 1, inviteDays ? Number(inviteDays) : null);
      setNewLinks(links);
      await loadBeta();
    } catch { setBetaMsg('Failed to create invite.'); }
    finally { setInviteCreating(false); }
  }

  async function handleCreateInvites(e: React.FormEvent) {
    e.preventDefault();
    setInviteCreating(true);
    setBetaMsg('');
    try {
      const links = await createInvites(
        inviteEmail.trim() || null,
        inviteCount,
        inviteDays ? Number(inviteDays) : null,
      );
      setNewLinks(links);
      setInviteEmail('');
      setInviteCount(1);
      setInviteDays('');
      await loadBeta();
    } catch { setBetaMsg('Failed to create invites.'); }
    finally { setInviteCreating(false); }
  }

  async function handleRevokeInvite(id: number) {
    await revokeInvite(id);
    setInvites((inv: InviteEntry[]) => inv.filter((x: InviteEntry) => x.id !== id));
    setNewLinks((nl: InviteEntry[]) => nl.filter((x: InviteEntry) => x.id !== id));
  }

  async function handleRevokeBeta(userId: number) {
    await revokeBetaAccess(userId);
    setBetaUsers((bu: BetaUser[]) => bu.filter((x: BetaUser) => x.id !== userId));
  }

  function copyText(text: string) {
    navigator.clipboard.writeText(text);
  }

  async function handleApproveAll() {
    setApproving(true);
    setApproveMsg('');
    try {
      const result = await approveDueCommissions();
      setApproveMsg(`✓ ${result.approved} commission${result.approved === 1 ? '' : 's'} approved.`);
      await load();
    } catch {
      setApproveMsg('Failed to approve commissions.');
    } finally {
      setApproving(false);
      setTimeout(() => setApproveMsg(''), 5000);
    }
  }

  function openPayoutModal(aff: AdminAffiliateRow) {
    setPayoutModal({ affiliate: aff });
    setPayoutError('');
    setCreatedBatchId(null);
    setModal('payout');
  }

  async function handleCreatePayout() {
    if (!payoutModal) return;
    setPayoutSaving(true);
    setPayoutError('');
    try {
      // Cover all-time approved commissions
      const start = '2020-01-01T00:00:00Z';
      const end = new Date(Date.now() + 86400000).toISOString();
      const batch = await createPayoutBatch(payoutModal.affiliate.id, start, end);
      setCreatedBatchId(batch.id);
      await load();
      // Transition to mark-paid modal
      setModal('markpaid');
      setMarkPaidModal({
        batchId: batch.id,
        amount: batch.total_amount_cents,
        affiliateEmail: payoutModal.affiliate.email,
        payoutEmail: payoutModal.affiliate.payout_email,
      });
      setPayoutRef('');
      setMarkPaidError('');
    } catch (err: any) {
      setPayoutError(err?.response?.data?.detail || 'Failed to create payout batch.');
    } finally {
      setPayoutSaving(false);
    }
  }

  function toggleCommissionSelection(affiliateId: number, commissionId: number) {
    setSelectedCommissions(prev => {
      const newSelected = { ...prev };
      if (!newSelected[affiliateId]) {
        newSelected[affiliateId] = new Set();
      }
      const affiliateSet = new Set(newSelected[affiliateId]);
      if (affiliateSet.has(commissionId)) {
        affiliateSet.delete(commissionId);
      } else {
        affiliateSet.add(commissionId);
      }
      newSelected[affiliateId] = affiliateSet;
      return newSelected;
    });
  }

  function toggleSelectAll(affiliateId: number, commissionIds: number[]) {
    setSelectedCommissions(prev => {
      const newSelected = { ...prev };
      const currentSelected = newSelected[affiliateId] || new Set();
      const allSelected = commissionIds.every(id => currentSelected.has(id));
      
      if (allSelected) {
        newSelected[affiliateId] = new Set();
      } else {
        newSelected[affiliateId] = new Set(commissionIds);
      }
      return newSelected;
    });
  }

  async function handlePaySelectedCommissions(affiliateId: number, affiliateEmail: string) {
    const selected = selectedCommissions[affiliateId];
    const payoutRef = payoutReferences[affiliateId];
    
    if (!selected || selected.size === 0) {
      alert('Please select at least one commission to pay.');
      return;
    }
    
    if (!payoutRef || payoutRef.trim() === '') {
      alert('Please enter a PayPal reference.');
      return;
    }
    
    if (!window.confirm(`Pay ${selected.size} commission(s) to ${affiliateEmail} for ${formatCents(
      approvedCommissions
        .filter(c => c.affiliate_id === affiliateId && selected.has(c.commission_id))
        .reduce((sum, c) => sum + c.commission_amount_cents, 0)
    )}?`)) {
      return;
    }
    
    setPaying(prev => ({ ...prev, [affiliateId]: true }));
    try {
      await paySelectedCommissions(affiliateId, Array.from(selected), payoutRef.trim());
      // Reload data but clear selections for this affiliate
      await loadPayouts();
      setPayoutReferences(prev => {
        const newRefs = { ...prev };
        delete newRefs[affiliateId];
        return newRefs;
      });
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to process payment.');
    } finally {
      setPaying(prev => ({ ...prev, [affiliateId]: false }));
    }
  }

  async function handleMarkPaid() {
    if (!markPaidModal || !payoutRef.trim()) return;
    setMarkPaidSaving(true);
    setMarkPaidError('');
    try {
      await markBatchPaid(markPaidModal.batchId, payoutRef.trim());
      setModal(null);
      setMarkPaidModal(null);
      await load();
    } catch (err: any) {
      setMarkPaidError(err?.response?.data?.detail || 'Failed to mark as paid.');
    } finally {
      setMarkPaidSaving(false);
    }
  }

  async function openTinModal(affiliateId: number) {
    setTinModal({ affiliateId, tin: null, legalName: null, taxClass: null, loading: true });
    setModal('tin');
    try {
      const result = await getAffiliateTin(affiliateId);
      setTinModal({
        affiliateId,
        tin: result.tin,
        legalName: result.legal_name,
        taxClass: result.tax_classification,
        loading: false,
      });
    } catch (err: any) {
      const detail = err?.response?.data?.detail || 'No TIN on file.';
      setTinModal({ affiliateId, tin: null, legalName: detail, taxClass: null, loading: false });
    }
  }

  function closeModal() {
    setModal(null);
    setPayoutModal(null);
    setMarkPaidModal(null);
    setTinModal(null);
    setCreatedBatchId(null);
    setPayoutRef('');
    setPayoutError('');
    setMarkPaidError('');
  }

  const owedRows = affiliates.filter(a => a.approved_amount_cents > 0);
  const totalOwed = owedRows.reduce((sum, a) => sum + a.approved_amount_cents, 0);

  // ── Payouts tab derived data ─────────────────────────────────────────────
  const affiliateMap = Object.fromEntries(affiliates.map(a => [a.id, a]));
  const totalInHold = affiliates.reduce(
    (s, a) => s + Math.max(0, a.total_earned_cents - a.total_paid_cents - a.approved_amount_cents),
    0,
  );
  const allTimePaid = affiliates.reduce((s, a) => s + a.total_paid_cents, 0);
  const _now = new Date();
  const thisMonthPaid = payouts
    .filter(b => b.status === 'paid' && b.paid_at)
    .filter(b => {
      const d = new Date(b.paid_at!);
      return d.getMonth() === _now.getMonth() && d.getFullYear() === _now.getFullYear();
    })
    .reduce((s, b) => s + b.total_amount_cents, 0);
  const paidBatches = payouts.filter(b => b.status === 'paid' && b.paid_at);
  const draftBatches = payouts.filter(b => b.status !== 'paid');
  const _groupMap: Record<string, { label: string; sortKey: string; batches: PayoutBatchOut[]; total: number }> = {};
  for (const b of paidBatches) {
    const d = new Date(b.paid_at!);
    const sortKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    const label = d.toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
    if (!_groupMap[sortKey]) _groupMap[sortKey] = { label, sortKey, batches: [], total: 0 };
    _groupMap[sortKey].batches.push(b);
    _groupMap[sortKey].total += b.total_amount_cents;
  }
  const monthGroups = Object.values(_groupMap).sort((a, b) => b.sortKey.localeCompare(a.sortKey));

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Nav */}
      <nav className="bg-white border-b border-gray-100 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/app')} className="flex items-center gap-2 text-gray-900 hover:text-indigo-700 transition-colors">
              <span className="text-2xl">💕</span>
              <span className="font-bold text-base">SamePageDating</span>
            </button>
            <span className="text-xs bg-indigo-100 text-indigo-700 font-semibold px-2 py-0.5 rounded-full">Admin</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500 hidden sm:block">{user?.email}</span>
            <button onClick={() => { logout(); navigate('/'); }} className="text-sm text-gray-500 hover:text-gray-800 transition-colors">Log Out</button>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-10 space-y-8">
        {/* Page header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        </div>

        {/* Tab nav */}
        <div className="flex gap-1 border-b border-gray-200">
          {(['taxes', 'payouts', 'beta'] as Tab[]).map(t => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`px-5 py-2.5 text-sm font-semibold rounded-t-lg transition-colors ${
                activeTab === t
                  ? 'bg-white border border-b-white border-gray-200 -mb-px text-indigo-700'
                  : 'text-gray-500 hover:text-gray-800'
              }`}
            >
              {t === 'taxes' ? 'Taxes & Affiliates' : t === 'payouts' ? 'Payouts' : 'Beta Access'}
            </button>
          ))}
        </div>

        {/* ── TAXES & AFFILIATES TAB ──────────────────────────────────────── */}
        {activeTab === 'taxes' && (
          <>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <p className="text-gray-500 text-sm">Tax profiles, W-9 status, and lifetime commission earnings for every affiliate.</p>
              <button onClick={load} className="text-xs text-gray-400 hover:text-gray-700 transition-colors self-start">↻ Refresh</button>
            </div>

            {/* Loading / Error */}
            {loading && (
              <div className="flex justify-center py-16">
                <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
              </div>
            )}
            {error && !loading && (
              <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-6 text-center">
                <p className="font-semibold">{error}</p>
              </div>
            )}

            {!loading && !error && (
              <>
                {/* Summary cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm text-center">
                    <div className="text-2xl font-extrabold text-gray-900">{affiliates.length}</div>
                    <div className="text-xs text-gray-500 mt-1">Total Affiliates</div>
                  </div>
                  <div className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm text-center">
                    <div className="text-2xl font-extrabold text-gray-900">{affiliates.filter((a: AdminAffiliateRow) => a.status === 'active').length}</div>
                    <div className="text-xs text-gray-500 mt-1">Active</div>
                  </div>
                  <div className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm text-center">
                    <div className="text-2xl font-extrabold text-green-700">{affiliates.filter((a: AdminAffiliateRow) => a.w9_collected).length}</div>
                    <div className="text-xs text-gray-500 mt-1">W-9 On File</div>
                  </div>
                  <div className={`rounded-xl border p-5 shadow-sm text-center ${
                    affiliates.filter((a: AdminAffiliateRow) => !a.w9_collected).length > 0 ? 'bg-red-50 border-red-200' : 'bg-white border-gray-100'
                  }`}>
                    <div className={`text-2xl font-extrabold ${
                      affiliates.filter((a: AdminAffiliateRow) => !a.w9_collected).length > 0 ? 'text-red-600' : 'text-gray-900'
                    }`}>{affiliates.filter((a: AdminAffiliateRow) => !a.w9_collected).length}</div>
                    <div className="text-xs text-gray-500 mt-1">W-9 Missing</div>
                  </div>
                </div>

                {/* Affiliate tax table */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-100">
                    <h2 className="font-semibold text-gray-900">Affiliate Tax &amp; Earnings Overview</h2>
                    <p className="text-xs text-gray-400 mt-0.5">Use the TIN button to view W-9 details. Go to the Payouts tab to issue payments.</p>
                  </div>
                  {affiliates.length === 0 ? (
                    <div className="p-10 text-center text-gray-400">No affiliates yet.</div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                          <tr>
                            <th className="px-5 py-3 text-left">Affiliate</th>
                            <th className="px-5 py-3 text-left">Status</th>
                            <th className="px-5 py-3 text-right">Lifetime Earned</th>
                            <th className="px-5 py-3 text-right">Total Paid Out</th>
                            <th className="px-5 py-3 text-right">Balance</th>
                            <th className="px-5 py-3 text-left">W-9</th>
                            <th className="px-5 py-3 text-left">TIN Info</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                          {affiliates.map((aff: AdminAffiliateRow) => {
                            const balance = aff.total_earned_cents - aff.total_paid_cents;
                            return (
                              <tr key={aff.id} className="hover:bg-gray-50">
                                <td className="px-5 py-3">
                                  <div className="font-medium text-gray-900">{aff.email}</div>
                                  <div className="text-xs text-gray-400">{aff.code} · {aff.commission_pct}% commission · {aff.total_referred} referral{aff.total_referred !== 1 ? 's' : ''}</div>
                                </td>
                                <td className="px-5 py-3">
                                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                                    aff.status === 'active' ? 'bg-green-100 text-green-700' :
                                    aff.status === 'suspended' ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {aff.status}
                                  </span>
                                </td>
                                <td className="px-5 py-3 text-right font-semibold text-gray-800">{formatCents(aff.total_earned_cents)}</td>
                                <td className="px-5 py-3 text-right text-gray-600">{formatCents(aff.total_paid_cents)}</td>
                                <td className="px-5 py-3 text-right">
                                  <span className={`font-semibold ${
                                    balance > 0 ? 'text-orange-600' : 'text-gray-400'
                                  }`}>{balance > 0 ? formatCents(balance) : '—'}</span>
                                </td>
                                <td className="px-5 py-3">
                                  {aff.w9_collected ? (
                                    <span className="text-green-600 text-xs font-medium">✓ On file</span>
                                  ) : (
                                    <span className="text-red-500 text-xs font-medium">⚠ Missing</span>
                                  )}
                                </td>
                                <td className="px-5 py-3">
                                  <button
                                    onClick={() => openTinModal(aff.id)}
                                    className="text-xs text-indigo-600 hover:text-indigo-800 transition-colors border border-indigo-200 px-2 py-1 rounded-lg"
                                  >
                                    View TIN
                                  </button>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </>
            )}
          </>
        )}

        {/* ── PAYOUTS TAB ────────────────────────────────────────────────── */}
        {activeTab === 'payouts' && (
          <>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <p className="text-gray-500 text-sm">Approve commissions, issue payouts, and track payment history by month.</p>
              <div className="flex items-center gap-3">
                {approveMsg && <span className="text-sm text-green-700 font-medium">{approveMsg}</span>}
                <button onClick={loadPayouts} className="text-xs text-gray-400 hover:text-gray-700 transition-colors border border-gray-200 px-3 py-1.5 rounded-lg">↻ Refresh</button>
                <button
                  onClick={handleApproveAll}
                  disabled={approving}
                  className="bg-indigo-600 text-white font-semibold px-5 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-60 transition-colors"
                >
                  {approving ? 'Approving…' : '✓ Approve All Due'}
                </button>
              </div>
            </div>

            {payoutsLoading && (
              <div className="flex justify-center py-16">
                <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
              </div>
            )}

            {!payoutsLoading && (
              <>
                {/* Summary cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className={`rounded-xl border p-5 shadow-sm text-center ${owedRows.length > 0 ? 'bg-orange-50 border-orange-200' : 'bg-white border-gray-100'}`}>
                    <div className={`text-2xl font-extrabold ${owedRows.length > 0 ? 'text-orange-600' : 'text-gray-900'}`}>{formatCents(totalOwed)}</div>
                    <div className="text-xs text-gray-500 mt-1">Needs Payment</div>
                    {owedRows.length > 0 && <div className="text-xs text-orange-500 mt-0.5 font-medium">{owedRows.length} affiliate{owedRows.length !== 1 ? 's' : ''}</div>}
                  </div>
                  <div className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm text-center">
                    <div className="text-2xl font-extrabold text-yellow-600">{formatCents(totalInHold)}</div>
                    <div className="text-xs text-gray-500 mt-1">In Hold Period</div>
                  </div>
                  <div className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm text-center">
                    <div className="text-2xl font-extrabold text-green-700">{formatCents(thisMonthPaid)}</div>
                    <div className="text-xs text-gray-500 mt-1">Paid This Month</div>
                  </div>
                  <div className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm text-center">
                    <div className="text-2xl font-extrabold text-gray-900">{formatCents(allTimePaid)}</div>
                    <div className="text-xs text-gray-500 mt-1">All-Time Paid</div>
                  </div>
                </div>

                {/* ── Ready to Pay Now ─────────────────────────────────────── */}
                <section>
                  <div className="flex items-center gap-3 mb-4">
                    <h2 className="text-lg font-bold text-gray-900">Ready to Pay Now</h2>
                    {approvedCommissions.length > 0 && (
                      <span className="text-xs bg-orange-100 text-orange-700 font-semibold px-2.5 py-1 rounded-full">
                        {approvedCommissions.length} commission{approvedCommissions.length !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                  {approvedCommissions.length === 0 ? (
                    <div className="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
                      <div className="text-3xl mb-2">✓</div>
                      <p className="text-green-800 font-semibold">All caught up!</p>
                      <p className="text-green-700 text-sm mt-1">No commissions are ready to pay right now.</p>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {/* Group commissions by affiliate */}
                      {Object.entries(
                        approvedCommissions.reduce((acc, comm) => {
                          if (!acc[comm.affiliate_id]) acc[comm.affiliate_id] = [];
                          acc[comm.affiliate_id].push(comm);
                          return acc;
                        }, {} as Record<number, AdminCommissionReviewRow[]>)
                      ).map(([affiliateIdStr, comms]) => {
                        const affiliateId = Number(affiliateIdStr);
                        const aff = affiliateMap[affiliateId];
                        if (!aff) return null;
                        
                        const missingPayout = !aff.payout_email;
                        const missingW9 = !aff.w9_collected;
                        const blocked = missingPayout || missingW9;
                        const reasons = [missingPayout && 'no payout email', missingW9 && 'W-9 missing'].filter(Boolean).join(', ');
                        
                        const selected = selectedCommissions[affiliateId] || new Set();
                        const selectedComms = comms.filter(c => selected.has(c.commission_id));
                        const selectedTotal = selectedComms.reduce((sum, c) => sum + c.commission_amount_cents, 0);
                        const allSelected = comms.every(c => selected.has(c.commission_id));
                        const someSelected = comms.some(c => selected.has(c.commission_id));
                        const payoutRef = payoutReferences[affiliateId] ||  '';
                        const isPaying = paying[affiliateId] || false;
                        
                        return (
                          <div key={affiliateId} className={`bg-white rounded-xl border p-5 ${blocked ? 'border-gray-200' : 'border-green-200'}`}>
                            {/* Affiliate Header */}
                            <div className="flex items-start justify-between mb-4 pb-4 border-b border-gray-100">
                              <div className="flex-1">
                                <div className="font-bold text-gray-900 text-lg">{aff.email}</div>
                                <div className="text-xs text-gray-500 mt-1">
                                  {aff.code} · {aff.commission_pct}% commission · {comms.length} commission{comms.length !== 1 ? 's' : ''} ready
                                </div>
                                {aff.payout_email ? (
                                  <div className="text-xs text-gray-400 mt-1">Pay to: <span className="font-mono text-gray-600">{aff.payout_email}</span></div>
                                ) : (
                                  <div className="text-xs text-amber-600 mt-2 font-medium">⚠ No payout email set</div>
                                )}
                                {missingW9 && <div className="text-xs text-red-500 mt-0.5 font-medium">⚠ W-9 not submitted</div>}
                                {blocked && <div className="text-xs text-gray-400 mt-1">Blocked: {reasons}</div>}
                              </div>
                            </div>

                            {/* Commission List */}
                            <div className="space-y-2 mb-4">
                              {comms.map(comm => (
                                <label
                                  key={comm.commission_id}
                                  className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                                    selected.has(comm.commission_id)
                                      ? 'border-green-300 bg-green-50'
                                      : 'border-gray-200 bg-gray-50 hover:bg-gray-100'
                                  } ${blocked ? 'opacity-50 cursor-not-allowed' : ''}`}
                                >
                                  <input
                                    type="checkbox"
                                    checked={selected.has(comm.commission_id)}
                                    onChange={() => !blocked && toggleCommissionSelection(affiliateId, comm.commission_id)}
                                    disabled={blocked}
                                    className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
                                  />
                                  <div className="flex-1 min-w-0">
                                    <div className="text-sm font-medium text-gray-900">{comm.referred_user_email}</div>
                                    <div className="text-xs text-gray-500">
                                      Cycle {comm.billing_cycle_number} · Approved{' '}
                                      {comm.approved_at ? new Date(comm.approved_at).toLocaleDateString() : 'recently'}
                                    </div>
                                  </div>
                                  <div className="font-bold text-green-700">{formatCents(comm.commission_amount_cents)}</div>
                                </label>
                              ))}
                            </div>

                            {/* Selection Summary & Actions */}
                            <div className="flex flex-col sm:flex-row items-start sm:items-end gap-3 pt-4 border-t border-gray-100">
                              <div className="flex-1 w-full">
                                <div className="flex items-center gap-2 mb-2">
                                  <button
                                    onClick={() => !blocked && toggleSelectAll(affiliateId, comms.map(c => c.commission_id))}
                                    disabled={blocked}
                                    className="text-xs text-indigo-600 hover:text-indigo-800 font-medium disabled:text-gray-400"
                                  >
                                    {allSelected ? 'Deselect All' : 'Select All'}
                                  </button>
                                  <span className="text-xs text-gray-400">·</span>
                                  <span className="text-xs text-gray-600">
                                    {selected.size} of {comms.length} selected · {formatCents(selectedTotal)}
                                  </span>
                                </div>
                                <input
                                  type="text"
                                  placeholder="PayPal Transaction ID (required)"
                                  value={payoutRef}
                                  onChange={(e) => setPayoutReferences(prev => ({ ...prev, [affiliateId]: e.target.value }))}
                                  disabled={blocked || isPaying}
                                  className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-100"
                                />
                              </div>
                              <button
                                onClick={() => handlePaySelectedCommissions(affiliateId, aff.email)}
                                disabled={blocked || selected.size === 0 || !payoutRef.trim() || isPaying}
                                className="font-semibold px-6 py-2.5 rounded-lg text-sm transition-colors shadow-sm whitespace-nowrap bg-green-600 text-white hover:bg-green-700 disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed"
                              >
                                {isPaying ? 'Processing...' : `Pay Now (${formatCents(selectedTotal)})`}
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </section>

                {/* ── Payment History by Month ──────────────────────────────── */}
                <section>
                  <h2 className="text-lg font-bold text-gray-900 mb-4">Payment History</h2>
                  {monthGroups.length === 0 ? (
                    <p className="text-gray-400 text-sm">No payments recorded yet.</p>
                  ) : (
                    <div className="space-y-4">
                      {monthGroups.map((mg, idx) => (
                        <div key={mg.sortKey} className="bg-white rounded-xl border border-gray-100 overflow-hidden shadow-sm">
                          <div className={`px-5 py-3 flex items-center justify-between ${idx === 0 ? 'bg-green-50 border-b border-green-100' : 'bg-gray-50 border-b border-gray-100'}`}>
                            <div className="flex items-center gap-3">
                              <span className={`font-bold text-sm ${idx === 0 ? 'text-green-800' : 'text-gray-700'}`}>{mg.label}</span>
                              <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${idx === 0 ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                                {mg.batches.length} payout{mg.batches.length !== 1 ? 's' : ''}
                              </span>
                            </div>
                            <span className={`font-extrabold text-sm ${idx === 0 ? 'text-green-700' : 'text-gray-700'}`}>{formatCents(mg.total)}</span>
                          </div>
                          <table className="w-full text-sm">
                            <tbody className="divide-y divide-gray-50">
                              {mg.batches.map(b => {
                                const aff = affiliateMap[b.affiliate_id];
                                return (
                                  <tr key={b.id} className="hover:bg-gray-50">
                                    <td className="px-5 py-3.5 font-medium text-gray-900">{aff?.email || `Affiliate #${b.affiliate_id}`}</td>
                                    <td className="px-5 py-3.5 text-right font-semibold text-green-700">{formatCents(b.total_amount_cents)}</td>
                                    <td className="px-5 py-3.5 text-gray-400 text-xs">{b.commission_count} commission{b.commission_count !== 1 ? 's' : ''}</td>
                                    <td className="px-5 py-3.5 text-gray-400 text-xs">Paid {new Date(b.paid_at!).toLocaleDateString()}</td>
                                    <td className="px-5 py-3.5 text-gray-400 text-xs font-mono">{b.payout_reference || '—'}</td>
                                    <td className="px-5 py-3.5">
                                      <span className="bg-green-100 text-green-700 text-xs font-semibold px-2 py-0.5 rounded-full">✓ Paid</span>
                                    </td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      ))}
                    </div>
                  )}
                </section>

                {/* ── Commission Details ──────────────────────────────────────── */}
                <section>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-bold text-gray-900">Commission Details</h2>
                    <button onClick={loadCommissions} className="text-xs text-gray-400 hover:text-gray-700 transition-colors border border-gray-200 px-3 py-1.5 rounded-lg">↻ Refresh</button>
                  </div>

                  {/* Filters */}
                  <div className="bg-white rounded-lg border border-gray-100 p-4 mb-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-gray-600 uppercase mb-2">Filter by Status</label>
                        <select
                          value={statusFilter}
                          onChange={(e) => setStatusFilter(e.target.value)}
                          className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        >
                          <option value="">All Statuses</option>
                          <option value="pending">Pending</option>
                          <option value="approved">Approved</option>
                          <option value="paid">Paid</option>
                          <option value="voided">Voided</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-gray-600 uppercase mb-2">Search (name/email)</label>
                        <input
                          type="text"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          placeholder="Search affiliates or referred users..."
                          className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Stats Cards */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    {[
                      { label: 'Total', count: commissions.length },
                      { label: 'Pending', count: commissions.filter(c => c.status === 'pending').length },
                      { label: 'Approved', count: commissions.filter(c => c.status === 'approved').length },
                      { label: 'Voided', count: commissions.filter(c => c.status === 'voided').length },
                    ].map((stat) => (
                      <div key={stat.label} className="bg-white rounded-lg border border-gray-100 p-4 text-center">
                        <div className="text-2xl font-bold text-gray-900">{stat.count}</div>
                        <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
                      </div>
                    ))}
                  </div>

                  {/* Commission Table */}
                  {commissionsLoading ? (
                    <div className="flex justify-center py-12">
                      <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                    </div>
                  ) : (
                    <>
                      <div className="bg-white rounded-lg border border-gray-100 overflow-hidden shadow-sm">
                        <div className="overflow-x-auto">
                          <table className="w-full text-sm">
                            <thead className="bg-gray-50 border-b border-gray-200">
                              <tr>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Status</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Affiliate</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Referred User</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Amount</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Commission</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Created</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Hold Until</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Notes</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                              {commissions.length === 0 ? (
                                <tr>
                                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                                    No commissions found
                                  </td>
                                </tr>
                              ) : (
                                commissions.map((c) => {
                                  const getStatusBadge = (status: string) => {
                                    const styles: Record<string, string> = {
                                      pending: 'bg-yellow-100 text-yellow-800',
                                      approved: 'bg-green-100 text-green-800',
                                      paid: 'bg-blue-100 text-blue-800',
                                      voided: 'bg-red-100 text-red-800',
                                    };
                                    return (
                                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
                                        {status}
                                      </span>
                                    );
                                  };
                                  const formatDate = (dateString: string | null) => {
                                    if (!dateString) return '—';
                                    return new Date(dateString).toLocaleDateString();
                                  };
                                  return (
                                    <tr key={c.commission_id} className="hover:bg-gray-50 transition-colors">
                                      <td className="px-4 py-3">
                                        {getStatusBadge(c.status)}
                                      </td>
                                      <td className="px-4 py-3">
                                        <div className="font-medium text-gray-900">{c.affiliate_name || c.affiliate_email}</div>
                                        <div className="text-xs text-gray-500">{c.affiliate_code}</div>
                                        {c.affiliate_payout_email && (
                                          <div className="text-xs text-green-600 mt-1">✓ {c.affiliate_payout_email}</div>
                                        )}
                                      </td>
                                      <td className="px-4 py-3">
                                        <div className="font-medium text-gray-900">{c.referred_user_name || c.referred_user_email}</div>
                                        <div className="text-xs text-gray-500">{c.referred_user_email}</div>
                                        <div className="text-xs text-gray-500 mt-1">
                                          {c.referred_user_subscription_status || 'no subscription'}
                                        </div>
                                      </td>
                                      <td className="px-4 py-3 font-medium text-gray-900">
                                        {formatCents(c.invoice_amount_cents)}
                                      </td>
                                      <td className="px-4 py-3">
                                        <div className="font-semibold text-green-700">{formatCents(c.commission_amount_cents)}</div>
                                        <div className="text-xs text-gray-500">{c.commission_pct}% · Cycle #{c.billing_cycle_number}</div>
                                      </td>
                                      <td className="px-4 py-3 text-gray-600">
                                        {formatDate(c.created_at)}
                                      </td>
                                      <td className="px-4 py-3 text-gray-600">
                                        {formatDate(c.hold_until)}
                                      </td>
                                      <td className="px-4 py-3">
                                        {c.voided_at && (
                                          <div className="text-xs text-red-600 font-medium">
                                            Voided: {formatDate(c.voided_at)}
                                          </div>
                                        )}
                                        {c.notes && (
                                          <div className="text-xs text-gray-500 max-w-xs truncate" title={c.notes}>
                                            {c.notes}
                                          </div>
                                        )}
                                      </td>
                                    </tr>
                                  );
                                })
                              )}
                            </tbody>
                          </table>
                        </div>
                      </div>

                      {/* Legend */}
                      {commissions.length > 0 && (
                        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                          <h3 className="text-sm font-semibold text-blue-900 mb-2">Status Guide</h3>
                          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs text-blue-800">
                            <div><strong>Pending:</strong> In 90-day anti-fraud hold</div>
                            <div><strong>Approved:</strong> Hold ended, ready for payout</div>
                            <div><strong>Paid:</strong> Already paid to affiliate</div>
                            <div><strong>Voided:</strong> Refund/chargeback occurred</div>
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </section>
              </>
            )}
          </>
        )}

        {/* ── BETA ACCESS TAB ────────────────────────────────────────────── */}
        {activeTab === 'beta' && (
          <div className="space-y-10">
            {betaLoading && (
              <div className="flex justify-center py-16">
                <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
              </div>
            )}
            {betaError && <p className="text-red-600 text-sm">{betaError}</p>}
            {betaMsg && <p className="text-yellow-700 text-sm">{betaMsg}</p>}

            {!betaLoading && (
              <>
                {/* ── Waitlist ─────────────────────────────────────────────── */}
                <section>
                  <div className="flex items-center justify-between mb-3">
                    <h2 className="text-lg font-bold text-gray-900">Waitlist <span className="text-gray-400 font-normal text-sm ml-1">({waitlist.length})</span></h2>
                    <button onClick={loadBeta} className="text-xs text-indigo-600 hover:underline">Refresh</button>
                  </div>
                  {waitlist.length === 0 ? (
                    <p className="text-gray-400 text-sm">No one waiting.</p>
                  ) : (
                    <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50 border-b border-gray-200">
                          <tr>
                            <th className="text-left px-4 py-3 font-semibold text-gray-600">Email</th>
                            <th className="text-left px-4 py-3 font-semibold text-gray-600">Name</th>
                            <th className="text-left px-4 py-3 font-semibold text-gray-600">Joined</th>
                            <th className="px-4 py-3" />
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                          {waitlist.map(w => (
                            <tr key={w.id} className="hover:bg-gray-50">
                              <td className="px-4 py-3 text-gray-900">{w.email}</td>
                              <td className="px-4 py-3 text-gray-500">{w.name || '—'}</td>
                              <td className="px-4 py-3 text-gray-400">{new Date(w.created_at).toLocaleDateString()}</td>
                              <td className="px-4 py-3">
                                <div className="flex gap-2 justify-end">
                                  <button
                                    onClick={() => handleSendInvite(w.email)}
                                    disabled={inviteCreating}
                                    className="text-xs font-semibold bg-indigo-600 text-white px-3 py-1.5 rounded-lg hover:bg-indigo-700 disabled:opacity-60 transition-colors"
                                  >
                                    Send Invite
                                  </button>
                                  <button
                                    onClick={() => handleDeleteWaitlist(w.id)}
                                    className="text-xs text-red-500 hover:text-red-700 border border-red-200 px-2 py-1.5 rounded-lg transition-colors"
                                  >
                                    Remove
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </section>

                {/* ── Invites ──────────────────────────────────────────────── */}
                <section>
                  <h2 className="text-lg font-bold text-gray-900 mb-3">Invites</h2>

                  {/* Create invite form */}
                  <form onSubmit={handleCreateInvites} className="bg-white border border-gray-200 rounded-xl p-5 mb-4 flex flex-wrap gap-3 items-end">
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Email (optional)</label>
                      <input
                        type="email"
                        value={inviteEmail}
                        onChange={e => setInviteEmail(e.target.value)}
                        placeholder="user@example.com"
                        className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-52 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Count</label>
                      <input
                        type="number"
                        min={1}
                        max={50}
                        value={inviteCount}
                        onChange={e => setInviteCount(Number(e.target.value))}
                        className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-20 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Expires (days)</label>
                      <input
                        type="number"
                        min={1}
                        value={inviteDays}
                        onChange={e => setInviteDays(e.target.value)}
                        placeholder="no expiry"
                        className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-28 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={inviteCreating}
                      className="bg-indigo-600 text-white font-semibold px-5 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-60 transition-colors"
                    >
                      {inviteCreating ? 'Generating…' : 'Generate'}
                    </button>
                  </form>

                  {/* Newly created invites banner */}
                  {newLinks.length > 0 && (
                    <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-4">
                      <p className="text-green-800 font-semibold text-sm mb-2">✓ {newLinks.length} invite{newLinks.length > 1 ? 's' : ''} created — share the code{newLinks.length > 1 ? 's' : ''} below:</p>
                      <ul className="space-y-2">
                        {newLinks.map(l => (
                          <li key={l.id} className="flex items-center gap-2 text-sm">
                            {l.email && <span className="text-gray-500 text-xs w-40 truncate">{l.email}</span>}
                            <code className="bg-white border border-green-200 rounded px-2 py-1 text-xs flex-1 font-mono tracking-wide">{l.invite_code}</code>
                            <button onClick={() => copyText(l.invite_code)} className="text-xs text-indigo-600 hover:underline whitespace-nowrap">Copy code</button>
                          </li>
                        ))}
                      </ul>
                      <button onClick={() => setNewLinks([])} className="mt-2 text-xs text-gray-400 hover:text-gray-600">Dismiss</button>
                    </div>
                  )}

                  {invites.length === 0 ? (
                    <p className="text-gray-400 text-sm">No invites yet.</p>
                  ) : (
                    <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50 border-b border-gray-200">
                          <tr>
                            <th className="text-left px-4 py-3 font-semibold text-gray-600">Email</th>
                            <th className="text-left px-4 py-3 font-semibold text-gray-600">Code</th>
                            <th className="text-left px-4 py-3 font-semibold text-gray-600">Status</th>
                            <th className="text-left px-4 py-3 font-semibold text-gray-600">Expires</th>
                            <th className="px-4 py-3" />
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                          {invites.map(inv => (
                            <tr key={inv.id} className="hover:bg-gray-50">
                              <td className="px-4 py-3 text-gray-900">{inv.email || <span className="text-gray-400">Open</span>}</td>
                              <td className="px-4 py-3">
                                <div className="flex items-center gap-1.5">
                                  <code className="text-xs font-mono text-gray-700 tracking-wide">{inv.invite_code}</code>
                                  <button onClick={() => copyText(inv.invite_code)} className="text-xs text-indigo-600 hover:underline ml-1">Copy</button>
                                </div>
                              </td>
                              <td className="px-4 py-3">
                                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${inv.used ? 'bg-gray-100 text-gray-500' : 'bg-green-100 text-green-700'}`}>
                                  {inv.used ? 'Used' : 'Pending'}
                                </span>
                              </td>
                              <td className="px-4 py-3 text-gray-400 text-xs">
                                {inv.expires_at ? new Date(inv.expires_at).toLocaleDateString() : '—'}
                              </td>
                              <td className="px-4 py-3 text-right">
                                {!inv.used && (
                                  <button
                                    onClick={() => handleRevokeInvite(inv.id)}
                                    className="text-xs text-red-500 hover:text-red-700 border border-red-200 px-2 py-1 rounded-lg transition-colors"
                                  >
                                    Revoke
                                  </button>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </section>

                {/* ── Beta Users ───────────────────────────────────────────── */}
                <section>
                  <h2 className="text-lg font-bold text-gray-900 mb-3">
                    Beta Users <span className="text-gray-400 font-normal text-sm ml-1">({betaUsers.length})</span>
                  </h2>
                  {betaUsers.length === 0 ? (
                    <p className="text-gray-400 text-sm">No beta users yet.</p>
                  ) : (
                    <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50 border-b border-gray-200">
                          <tr>
                            <th className="text-left px-4 py-3 font-semibold text-gray-600">Email</th>
                            <th className="text-left px-4 py-3 font-semibold text-gray-600">Name</th>
                            <th className="text-left px-4 py-3 font-semibold text-gray-600">Joined</th>
                            <th className="px-4 py-3" />
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                          {betaUsers.map(bu => (
                            <tr key={bu.id} className="hover:bg-gray-50">
                              <td className="px-4 py-3 text-gray-900">{bu.email}</td>
                              <td className="px-4 py-3 text-gray-500">{bu.full_name || '—'}</td>
                              <td className="px-4 py-3 text-gray-400">{new Date(bu.created_at).toLocaleDateString()}</td>
                              <td className="px-4 py-3 text-right">
                                <button
                                  onClick={() => handleRevokeBeta(bu.id)}
                                  className="text-xs text-red-500 hover:text-red-700 border border-red-200 px-2 py-1 rounded-lg transition-colors"
                                >
                                  Revoke Access
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </section>
              </>
            )}
          </div>
        )}
      </div>

      {/* Payout Modal */}
      {modal === 'payout' && payoutModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 className="font-bold text-gray-900 text-lg mb-1">Create Payout Batch</h2>
            <p className="text-sm text-gray-500 mb-5">
              This will group all approved commissions for <strong>{payoutModal.affiliate.email}</strong> into a payout batch.
            </p>
            <div className="bg-gray-50 rounded-xl p-4 mb-5 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Amount</span>
                <span className="font-bold text-green-700">{formatCents(payoutModal.affiliate.approved_amount_cents)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Send to</span>
                <span className="font-mono text-gray-800">{payoutModal.affiliate.payout_email || <em className="text-amber-500 not-italic">No payout email set</em>}</span>
              </div>
            </div>
            {payoutError && <p className="text-red-600 text-sm mb-3">{payoutError}</p>}
            {!payoutModal.affiliate.payout_email && (
              <p className="text-amber-600 text-xs mb-3">⚠️ This affiliate has not set a payout email. You can still create the batch, but coordinate payment manually.</p>
            )}
            <div className="flex gap-3">
              <button onClick={closeModal} className="flex-1 border border-gray-300 text-gray-700 font-semibold py-2.5 rounded-lg text-sm hover:bg-gray-50 transition-colors">Cancel</button>
              <button
                onClick={handleCreatePayout}
                disabled={payoutSaving}
                className="flex-1 bg-green-600 text-white font-semibold py-2.5 rounded-lg text-sm hover:bg-green-700 disabled:opacity-60 transition-colors"
              >
                {payoutSaving ? 'Creating…' : 'Create Batch'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Mark Paid Modal */}
      {modal === 'markpaid' && markPaidModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 className="font-bold text-gray-900 text-lg mb-1">Mark as Paid</h2>
            <p className="text-sm text-gray-500 mb-4">
              Batch #{markPaidModal.batchId} for <strong>{markPaidModal.affiliateEmail}</strong> — <strong>{formatCents(markPaidModal.amount)}</strong>
            </p>
            {markPaidModal.payoutEmail && (
              <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-3 text-sm text-green-800 mb-4">
                Send payment to: <strong className="font-mono">{markPaidModal.payoutEmail}</strong>
              </div>
            )}
            <label className="block text-xs font-medium text-gray-700 mb-1">Payment Reference <span className="text-red-500">*</span></label>
            <input
              type="text"
              value={payoutRef}
              onChange={e => setPayoutRef(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="e.g. PayPal transaction ID, check #, etc."
            />
            {markPaidError && <p className="text-red-600 text-sm mb-3">{markPaidError}</p>}
            <div className="flex gap-3">
              <button onClick={closeModal} className="flex-1 border border-gray-300 text-gray-700 font-semibold py-2.5 rounded-lg text-sm hover:bg-gray-50 transition-colors">Cancel</button>
              <button
                onClick={handleMarkPaid}
                disabled={markPaidSaving || !payoutRef.trim()}
                className="flex-1 bg-indigo-600 text-white font-semibold py-2.5 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-60 transition-colors"
              >
                {markPaidSaving ? 'Saving…' : 'Mark Paid'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* TIN Modal */}
      {modal === 'tin' && tinModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
            <h2 className="font-bold text-gray-900 text-lg mb-4">TIN / 1099 Info</h2>
            {tinModal.loading ? (
              <div className="flex justify-center py-6">
                <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : tinModal.tin ? (
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-500 text-xs uppercase tracking-wide">Legal Name</span>
                  <p className="font-medium text-gray-900 mt-0.5">{tinModal.legalName || '—'}</p>
                </div>
                <div>
                  <span className="text-gray-500 text-xs uppercase tracking-wide">Tax Classification</span>
                  <p className="font-medium text-gray-900 mt-0.5">{tinModal.taxClass || '—'}</p>
                </div>
                <div>
                  <span className="text-gray-500 text-xs uppercase tracking-wide">TIN</span>
                  <p className="font-mono font-bold text-gray-900 mt-0.5 text-base">{tinModal.tin}</p>
                </div>
                <p className="text-xs text-red-500 mt-2">⚠️ Admin only — never share this screen.</p>
              </div>
            ) : (
              <p className="text-gray-600 text-sm py-2">{tinModal.legalName}</p>
            )}
            <button onClick={closeModal} className="w-full mt-6 border border-gray-300 text-gray-700 font-semibold py-2.5 rounded-lg text-sm hover:bg-gray-50 transition-colors">Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
