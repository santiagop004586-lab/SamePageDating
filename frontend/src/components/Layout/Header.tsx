import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import SettingsPanel from './SettingsPanel';
import FeedbackModal from './FeedbackModal';

const Header: React.FC = () => {
  const { user, logout, appMode, referralsEnabled } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const isWaitlistOrBeta = appMode !== 'production';
  const showReferrals = referralsEnabled;

  return (
    <>
      {/* Beta banner */}
      {isWaitlistOrBeta && (
        <div className="bg-indigo-600 text-white text-center text-xs font-semibold py-1.5 px-4 flex items-center justify-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse inline-block" />
          You're in the <strong>private beta</strong> — thanks for helping us test! Share feedback using the button in the top bar.
        </div>
      )}
      <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">DF</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Deal Finder</h1>
              <p className="text-sm text-gray-500">Real Estate Investment Analytics</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Referrals button — shown whenever referral system is enabled */}
            {user && showReferrals && (
              <button
                onClick={() => navigate('/affiliate-dashboard')}
                className="flex items-center gap-1.5 text-sm font-semibold text-green-700 border border-green-600 px-3 py-1.5 rounded-lg hover:bg-green-50 transition-colors"
              >
                💸 Referrals
              </button>
            )}

            {/* Feedback button — active beta only, and hidden whenever referrals are enabled */}
            {user && appMode === 'active_beta' && (
              <button
                onClick={() => setFeedbackOpen(true)}
                className="flex items-center gap-1.5 text-sm font-semibold text-indigo-700 border border-indigo-400 px-3 py-1.5 rounded-lg hover:bg-indigo-50 transition-colors"
              >
                🧪 Beta Feedback
              </button>
            )}

            {/* User menu */}
            {user && (
              <div className="relative">
                <button
                  onClick={() => setMenuOpen((v) => !v)}
                  className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 transition-colors rounded-lg px-3 py-2 text-sm font-medium text-gray-700"
                >
                  <div className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold">
                    {(user.full_name || user.email).charAt(0).toUpperCase()}
                  </div>
                  <span className="max-w-[120px] truncate">{user.full_name || user.email}</span>
                  <span className="text-gray-400">▾</span>
                </button>

                {menuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-30"
                      onClick={() => setMenuOpen(false)}
                    />
                    <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-100 rounded-xl shadow-lg z-40 py-1 overflow-hidden">
                      <div className="px-4 py-2 border-b border-gray-50">
                        <p className="text-xs text-gray-400 truncate">{user.email}</p>
                      </div>
                      <button
                        onClick={() => { setMenuOpen(false); setSettingsOpen(true); }}
                        className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                      >
                        ⚙️ Settings
                      </button>
                      <button
                        onClick={() => { setMenuOpen(false); logout(); }}
                        className="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                      >
                        Sign Out
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      {settingsOpen && <SettingsPanel onClose={() => setSettingsOpen(false)} />}
      {feedbackOpen && <FeedbackModal onClose={() => setFeedbackOpen(false)} />}
    </>
  );
};

export default Header;
