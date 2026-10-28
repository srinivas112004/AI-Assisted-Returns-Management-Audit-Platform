import React, { useState } from 'react';
import { Database, Download, RefreshCw, CheckCircle2, ShieldCheck, FileDown } from 'lucide-react';
import api from '../api/client';

const ENTITIES_LIST = [
  'customers',
  'products',
  'return_policies',
  'orders',
  'order_lines',
  'return_requests',
  'return_lines',
  'return_authorizations',
  'return_shipments',
  'inspections',
  'refunds',
  'refund_attempts',
  'inventory_dispositions',
  'inventory_movements',
  'return_events',
  'ground_truth',
];

export const GeneratorPage: React.FC = () => {
  const [profile, setProfile] = useState<'starter' | 'full'>('starter');
  const [seed, setSeed] = useState<number>(20261022);
  const [adminKey, setAdminKey] = useState('yotaa-secure-admin-token-2026');
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsGenerating(true);
      setError(null);
      setResult(null);

      const res = await api.post(
        '/admin/generate-data',
        { profile, seed },
        {
          headers: { 'X-Admin-Key': adminKey },
        }
      );
      setResult(res.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Data generation failed.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Synthetic Dataset Generator & Exports</h1>
        <p className="text-xs text-slate-500 mt-1">
          Generate deterministic, seed-locked baseline records and labelled negative anomalies. No real customer PII is used.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Generator Controls */}
        <div className="lg:col-span-1 bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
          <h2 className="text-sm font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-600" />
            Generation Parameters
          </h2>

          <form onSubmit={handleGenerate} className="space-y-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Dataset Profile</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setProfile('starter')}
                  className={`py-2 px-3 rounded-lg border text-left font-medium transition-colors ${
                    profile === 'starter'
                      ? 'border-blue-600 bg-blue-50 text-blue-700 font-semibold'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span className="block text-xs">Starter Profile</span>
                  <span className="text-[10px] text-slate-400 block mt-0.5">300 Orders / 60 RMAs</span>
                </button>

                <button
                  type="button"
                  onClick={() => setProfile('full')}
                  className={`py-2 px-3 rounded-lg border text-left font-medium transition-colors ${
                    profile === 'full'
                      ? 'border-blue-600 bg-blue-50 text-blue-700 font-semibold'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span className="block text-xs">Full Profile</span>
                  <span className="text-[10px] text-slate-400 block mt-0.5">30k Orders / 5k RMAs</span>
                </button>
              </div>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Deterministic Random Seed</label>
              <input
                type="number"
                required
                value={seed}
                onChange={(e) => setSeed(parseInt(e.target.value, 10) || 20261022)}
                className="w-full px-3 py-1.5 border border-slate-300 rounded-lg font-mono"
              />
              <p className="text-[10px] text-slate-400 mt-1">Default: 20261022 (ensures identical outputs)</p>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Admin Security Key (X-Admin-Key)</label>
              <input
                type="password"
                required
                value={adminKey}
                onChange={(e) => setAdminKey(e.target.value)}
                className="w-full px-3 py-1.5 border border-slate-300 rounded-lg font-mono text-[11px]"
              />
            </div>

            {error && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-lg text-xs">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isGenerating}
              className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold shadow-xs flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Generating Dataset...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  Execute Generator
                </>
              )}
            </button>
          </form>
        </div>

        {/* Generator Output / Results */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-semibold text-slate-900 mb-2">Generation Manifest & Output</h2>
            <p className="text-xs text-slate-500 mb-4">
              Child entities deterministically reference valid parent IDs. File checksums are 100% reproducible.
            </p>

            {result ? (
              <div className="space-y-4">
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>{result.message}</span>
                </div>

                <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                  <pre className="font-mono text-[11px] text-slate-800 overflow-x-auto">
                    {JSON.stringify(result.summary, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center text-xs text-slate-400">
                Execute generator to view live row count manifest and entity statistics.
              </div>
            )}
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span className="font-medium text-slate-700">Reproducibility Guarantee:</span>
            <span>Deterministic SHA-256 Verified</span>
          </div>
        </div>
      </div>

      {/* Exportable Entities Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100">
          <h2 className="text-sm font-semibold text-slate-900">Download Raw Entity Exports</h2>
          <p className="text-xs text-slate-500">Download clean CSV or JSON files directly from the database</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-3 px-4">Entity Collection</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4 text-right">Download Link</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {ENTITIES_LIST.map((entity) => (
                <tr key={entity} className="hover:bg-slate-50/50">
                  <td className="py-2.5 px-4 font-mono font-medium text-slate-800 capitalize">
                    {entity.replace('_', ' ')}
                  </td>
                  <td className="py-2.5 px-4 text-slate-500">CSV &bull; JSON</td>
                  <td className="py-2.5 px-4 text-right space-x-2">
                    <a
                      href={`/api/exports/${entity}.csv`}
                      download={`${entity}.csv`}
                      className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded hover:bg-slate-50"
                    >
                      <Download className="w-3 h-3 text-slate-500" />
                      .CSV
                    </a>
                    <a
                      href={`/api/exports/${entity}.json`}
                      download={`${entity}.json`}
                      className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded hover:bg-blue-100"
                    >
                      <Download className="w-3 h-3 text-blue-600" />
                      .JSON
                    </a>
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

