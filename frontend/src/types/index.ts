export interface DashboardCards {
  total_orders: number;
  return_requests: number;
  return_rate_percent: number;
  eligible_requests: number;
  rejected_requests: number;
  pending_review_requests: number;
  pending_inspections: number;
  refund_amount: number;
  blocked_duplicate_refunds: number;
  detected_anomalies: number;
  total_anomalies: number;
  validation_pass_rate: number;
  validation_overall_status: string;
}

export interface DashboardSummaryResponse {
  cards: DashboardCards;
  disposition_breakdown: Record<string, number>;
  recent_returns: Array<{
    id: number;
    rma_number: string;
    order_id: string;
    customer_name: string;
    status: string;
    overall_eligibility: string;
    requested_date: string;
  }>;
}

export interface Customer {
  id: number;
  customer_id: string;
  name: string;
  email: string;
  phone?: string;
  segment: string;
  risk_score: number;
  orders_count: number;
  created_at: string;
}

export interface OrderItem {
  id: number;
  order_id: string;
  customer_id: string;
  customer_name: string;
  order_date: string;
  delivery_date?: string;
  status: string;
  subtotal: number;
  discount_amount: number;
  tax_amount: number;
  shipping_amount: number;
  total_amount: number;
  payment_method: string;
  lines_count: number;
  returns_count: number;
}

export interface OrderLineDetail {
  id: number;
  line_number: number;
  product_id: number;
  sku: string;
  product_name: string;
  category: string;
  quantity: number;
  unit_price: number;
  line_subtotal: number;
  allocated_discount: number;
  line_tax: number;
  total_line_amount: number;
  returned_quantity: number;
  available_quantity: number;
  is_returnable: boolean;
  return_window_days: number;
}

export interface OrderDetail extends OrderItem {
  shipping_address?: string;
  customer?: {
    customer_id: string;
    name: string;
    email: string;
    phone?: string;
    segment: string;
  };
  lines: OrderLineDetail[];
  return_requests: Array<{
    id: number;
    rma_number: string;
    status: string;
    overall_eligibility: string;
    requested_date: string;
  }>;
}

export interface ReturnListItem {
  id: number;
  rma_number: string;
  order_id: string;
  customer_id: string;
  customer_name: string;
  status: string;
  overall_eligibility: string;
  requested_date: string;
  channel: string;
  reason_category: string;
  lines_count: number;
  has_authorization: boolean;
  shipments_count: number;
  refunds_count: number;
}

export interface ReturnLineDetail {
  id: number;
  return_line_id: string;
  product_id: number;
  sku: string;
  name: string;
  category: string;
  requested_quantity: number;
  eligible_quantity: number;
  approved_quantity: number;
  rejected_quantity: number;
  eligibility_status: string;
  ineligibility_reason?: string;
  policy_code_applied?: string;
  override_approved: boolean;
  override_reason?: string;
  override_by?: string;
  estimated_refund_amount: number;
  actual_refund_amount: number;
  disposition_status: string;
  inspections: Array<{
    inspection_id: string;
    item_condition: string;
    packaging_condition: string;
    result: string;
    damage_type: string;
    recommended_disposition: string;
    inspector_id: string;
    timestamp: string;
  }>;
  dispositions: Array<{
    disposition_id: string;
    disposition_type: string;
    quantity: number;
    warehouse_location: string;
    status: string;
    date: string;
  }>;
}

export interface ReturnLifecycleDetail {
  id: number;
  rma_number: string;
  status: string;
  overall_eligibility: string;
  requested_date: string;
  channel: string;
  reason_category: string;
  customer_comments?: string;
  order?: {
    order_id: string;
    order_date: string;
    delivery_date?: string;
    total_amount: number;
  };
  customer?: {
    customer_id: string;
    name: string;
    email: string;
    segment: string;
  };
  authorization?: {
    authorization_number: string;
    authorized_date: string;
    authorized_by: string;
    authorized_quantity: number;
    status: string;
    valid_until: string;
  };
  lines: ReturnLineDetail[];
  shipments: Array<{
    id: number;
    shipment_id: string;
    carrier: string;
    tracking_number: string;
    status: string;
    shipped_date?: string;
    received_date?: string;
    destination_warehouse: string;
    inspections_count: number;
  }>;
  refunds: Array<{
    id: number;
    refund_id: string;
    idempotency_key: string;
    refund_method: string;
    base_unit_refund: number;
    tax_refund: number;
    restocking_fee_deducted: number;
    net_refund_amount: number;
    status: string;
    processed_at: string;
    gateway_reference: string;
  }>;
  audit_timeline: Array<{
    event_id: string;
    entity_type: string;
    entity_id: string;
    event_type: string;
    previous_state?: string;
    new_state?: string;
    actor: string;
    reason?: string;
    timestamp: string;
  }>;
}

export interface ShipmentItem {
  id: number;
  shipment_id: string;
  rma_number: string;
  carrier: string;
  tracking_number: string;
  status: string;
  shipped_date?: string;
  received_date?: string;
  destination_warehouse: string;
  inspections_count: number;
  created_at: string;
}

export interface InspectionItem {
  id: number;
  inspection_id: string;
  shipment_id: string;
  return_line_id: string;
  product_name: string;
  inspected_quantity: number;
  item_condition: string;
  packaging_condition: string;
  result: string;
  damage_type: string;
  missing_components?: string;
  notes?: string;
  inspector_id: string;
  recommended_disposition: string;
  timestamp: string;
}

export interface RefundItem {
  id: number;
  refund_id: string;
  rma_number: string;
  return_line_id?: string;
  idempotency_key: string;
  refund_method: string;
  base_unit_refund: number;
  tax_refund: number;
  shipping_refund: number;
  restocking_fee_deducted: number;
  net_refund_amount: number;
  status: string;
  processed_at: string;
  gateway_reference: string;
}

export interface RefundAttemptItem {
  id: number;
  refund_id?: string;
  rma_number?: string;
  idempotency_key: string;
  requested_amount: number;
  outcome: string;
  reason: string;
  timestamp: string;
}

export interface DispositionItem {
  id: number;
  disposition_id: string;
  return_line_id: string;
  product_name?: string;
  inspection_id?: string;
  disposition_type: string;
  quantity: number;
  warehouse_location: string;
  status: string;
  technician_id: string;
  notes?: string;
  date: string;
}

export interface MovementItem {
  id: number;
  movement_id: string;
  product_sku: string;
  product_name: string;
  movement_type: string;
  quantity: number;
  from_location: string;
  to_location: string;
  reference_id: string;
  timestamp: string;
}

export interface ValidationReport {
  overall_status: string;
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  warning_checks: number;
  total_violations: number;
  timestamp: string;
  checks: Array<{
    check_name: string;
    status: string;
    description: string;
    violations_count: number;
    sample_violations: string[];
  }>;
}

export interface EvaluationMetrics {
  timestamp: string;
  total_records_processed: number;
  valid_records: number;
  invalid_records: number;
  total_anomalies: number;
  detected_anomalies: number;
  missed_anomalies: number;
  false_positives: number;
  precision: number;
  recall: number;
  f1_score: number;
  detection_rate_by_issue_type: Record<string, { total: number; detected: number; rate: number }>;
  eligibility_decision_accuracy: number;
  refund_reconciliation_pass_rate: number;
  duplicate_refund_prevention_rate: number;
  inventory_disposition_compliance_rate: number;
  referential_integrity_pass_rate: number;
}

