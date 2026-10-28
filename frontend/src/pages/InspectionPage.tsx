import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { ClipboardCheck, RefreshCw, Filter, Eye } from 'lucide-react';
import api from '../api/client';
import { InspectionItem } from '../types';
import { Badge, getStatusBadgeVariant } from '../components/Badge';
import { Pagination } from '../components/Pagination';

export const InspectionPage: React.FC = () => {
  const [inspections, setInspections] = useState<InspectionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const [resultFilter, setResultFilter] = useState('');
  const [dispositionFilter, setDispositionFilter] = useState('');

  const fetchInspections = async () => {
    try {
      setLoading(true);
      const res = await api.get('/inspections', {
        params: {
          page,
          page_size: 15,
          result: resultFilter || undefined,
          disposition: dispositionFilter || undefined,
        },
      });
      setInspections(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInspections();
  }, [page, resultFilter, dispositionFilter]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Warehouse Inspection Workspace</h1>
        <p className="text-xs text-slate-500 mt-1">
          Quality assurance evaluations, item condition tagging, packaging verification, and disposition recommendation rules.
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <select
            value={resultFilter}
            onChange={(e) => {
              setResultFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700"
          >
            <option value="">All QA Results</option>
            <option value="PASS">PASS</option>
            <option value="PASS_WITH_RESTOCKING_FEE">PASS_WITH_RESTOCKING_FEE</option>
            <option value="REFURBISHABLE">REFURBISHABLE</option>
            <option value="QUARANTINE_REQUIRED">QUARANTINE_REQUIRED</option>
            <option value="REJECT_SCRAP">REJECT_SCRAP</option>
          </select>

          <select
            value={dispositionFilter}
            onChange={(e) => {
              setDispositionFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700"
          >
            <option value="">All Recommended Dispositions</option>
            <option value="RESTOCK">RESTOCK</option>
            <option value="REFURBISH">REFURBISH</option>
            <option value="QUARANTINE">QUARANTINE</option>
            <option value="SCRAP">SCRAP</option>
          </select>
        </div>

        <button onClick={fetchInspections} className="p-1.5 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-3 px-4">Inspection ID</th>
                <th className="py-3 px-4">Shipment ID</th>
                <th className="py-3 px-4">Return Line</th>
                <th className="py-3 px-4">Product Name</th>
                <th className="py-3 px-4">Item Condition</th>
                <th className="py-3 px-4">Packaging</th>
                <th className="py-3 px-4">Damage Type</th>
                <th className="py-3 px-4">QA Result</th>
                <th className="py-3 px-4">Recommended Disposition</th>
                <th className="py-3 px-4">Inspector</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={10} className="text-center py-12 text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                    Loading inspections...
                  </td>
                </tr>
              ) : inspections.length === 0 ? (
                <tr>
                  <td colSpan={10} className="text-center py-12 text-slate-500">
                    No inspection records found.
                  </td>
                </tr>
              ) : (
                inspections.map((i) => (
                  <tr key={i.id} className="hover:bg-slate-50/50">
                    <td className="py-3 px-4 font-mono font-medium text-slate-900">{i.inspection_id}</td>
                    <td className="py-3 px-4 font-mono text-slate-600">{i.shipment_id}</td>
                    <td className="py-3 px-4 font-mono text-blue-600 font-medium">{i.return_line_id}</td>
                    <td className="py-3 px-4 font-medium text-slate-800">{i.product_name}</td>
                    <td className="py-3 px-4 text-slate-700">{i.item_condition}</td>
                    <td className="py-3 px-4 text-slate-600">{i.packaging_condition}</td>
                    <td className="py-3 px-4 text-slate-500">{i.damage_type}</td>
                    <td className="py-3 px-4">
                      <Badge variant={getStatusBadgeVariant(i.result)}>{i.result}</Badge>
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant={getStatusBadgeVariant(i.recommended_disposition)}>
                        {i.recommended_disposition}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-500 text-[11px]">{i.inspector_id}</td>
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
