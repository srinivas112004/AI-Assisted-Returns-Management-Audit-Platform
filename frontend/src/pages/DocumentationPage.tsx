import React, { useEffect, useState } from 'react';
import { BookOpen, Search, Layers, RefreshCw, Key, ShieldCheck } from 'lucide-react';
import api from '../api/client';

export const DocumentationPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedEntity, setSelectedEntity] = useState<string>('ReturnRequest');
  const [search, setSearch] = useState('');

  const fetchDocs = async () => {
    try {
      setLoading(true);
      const res = await api.get('/data-dictionary');
      setData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
      </div>
    );
  }

  const currentEntity = data.entities.find((e: any) => e.entity_name === selectedEntity) || data.entities[0];

  const filteredFields = currentEntity.fields.filter((f: any) =>
    f.name.toLowerCase().includes(search.toLowerCase()) ||
    f.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Data Dictionary & Architectural Specs</h1>
        <p className="text-xs text-slate-500 mt-1">
          Complete schema documentation, primary/foreign key cardinalities, business rule formulas, and invariant constraints.
        </p>
      </div>

      {/* Business Rules Formula Card */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
        <h2 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-blue-600" />
          Refund Arithmetic & Allocation Formulas (docs/business_rules.md)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 font-mono text-[11px] text-slate-700 space-y-1">
            <span className="font-bold text-slate-900 block font-sans text-xs">Line Payout Equation:</span>
            <p>unit_cost = unit_price * return_qty</p>
            <p>discount_alloc = (order_line_discount / purchased_qty) * return_qty</p>
            <p>base_net = unit_cost - discount_alloc</p>
            <p>tax_alloc = (line_tax / purchased_qty) * return_qty</p>
            <p>restock_fee = base_net * (restocking_fee_percent / 100)</p>
            <p className="font-bold text-blue-700">net_refund = base_net + tax_alloc - restock_fee</p>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 text-slate-600 text-xs space-y-1.5">
            <span className="font-bold text-slate-900 block">Critical Governance Invariants:</span>
            <p>&bull; <strong>Idempotency:</strong> Duplicate requests with existing key are rejected with code <code>BLOCKED_DUPLICATE</code>.</p>
            <p>&bull; <strong>Balance Boundary:</strong> <code>total_refunds + pending &le; paid_amount</code>. Overlimit refunds rejected.</p>
            <p>&bull; <strong>Inspection First:</strong> Goods must be <code>DELIVERED</code> & inspected before <code>RESTOCK</code> disposition.</p>
            <p>&bull; <strong>Override Auditing:</strong> Late submissions require explicit authorized supervisor ID & rationale.</p>
          </div>
        </div>
      </div>

      {/* Interactive Data Dictionary */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
          {/* Entity Selector Pills */}
          <div className="flex flex-wrap items-center gap-1.5">
            {data.entities.map((e: any) => (
              <button
                key={e.entity_name}
                onClick={() => {
                  setSelectedEntity(e.entity_name);
                  setSearch('');
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  selectedEntity === e.entity_name
                    ? 'bg-blue-600 text-white font-semibold'
                    : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
                }`}
              >
                {e.entity_name}
              </button>
            ))}
          </div>

          {/* Search Field */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search field or description..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Selected Entity Header */}
        <div className="p-4 bg-slate-50/60 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Entity: {currentEntity.entity_name} <span className="font-mono text-xs text-slate-400 font-normal">({currentEntity.table_name})</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">{currentEntity.description}</p>
          </div>
          <span className="text-xs font-medium bg-slate-200 text-slate-700 px-2.5 py-1 rounded-full">
            {currentEntity.fields.length} Fields
          </span>
        </div>

        {/* Fields Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-2.5 px-4">Field Name</th>
                <th className="py-2.5 px-4">Data Type</th>
                <th className="py-2.5 px-4">Key / Index</th>
                <th className="py-2.5 px-4">Nullable</th>
                <th className="py-2.5 px-4">Field Description & Rules</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredFields.map((f: any) => (
                <tr key={f.name} className="hover:bg-slate-50/50">
                  <td className="py-2.5 px-4 font-mono font-semibold text-slate-900">{f.name}</td>
                  <td className="py-2.5 px-4 font-mono text-slate-600 text-[11px]">{f.type}</td>
                  <td className="py-2.5 px-4">
                    {f.key !== '-' ? (
                      <span className="font-mono text-[10px] font-bold px-1.5 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 rounded">
                        {f.key}
                      </span>
                    ) : (
                      <span className="text-slate-300">-</span>
                    )}
                  </td>
                  <td className="py-2.5 px-4 text-slate-600">
                    {f.required ? <span className="text-rose-600 font-medium">NOT NULL</span> : <span className="text-slate-400">NULL</span>}
                  </td>
                  <td className="py-2.5 px-4 text-slate-700">{f.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
