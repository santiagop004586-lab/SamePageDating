import api from './api';

export interface AffiliateOut {
  id: number;
  user_id: number;
  code: string;
  status: string;
  commission_pct: string;
  max_months: number | null;
  hold_days: number;
  total_referred: number;
  total_earned_cents: number;
  total_paid_cents: number;
  payout_email: string | null;
  // Stripe Connect fields
  stripe_account_id: string | null;
  stripe_onboarding_completed: boolean;
  payouts_enabled: boolean;
  stripe_account_status: string | null;
  stripe_charges_enabled: boolean;
  created_at: string;
}

export interface CommissionOut {
  id: number;
  affiliate_id: number;
  attribution_id: number;
  referred_user_id: number;
  stripe_invoice_id: string;
  invoice_amount_cents: number;
  commission_pct: string;
  commission_amount_cents: number;
  status: string;
  hold_until: string | null;
  billing_cycle_number: number;
  payout_batch_id: number | null;
  notes: string | null;
  created_at: string;
  approved_at: string | null;
  paid_at: string | null;
  voided_at: string | null;
}

export interface PayoutBatchOut {
  id: number;
  affiliate_id: number;
  period_start: string;
  period_end: string;
  total_amount_cents: number;
  commission_count: number;
  status: string;
  payout_method: string;
  payout_reference: string | null;
  stripe_transfer_id: string | null;
  created_at: string;
  paid_at: string | null;
}

export interface AffiliateDashboard {
  affiliate: AffiliateOut;
  referral_link: string;
  commissions: CommissionOut[];
  pending_amount_cents: number;
  approved_amount_cents: number;
  paid_amount_cents: number;
  w9_collected: boolean;
  
  // Detailed user metrics
  total_signups: number;  // Total users who signed up with referral link
  users_in_trial: number;  // Users currently in free trial
  users_paid_in_hold: number;  // Users who paid but commissions still in hold period
  users_approved_current_cycle: number;  // Users with approved commissions this cycle
  all_time_paid_users: number;  // Total users who have ever paid
}

export interface TaxProfileOut {
  id: number;
  affiliate_id: number;
  legal_name: string | null;
  business_name: string | null;
  tax_classification: string | null;
  tin_last4: string | null;
  w9_collected: boolean;
  w9_collected_at: string | null;
  address_line1: string | null;
  address_line2: string | null;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  country: string;
  ytd_paid_cents: Record<string, number>;
  signature_text: string | null;
  perjury_acknowledged: boolean;
  certification_confirmed: boolean;
  created_at: string;
}

export interface TaxProfileUpsert {
  legal_name?: string;
  business_name?: string;
  tax_classification?: string;
  tin?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  w9_collected?: boolean;
  signature_text?: string;
  perjury_acknowledged?: boolean;
  certification_confirmed?: boolean;
}
// Stripe Connect enrollment response
export interface StripeConnectEnrollResponse {
  id: number;
  code: string;
  status: string;
  commission_pct: number;
  stripe_onboarding_completed: boolean;
  payouts_enabled: boolean;
  onboarding_url: string | null;
  message: string;
}

// Stripe Connect status check response
export interface StripeConnectStatusResponse {
  payouts_enabled: boolean;
  onboarding_completed: boolean;
  account_status: string;
  message: string;
}

export async function enrollAffiliate(): Promise<StripeConnectEnrollResponse> {
  const { data } = await api.post<StripeConnectEnrollResponse>('/api/v1/affiliates/enroll');
  return data;
}

export async function getAffiliateDashboard(): Promise<AffiliateDashboard> {
  const { data } = await api.get<AffiliateDashboard>('/api/v1/affiliates/me');
  return data;
}

export async function getCommissions(page = 1): Promise<CommissionOut[]> {
  const { data } = await api.get<CommissionOut[]>(`/api/v1/affiliates/commissions?page=${page}`);
  return data;
}

// Stripe Connect functions
export async function getStripeOnboardingLink(): Promise<{ onboarding_url: string }> {
  const { data } = await api.get<{ onboarding_url: string }>('/api/v1/affiliates/onboarding-link');
  return data;
}

export async function refreshStripeConnectStatus(): Promise<StripeConnectStatusResponse> {
  const { data } = await api.get<StripeConnectStatusResponse>('/api/v1/affiliates/connect/refresh');
  return data;
}

export async function getPayouts(): Promise<PayoutBatchOut[]> {
  const { data } = await api.get<PayoutBatchOut[]>('/api/v1/affiliates/payouts');
  return data;
}

export async function getTaxProfile(): Promise<TaxProfileOut> {
  const { data } = await api.get<TaxProfileOut>('/api/v1/affiliates/tax-profile');
  return data;
}

export async function upsertTaxProfile(body: TaxProfileUpsert): Promise<TaxProfileOut> {
  const { data } = await api.put<TaxProfileOut>('/api/v1/affiliates/tax-profile', body);
  return data;
}

export async function updatePayoutInfo(payoutEmail: string): Promise<AffiliateOut> {
  const { data } = await api.put<AffiliateOut>('/api/v1/affiliates/payout-info', { payout_email: payoutEmail });
  return data;
}

export function formatCents(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}
