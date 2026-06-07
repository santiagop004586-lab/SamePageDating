import api from './api';
import type { AffiliateOut, PayoutBatchOut } from './affiliateService';

export interface AdminAffiliateRow {
  id: number;
  user_id: number;
  email: string;
  code: string;
  status: string;
  commission_pct: string;
  total_referred: number;
  total_earned_cents: number;
  total_paid_cents: number;
  payout_email: string | null;
  approved_amount_cents: number;
  w9_collected: boolean;
  created_at: string;
}

export interface AdminTinResult {
  affiliate_id: number;
  legal_name: string | null;
  tin: string;
  tax_classification: string | null;
}

export interface AdminCommissionReviewRow {
  // Commission fields
  commission_id: number;
  status: string;
  commission_amount_cents: number;
  invoice_amount_cents: number;
  commission_pct: string;
  billing_cycle_number: number;
  stripe_invoice_id: string;
  stripe_subscription_id: string | null;
  hold_until: string | null;
  created_at: string;
  approved_at: string | null;
  voided_at: string | null;
  notes: string | null;
  
  // Affiliate info
  affiliate_id: number;
  affiliate_email: string;
  affiliate_name: string | null;
  affiliate_code: string;
  affiliate_payout_email: string | null;
  
  // Referred user info
  referred_user_id: number;
  referred_user_email: string;
  referred_user_name: string | null;
  referred_user_subscription_status: string | null;
}

export async function listAdminAffiliates(page = 1): Promise<AdminAffiliateRow[]> {
  const { data } = await api.get<AdminAffiliateRow[]>(`/api/v1/admin/affiliates?page=${page}`);
  return data;
}

export async function reviewCommissions(params?: {
  page?: number;
  status?: string;
  affiliateId?: number;
  search?: string;
}): Promise<AdminCommissionReviewRow[]> {
  const query = new URLSearchParams();
  if (params?.page) query.append('page', params.page.toString());
  if (params?.status) query.append('status', params.status);
  if (params?.affiliateId) query.append('affiliate_id', params.affiliateId.toString());
  if (params?.search) query.append('search', params.search);
  
  const { data } = await api.get<AdminCommissionReviewRow[]>(
    `/api/v1/admin/commissions/review?${query.toString()}`
  );
  return data;
}

export async function approveDueCommissions(): Promise<{ approved: number }> {
  const { data } = await api.post<{ approved: number }>('/api/v1/admin/commissions/approve-due');
  return data;
}

export async function createPayoutBatch(
  affiliateId: number,
  periodStart: string,
  periodEnd: string,
): Promise<PayoutBatchOut> {
  const { data } = await api.post<PayoutBatchOut>(
    `/api/v1/admin/payouts?affiliate_id=${affiliateId}`,
    { period_start: periodStart, period_end: periodEnd },
  );
  return data;
}

export async function markBatchPaid(batchId: number, payoutReference: string): Promise<PayoutBatchOut> {
  const { data } = await api.post<PayoutBatchOut>(
    `/api/v1/admin/payouts/${batchId}/mark-paid`,
    { payout_reference: payoutReference },
  );
  return data;
}

export async function paySelectedCommissions(
  affiliateId: number,
  commissionIds: number[],
  payoutReference: string,
): Promise<PayoutBatchOut> {
  const { data } = await api.post<PayoutBatchOut>('/api/v1/admin/payouts/pay-selected', {
    affiliate_id: affiliateId,
    commission_ids: commissionIds,
    payout_reference: payoutReference,
  });
  return data;
}

export async function listAdminPayouts(page = 1): Promise<PayoutBatchOut[]> {
  const { data } = await api.get<PayoutBatchOut[]>(`/api/v1/admin/payouts?page=${page}`);
  return data;
}

export async function updateAffiliate(
  affiliateId: number,
  body: { status?: string; commission_pct?: string; hold_days?: number },
): Promise<AffiliateOut> {
  const { data } = await api.patch<AffiliateOut>(`/api/v1/admin/affiliates/${affiliateId}`, body);
  return data;
}

export async function getAffiliateTin(affiliateId: number): Promise<AdminTinResult> {
  const { data } = await api.get<AdminTinResult>(`/api/v1/admin/affiliates/${affiliateId}/tin`);
  return data;
}

// ─── Beta / Invite / Waitlist ───────────────────────────────────────────────

export interface WaitlistEntry {
  id: number;
  email: string;
  name: string | null;
  created_at: string;
}

export interface InviteEntry {
  id: number;
  email: string | null;
  invite_code: string;
  link?: string;
  used: boolean;
  created_at: string;
  expires_at: string | null;
}

export interface BetaUser {
  id: number;
  email: string;
  full_name: string | null;
  created_at: string;
}

export async function listWaitlist(): Promise<WaitlistEntry[]> {
  const { data } = await api.get<WaitlistEntry[]>('/api/v1/admin/waitlist');
  return data;
}

export async function deleteWaitlistEntry(id: number): Promise<void> {
  await api.delete(`/api/v1/admin/waitlist/${id}`);
}

export async function listInvites(): Promise<InviteEntry[]> {
  const { data } = await api.get<InviteEntry[]>('/api/v1/admin/invites');
  return data;
}

export async function createInvites(
  email: string | null,
  count: number,
  expiresDays: number | null,
): Promise<InviteEntry[]> {
  const { data } = await api.post<InviteEntry[]>('/api/v1/admin/invites', {
    email: email || null,
    count,
    expires_days: expiresDays || null,
  });
  return data;
}

export async function revokeInvite(id: number): Promise<void> {
  await api.delete(`/api/v1/admin/invites/${id}`);
}

export async function listBetaUsers(): Promise<BetaUser[]> {
  const { data } = await api.get<BetaUser[]>('/api/v1/admin/beta-users');
  return data;
}

export async function revokeBetaAccess(userId: number): Promise<void> {
  await api.post(`/api/v1/admin/beta-users/${userId}/revoke`);
}
