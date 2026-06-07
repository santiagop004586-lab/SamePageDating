import api from './api';

export async function createCheckoutSession(referralCode?: string): Promise<string> {
  const { data } = await api.post<{ url: string }>('/api/v1/billing/create-checkout-session', {
    referral_code: referralCode || null,
  });
  return data.url;
}

export async function createPortalSession(): Promise<string> {
  const { data } = await api.post<{ url: string }>('/api/v1/billing/create-portal-session');
  return data.url;
}

export interface BillingStatus {
  subscription_status: string | null;
  trial_end: string | null;
  current_period_end: string | null;
  has_payment_method: boolean;
}

export async function getBillingStatus(): Promise<BillingStatus> {
  const { data } = await api.get<BillingStatus>('/api/v1/billing/status');
  return data;
}

export async function syncFromSession(sessionId: string): Promise<void> {
  await api.post(`/api/v1/billing/sync-from-session?session_id=${encodeURIComponent(sessionId)}`);
}
