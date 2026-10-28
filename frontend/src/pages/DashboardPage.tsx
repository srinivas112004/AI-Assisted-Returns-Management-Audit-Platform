import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShoppingCart,
  RotateCcw,
  Percent,
  CheckCircle2,
  Clock,
  DollarSign,
  ShieldAlert,
  Boxes,
  FileCheck2,
  ArrowUpRight,
  RefreshCw,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import api from '../api/client';
import { DashboardSummaryResponse } from '../types';
import { Badge, getStatusBadgeVariant } from '../components/Badge';

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get<DashboardSummaryResponse>('/dashboard/summary');
      setData(res.data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load dashboard summary');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-2">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
          <span className="text-xs text-slate-500 font-medium">Loading platform analytics...</span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-rose-800">
        <p className="font-medium text-sm">Failed to load dashboard data.</p>
        <p className="text-xs mt-1 text-rose-600">{error}</p>
        <button
          onClick={fetchSummary}
          className="mt-3 px-3 py-1.5 bg-rose-600 text-white rounded text-xs font-medium hover:bg-rose-700"
        >
          Retry
        </button>
      </div>
    );
  }

  const { cards, disposition_breakdown, recent_returns } = data;

  const dispChartData = [
    { name: 'Restock', value: disposition_breakdown['RESTOCK'] || 0, color: '#10b981' },
    { name: 'Refurbish', value: disposition_breakdown['REFURBISH'] || 0, color: '#3b82f6' },
    { name: 'Quarantine', value: disposition_breakdown['QUARANTINE'] || 0, color: '#f59e0b' },
    { name: 'Scrap', value: disposition_breakdown['SCRAP'] || 0, color: '#ef4444' },
  ];

  const eligibilityChartData = [
    { name: 'Eligible', count: cards.eligible_requests },
    { name: 'Rejected', count: cards.rejected_requests },
    { name: 'Pending Review', count: cards.pending_review_requests },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Title & Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Returns Operations & Audit Dashboard</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time telemetry, reverse logistics pipeline, duplicate protection, and anomaly detection.
          </p>
        </div>
        <button
          onClick={fetchSummary}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50 shadow-sm transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* Primary KPI Cards (10 required metrics) */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {/* 1. Total Orders */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Total Orders</span>
            <ShoppingCart className="w-4 h-4 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{cards.total_orders.toLocaleString()}</p>
          <p className="text-[11px] text-slate-400 mt-1">Persisted orders</p>
        </div>

        {/* 2. Return Requests */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Return Requests</span>
            <RotateCcw className="w-4 h-4 text-indigo-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{cards.return_requests.toLocaleString()}</p>
          <p className="text-[11px] text-slate-400 mt-1">RMAs registered</p>
        </div>

        {/* 3. Return Rate */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Return Rate</span>
            <Percent className="w-4 h-4 text-sky-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{cards.return_rate_percent}%</p>
          <p className="text-[11px] text-slate-400 mt-1">RMAs / Orders</p>
        </div>

        {/* 4. Eligible vs Rejected */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Eligible / Rejected</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            <span className="text-emerald-600">{cards.eligible_requests}</span>
            <span className="text-slate-300 mx-1">/</span>
            <span className="text-rose-600">{cards.rejected_requests}</span>
          </p>
          <p className="text-[11px] text-slate-400 mt-1">{cards.pending_review_requests} pending review</p>
        </div>

        {/* 5. Pending Inspections */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Pending Inspections</span>
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{cards.pending_inspections}</p>
          <p className="text-[11px] text-slate-400 mt-1">Dock parcels waiting</p>
        </div>

        {/* 6. Refund Amount */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Refund Amount</span>
            <DollarSign className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            ${cards.refund_amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p className="text-[11px] text-slate-400 mt-1">Reconciled payouts</p>
        </div>

        {/* 7. Blocked Duplicate Payments */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Blocked Duplicates</span>
            <ShieldAlert className="w-4 h-4 text-rose-600" />
          </div>
          <p className="text-2xl font-bold text-rose-600 mt-2">{cards.blocked_duplicate_refunds}</p>
          <p className="text-[11px] text-slate-400 mt-1">Idempotency protected</p>
        </div>

        {/* 8. Total Dispositions */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Dispositions</span>
            <Boxes className="w-4 h-4 text-purple-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {(dispChartData.reduce((acc, curr) => acc + curr.value, 0)).toLocaleString()}
          </p>
          <p className="text-[11px] text-slate-400 mt-1">Restock, Refurb, Scrap</p>
        </div>

        {/* 9. Detected Anomalies */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Detected Anomalies</span>
            <ShieldAlert className="w-4 h-4 text-amber-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            <span className="text-blue-600">{cards.detected_anomalies}</span>
            <span className="text-slate-300 mx-1">/</span>
            <span className="text-slate-500">{cards.total_anomalies}</span>
          </p>
          <p className="text-[11px] text-slate-400 mt-1">Ground truth tested</p>
        </div>

        {/* 10. Validation Pass Rate */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Validation Status</span>
            <FileCheck2 className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-bold text-emerald-600 mt-2">{cards.validation_pass_rate}%</p>
          <p className="text-[11px] text-slate-400 mt-1">
            Overall: <span className="font-semibold text-emerald-700">{cards.validation_overall_status}</span>
          </p>
        </div>
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Eligibility Breakdown Bar Chart */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
          <h2 className="text-sm font-semibold text-slate-900 mb-1">Return Request Decisions</h2>
          <p className="text-xs text-slate-500 mb-4">Rule engine evaluation distribution</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={eligibilityChartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Inventory Disposition Breakdown Donut Chart */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
          <h2 className="text-sm font-semibold text-slate-900 mb-1">Inventory Disposition Breakdown</h2>
          <p className="text-xs text-slate-500 mb-4">Warehouse physical routing outcomes</p>
          <div className="h-56 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={dispChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {dispChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-slate-100 text-xs">
            {dispChartData.map((item) => (
              <div key={item.name} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                <span className="text-slate-600">{item.name}:</span>
                <span className="font-semibold text-slate-900 ml-auto">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Links & Pipeline Overview */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-semibold text-slate-900 mb-1">Audit & Governance Quick Links</h2>
            <p className="text-xs text-slate-500 mb-4">High-priority operational workflows</p>
            <div className="space-y-2.5">
              <NavLink
                to="/eligibility"
                className="flex items-center justify-between p-3 rounded-lg border border-slate-100 hover:border-blue-200 hover:bg-blue-50/50 transition-colors"
              >
                <div>
                  <p className="text-xs font-semibold text-slate-900">Eligibility & Exceptions</p>
                  <p className="text-[11px] text-slate-500">Authorize returns or approve policy overrides</p>
                </div>
                <ArrowUpRight className="w-4 h-4 text-blue-600" />
              </NavLink>

              <NavLink
                to="/inspections"
                className="flex items-center justify-between p-3 rounded-lg border border-slate-100 hover:border-blue-200 hover:bg-blue-50/50 transition-colors"
              >
                <div>
                  <p className="text-xs font-semibold text-slate-900">Inspection Workspace</p>
                  <p className="text-[11px] text-slate-500">Record package conditions and disposition routing</p>
                </div>
                <ArrowUpRight className="w-4 h-4 text-blue-600" />
              </NavLink>

              <NavLink
                to="/validation"
                className="flex items-center justify-between p-3 rounded-lg border border-slate-100 hover:border-blue-200 hover:bg-blue-50/50 transition-colors"
              >
                <div>
                  <p className="text-xs font-semibold text-slate-900">Validation Engine Report</p>
                  <p className="text-[11px] text-slate-500">Inspect system invariants and data reconciliation</p>
                </div>
                <ArrowUpRight className="w-4 h-4 text-blue-600" />
              </NavLink>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 text-xs text-slate-500 flex items-center justify-between">
            <span>Platform Seed: <strong className="text-slate-800 font-mono">20261022</strong></span>
            <NavLink to="/generator" className="text-blue-600 font-medium hover:underline">
              Dataset Settings &rarr;
            </NavLink>
          </div>
        </div>
      </div>

      {/* Recent Returns Queue Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Recent Return Requests</h2>
            <p className="text-xs text-slate-500 mt-0.5">Live reverse logistics lifecycle tracking</p>
          </div>
          <NavLink
            to="/returns"
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 inline-flex items-center gap-1"
          >
            View All Returns Queue &rarr;
          </NavLink>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-3 px-4">RMA Number</th>
                <th className="py-3 px-4">Order ID</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Requested Date</th>
                <th className="py-3 px-4">Eligibility</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recent_returns.map((rma) => (
                <tr key={rma.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="py-3 px-4 font-mono font-medium text-blue-600">
                    <NavLink to={`/returns/${rma.rma_number}`} className="hover:underline">
                      {rma.rma_number}
                    </NavLink>
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-700">{rma.order_id}</td>
                  <td className="py-3 px-4 text-slate-800">{rma.customer_name}</td>
                  <td className="py-3 px-4 text-slate-500">
                    {new Date(rma.requested_date).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={getStatusBadgeVariant(rma.overall_eligibility)}>
                      {rma.overall_eligibility}
                    </Badge>
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={getStatusBadgeVariant(rma.status)}>
                      {rma.status}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <NavLink
                      to={`/returns/${rma.rma_number}`}
                      className="px-2.5 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded hover:bg-slate-50 transition-colors"
                    >
                      View Details
                    </NavLink>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
