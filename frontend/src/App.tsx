import React, { useState } from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import MapContainer from './components/Map/MapContainer';
import PropertyList from './components/Properties/PropertyList';
import Header from './components/Layout/Header';
import TopFilterBar from './components/Filters/TopFilterBar';
import AssumptionsBar from './components/Layout/AssumptionsBar';
import { FiltersProvider } from './contexts/FiltersContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import WaitlistPage from './pages/WaitlistPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import SubscribePage from './pages/SubscribePage';
import SubscriptionSuccessPage from './pages/SubscriptionSuccessPage';
import AffiliateLandingPage from './pages/AffiliateLandingPage';
import AffiliateLoginPage from './pages/AffiliateLoginPage';
import AffiliateSignupPage from './pages/AffiliateSignupPage';
import AffiliateDashboardPage from './pages/AffiliateDashboardPage';
import AffiliateConnectReturn from './pages/AffiliateConnectReturn';
import AdminPage from './pages/AdminPage';
import TermsOfServicePage from './pages/TermsOfServicePage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import AffiliateAgreementPage from './pages/AffiliateAgreementPage';

// Dating app pages
import ProfilePage from './pages/ProfilePage';
import CompatibilityQuestionnairePage from './pages/CompatibilityQuestionnairePage';
import DiscoveryPage from './pages/DiscoveryPage';
import MatchesPage from './pages/MatchesPage';
import ChatPage from './pages/ChatPage';

const ACTIVE_STATUSES = ['trialing', 'active', 'past_due'];

// Guard for routes that should only be accessible in production mode
function ProductionOnlyRoute({ children }: { children: React.ReactNode }) {
  const { appMode } = useAuth();
  
  // Only allow access in production mode
  if (appMode !== 'production') {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
}

function SubscriptionGuard({ children }: { children: React.ReactNode }) {
  const { user, appMode, logout } = useAuth();
  const navigate = useNavigate();
  
  // Admin always bypasses paywall.
  if (user?.is_admin) return <>{children}</>;

  // In active_beta mode, subscription is not required.
  if (appMode === 'active_beta') return <>{children}</>;
  
  // Check if subscription status is active
  const hasActiveStatus = ACTIVE_STATUSES.includes(user?.subscription_status ?? '');
  
  // Check if subscription period has ended
  const periodEnd = user?.subscription_current_period_end 
    ? new Date(user.subscription_current_period_end) 
    : null;
  const periodExpired = periodEnd && periodEnd < new Date();
  
  // Block access if status is inactive OR period has expired
  if (!hasActiveStatus || periodExpired) {
    // In waitlist mode, show beta access denied message
    if (appMode === 'waitlist') {
      return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Restricted</h2>
            <p className="text-gray-600 mb-6">
              You don't have access to the beta at this moment. Please contact support if you believe this is an error.
            </p>
            <div className="space-y-3">
              <button
                onClick={() => navigate('/')}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Return to Home
              </button>
              <button
                onClick={() => { logout(); navigate('/'); }}
                className="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
              >
                Log Out
              </button>
            </div>
          </div>
        </div>
      );
    }
    // In production mode, redirect to subscribe page
    return <Navigate to="/subscribe" replace />;
  }
  
  return <>{children}</>;
}

function AppShell() {
  const [activeTab, setActiveTab] = useState<'map' | 'list'>('list');

  return (
    <FiltersProvider>
      <div className="flex flex-col h-screen">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <TopFilterBar />
          <div className="flex-1 flex flex-col min-h-0">
            <AssumptionsBar />
            {/* Tab Navigation */}
            <div className="bg-white border-b border-gray-200">
              <div className="flex">
                <button
                  onClick={() => setActiveTab('list')}
                  className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'list'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-800'
                  }`}
                >
                  List View
                </button>
                <button
                  onClick={() => setActiveTab('map')}
                  className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'map'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-800'
                  }`}
                >
                  Map View
                </button>
              </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-hidden">
              {activeTab === 'list' ? <PropertyList /> : <MapContainer />}
            </div>
          </div>
        </div>
      </div>
    </FiltersProvider>
  );
}

function SignupOrWaitlist() {
  // SignupPage handles the invite-token gate internally
  return <SignupPage />;
}

function AppRoutes() {
  const { referralsEnabled } = useAuth();
  
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/waitlist" element={<WaitlistPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupOrWaitlist />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route
            path="/subscribe"
            element={
              <ProtectedRoute>
                <ProductionOnlyRoute>
                  <SubscribePage />
                </ProductionOnlyRoute>
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription-success"
            element={
              <ProtectedRoute>
                <ProductionOnlyRoute>
                  <SubscriptionSuccessPage />
                </ProductionOnlyRoute>
              </ProtectedRoute>
            }
          />
          <Route
            path="/app"
            element={
              <ProtectedRoute>
                <SubscriptionGuard>
                  <AppShell />
                </SubscriptionGuard>
              </ProtectedRoute>
            }
          />
          
          {/* Dating app routes */}
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/compatibility-questionnaire"
            element={
              <ProtectedRoute>
                <CompatibilityQuestionnairePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/discovery"
            element={
              <ProtectedRoute>
                <DiscoveryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/matches"
            element={
              <ProtectedRoute>
                <MatchesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat/:matchId"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />
          {/* Affiliate routes are hidden in active beta mode */}
          <Route path="/affiliates" element={!referralsEnabled ? <Navigate to="/" replace /> : <AffiliateLandingPage />} />
          <Route path="/affiliate-login" element={!referralsEnabled ? <Navigate to="/" replace /> : <AffiliateLoginPage />} />
          <Route path="/affiliate-signup" element={!referralsEnabled ? <Navigate to="/" replace /> : <AffiliateSignupPage />} />
          <Route
            path="/affiliate-dashboard"
            element={
              !referralsEnabled ? <Navigate to="/" replace /> : (
              <ProtectedRoute>
                <AffiliateDashboardPage />
              </ProtectedRoute>
              )
            }
          />
          <Route
            path="/affiliates/connect/return"
            element={
              !referralsEnabled ? <Navigate to="/" replace /> : (
              <ProtectedRoute>
                <AffiliateConnectReturn />
              </ProtectedRoute>
              )
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <AdminPage />
              </ProtectedRoute>
            }
          />
          {/* Legal Pages - Public Access */}
          <Route path="/terms-of-service" element={<TermsOfServicePage />} />
          <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
          <Route path="/affiliate-agreement" element={<AffiliateAgreementPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
  );
}

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || '';

function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
