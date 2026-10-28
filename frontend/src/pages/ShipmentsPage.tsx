import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Truck, CheckCircle2, RefreshCw, Search } from 'lucide-react';
import api from '../api/client';
import { ShipmentItem } from '../types';
import { Badge, getStatusBadgeVariant } from '../components/Badge';
import { Pagination } from '../components/Pagination';

export const ShipmentsPage: React.FC = () => {
  const [shipments, setShipments] = useState<ShipmentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [carrierFilter, setCarrierFilter] = useState('');

  const fetchShipments = async () => {
    try {
      setLoading(true);
      const res = await api.get('/shipments', {
        params: {
          page,
          page_size: 15,
          search: search || undefined,
          status: statusFilter || undefined,
          carrier: carrierFilter || undefined,
        },
      });
      setShipments(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShipments();
  }, [page, statusFilter, carrierFilter]);

  const handleReceive = async (shipmentId: string) => {
    try {
      await api.post(`/shipments/${shipmentId}/receive`, {
        receiver_id: 'DOCK_STA_01',
      });
      fetchShipments();
    } catch (err: any) {
      alert(err?.response?.data?.detail || err?.message || 'Receive failed');
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Warehouse Reverse Logistics Shipments</h1>
        <p className="text-xs text-slate-500 mt-1">
          Monitor inbound return parcels across carriers, tracking IDs, dock intake scans, and delivery confirmation.
        </p>
      </div>

      {/* Toolbar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            setPage(1);
            fetchShipments();
          }}
          className="flex-1 max-w-sm relative"
        >
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search tracking or shipment ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </form>

        <div className="flex items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700"
          >
            <option value="">All Statuses</option>
            <option value="IN_TRANSIT">IN_TRANSIT</option>
            <option value="DELIVERED">DELIVERED</option>
            <option value="LABEL_CREATED">LABEL_CREATED</option>
            <option value="MISSING">MISSING</option>
          </select>

          <select
            value={carrierFilter}
            onChange={(e) => {
              setCarrierFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700"
          >
            <option value="">All Carriers</option>
            <option value="UPS">UPS</option>
            <option value="FEDEX">FedEx</option>
            <option value="USPS">USPS</option>
            <option value="DHL">DHL</option>
          </select>

          <button onClick={fetchShipments} className="p-1.5 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Shipments Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-3 px-4">Shipment ID</th>
                <th className="py-3 px-4">RMA Number</th>
                <th className="py-3 px-4">Carrier</th>
                <th className="py-3 px-4">Tracking Number</th>
                <th className="py-3 px-4">Shipped Date</th>
                <th className="py-3 px-4">Received Date</th>
                <th className="py-3 px-4">Warehouse</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                    Loading shipments...
                  </td>
                </tr>
              ) : shipments.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-slate-500">
                    No shipments found matching filter.
                  </td>
                </tr>
              ) : (
                shipments.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/50">
                    <td className="py-3 px-4 font-mono font-medium text-slate-900">{s.shipment_id}</td>
                    <td className="py-3 px-4 font-mono text-blue-600">
                      <NavLink to={`/returns/${s.rma_number}`} className="hover:underline">
                        {s.rma_number}
                      </NavLink>
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-700">{s.carrier}</td>
                    <td className="py-3 px-4 font-mono text-slate-600">{s.tracking_number}</td>
                    <td className="py-3 px-4 text-slate-500">{s.shipped_date ? new Date(s.shipped_date).toLocaleDateString() : '-'}</td>
                    <td className="py-3 px-4 text-slate-500">{s.received_date ? new Date(s.received_date).toLocaleDateString() : 'Awaiting arrival'}</td>
                    <td className="py-3 px-4 text-slate-600">{s.destination_warehouse}</td>
                    <td className="py-3 px-4">
                      <Badge variant={getStatusBadgeVariant(s.status)}>{s.status}</Badge>
                    </td>
                    <td className="py-3 px-4 text-right">
                      {s.status !== 'DELIVERED' ? (
                        <button
                          onClick={() => handleReceive(s.shipment_id)}
                          className="px-2.5 py-1 text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white rounded"
                        >
                          Receive Dock
                        </button>
                      ) : (
                        <NavLink
                          to={`/returns/${s.rma_number}`}
                          className="px-2.5 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded hover:bg-slate-50"
                        >
                          View RMA
                        </NavLink>
                      )}
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

