import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { CheckCircle2, AlertTriangle, ShieldCheck, RefreshCw, Eye } from 'lucide-react';
import api from '../api/client';
import { ReturnListItem } from '../types';
import { Badge, getStatusBadgeVariant } from '../components/Badge';
import { Pagination } from '../components/Pagination';

export const EligibilityAuthPage: React.FC = () => {
  const [items, setItems] = useState<ReturnListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [eligibilityFilter, setEligibilityFilter] = useState('FULLY_ELIGIBLE');

  const fetchItems = async () => {
    try {
      setLoading(true);
      const res = await api.get('/returns', {
        params: {
          page,
          page_size: 15,
          eligibility: eligibilityFilter || undefined,
        },
      });
      setItems(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [page, eligibilityFilter]);

  const authorizeRma = async (rmaNumber: string) => {
    try {
      await api.post(`/returns/${rmaNumber}/authorize`, {
        authorized_by: 'AUTH_WORKSPACE',
        validity_days: 14,
      });
      fetchItems();
    } catch (err: any) {
      alert(err?.response?.data?.detail || err?.message || 'Authorization failed');
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Eligibility & Authorization Desk</h1>
        <p className="text-xs text-slate-500 mt-1">
          Review policy evaluation verdicts, grant supervisor overrides, and issue deterministic return authorizations.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 gap-6 text-xs font-semibold">
        {[
          { label: 'Fully Eligible', value: 'FULLY_ELIGIBLE' },
          { label: 'Partially Eligible', value: 'PARTIALLY_ELIGIBLE' },
          { label: 'Ineligible / Overdue', value: 'INELIGIBLE' },
          { label: 'Pending Review', value: 'PENDING_REVIEW' },
          { label: 'All Requests', value: '' },
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => {
              setEligibilityFilter(tab.value);
              setPage(1);
            }}
            className={`pb-3 border-b-2 transition-colors ${
              eligibilityFilter === tab.value
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-3 px-4">RMA Number</th>
                <th className="py-3 px-4">Order ID</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Requested Date</th>
                <th className="py-3 px-4">Reason</th>
                <th className="py-3 px-4">Eligibility</th>
                <th className="py-3 px-4">Auth Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                    Loading requests...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-slate-500">
                    No requests found matching category '{eligibilityFilter || 'All'}'.
                  </td>
                </tr>
              ) : (
                items.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/50">
                    <td className="py-3 px-4 font-mono font-medium text-blue-600">
                      <NavLink to={`/returns/${r.rma_number}`} className="hover:underline">
                        {r.rma_number}
                      </NavLink>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-700">{r.order_id}</td>
                    <td className="py-3 px-4 text-slate-800">{r.customer_name}</td>
                    <td className="py-3 px-4 text-slate-500">{new Date(r.requested_date).toLocaleDateString()}</td>
                    <td className="py-3 px-4 text-slate-600">{r.reason_category}</td>
                    <td className="py-3 px-4">
                      <Badge variant={getStatusBadgeVariant(r.overall_eligibility)}>
                        {r.overall_eligibility}
                      </Badge>
                    </td>
                    <td className="py-3 px-4">
                      {r.has_authorization ? (
                        <span className="text-emerald-600 font-medium flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Authorized
                        </span>
                      ) : (
                        <span className="text-slate-400 font-medium">Pending Auth</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      {!r.has_authorization && ['FULLY_ELIGIBLE', 'PARTIALLY_ELIGIBLE'].includes(r.overall_eligibility) && (
                        <button
                          onClick={() => authorizeRma(r.rma_number)}
                          className="px-2.5 py-1 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded shadow-2xs"
                        >
                          Authorize
                        </button>
                      )}
                      <NavLink
                        to={`/returns/${r.rma_number}`}
                        className="px-2.5 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded hover:bg-slate-50"
                      >
                        Inspect Rules
                      </NavLink>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

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

