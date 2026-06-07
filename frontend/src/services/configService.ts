import api from './api';

export interface SystemConfig {
  app_mode: 'waitlist' | 'active_beta' | 'production';
  referrals_enabled: boolean;
}

export async function getSystemConfig(): Promise<SystemConfig> {
  const response = await api.get<SystemConfig>('/api/v1/config/system');
  return response.data;
}

// No-op retained for backward compatibility.
export function clearConfigCache(): void {
  return;
}
