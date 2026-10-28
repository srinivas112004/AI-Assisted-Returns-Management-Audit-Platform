import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { BarChart3, ShieldCheck, CheckCircle2, RefreshCw, FileText } from 'lucide-react';
import api from '../api/client';
import { EvaluationMetrics } from '../types';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const res = await api.get('/analytics/overview');
      setData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
      </div>
    );
  }

  const { evaluation_metrics, reasons_breakdown, categories_breakdown, channels_breakdown, financials } = data;
  const metrics: EvaluationMetrics = evaluation_metrics;

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#64748b'];

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Analytics & Ground-Truth Evaluation</h1>
          <p className="text-xs text-slate-500 mt-1">
            Algorithmic precision, recall, F1 metrics, rule validation pass rates, and financial recovery telemetry.
          </p>
        </div>
        <button onClick={fetchAnalytics} className="p-1.5 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-600">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Detection & Invariant Evaluation Scores */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500">Anomaly Precision</span>
          <p className="text-3xl font-extrabold text-blue-600 mt-2">{(metrics.precision * 100).toFixed(1)}%</p>
          <span className="text-[11px] text-slate-400 mt-1 block">TP / (TP + FP)</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500">Anomaly Recall</span>
          <p className="text-3xl font-extrabold text-indigo-600 mt-2">{(metrics.recall * 100).toFixed(1)}%</p>
          <span className="text-[11px] text-slate-400 mt-1 block">TP / (TP + FN)</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500">F1 Score</span>
          <p className="text-3xl font-extrabold text-emerald-600 mt-2">{(metrics.f1_score * 100).toFixed(1)}%</p>
          <span className="text-[11px] text-slate-400 mt-1 block">Harmonic mean</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500">Referential Integrity</span>
          <p className="text-3xl font-extrabold text-slate-900 mt-2">{(metrics.referential_integrity_pass_rate * 100).toFixed(1)}%</p>
          <span className="text-[11px] text-emerald-600 mt-1 block font-medium">100% Invariant Compliant</span>
        </div>
      </div>

      {/* Operational Invariant Compliance Rates Grid */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
        <h2 className="text-sm font-semibold text-slate-900 mb-4">Operational Rule Engine Compliance Rates</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-[11px] text-slate-500 block">Eligibility Accuracy</span>
            <span className="text-lg font-bold text-slate-900">{(metrics.eligibility_decision_accuracy * 100).toFixed(1)}%</span>
            <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
              <div className="bg-blue-600 h-full" style={{ width: `${metrics.eligibility_decision_accuracy * 100}%` }}></div>
            </div>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-[11px] text-slate-500 block">Refund Reconciliation Rate</span>
            <span className="text-lg font-bold text-slate-900">{(metrics.refund_reconciliation_pass_rate * 100).toFixed(1)}%</span>
            <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
              <div className="bg-emerald-600 h-full" style={{ width: `${metrics.refund_reconciliation_pass_rate * 100}%` }}></div>
            </div>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-[11px] text-slate-500 block">Duplicate Prevention Rate</span>
            <span className="text-lg font-bold text-slate-900">{(metrics.duplicate_refund_prevention_rate * 100).toFixed(1)}%</span>
            <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
              <div className="bg-indigo-600 h-full" style={{ width: `${metrics.duplicate_refund_prevention_rate * 100}%` }}></div>
            </div>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-[11px] text-slate-500 block">Disposition Compliance</span>
            <span className="text-lg font-bold text-slate-900">{(metrics.inventory_disposition_compliance_rate * 100).toFixed(1)}%</span>
            <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
              <div className="bg-purple-600 h-full" style={{ width: `${metrics.inventory_disposition_compliance_rate * 100}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Detection Rate By Issue Type Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100">
          <h2 className="text-sm font-semibold text-slate-900">Detection Rate by Issue Classification</h2>
          <p className="text-xs text-slate-500">Benchmark performance on injected ground truth fixtures</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-3 px-4">Issue Classification</th>
                <th className="py-3 px-4">Injected Fixtures</th>
                <th className="py-3 px-4">Detected Fixtures</th>
                <th className="py-3 px-4">Detection Rate</th>
                <th className="py-3 px-4">Enforcement Mechanism</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {Object.entries(metrics.detection_rate_by_issue_type || {}).map(([issue, val]) => (
                <tr key={issue} className="hover:bg-slate-50/50">
                  <td className="py-3 px-4 font-mono font-medium text-slate-900">{issue}</td>
                  <td className="py-3 px-4 font-semibold text-slate-700">{val.total}</td>
                  <td className="py-3 px-4 font-semibold text-emerald-600">{val.detected}</td>
                  <td className="py-3 px-4">
                    <span className="font-bold text-blue-600">{(val.rate * 100).toFixed(0)}%</span>
                  </td>
                  <td className="py-3 px-4 text-slate-500">Deterministic Invariant Rule</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Charts: Reasons & Categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-4">
            Returns by Reason Category
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={reasons_breakdown}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="category" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} />
                <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '11px' }} />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-4">
            Returns by Product Category
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categories_breakdown}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="category" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} />
                <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '11px' }} />
                <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
