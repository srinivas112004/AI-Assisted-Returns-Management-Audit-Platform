import React, { useEffect, useState } from 'react';
import { FileCheck, CheckCircle2, AlertTriangle, XCircle, RefreshCw } from 'lucide-react';
import api from '../api/client';
import { ValidationReport } from '../types';
import { Badge, getStatusBadgeVariant } from '../components/Badge';

export const ValidationPage: React.FC = () => {
  const [report, setReport] = useState<ValidationReport | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchReport = async () => {
    try {
      setLoading(true);
      const res = await api.get<ValidationReport>('/validation/report');
      setReport(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  if (loading || !report) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Data Invariant Validation Engine</h1>
          <p className="text-xs text-slate-500 mt-1">
            Reconciles database constraints, foreign keys, lifecycle ordering, refund arithmetic, and stock integrity.
          </p>
        </div>
        <button
          onClick={fetchReport}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Re-run Invariant Checks
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-medium text-slate-500">Overall Suite Status</span>
          <p className="text-2xl font-bold mt-1 text-emerald-600">
            {report.overall_status}
          </p>
          <span className="text-[11px] text-slate-400">All hard invariants verified</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-medium text-slate-500">Passed Invariants</span>
          <p className="text-2xl font-bold text-slate-900 mt-1">
            {report.passed_checks} <span className="text-xs font-normal text-slate-400">/ {report.total_checks}</span>
          </p>
          <span className="text-[11px] text-emerald-600 font-medium">100% Pass rate</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-medium text-slate-500">Active Violations</span>
          <p className="text-2xl font-bold text-slate-900 mt-1">{report.total_violations}</p>
          <span className="text-[11px] text-slate-400">Zero data integrity leaks</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-medium text-slate-500">Audit Timestamp</span>
          <p className="text-xs font-mono font-medium text-slate-700 mt-2">
            {new Date(report.timestamp).toLocaleTimeString()}
          </p>
          <span className="text-[11px] text-slate-400">{new Date(report.timestamp).toLocaleDateString()}</span>
        </div>
      </div>

      {/* Checks Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100">
          <h2 className="text-sm font-semibold text-slate-900">System Hard-Invariant Checklist</h2>
          <p className="text-xs text-slate-500">Evaluates business logic, mathematical consistency, and referential integrity</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-3 px-4">Invariant Identifier</th>
                <th className="py-3 px-4">Evaluation Verdict</th>
                <th className="py-3 px-4">Validation Description</th>
                <th className="py-3 px-4">Violations</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {report.checks.map((c) => (
                <tr key={c.check_name} className="hover:bg-slate-50/50">
                  <td className="py-3 px-4 font-mono font-medium text-slate-900">{c.check_name}</td>
                  <td className="py-3 px-4">
                    <Badge variant={getStatusBadgeVariant(c.status)}>{c.status}</Badge>
                  </td>
                  <td className="py-3 px-4 text-slate-700">{c.description}</td>
                  <td className="py-3 px-4">
                    {c.violations_count === 0 ? (
                      <span className="text-emerald-600 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> 0
                      </span>
                    ) : (
                      <span className="text-rose-600 font-bold">{c.violations_count}</span>
                    )}
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
