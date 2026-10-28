import React, { useEffect, useState } from 'react';
import { CreditCard, ShieldAlert, CheckCircle2, RefreshCw, DollarSign } from 'lucide-react';
import api from '../api/client';
import { RefundItem, RefundAttemptItem } from '../types';
import { Badge, getStatusBadgeVariant } from '../components/Badge';
import { Pagination } from '../components/Pagination';

export const RefundsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'refunds' | 'attempts'>('refunds');
  const [refunds, setRefunds] = useState<RefundItem[]>([]);
  const [attempts, setAttempts] = useState<RefundAttemptItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const fetchRefunds = async () => {
    try {
      setLoading(true);
      const res = await api.get('/refunds', { params: { page, page_size: 15 } });
      setRefunds(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAttempts = async () => {
    try {
      setLoading(true);
      const res = await api.get('/refunds/attempts', { params: { page, page_size: 15 } });
      setAttempts(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'refunds') {
      fetchRefunds();
    } else {
      fetchAttempts();
    }
  }, [activeTab, page]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Refund & Payout Management</h1>
        <p className="text-xs text-slate-500 mt-1">
          Exact monetary calculation, tax reconciliation, restocking fees, and duplicate payment prevention log.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 gap-6 text-xs font-semibold">
        <button
          onClick={() => {
            setActiveTab('refunds');
            setPage(1);
          }}
          className={`pb-3 border-b-2 flex items-center gap-1.5 transition-colors ${
            activeTab === 'refunds' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <CreditCard className="w-4 h-4" />
          Completed Disbursements
        </button>

        <button
          onClick={() => {
            setActiveTab('attempts');
            setPage(1);
          }}
          className={`pb-3 border-b-2 flex items-center gap-1.5 transition-colors ${
            activeTab === 'attempts' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <ShieldAlert className="w-4 h-4 text-rose-600" />
          Idempotency & Attempt Guard Log
        </button>
      </div>

      {/* Content */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        {activeTab === 'refunds' ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                  <th className="py-3 px-4">Refund ID</th>
                  <th className="py-3 px-4">RMA Number</th>
                  <th className="py-3 px-4">Method</th>
                  <th className="py-3 px-4">Item Amount</th>
                  <th className="py-3 px-4">Tax Refund</th>
                  <th className="py-3 px-4">Restock Fee Deducted</th>
                  <th className="py-3 px-4 font-bold text-slate-900">Net Disbursed</th>
                  <th className="py-3 px-4">Idempotency Key</th>
                  <th className="py-3 px-4">Processed At</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={10} className="text-center py-12 text-slate-400">
                      <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                      Loading refunds...
                    </td>
                  </tr>
                ) : refunds.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="text-center py-12 text-slate-500">
                      No refund records found.
                    </td>
                  </tr>
                ) : (
                  refunds.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-50/50">
                      <td className="py-3 px-4 font-mono font-medium text-slate-900">{r.refund_id}</td>
                      <td className="py-3 px-4 font-mono text-blue-600 font-medium">{r.rma_number}</td>
                      <td className="py-3 px-4 text-slate-600">{r.refund_method}</td>
                      <td className="py-3 px-4 text-slate-700">${r.base_unit_refund.toFixed(2)}</td>
                      <td className="py-3 px-4 text-slate-500">${r.tax_refund.toFixed(2)}</td>
                      <td className="py-3 px-4 text-amber-600">-${r.restocking_fee_deducted.toFixed(2)}</td>
                      <td className="py-3 px-4 font-bold text-emerald-600 text-sm">
                        ${r.net_refund_amount.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-400 text-[10px] max-w-xs truncate" title={r.idempotency_key}>
                        {r.idempotency_key}
                      </td>
                      <td className="py-3 px-4 text-slate-500">{new Date(r.processed_at).toLocaleString()}</td>
                      <td className="py-3 px-4">
                        <Badge variant="success">COMPLETED</Badge>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                  <th className="py-3 px-4">Attempt Timestamp</th>
                  <th className="py-3 px-4">RMA Number</th>
                  <th className="py-3 px-4">Idempotency Key</th>
                  <th className="py-3 px-4">Requested Amount</th>
                  <th className="py-3 px-4">Outcome</th>
                  <th className="py-3 px-4">Safeguard Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="text-center py-12 text-slate-400">
                      <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                      Loading attempt records...
                    </td>
                  </tr>
                ) : attempts.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-12 text-slate-500">
                      No refund attempts logged.
                    </td>
                  </tr>
                ) : (
                  attempts.map((a) => (
                    <tr key={a.id} className="hover:bg-slate-50/50">
                      <td className="py-3 px-4 text-slate-500">{new Date(a.timestamp).toLocaleString()}</td>
                      <td className="py-3 px-4 font-mono text-blue-600 font-medium">{a.rma_number || '-'}</td>
                      <td className="py-3 px-4 font-mono text-slate-700">{a.idempotency_key}</td>
                      <td className="py-3 px-4 font-bold text-slate-900">${a.requested_amount.toFixed(2)}</td>
                      <td className="py-3 px-4">
                        <Badge variant={getStatusBadgeVariant(a.outcome)}>{a.outcome}</Badge>
                      </td>
                      <td className="py-3 px-4 text-slate-600">{a.reason}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        <Pagination
          currentPage={page}
          totalPages={totalPages}
          totalItems={totalItems}
          pageSize={15}
          onPageChange={(p) => setPage(p)}
        />
      </div>
    </div>
  );
};

