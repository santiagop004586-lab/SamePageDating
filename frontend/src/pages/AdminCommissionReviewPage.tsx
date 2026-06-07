import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { reviewCommissions, type AdminCommissionReviewRow } from '../services/adminService';

export default function AdminCommissionReviewPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const [commissions, setCommissions] = useState<AdminCommissionReviewRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  
  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);
  
  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await reviewCommissions({
        status: statusFilter || undefined,
        search: debouncedSearch || undefined,
      });
      setCommissions(data);
    } catch (err: any) {
      if (err?.response?.status === 403) {
        setError('Admin access required');
        setTimeout(() => navigate('/'), 2000);
      } else {
        setError('Failed to load commissions');
      }
    } finally {
      setLoading(false);
    }
  }, [statusFilter, debouncedSearch, navigate]);
  
  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/');
    }
  }, [user, navigate]);
  
  useEffect(() => {
    load();
  }, [load]);
  
  const formatCents = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };
  
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString();
  };
  
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
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate('/')} 
              className="text-2xl hover:opacity-80 transition-opacity"
            >
              🏨️
            </button>
            <h1 className="text-xl font-bold text-gray-900">Commission Review</h1>
            <span className="text-xs bg-red-100 text-red-700 font-semibold px-2 py-1 rounded-full">ADMIN</span>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate('/admin')}
              className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              ← Back to Admin
            </button>
            <span className="text-sm text-gray-500">{user?.email}</span>
            <button 
              onClick={() => { logout(); navigate('/'); }} 
              className="text-sm text-gray-500 hover:text-gray-800 transition-colors"
            >
              Log Out
            </button>
          </div>
        </div>
      </nav>
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="paid">Paid</option>
                <option value="voided">Voided</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Search (name/email)</label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search affiliates or referred users..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
        
        {/* Stats Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Total', count: commissions.length },
            { label: 'Pending', count: commissions.filter(c => c.status === 'pending').length },
            { label: 'Approved', count: commissions.filter(c => c.status === 'approved').length },
            { label: 'Voided', count: commissions.filter(c => c.status === 'voided').length },
          ].map((stat) => (
            <div key={stat.label} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="text-2xl font-bold text-gray-900">{stat.count}</div>
              <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
        
        {/* Loading & Error States */}
        {loading && (
          <div className="flex justify-center py-12">
            <div className="text-center">
              <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-gray-500 text-sm">Loading commissions...</p>
            </div>
          </div>
        )}
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">
            {error}
          </div>
        )}
        
        {/* Commission Table */}
        {!loading && !error && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
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
                    commissions.map((commission) => (
                      <tr key={commission.commission_id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3">
                          {getStatusBadge(commission.status)}
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-medium text-gray-900">{commission.affiliate_name || commission.affiliate_email}</div>
                          <div className="text-xs text-gray-500">{commission.affiliate_code}</div>
                          {commission.affiliate_payout_email && (
                            <div className="text-xs text-green-600 mt-1">✓ {commission.affiliate_payout_email}</div>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-medium text-gray-900">{commission.referred_user_name || commission.referred_user_email}</div>
                          <div className="text-xs text-gray-500">{commission.referred_user_email}</div>
                          <div className="text-xs text-gray-500 mt-1">
                            {commission.referred_user_subscription_status || 'no subscription'}
                          </div>
                        </td>
                        <td className="px-4 py-3 font-medium text-gray-900">
                          {formatCents(commission.invoice_amount_cents)}
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-semibold text-green-700">{formatCents(commission.commission_amount_cents)}</div>
                          <div className="text-xs text-gray-500">{commission.commission_pct}% · Cycle #{commission.billing_cycle_number}</div>
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {formatDate(commission.created_at)}
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {commission.hold_until ? formatDate(commission.hold_until) : '-'}
                        </td>
                        <td className="px-4 py-3">
                          {commission.voided_at && (
                            <div className="text-xs text-red-600 font-medium">
                              Voided: {formatDate(commission.voided_at)}
                            </div>
                          )}
                          {commission.notes && (
                            <div className="text-xs text-gray-500 max-w-xs truncate" title={commission.notes}>
                              {commission.notes}
                            </div>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
        
        {/* Legend */}
        {!loading && !error && commissions.length > 0 && (
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
      </div>
    </div>
  );
}
