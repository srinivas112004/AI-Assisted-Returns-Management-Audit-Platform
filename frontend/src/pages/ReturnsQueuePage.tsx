import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Search, Plus, RotateCcw, Filter, RefreshCw, Eye } from 'lucide-react';
import api from '../api/client';
import { ReturnListItem } from '../types';
import { Badge, getStatusBadgeVariant } from '../components/Badge';
import { Pagination } from '../components/Pagination';
import { Modal } from '../components/Modal';

export const ReturnsQueuePage: React.FC = () => {
  const [returns, setReturns] = useState<ReturnListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [eligibilityFilter, setEligibilityFilter] = useState('');
  const [channelFilter, setChannelFilter] = useState('');

  // Create RMA Modal
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createOrderId, setCreateOrderId] = useState('');
  const [createCustomerId, setCreateCustomerId] = useState('');
  const [createReason, setCreateReason] = useState('DEFECTIVE');
  const [createChannel, setCreateChannel] = useState('WEB');
  const [createComments, setCreateComments] = useState('');
  const [createOrderLineId, setCreateOrderLineId] = useState('');
  const [createQuantity, setCreateQuantity] = useState(1);
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const fetchReturns = async () => {
    try {
      setLoading(true);
      const res = await api.get('/returns', {
        params: {
          page,
          page_size: 15,
          search: search || undefined,
          status: statusFilter || undefined,
          eligibility: eligibilityFilter || undefined,
          channel: channelFilter || undefined,
        },
      });
      setReturns(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReturns();
  }, [page, statusFilter, eligibilityFilter, channelFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchReturns();
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setCreateSubmitting(true);
      setCreateError(null);
      await api.post('/returns', {
        order_id: createOrderId.trim(),
        customer_id: createCustomerId.trim(),
        reason_category: createReason,
        channel: createChannel,
        customer_comments: createComments || undefined,
        lines: [
          {
            order_line_id: parseInt(createOrderLineId, 10),
            requested_quantity: createQuantity,
          },
        ],
      });
      setIsCreateOpen(false);
      // Reset form
      setCreateOrderId('');
      setCreateCustomerId('');
      setCreateOrderLineId('');
      setCreateQuantity(1);
      setCreateComments('');
      fetchReturns();
    } catch (err: any) {
      setCreateError(err?.response?.data?.detail || err?.message || 'Failed to submit return request.');
    } finally {
      setCreateSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Title & Action */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Returns Queue</h1>
          <p className="text-xs text-slate-500 mt-1">
            Active and historical customer return authorizations across channels.
          </p>
        </div>
        <button
          onClick={() => setIsCreateOpen(true)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Return Request
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <form onSubmit={handleSearch} className="flex-1 max-w-sm relative">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search RMA number (e.g. RMA-2026-000001)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white transition-colors"
          />
        </form>

        <div className="flex flex-wrap items-center gap-2">
          {/* Eligibility Filter */}
          <select
            value={eligibilityFilter}
            onChange={(e) => {
              setEligibilityFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Eligibilities</option>
            <option value="FULLY_ELIGIBLE">FULLY_ELIGIBLE</option>
            <option value="PARTIALLY_ELIGIBLE">PARTIALLY_ELIGIBLE</option>
            <option value="INELIGIBLE">INELIGIBLE</option>
            <option value="PENDING_REVIEW">PENDING_REVIEW</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="SUBMITTED">SUBMITTED</option>
            <option value="ELIGIBLE">ELIGIBLE</option>
            <option value="AUTHORIZED">AUTHORIZED</option>
            <option value="IN_TRANSIT">IN_TRANSIT</option>
            <option value="RECEIVED">RECEIVED</option>
            <option value="INSPECTED">INSPECTED</option>
            <option value="COMPLETED">COMPLETED</option>
            <option value="REJECTED">REJECTED</option>
          </select>

          {/* Channel Filter */}
          <select
            value={channelFilter}
            onChange={(e) => {
              setChannelFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Channels</option>
            <option value="WEB">WEB</option>
            <option value="MOBILE">MOBILE</option>
            <option value="SUPPORT_PORTAL">SUPPORT_PORTAL</option>
            <option value="IN_STORE">IN_STORE</option>
          </select>

          <button
            onClick={fetchReturns}
            className="p-1.5 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
            title="Refresh Queue"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
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
                <th className="py-3 px-4">Reason</th>
                <th className="py-3 px-4">Channel</th>
                <th className="py-3 px-4">Requested Date</th>
                <th className="py-3 px-4">Eligibility</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                    Loading return requests...
                  </td>
                </tr>
              ) : returns.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-slate-500">
                    No returns found matching the active criteria.
                  </td>
                </tr>
              ) : (
                returns.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-blue-600">
                      <NavLink to={`/returns/${r.rma_number}`} className="hover:underline">
                        {r.rma_number}
                      </NavLink>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-700">{r.order_id}</td>
                    <td className="py-3 px-4 text-slate-800">{r.customer_name}</td>
                    <td className="py-3 px-4 text-slate-600">{r.reason_category}</td>
                    <td className="py-3 px-4 text-slate-500">{r.channel}</td>
                    <td className="py-3 px-4 text-slate-500">
                      {new Date(r.requested_date).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant={getStatusBadgeVariant(r.overall_eligibility)}>
                        {r.overall_eligibility}
                      </Badge>
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant={getStatusBadgeVariant(r.status)}>{r.status}</Badge>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <NavLink
                        to={`/returns/${r.rma_number}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-blue-600 hover:text-blue-700 bg-blue-50/60 hover:bg-blue-100/60 rounded border border-blue-200 transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        Details
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

      {/* Create RMA Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Create New Return Request (RMA)"
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
          {createError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-lg">
              {createError}
            </div>
          )}

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Order Business ID</label>
            <input
              type="text"
              required
              placeholder="e.g. ORD-2026-000001"
              value={createOrderId}
              onChange={(e) => setCreateOrderId(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Customer Business ID</label>
            <input
              type="text"
              required
              placeholder="e.g. CUST-2026-000001"
              value={createCustomerId}
              onChange={(e) => setCreateCustomerId(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Order Line Database ID</label>
              <input
                type="number"
                required
                min="1"
                placeholder="e.g. 1"
                value={createOrderLineId}
                onChange={(e) => setCreateOrderLineId(e.target.value)}
                className="w-full px-3 py-1.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Return Quantity</label>
              <input
                type="number"
                required
                min="1"
                value={createQuantity}
                onChange={(e) => setCreateQuantity(parseInt(e.target.value, 10) || 1)}
                className="w-full px-3 py-1.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Reason Category</label>
              <select
                value={createReason}
                onChange={(e) => setCreateReason(e.target.value)}
                className="w-full px-3 py-1.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="DEFECTIVE">DEFECTIVE</option>
                <option value="WRONG_ITEM">WRONG_ITEM</option>
                <option value="SIZE_FIT">SIZE_FIT</option>
                <option value="CHANGED_MIND">CHANGED_MIND</option>
                <option value="NOT_AS_DESCRIBED">NOT_AS_DESCRIBED</option>
                <option value="ARRIVED_LATE">ARRIVED_LATE</option>
                <option value="MISSING_PARTS">MISSING_PARTS</option>
              </select>
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Intake Channel</label>
              <select
                value={createChannel}
                onChange={(e) => setCreateChannel(e.target.value)}
                className="w-full px-3 py-1.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="WEB">WEB</option>
                <option value="MOBILE">MOBILE</option>
                <option value="SUPPORT_PORTAL">SUPPORT_PORTAL</option>
                <option value="IN_STORE">IN_STORE</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Customer Comments</label>
            <textarea
              rows={2}
              placeholder="Optional customer explanation..."
              value={createComments}
              onChange={(e) => setCreateComments(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsCreateOpen(false)}
              className="px-3 py-1.5 text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createSubmitting}
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold shadow-xs disabled:opacity-50 transition-colors"
            >
              {createSubmitting ? 'Evaluating...' : 'Submit & Evaluate RMA'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
