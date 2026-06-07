import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { refreshStripeConnectStatus } from '../services/affiliateService';

const AffiliateConnectReturn: React.FC = () => {
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'pending' | 'error'>('loading');
  const [message, setMessage] = useState<string>('Verifying your Stripe Connect account...');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await refreshStripeConnectStatus();
        
        if (response.payouts_enabled) {
          setStatus('success');
          setMessage('Your Stripe Connect account is fully set up! You can now receive affiliate payouts.');
          setTimeout(() => {
            navigate('/affiliate-dashboard');
          }, 3000);
        } else if (response.onboarding_completed) {
          setStatus('pending');
          setMessage('Your account is under review. Stripe will verify your information, which may take 1-2 business days.');
          setTimeout(() => {
            navigate('/affiliate-dashboard');
          }, 5000);
        } else {
          setStatus('pending');
          setMessage('Your onboarding is incomplete. Please check your dashboard for next steps.');
          setTimeout(() => {
            navigate('/affiliate-dashboard');
          }, 3000);
        }
      } catch (error) {
        console.error('Failed to check Stripe status:', error);
        setStatus('error');
        setMessage('Failed to verify your account status. Please contact support if this issue persists.');
        setTimeout(() => {
          navigate('/affiliate-dashboard');
        }, 5000);
      }
    };

    checkStatus();
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          {/* Status Icon */}
          <div className="mb-6">
            {status === 'loading' && (
              <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
            )}
            {status === 'success' && (
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100">
                <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            )}
            {status === 'pending' && (
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-100">
                <svg className="w-10 h-10 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            )}
            {status === 'error' && (
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100">
                <svg className="w-10 h-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
            )}
          </div>

          {/* Status Message */}
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {status === 'loading' && 'Checking Status...'}
            {status === 'success' && 'Setup Complete!'}
            {status === 'pending' && 'Almost There!'}
            {status === 'error' && 'Verification Error'}
          </h2>

          <p className="text-gray-600 mb-6">{message}</p>

          {/* Redirect Notice */}
          <p className="text-sm text-gray-500">
            Redirecting to your dashboard in a few seconds...
          </p>

          {/* Manual Link */}
          <button
            onClick={() => navigate('/affiliate-dashboard')}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium underline"
          >
            Go to Dashboard Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default AffiliateConnectReturn;
