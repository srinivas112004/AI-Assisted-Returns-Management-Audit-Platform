import React, { useEffect, useState } from 'react';
import { Boxes, ArrowRightLeft, RefreshCw, Filter } from 'lucide-react';
import api from '../api/client';
import { DispositionItem, MovementItem } from '../types';
import { Badge, getStatusBadgeVariant } from '../components/Badge';
import { Pagination } from '../components/Pagination';

export const DispositionsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dispositions' | 'movements'>('dispositions');
  const [dispositions, setDispositions] = useState<DispositionItem[]>([]);
  const [movements, setMovements] = useState<MovementItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const fetchDispositions = async () => {
    try {
      setLoading(true);
      const res = await api.get('/dispositions', { params: { page, page_size: 15 } });
      setDispositions(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMovements = async () => {
    try {
      setLoading(true);
      const res = await api.get('/dispositions/movements', { params: { page, page_size: 15 } });
      setMovements(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'dispositions') {
      fetchDispositions();
    } else {
      fetchMovements();
    }
  }, [activeTab, page]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Inventory Disposition & Movements</h1>
        <p className="text-xs text-slate-500 mt-1">
          Traceable physical routing into Restock, Refurbish, Quarantine, or Scrap with auditable stock transactions.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 gap-6 text-xs font-semibold">
        <button
          onClick={() => {
            setActiveTab('dispositions');
            setPage(1);
          }}
          className={`pb-3 border-b-2 flex items-center gap-1.5 transition-colors ${
            activeTab === 'dispositions' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Boxes className="w-4 h-4" />
          Disposition Decisions
        </button>

        <button
          onClick={() => {
            setActiveTab('movements');
            setPage(1);
          }}
          className={`pb-3 border-b-2 flex items-center gap-1.5 transition-colors ${
            activeTab === 'movements' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <ArrowRightLeft className="w-4 h-4 text-indigo-600" />
          Stock Movements Ledger
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        {activeTab === 'dispositions' ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                  <th className="py-3 px-4">Disposition ID</th>
                  <th className="py-3 px-4">Return Line</th>
                  <th className="py-3 px-4">Product Name</th>
                  <th className="py-3 px-4">Inspection ID</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Quantity</th>
                  <th className="py-3 px-4">Warehouse Location</th>
                  <th className="py-3 px-4">Technician</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={10} className="text-center py-12 text-slate-400">
                      <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                      Loading dispositions...
                    </td>
                  </tr>
                ) : dispositions.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="text-center py-12 text-slate-500">
                      No disposition records found.
                    </td>
                  </tr>
                ) : (
                  dispositions.map((d) => (
                    <tr key={d.id} className="hover:bg-slate-50/50">
                      <td className="py-3 px-4 font-mono font-medium text-slate-900">{d.disposition_id}</td>
                      <td className="py-3 px-4 font-mono text-blue-600 font-medium">{d.return_line_id}</td>
                      <td className="py-3 px-4 font-medium text-slate-800">{d.product_name || '-'}</td>
                      <td className="py-3 px-4 font-mono text-slate-500">{d.inspection_id || 'N/A'}</td>
                      <td className="py-3 px-4">
                        <Badge variant={getStatusBadgeVariant(d.disposition_type)}>{d.disposition_type}</Badge>
                      </td>
                      <td className="py-3 px-4 font-semibold text-slate-900">{d.quantity}</td>
                      <td className="py-3 px-4 font-mono text-slate-600">{d.warehouse_location}</td>
                      <td className="py-3 px-4 text-slate-600">{d.technician_id}</td>
                      <td className="py-3 px-4">
                        <Badge variant="success">COMPLETED</Badge>
                      </td>
                      <td className="py-3 px-4 text-slate-500">{new Date(d.date).toLocaleString()}</td>
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
                  <th className="py-3 px-4">Movement ID</th>
                  <th className="py-3 px-4">Product SKU</th>
                  <th className="py-3 px-4">Product Name</th>
                  <th className="py-3 px-4">Movement Type</th>
                  <th className="py-3 px-4">Quantity</th>
                  <th className="py-3 px-4">From Location</th>
                  <th className="py-3 px-4">To Location</th>
                  <th className="py-3 px-4">Reference ID</th>
                  <th className="py-3 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={9} className="text-center py-12 text-slate-400">
                      <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                      Loading movements...
                    </td>
                  </tr>
                ) : movements.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="text-center py-12 text-slate-500">
                      No inventory movements recorded.
                    </td>
                  </tr>
                ) : (
                  movements.map((m) => (
                    <tr key={m.id} className="hover:bg-slate-50/50">
                      <td className="py-3 px-4 font-mono font-medium text-slate-900">{m.movement_id}</td>
                      <td className="py-3 px-4 font-mono text-slate-600">{m.product_sku}</td>
                      <td className="py-3 px-4 font-medium text-slate-800">{m.product_name}</td>
                      <td className="py-3 px-4">
                        <span className="font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded text-[11px]">
                          {m.movement_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-bold text-slate-900">{m.quantity}</td>
                      <td className="py-3 px-4 text-slate-600">{m.from_location}</td>
                      <td className="py-3 px-4 font-mono text-slate-800 font-medium">{m.to_location}</td>
                      <td className="py-3 px-4 font-mono text-slate-500">{m.reference_id}</td>
                      <td className="py-3 px-4 text-slate-500">{new Date(m.timestamp).toLocaleString()}</td>
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
