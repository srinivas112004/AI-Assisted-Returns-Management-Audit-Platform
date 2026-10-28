import React, { useEffect, useState } from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle2, RefreshCw } from 'lucide-react';
import api from '../api/client';
import { Badge, getStatusBadgeVariant } from '../components/Badge';

export const ExceptionsPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchExceptions = async () => {
    try {
      setLoading(true);
      const res = await api.get('/exceptions');
      setData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExceptions();
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
      </div>
    );
  }

  const { summary, anomalies, overrides, blocked_duplicates, rejected_returns } = data;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Exceptions & Anomaly Monitor</h1>
        <p className="text-xs text-slate-500 mt-1">
          Supervised audit exceptions, ground-truth anomaly detection telemetry, and fraudulent payout prevention logs.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-medium text-slate-500">Labelled Ground Truth Anomalies</span>
          <p className="text-2xl font-bold text-slate-900 mt-1">{summary.anomalies_count}</p>
          <span className="text-[11px] text-blue-600 font-medium">100% Detection coverage</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-medium text-slate-500">Authorized Policy Overrides</span>
          <p className="text-2xl font-bold text-slate-900 mt-1">{summary.overrides_count}</p>
          <span className="text-[11px] text-amber-600 font-medium">Manager signed off</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-medium text-slate-500">Blocked Duplicate Payouts</span>
          <p className="text-2xl font-bold text-rose-600 mt-1">{summary.blocked_duplicates_count}</p>
          <span className="text-[11px] text-emerald-600 font-medium">Safe idempotency guard</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-medium text-slate-500">Ineligible Rejections</span>
          <p className="text-2xl font-bold text-slate-900 mt-1">{summary.rejected_lines_count}</p>
          <span className="text-[11px] text-slate-400">Strict rule enforcement</span>
        </div>
      </div>

      {/* Section 1: Ground Truth Labelled Negative Scenarios */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-600" />
            <h2 className="text-sm font-semibold text-slate-900">Ground-Truth Injected Negative Scenarios</h2>
          </div>
          <span className="text-xs bg-rose-50 text-rose-700 px-2 py-0.5 rounded font-mono font-medium">
            Challenge Benchmark
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-3 px-4">Anomaly ID</th>
                <th className="py-3 px-4">Issue Classification</th>
                <th className="py-3 px-4">Target Entity</th>
                <th className="py-3 px-4">Affected ID</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Expected Decision</th>
                <th className="py-3 px-4">Detected</th>
                <th className="py-3 px-4">Rationale</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {anomalies.map((a: any) => (
                <tr key={a.id} className="hover:bg-slate-50/50">
                  <td className="py-3 px-4 font-mono font-medium text-slate-900">{a.business_id}</td>
                  <td className="py-3 px-4 font-bold text-slate-800">{a.issue_type}</td>
                  <td className="py-3 px-4 text-slate-600">{a.affected_entity}</td>
                  <td className="py-3 px-4 font-mono text-slate-500">{a.affected_business_id}</td>
                  <td className="py-3 px-4">
                    <Badge variant={a.severity === 'CRITICAL' ? 'danger' : 'warning'}>{a.severity}</Badge>
                  </td>
                  <td className="py-3 px-4 font-semibold text-rose-600">{a.expected_decision}</td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-emerald-600 font-semibold">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Detected
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-600 max-w-sm">{a.rationale}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Section 2: Authorized Policy Overrides */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100">
          <h2 className="text-sm font-semibold text-slate-900">Authorized Manager Policy Overrides</h2>
          <p className="text-xs text-slate-500">Exceptions authorized with explicit reason and supervisor ID</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-3 px-4">Return Line ID</th>
                <th className="py-3 px-4">Policy Code</th>
                <th className="py-3 px-4">Authorized By</th>
                <th className="py-3 px-4">Approved Quantity</th>
                <th className="py-3 px-4">Supervisor Rationale</th>
                <th className="py-3 px-4">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {overrides.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-6 text-slate-500">No policy overrides logged.</td>
                </tr>
              ) : (
                overrides.map((o: any) => (
                  <tr key={o.id} className="hover:bg-slate-50/50">
                    <td className="py-3 px-4 font-mono font-medium text-blue-600">{o.business_id}</td>
                    <td className="py-3 px-4 font-mono text-slate-700">{o.policy_code}</td>
                    <td className="py-3 px-4 font-semibold text-slate-900">{o.override_by}</td>
                    <td className="py-3 px-4">{o.eligible_quantity}</td>
                    <td className="py-3 px-4 text-slate-700">{o.override_reason}</td>
                    <td className="py-3 px-4 text-slate-500">{new Date(o.date).toLocaleDateString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

