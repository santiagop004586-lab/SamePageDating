import api from './api';

const TOKEN_KEY = 'sec8_access_token';
const REFRESH_KEY = 'sec8_refresh_token';

export interface UserOut {
  id: number;
  email: string;
  full_name: string | null;
  is_verified: boolean;
  is_admin: boolean;
  beta_user: boolean;
  created_at: string;
  subscription_status?: string | null;
  subscription_current_period_end?: string | null;
  stripe_customer_id?: string | null;
  auth_provider?: string;
  totp_enabled?: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserOut;
}

export interface PartialTokenResponse {
  requires_2fa: true;
  partial_token: string;
}

export type LoginResult = TokenResponse | PartialTokenResponse;

export function isPartialToken(r: LoginResult): r is PartialTokenResponse {
  return (r as PartialTokenResponse).requires_2fa === true;
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

function saveTokens(access: string, refresh: string) {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export async function register(
  email: string,
  password: string,
  fullName?: string,
  referralCode?: string,
  inviteToken?: string,
): Promise<UserOut> {
  const { data } = await api.post<UserOut>('/api/v1/auth/register', {
    email,
    password,
    full_name: fullName || null,
    referral_code: referralCode || null,
    invite_token: inviteToken || null,
  });
  return data;
}

export async function login(email: string, password: string): Promise<LoginResult> {
  const { data } = await api.post<LoginResult>('/api/v1/auth/login', { email, password });
  if (!isPartialToken(data)) {
    saveTokens(data.access_token, data.refresh_token);
  }
  return data;
}

export async function loginWithGoogle(
  idToken: string,
  inviteToken?: string,
  referralCode?: string,
): Promise<LoginResult> {
  const { data } = await api.post<LoginResult>('/api/v1/auth/google', {
    id_token: idToken,
    invite_token: inviteToken || null,
    referral_code: referralCode || null,
  });
  if (!isPartialToken(data)) {
    saveTokens(data.access_token, data.refresh_token);
  }
  return data;
}

export async function verify2fa(partialToken: string, code: string): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/api/v1/auth/2fa/verify', {
    partial_token: partialToken,
    code,
  });
  saveTokens(data.access_token, data.refresh_token);
  return data;
}

export async function setup2fa(): Promise<{ secret: string; uri: string }> {
  const { data } = await api.post<{ secret: string; uri: string }>('/api/v1/auth/2fa/setup');
  return data;
}

export async function enable2fa(code: string): Promise<UserOut> {
  const { data } = await api.post<UserOut>('/api/v1/auth/2fa/enable', { code });
  return data;
}

export async function disable2fa(password: string): Promise<UserOut> {
  const { data } = await api.post<UserOut>('/api/v1/auth/2fa/disable', { password });
  return data;
}

export function logout() {
  clearTokens();
}

export async function getMe(): Promise<UserOut> {
  const { data } = await api.get<UserOut>('/api/v1/auth/me');
  return data;
}

export async function verifyEmail(token: string): Promise<UserOut> {
  const { data } = await api.post<UserOut>('/api/v1/auth/verify-email', { token });
  return data;
}

export async function resendVerification(email: string): Promise<void> {
  await api.post('/api/v1/auth/resend-verification', { email });
}

export async function forgotPassword(email: string): Promise<void> {
  await api.post('/api/v1/auth/forgot-password', { email });
}

export async function resetPassword(token: string, newPassword: string): Promise<void> {
  await api.post('/api/v1/auth/reset-password', { token, new_password: newPassword });
}

export async function updateProfile(fullName: string): Promise<UserOut> {
  const { data } = await api.put<UserOut>('/api/v1/auth/me', { full_name: fullName });
  return data;
}

export async function changePassword(
  currentPassword: string,
  newPassword: string
): Promise<void> {
  await api.post('/api/v1/auth/me/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
}

export { saveTokens };
