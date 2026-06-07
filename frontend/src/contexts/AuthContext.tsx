import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import * as authService from '../services/authService';
import type { UserOut, LoginResult } from '../services/authService';
import { getSystemConfig } from '../services/configService';

interface AuthContextValue {
  user: UserOut | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  appMode: 'waitlist' | 'active_beta' | 'production';
  referralsEnabled: boolean;
  /** Returns the raw LoginResult so the caller can handle 2FA step. */
  login: (email: string, password: string) => Promise<LoginResult>;
  /** Returns the raw LoginResult so the caller can handle 2FA step. */
  loginWithGoogle: (idToken: string, inviteToken?: string, referralCode?: string) => Promise<LoginResult>;
  /** Call after /auth/2fa/verify succeeds to store the user in context. */
  finalizeLogin: (user: UserOut) => void;
  logout: () => void;
  register: (email: string, password: string, fullName?: string, referralCode?: string, inviteToken?: string) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [appMode, setAppMode] = useState<'waitlist' | 'active_beta' | 'production'>('waitlist');
  const [referralsEnabled, setReferralsEnabled] = useState<boolean>(false);

  useEffect(() => {
    // Fetch system config (app mode + feature flags)
    getSystemConfig()
      .then(config => {
        setAppMode(config.app_mode);
        setReferralsEnabled(config.referrals_enabled);
      })
      .catch(() => {
        // Keep safe defaults if config fetch fails.
      });
  }, []);

  const refreshUser = useCallback(async () => {
    const token = authService.getToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const me = await authService.getMe();
      setUser(me);
    } catch {
      authService.clearTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = useCallback(async (email: string, password: string): Promise<LoginResult> => {
    const result = await authService.login(email, password);
    if (!authService.isPartialToken(result)) {
      setUser(result.user);
    }
    return result;
  }, []);

  const loginWithGoogle = useCallback(
    async (idToken: string, inviteToken?: string, referralCode?: string): Promise<LoginResult> => {
      const result = await authService.loginWithGoogle(idToken, inviteToken, referralCode);
      if (!authService.isPartialToken(result)) {
        setUser(result.user);
      }
      return result;
    },
    []
  );

  const finalizeLogin = useCallback((u: UserOut) => {
    setUser(u);
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
  }, []);

  const register = useCallback(
    async (email: string, password: string, fullName?: string, referralCode?: string, inviteToken?: string) => {
      await authService.register(email, password, fullName, referralCode, inviteToken);
    },
    []
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        appMode,
        referralsEnabled,
        login,
        loginWithGoogle,
        finalizeLogin,
        logout,
        register,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

