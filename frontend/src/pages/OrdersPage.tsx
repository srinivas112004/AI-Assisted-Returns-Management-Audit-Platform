import React, { useEffect, useState } from 'react';
import { Search, ShoppingCart, RefreshCw, Eye, ArrowRight } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import api from '../api/client';
import { OrderItem, OrderDetail } from '../types';
import { Badge, getStatusBadgeVariant } from '../components/Badge';
import { Pagination } from '../components/Pagination';
import { Modal } from '../components/Modal';

export const OrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<OrderItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Selected Order Detail Modal
  const [selectedOrder, setSelectedOrder] = useState<OrderDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const res = await api.get('/orders', {
        params: {
          page,
          page_size: 15,
          search: search || undefined,
          status: statusFilter || undefined,
        },
      });
      setOrders(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [page, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchOrders();
  };

  const viewOrderDetail = async (orderId: string) => {
    try {
      setDetailLoading(true);
      const res = await api.get<OrderDetail>(`/orders/${orderId}`);
      setSelectedOrder(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Orders Explorer</h1>
          <p className="text-xs text-slate-500 mt-1">
            Browse customer purchase orders, line item items, delivery status, and historical returns.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="flex-1 max-w-md relative">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search Order ID (e.g. ORD-2026-000001)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white transition-colors"
          />
        </form>

        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="DELIVERED">DELIVERED</option>
            <option value="PARTIALLY_RETURNED">PARTIALLY_RETURNED</option>
            <option value="FULLY_RETURNED">FULLY_RETURNED</option>
            <option value="PENDING">PENDING</option>
          </select>

          <button
            onClick={fetchOrders}
            className="p-1.5 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-3 px-4">Order ID</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Order Date</th>
                <th className="py-3 px-4">Delivery Date</th>
                <th className="py-3 px-4">Total Amount</th>
                <th className="py-3 px-4">Lines</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                    Loading orders...
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-slate-500">
                    No orders found matching the filter criteria.
                  </td>
                </tr>
              ) : (
                orders.map((o) => (
                  <tr key={o.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-slate-900">{o.order_id}</td>
                    <td className="py-3 px-4">
                      <span className="font-medium text-slate-800 block">{o.customer_name}</span>
                      <span className="text-[10px] text-slate-400 font-mono">{o.customer_id}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-500">{new Date(o.order_date).toLocaleDateString()}</td>
                    <td className="py-3 px-4 text-slate-500">
                      {o.delivery_date ? new Date(o.delivery_date).toLocaleDateString() : 'Pending'}
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-900">
                      ${o.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      {o.lines_count} item{o.lines_count > 1 ? 's' : ''}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant={getStatusBadgeVariant(o.status)}>{o.status}</Badge>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => viewOrderDetail(o.order_id)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-blue-600 hover:text-blue-700 bg-blue-50/60 hover:bg-blue-100/60 rounded border border-blue-200 transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        View
                      </button>
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

      {/* Order Detail Modal */}
      <Modal
        isOpen={selectedOrder !== null}
        onClose={() => setSelectedOrder(null)}
        title={selectedOrder ? `Order Details: ${selectedOrder.order_id}` : 'Order Details'}
      >
        {selectedOrder && (
          <div className="space-y-5 text-xs">
            {/* Header metadata */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
              <div>
                <span className="text-[11px] text-slate-400 block">Customer</span>
                <span className="font-semibold text-slate-800">{selectedOrder.customer?.name}</span>
                <span className="text-[10px] text-slate-500 block">{selectedOrder.customer?.segment}</span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Order Date</span>
                <span className="font-medium text-slate-700">{new Date(selectedOrder.order_date).toLocaleDateString()}</span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Delivery Date</span>
                <span className="font-medium text-slate-700">
                  {selectedOrder.delivery_date ? new Date(selectedOrder.delivery_date).toLocaleDateString() : 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Total Amount</span>
                <span className="font-bold text-slate-900">${selectedOrder.total_amount.toFixed(2)}</span>
              </div>
            </div>

            {/* Line Items */}
            <div>
              <h4 className="font-semibold text-slate-800 mb-2">Purchased Order Lines</h4>
              <div className="border border-slate-200 rounded-lg overflow-hidden">
                <table className="w-full text-left">
                  <thead className="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <tr>
                      <th className="p-2">Item</th>
                      <th className="p-2">Category</th>
                      <th className="p-2">Qty</th>
                      <th className="p-2">Unit Price</th>
                      <th className="p-2">Net Paid</th>
                      <th className="p-2">Available to Return</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {selectedOrder.lines.map((l) => (
                      <tr key={l.id}>
                        <td className="p-2">
                          <span className="font-medium text-slate-900 block">{l.product_name}</span>
                          <span className="text-[10px] text-slate-400 font-mono">{l.sku}</span>
                        </td>
                        <td className="p-2 text-slate-600">{l.category}</td>
                        <td className="p-2 font-medium">{l.quantity}</td>
                        <td className="p-2">${l.unit_price.toFixed(2)}</td>
                        <td className="p-2 font-semibold text-slate-900">${l.total_line_amount.toFixed(2)}</td>
                        <td className="p-2">
                          {l.available_quantity > 0 ? (
                            <span className="text-emerald-600 font-semibold">{l.available_quantity} available</span>
                          ) : (
                            <span className="text-slate-400">0 left</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Existing RMAs on this order */}
            {selectedOrder.return_requests.length > 0 && (
              <div>
                <h4 className="font-semibold text-slate-800 mb-2">Existing Return Requests (RMAs)</h4>
                <div className="space-y-1.5">
                  {selectedOrder.return_requests.map((r) => (
                    <div
                      key={r.id}
                      className="flex items-center justify-between p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-medium text-blue-600">{r.rma_number}</span>
                        <Badge variant={getStatusBadgeVariant(r.overall_eligibility)}>
                          {r.overall_eligibility}
                        </Badge>
                      </div>
                      <NavLink
                        to={`/returns/${r.rma_number}`}
                        className="text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
                      >
                        View RMA Lifecycle &rarr;
                      </NavLink>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedOrder(null)}
                className="px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
