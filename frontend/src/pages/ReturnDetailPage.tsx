import React, { useEffect, useState } from 'react';
import { useParams, NavLink } from 'react-router-dom';
import {
  ArrowLeft,
  CheckCircle2,
  Clock,
  ShieldCheck,
  Truck,
  ClipboardCheck,
  CreditCard,
  Boxes,
  AlertCircle,
  RefreshCw,
  Plus,
  ShieldAlert,
  History,
} from 'lucide-react';
import api from '../api/client';
import { ReturnLifecycleDetail } from '../types';
import { Badge, getStatusBadgeVariant } from '../components/Badge';
import { Modal } from '../components/Modal';

export const ReturnDetailPage: React.FC = () => {
  const { rmaNumber } = useParams<{ rmaNumber: string }>();
  const [data, setData] = useState<ReturnLifecycleDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  // Modals state
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isShipModalOpen, setIsShipModalOpen] = useState(false);
  const [isInspModalOpen, setIsInspModalOpen] = useState(false);
  const [isRefundModalOpen, setIsRefundModalOpen] = useState(false);
  const [isDispModalOpen, setIsDispModalOpen] = useState(false);
  const [isOverrideModalOpen, setIsOverrideModalOpen] = useState(false);

  // Form states
  const [selectedLineId, setSelectedLineId] = useState<string>('');
  const [carrier, setCarrier] = useState('UPS');
  const [itemCondition, setItemCondition] = useState('OPENED_LIKE_NEW');
  const [pkgCondition, setPkgCondition] = useState('INTACT');
  const [damageType, setDamageType] = useState('NONE');
  const [dispType, setDispType] = useState('RESTOCK');
  const [dispLocation, setDispLocation] = useState('WH-BIN-A12');
  const [overrideReason, setOverrideReason] = useState('Customer goodwill courtesy approved by supervisor');
  const [overrideBy, setOverrideBy] = useState('MGR_DESK_01');
  const [idempotencyKey, setIdempotencyKey] = useState('');
  const [applyRestockFee, setApplyRestockFee] = useState(false);

  const fetchDetail = async () => {
    if (!rmaNumber) return;
    try {
      setLoading(true);
      setError(null);
      const res = await api.get<ReturnLifecycleDetail>(`/returns/${rmaNumber}`);
      setData(res.data);
      if (res.data.lines.length > 0) {
        setSelectedLineId(res.data.lines[0].return_line_id);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to fetch RMA details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [rmaNumber]);

  // Actions
  const handleReevaluate = async () => {
    if (!rmaNumber) return;
    try {
      await api.post(`/returns/${rmaNumber}/evaluate`);
      setActionMessage('Return request re-evaluated against latest policy rules.');
      fetchDetail();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message);
    }
  };

  const handleAuthorize = async () => {
    if (!rmaNumber) return;
    try {
      await api.post(`/returns/${rmaNumber}/authorize`, {
        authorized_by: 'SUPERVISOR_CONSOLE',
        validity_days: 14,
      });
      setIsAuthModalOpen(false);
      setActionMessage('Return request successfully authorized.');
      fetchDetail();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message);
    }
  };

  const handleCreateShipment = async () => {
    if (!rmaNumber) return;
    try {
      await api.post(`/returns/${rmaNumber}/shipments`, {
        carrier,
        destination_warehouse: 'WH-CENTRAL-01',
      });
      setIsShipModalOpen(false);
      setActionMessage('Return shipment label generated and parcel placed IN_TRANSIT.');
      fetchDetail();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message);
    }
  };

  const handleReceiveShipment = async (shipmentId: string) => {
    try {
      await api.post(`/shipments/${shipmentId}/receive`, {
        receiver_id: 'DOCK_STATION_A',
      });
      setActionMessage(`Shipment ${shipmentId} marked received at warehouse intake dock.`);
      fetchDetail();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message);
    }
  };

  const handleRecordInspection = async (shipmentId: string) => {
    try {
      await api.post(`/shipments/${shipmentId}/inspect`, {
        return_line_id: selectedLineId,
        inspected_quantity: 1,
        item_condition: itemCondition,
        packaging_condition: pkgCondition,
        damage_type: damageType,
        inspector_id: 'INSPECTOR_QA_01',
      });
      setIsInspModalOpen(false);
      setActionMessage('Warehouse inspection successfully recorded and outcome verified.');
      fetchDetail();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message);
    }
  };

  const handleExecuteDisposition = async () => {
    if (!rmaNumber) return;
    try {
      await api.post(`/returns/${rmaNumber}/disposition`, {
        return_line_id: selectedLineId,
        disposition_type: dispType,
        quantity: 1,
        warehouse_location: dispLocation,
        technician_id: 'TECH_ROUTING_01',
      });
      setIsDispModalOpen(false);
      setActionMessage(`Inventory disposition executed: ${dispType} routed to ${dispLocation}.`);
      fetchDetail();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message);
    }
  };

  const handleProcessRefund = async (isDuplicateTest = false) => {
    if (!rmaNumber) return;
    try {
      const key = isDuplicateTest
        ? (data?.refunds[0]?.idempotency_key || `IDEMP-TEST-${rmaNumber}`)
        : (idempotencyKey || `IDEMP-${Date.now()}-${rmaNumber}`);

      const res = await api.post(`/returns/${rmaNumber}/refund`, {
        idempotency_key: key,
        return_line_id: selectedLineId,
        refund_method: 'ORIGINAL_PAYMENT',
        apply_restocking_fee: applyRestockFee,
      });

      setIsRefundModalOpen(false);
      if (res.data.blocked) {
        setActionMessage(`[SAFEGUARD TRIGGERED] Duplicate refund blocked! Idempotency key '${key}' already settled.`);
      } else {
        setActionMessage(`Refund of $${res.data.net_refund_amount.toFixed(2)} disbursed successfully.`);
      }
      fetchDetail();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message);
    }
  };

  const handleApplyOverride = async () => {
    if (!rmaNumber) return;
    try {
      await api.post(`/returns/${rmaNumber}/override-line`, {
        override_by: overrideBy,
        override_reason: overrideReason,
      }, {
        params: { return_line_id: selectedLineId },
      });
      setIsOverrideModalOpen(false);
      setActionMessage(`Exception override granted for line ${selectedLineId}.`);
      fetchDetail();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-2">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
          <span className="text-xs text-slate-500 font-medium">Loading lifecycle records...</span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 max-w-4xl mx-auto">
        <p className="font-semibold text-sm">Failed to load Return Request.</p>
        <p className="text-xs mt-1 text-rose-600">{error}</p>
        <NavLink
          to="/returns"
          className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-600 text-white rounded text-xs font-medium hover:bg-rose-700"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Returns Queue
        </NavLink>
      </div>
    );
  }

  const activeShipment = data.shipments[0];
  const activeRefund = data.refunds[0];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Navigation & Status Banner */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <NavLink
            to="/returns"
            className="p-1.5 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg text-slate-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </NavLink>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-bold font-mono text-slate-900 tracking-tight">{data.rma_number}</h1>
              <Badge variant={getStatusBadgeVariant(data.overall_eligibility)}>
                {data.overall_eligibility}
              </Badge>
              <Badge variant={getStatusBadgeVariant(data.status)}>{data.status}</Badge>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Order: <span className="font-mono text-slate-700 font-medium">{data.order?.order_id}</span> &bull; Customer:{' '}
              <span className="text-slate-700 font-medium">{data.customer?.name}</span> ({data.customer?.customer_id})
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReevaluate}
            className="inline-flex items-center gap-1 px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-medium transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Re-evaluate Rules
          </button>
        </div>
      </div>

      {actionMessage && (
        <div className="p-3 bg-blue-50 border border-blue-200 text-blue-800 rounded-xl text-xs font-medium flex items-center justify-between">
          <span>{actionMessage}</span>
          <button onClick={() => setActionMessage(null)} className="text-blue-500 hover:text-blue-700">
            &times;
          </button>
        </div>
      )}

      {/* Complete Lifecycle Stepper / Interactive Timeline */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-6">
          Reverse Logistics Lifecycle Pipeline
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-7 gap-3 relative">
          {/* Step 1: Request */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/50 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-1.5 text-slate-900 font-semibold text-xs mb-1">
                <span className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px]">1</span>
                <span>Request</span>
              </div>
              <p className="text-[11px] text-slate-500">{data.reason_category}</p>
              <p className="text-[10px] text-slate-400 mt-1">{new Date(data.requested_date).toLocaleDateString()}</p>
            </div>
            <span className="mt-3 text-[10px] text-emerald-600 font-medium flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> Submitted
            </span>
          </div>

          {/* Step 2: Eligibility */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/50 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-1.5 text-slate-900 font-semibold text-xs mb-1">
                <span className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px]">2</span>
                <span>Eligibility</span>
              </div>
              <p className="text-[11px] font-medium text-slate-700">{data.overall_eligibility}</p>
              {data.lines.some((l) => l.eligibility_status === 'INELIGIBLE') && (
                <button
                  onClick={() => setIsOverrideModalOpen(true)}
                  className="mt-2 text-[10px] text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 px-2 py-0.5 rounded font-medium block"
                >
                  Apply Override
                </button>
              )}
            </div>
            <span className="mt-3 text-[10px] text-slate-500 font-medium">Policy evaluated</span>
          </div>

          {/* Step 3: Authorization */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/50 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-1.5 text-slate-900 font-semibold text-xs mb-1">
                <span className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px]">3</span>
                <span>Authorization</span>
              </div>
              {data.authorization ? (
                <div>
                  <span className="text-[10px] font-mono text-blue-600 block">{data.authorization.authorization_number}</span>
                  <span className="text-[10px] text-slate-500">{data.authorization.authorized_quantity} units approved</span>
                </div>
              ) : (
                <button
                  onClick={() => setIsAuthModalOpen(true)}
                  disabled={data.overall_eligibility === 'INELIGIBLE'}
                  className="mt-1 text-[11px] px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium disabled:opacity-40"
                >
                  Authorize RMA
                </button>
              )}
            </div>
            <span className="mt-3 text-[10px] font-medium text-slate-600">
              {data.authorization ? 'Authorized' : 'Awaiting Auth'}
            </span>
          </div>

          {/* Step 4: Shipment */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/50 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-1.5 text-slate-900 font-semibold text-xs mb-1">
                <span className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px]">4</span>
                <span>Shipment</span>
              </div>
              {activeShipment ? (
                <div>
                  <span className="text-[10px] font-mono text-slate-800 block">{activeShipment.carrier} - {activeShipment.tracking_number}</span>
                  <Badge variant={getStatusBadgeVariant(activeShipment.status)} size="sm">
                    {activeShipment.status}
                  </Badge>
                  {activeShipment.status !== 'DELIVERED' && (
                    <button
                      onClick={() => handleReceiveShipment(activeShipment.shipment_id)}
                      className="mt-2 text-[10px] bg-emerald-600 hover:bg-emerald-700 text-white px-2 py-0.5 rounded font-medium block"
                    >
                      Receive at Dock
                    </button>
                  )}
                </div>
              ) : (
                <button
                  onClick={() => setIsShipModalOpen(true)}
                  disabled={!data.authorization}
                  className="mt-1 text-[11px] px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium disabled:opacity-40"
                >
                  Create Shipment
                </button>
              )}
            </div>
            <span className="mt-3 text-[10px] text-slate-500 font-medium">Logistics</span>
          </div>

          {/* Step 5: Inspection */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/50 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-1.5 text-slate-900 font-semibold text-xs mb-1">
                <span className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px]">5</span>
                <span>Inspection</span>
              </div>
              {data.lines.some((l) => l.inspections.length > 0) ? (
                <div>
                  <Badge variant={getStatusBadgeVariant(data.lines[0].inspections[0].result)} size="sm">
                    {data.lines[0].inspections[0].result}
                  </Badge>
                  <span className="text-[10px] text-slate-500 block mt-1">
                    Rec: <strong>{data.lines[0].inspections[0].recommended_disposition}</strong>
                  </span>
                </div>
              ) : (
                <button
                  onClick={() => setIsInspModalOpen(true)}
                  disabled={!activeShipment || activeShipment.status !== 'DELIVERED'}
                  className="mt-1 text-[11px] px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium disabled:opacity-40"
                  title={activeShipment?.status !== 'DELIVERED' ? 'Shipment must be received before inspection' : ''}
                >
                  Record QA
                </button>
              )}
            </div>
            <span className="mt-3 text-[10px] text-slate-500 font-medium">QA Bay</span>
          </div>

          {/* Step 6: Disposition */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/50 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-1.5 text-slate-900 font-semibold text-xs mb-1">
                <span className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px]">6</span>
                <span>Disposition</span>
              </div>
              {data.lines.some((l) => l.dispositions.length > 0) ? (
                <div>
                  <Badge variant={getStatusBadgeVariant(data.lines[0].dispositions[0].disposition_type)} size="sm">
                    {data.lines[0].dispositions[0].disposition_type}
                  </Badge>
                  <span className="text-[10px] text-slate-400 block font-mono mt-1">
                    {data.lines[0].dispositions[0].warehouse_location}
                  </span>
                </div>
              ) : (
                <button
                  onClick={() => setIsDispModalOpen(true)}
                  disabled={!data.lines.some((l) => l.inspections.length > 0)}
                  className="mt-1 text-[11px] px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium disabled:opacity-40"
                  title="Requires completed inspection before disposition"
                >
                  Route Stock
                </button>
              )}
            </div>
            <span className="mt-3 text-[10px] text-slate-500 font-medium">Inventory Movement</span>
          </div>

          {/* Step 7: Refund */}
          <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/50 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-1.5 text-slate-900 font-semibold text-xs mb-1">
                <span className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px]">7</span>
                <span>Refund</span>
              </div>
              {activeRefund ? (
                <div>
                  <span className="font-bold text-slate-900 block text-xs">${activeRefund.net_refund_amount.toFixed(2)}</span>
                  <Badge variant="success" size="sm">Disbursed</Badge>
                  <button
                    onClick={() => handleProcessRefund(true)}
                    className="mt-2 text-[10px] text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 px-2 py-0.5 rounded font-medium block"
                    title="Simulate idempotency duplicate prevention"
                  >
                    Test Dup Payout
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setIsRefundModalOpen(true)}
                  disabled={!data.authorization}
                  className="mt-1 text-[11px] px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium disabled:opacity-40"
                >
                  Issue Refund
                </button>
              )}
            </div>
            <span className="mt-3 text-[10px] text-slate-500 font-medium">Reconciliation</span>
          </div>
        </div>
      </div>

      {/* Return Lines Breakdown */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Return Line Items</h3>
            <p className="text-xs text-slate-500">Itemized policy evaluation and financial tracking</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-2.5 px-4">Line ID</th>
                <th className="py-2.5 px-4">Product</th>
                <th className="py-2.5 px-4">Requested</th>
                <th className="py-2.5 px-4">Approved</th>
                <th className="py-2.5 px-4">Policy Code</th>
                <th className="py-2.5 px-4">Eligibility</th>
                <th className="py-2.5 px-4">Reason / Notes</th>
                <th className="py-2.5 px-4">Est. Refund</th>
                <th className="py-2.5 px-4">Actual Refund</th>
                <th className="py-2.5 px-4">Disposition</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.lines.map((l) => (
                <tr key={l.id} className="hover:bg-slate-50/50">
                  <td className="py-2.5 px-4 font-mono font-medium text-slate-800">{l.return_line_id}</td>
                  <td className="py-2.5 px-4">
                    <span className="font-medium text-slate-900 block">{l.name}</span>
                    <span className="text-[10px] text-slate-400 font-mono">{l.sku}</span>
                  </td>
                  <td className="py-2.5 px-4">{l.requested_quantity}</td>
                  <td className="py-2.5 px-4 font-semibold text-slate-900">{l.approved_quantity}</td>
                  <td className="py-2.5 px-4 font-mono text-slate-600">{l.policy_code_applied || 'POL-STD-30'}</td>
                  <td className="py-2.5 px-4">
                    <Badge variant={getStatusBadgeVariant(l.eligibility_status)}>
                      {l.eligibility_status}
                    </Badge>
                  </td>
                  <td className="py-2.5 px-4 text-slate-600 max-w-xs truncate">
                    {l.ineligibility_reason || (l.override_approved ? `Override: ${l.override_reason}` : 'Compliant with policy')}
                  </td>
                  <td className="py-2.5 px-4 font-medium text-slate-800">${l.estimated_refund_amount.toFixed(2)}</td>
                  <td className="py-2.5 px-4 font-bold text-emerald-600">${l.actual_refund_amount.toFixed(2)}</td>
                  <td className="py-2.5 px-4">
                    <Badge variant={getStatusBadgeVariant(l.disposition_status)} size="sm">
                      {l.disposition_status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Append-Only Audit History Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-slate-500" />
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Immutable Audit Trail</h3>
              <p className="text-xs text-slate-500">Append-only lifecycle event log for governance and compliance</p>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
                <th className="py-2.5 px-4">Event ID</th>
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Entity</th>
                <th className="py-2.5 px-4">Event Type</th>
                <th className="py-2.5 px-4">Actor</th>
                <th className="py-2.5 px-4">State Transition</th>
                <th className="py-2.5 px-4">Reason / Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.audit_timeline.map((e) => (
                <tr key={e.event_id} className="hover:bg-slate-50/50">
                  <td className="py-2.5 px-4 font-mono text-slate-600">{e.event_id}</td>
                  <td className="py-2.5 px-4 text-slate-500">{new Date(e.timestamp).toLocaleString()}</td>
                  <td className="py-2.5 px-4">
                    <span className="font-medium text-slate-800">{e.entity_type}</span>
                    <span className="text-[10px] text-slate-400 font-mono block">{e.entity_id}</span>
                  </td>
                  <td className="py-2.5 px-4 font-semibold text-blue-600">{e.event_type}</td>
                  <td className="py-2.5 px-4 text-slate-700 font-mono text-[11px]">{e.actor}</td>
                  <td className="py-2.5 px-4 text-slate-600">
                    {e.previous_state ? <span>{e.previous_state} &rarr; </span> : null}
                    <strong className="text-slate-900">{e.new_state || 'N/A'}</strong>
                  </td>
                  <td className="py-2.5 px-4 text-slate-500">{e.reason || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modals for actions */}
      {/* 1. Authorize Modal */}
      <Modal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} title="Issue Return Authorization">
        <div className="space-y-4 text-xs">
          <p className="text-slate-600">
            Confirm issuance of Return Authorization token (RMA-AUTH-2026-XXXXXX) for eligible line quantities.
          </p>
          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={() => setIsAuthModalOpen(false)}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleAuthorize}
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
            >
              Confirm Authorization
            </button>
          </div>
        </div>
      </Modal>

      {/* 2. Create Shipment Modal */}
      <Modal isOpen={isShipModalOpen} onClose={() => setIsShipModalOpen(false)} title="Generate Return Shipment">
        <div className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Carrier</label>
            <select
              value={carrier}
              onChange={(e) => setCarrier(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
            >
              <option value="UPS">UPS Ground</option>
              <option value="FEDEX">FedEx Express Reverse</option>
              <option value="USPS">USPS Priority Return</option>
              <option value="DHL">DHL Parcel</option>
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={() => setIsShipModalOpen(false)}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleCreateShipment}
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
            >
              Generate Label & Dispatch
            </button>
          </div>
        </div>
      </Modal>

      {/* 3. Record Inspection Modal */}
      <Modal isOpen={isInspModalOpen} onClose={() => setIsInspModalOpen(false)} title="Warehouse Physical Inspection">
        <div className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Item Physical Condition</label>
            <select
              value={itemCondition}
              onChange={(e) => setItemCondition(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
            >
              <option value="UNOPENED">UNOPENED (Factory sealed)</option>
              <option value="OPENED_LIKE_NEW">OPENED_LIKE_NEW (Packaging open, item pristine)</option>
              <option value="SLIGHT_WEAR">SLIGHT_WEAR (Minor cosmetic marks)</option>
              <option value="SIGNIFICANT_DAMAGE">SIGNIFICANT_DAMAGE (Functional defect / impact)</option>
              <option value="DESTROYED">DESTROYED (Crushed / flooded / scrap)</option>
              <option value="COUNTERFEIT">COUNTERFEIT (Serial mismatch / suspected fraud)</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Packaging Condition</label>
            <select
              value={pkgCondition}
              onChange={(e) => setPkgCondition(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
            >
              <option value="INTACT">INTACT</option>
              <option value="DAMAGED_REPAIRABLE">DAMAGED_REPAIRABLE</option>
              <option value="MISSING">MISSING</option>
              <option value="DESTROYED">DESTROYED</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Damage Classification</label>
            <select
              value={damageType}
              onChange={(e) => setDamageType(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
            >
              <option value="NONE">NONE</option>
              <option value="COSMETIC">COSMETIC</option>
              <option value="ELECTRICAL">ELECTRICAL</option>
              <option value="WATER">WATER</option>
              <option value="IMPACT">IMPACT</option>
              <option value="PACKAGING_ONLY">PACKAGING_ONLY</option>
              <option value="TAMPERED">TAMPERED</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={() => setIsInspModalOpen(false)}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium"
            >
              Cancel
            </button>
            <button
              onClick={() => handleRecordInspection(activeShipment?.shipment_id || '')}
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
            >
              Save QA Inspection
            </button>
          </div>
        </div>
      </Modal>

      {/* 4. Execute Disposition Modal */}
      <Modal isOpen={isDispModalOpen} onClose={() => setIsDispModalOpen(false)} title="Execute Inventory Disposition">
        <div className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Disposition Routing</label>
            <select
              value={dispType}
              onChange={(e) => setDispType(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
            >
              <option value="RESTOCK">RESTOCK (Return to active sellable stock)</option>
              <option value="REFURBISH">REFURBISH (Route to technical repair bench)</option>
              <option value="QUARANTINE">QUARANTINE (Hold for investigation)</option>
              <option value="SCRAP">SCRAP (Write-off recycle / waste)</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Destination Warehouse Bin</label>
            <input
              type="text"
              value={dispLocation}
              onChange={(e) => setDispLocation(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={() => setIsDispModalOpen(false)}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleExecuteDisposition}
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
            >
              Execute Stock Movement
            </button>
          </div>
        </div>
      </Modal>

      {/* 5. Process Refund Modal */}
      <Modal isOpen={isRefundModalOpen} onClose={() => setIsRefundModalOpen(false)} title="Process Idempotent Customer Refund">
        <div className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Idempotency Key (Unique Transaction Token)</label>
            <input
              type="text"
              placeholder={`IDEMP-${Date.now()}-${rmaNumber}`}
              value={idempotencyKey}
              onChange={(e) => setIdempotencyKey(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg font-mono text-[11px]"
            />
            <p className="text-[10px] text-slate-400 mt-1">
              Guarantees single payment execution even if network calls or webhooks retry.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="applyFee"
              checked={applyRestockFee}
              onChange={(e) => setApplyRestockFee(e.target.checked)}
              className="rounded text-blue-600"
            />
            <label htmlFor="applyFee" className="text-slate-700 font-medium">
              Apply Restocking Fee (per category policy)
            </label>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={() => setIsRefundModalOpen(false)}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium"
            >
              Cancel
            </button>
            <button
              onClick={() => handleProcessRefund(false)}
              className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-semibold"
            >
              Confirm Disburse Refund
            </button>
          </div>
        </div>
      </Modal>

      {/* 6. Exception Override Modal */}
      <Modal isOpen={isOverrideModalOpen} onClose={() => setIsOverrideModalOpen(false)} title="Authorize Policy Exception Override">
        <div className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Supervisor Identifier</label>
            <input
              type="text"
              value={overrideBy}
              onChange={(e) => setOverrideBy(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg font-mono"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Authorized Exception Rationale</label>
            <textarea
              rows={2}
              value={overrideReason}
              onChange={(e) => setOverrideReason(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={() => setIsOverrideModalOpen(false)}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleApplyOverride}
              className="px-4 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold"
            >
              Approve Exception
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
