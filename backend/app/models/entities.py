from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    String, Integer, Numeric, Boolean, DateTime, ForeignKey, Text, Float, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

# 1. Customer
class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    segment: Mapped[str] = mapped_column(String(32), default="STANDARD", nullable=False) # STANDARD, VIP, WHOLESALE
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")
    return_requests: Mapped[List["ReturnRequest"]] = relationship("ReturnRequest", back_populates="customer")


# 2. Product
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True) # Electronics, Apparel, Home & Kitchen, Health & Personal Care, Perishable/Food
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_returnable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    default_return_window_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    restockable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_serial_number: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    order_lines: Mapped[List["OrderLine"]] = relationship("OrderLine", back_populates="product")


# 3. Return Policy
class ReturnPolicy(Base):
    __tablename__ = "return_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True) # POL-STD-30, POL-ELEC-14, POL-NON-RET
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    return_window_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    restocking_fee_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    requires_original_packaging: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_opened_box: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


# 4. Order
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True) # ORD-2026-000001
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="DELIVERED", nullable=False) # PENDING, PROCESSING, DELIVERED, CANCELLED, PARTIALLY_RETURNED, FULLY_RETURNED
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    shipping_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(32), default="CREDIT_CARD", nullable=False)
    shipping_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    lines: Mapped[List["OrderLine"]] = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")
    return_requests: Mapped[List["ReturnRequest"]] = relationship("ReturnRequest", back_populates="order")


# 5. OrderLine
class OrderLine(Base):
    __tablename__ = "order_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    line_subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    allocated_discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    line_tax: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    total_line_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    returned_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="lines")
    product: Mapped["Product"] = relationship("Product", back_populates="order_lines")
    return_lines: Mapped[List["ReturnLine"]] = relationship("ReturnLine", back_populates="order_line")


# 6. ReturnRequest (RMA)
class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rma_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True) # RMA-2026-000001
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="SUBMITTED", nullable=False) # DRAFT, SUBMITTED, ELIGIBILITY_PENDING, ELIGIBLE, PARTIALLY_ELIGIBLE, REJECTED, AUTHORIZED, IN_TRANSIT, RECEIVED, INSPECTED, PARTIALLY_REFUNDED, COMPLETED, CANCELLED
    overall_eligibility: Mapped[str] = mapped_column(String(32), default="PENDING_REVIEW", nullable=False) # FULLY_ELIGIBLE, PARTIALLY_ELIGIBLE, INELIGIBLE, PENDING_REVIEW
    requested_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), default="WEB", nullable=False) # WEB, MOBILE, SUPPORT_PORTAL, IN_STORE
    reason_category: Mapped[str] = mapped_column(String(64), nullable=False) # DEFECTIVE, WRONG_ITEM, SIZE_FIT, CHANGED_MIND, NOT_AS_DESCRIBED, ARRIVED_LATE, MISSING_PARTS
    customer_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="return_requests")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="return_requests")
    lines: Mapped[List["ReturnLine"]] = relationship("ReturnLine", back_populates="return_request", cascade="all, delete-orphan")
    authorization: Mapped[Optional["ReturnAuthorization"]] = relationship("ReturnAuthorization", back_populates="return_request", uselist=False)
    shipments: Mapped[List["ReturnShipment"]] = relationship("ReturnShipment", back_populates="return_request")
    refunds: Mapped[List["Refund"]] = relationship("Refund", back_populates="return_request")


# 7. ReturnLine
class ReturnLine(Base):
    __tablename__ = "return_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    return_line_id: Mapped[str] = mapped_column(String(48), unique=True, nullable=False, index=True) # RMAL-RMA-2026-000001-01
    return_request_id: Mapped[int] = mapped_column(Integer, ForeignKey("return_requests.id"), nullable=False, index=True)
    order_line_id: Mapped[int] = mapped_column(Integer, ForeignKey("order_lines.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    requested_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    eligible_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    approved_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    eligibility_status: Mapped[str] = mapped_column(String(32), default="PENDING_REVIEW", nullable=False) # ELIGIBLE, INELIGIBLE, PENDING_OVERRIDE, OVERRIDDEN
    ineligibility_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    policy_code_applied: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    override_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    override_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    override_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    estimated_refund_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    actual_refund_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    disposition_status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False) # PENDING, RESTOCKED, REFURBISHED, QUARANTINED, SCRAPPED, SPLIT
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    return_request: Mapped["ReturnRequest"] = relationship("ReturnRequest", back_populates="lines")
    order_line: Mapped["OrderLine"] = relationship("OrderLine", back_populates="return_lines")
    product: Mapped["Product"] = relationship("Product")
    inspections: Mapped[List["Inspection"]] = relationship("Inspection", back_populates="return_line")
    refunds: Mapped[List["Refund"]] = relationship("Refund", back_populates="return_line")
    dispositions: Mapped[List["InventoryDisposition"]] = relationship("InventoryDisposition", back_populates="return_line")


# 8. ReturnAuthorization
class ReturnAuthorization(Base):
    __tablename__ = "return_authorizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    authorization_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True) # RMA-AUTH-2026-000001
    return_request_id: Mapped[int] = mapped_column(Integer, ForeignKey("return_requests.id"), unique=True, nullable=False, index=True)
    authorized_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    authorized_by: Mapped[str] = mapped_column(String(64), nullable=False)
    authorized_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ISSUED", nullable=False) # ISSUED, IN_USE, EXPIRED, CANCELLED
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    return_request: Mapped["ReturnRequest"] = relationship("ReturnRequest", back_populates="authorization")
    shipments: Mapped[List["ReturnShipment"]] = relationship("ReturnShipment", back_populates="authorization")


# 9. ReturnShipment
class ReturnShipment(Base):
    __tablename__ = "return_shipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shipment_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True) # RTS-2026-000001
    return_request_id: Mapped[int] = mapped_column(Integer, ForeignKey("return_requests.id"), nullable=False, index=True)
    return_authorization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("return_authorizations.id"), nullable=True, index=True)
    carrier: Mapped[str] = mapped_column(String(32), default="UPS", nullable=False) # UPS, FEDEX, USPS, DHL
    tracking_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="LABEL_CREATED", nullable=False) # LABEL_CREATED, IN_TRANSIT, DELIVERED, MISSING, CANCELLED
    shipped_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    received_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    destination_warehouse: Mapped[str] = mapped_column(String(64), default="WH-CENTRAL-01", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    return_request: Mapped["ReturnRequest"] = relationship("ReturnRequest", back_populates="shipments")
    authorization: Mapped[Optional["ReturnAuthorization"]] = relationship("ReturnAuthorization", back_populates="shipments")
    inspections: Mapped[List["Inspection"]] = relationship("Inspection", back_populates="shipment")


# 10. Inspection
class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inspection_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True) # INS-2026-000001
    return_shipment_id: Mapped[int] = mapped_column(Integer, ForeignKey("return_shipments.id"), nullable=False, index=True)
    return_line_id: Mapped[int] = mapped_column(Integer, ForeignKey("return_lines.id"), nullable=False, index=True)
    inspected_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    item_condition: Mapped[str] = mapped_column(String(32), nullable=False) # UNOPENED, OPENED_LIKE_NEW, SLIGHT_WEAR, SIGNIFICANT_DAMAGE, DESTROYED, COUNTERFEIT
    packaging_condition: Mapped[str] = mapped_column(String(32), nullable=False) # INTACT, DAMAGED_REPAIRABLE, MISSING, DESTROYED
    result: Mapped[str] = mapped_column(String(32), nullable=False) # PASS, PASS_WITH_RESTOCKING_FEE, REFURBISHABLE, QUARANTINE_REQUIRED, REJECT_SCRAP, NOT_RECEIVED
    damage_type: Mapped[str] = mapped_column(String(32), default="NONE", nullable=False) # NONE, COSMETIC, ELECTRICAL, WATER, IMPACT, PACKAGING_ONLY, TAMPERED
    missing_components: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    inspector_id: Mapped[str] = mapped_column(String(64), nullable=False)
    inspection_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recommended_disposition: Mapped[str] = mapped_column(String(32), nullable=False) # RESTOCK, REFURBISH, QUARANTINE, SCRAP
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    shipment: Mapped["ReturnShipment"] = relationship("ReturnShipment", back_populates="inspections")
    return_line: Mapped["ReturnLine"] = relationship("ReturnLine", back_populates="inspections")
    dispositions: Mapped[List["InventoryDisposition"]] = relationship("InventoryDisposition", back_populates="inspection")


# 11. Refund
class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    refund_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True) # REF-2026-000001
    return_request_id: Mapped[int] = mapped_column(Integer, ForeignKey("return_requests.id"), nullable=False, index=True)
    return_line_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("return_lines.id"), nullable=True, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    refund_method: Mapped[str] = mapped_column(String(32), default="ORIGINAL_PAYMENT", nullable=False) # ORIGINAL_PAYMENT, STORE_CREDIT, BANK_TRANSFER
    base_unit_refund: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax_refund: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    shipping_refund: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    restocking_fee_deducted: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    net_refund_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False) # PENDING, COMPLETED, FAILED, BLOCKED_DUPLICATE
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    gateway_reference: Mapped[str] = mapped_column(String(64), nullable=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    return_request: Mapped["ReturnRequest"] = relationship("ReturnRequest", back_populates="refunds")
    return_line: Mapped[Optional["ReturnLine"]] = relationship("ReturnLine", back_populates="refunds")
    attempts: Mapped[List["RefundAttempt"]] = relationship("RefundAttempt", back_populates="refund")


# 12. RefundAttempt (Duplicate prevention audit log)
class RefundAttempt(Base):
    __tablename__ = "refund_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    refund_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("refunds.id"), nullable=True, index=True)
    return_request_id: Mapped[int] = mapped_column(Integer, ForeignKey("return_requests.id"), nullable=False, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    attempt_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    requested_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False) # SUCCESS, BLOCKED_DUPLICATE, REJECTED_OVERLIMIT, FAILED_GATEWAY
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    refund: Mapped[Optional["Refund"]] = relationship("Refund", back_populates="attempts")
    return_request: Mapped["ReturnRequest"] = relationship("ReturnRequest")


# 13. InventoryDisposition
class InventoryDisposition(Base):
    __tablename__ = "inventory_dispositions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disposition_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True) # DISP-2026-000001
    return_line_id: Mapped[int] = mapped_column(Integer, ForeignKey("return_lines.id"), nullable=False, index=True)
    inspection_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("inspections.id"), nullable=True, index=True)
    disposition_type: Mapped[str] = mapped_column(String(32), nullable=False) # RESTOCK, REFURBISH, QUARANTINE, SCRAP
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    warehouse_location: Mapped[str] = mapped_column(String(64), nullable=False)
    disposition_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    technician_id: Mapped[str] = mapped_column(String(64), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False) # PENDING, COMPLETED, REJECTED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    return_line: Mapped["ReturnLine"] = relationship("ReturnLine", back_populates="dispositions")
    inspection: Mapped[Optional["Inspection"]] = relationship("Inspection", back_populates="dispositions")
    movements: Mapped[List["InventoryMovement"]] = relationship("InventoryMovement", back_populates="disposition")


# 14. InventoryMovement
class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movement_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True) # MOV-2026-000001
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    inventory_disposition_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("inventory_dispositions.id"), nullable=True, index=True)
    movement_type: Mapped[str] = mapped_column(String(32), nullable=False) # INBOUND_RESTOCK, REFURBISH_TRANSFER, QUARANTINE_HOLD, SCRAP_WRITE_OFF
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    from_location: Mapped[str] = mapped_column(String(64), nullable=False)
    to_location: Mapped[str] = mapped_column(String(64), nullable=False)
    reference_id: Mapped[str] = mapped_column(String(64), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    product: Mapped["Product"] = relationship("Product")
    disposition: Mapped[Optional["InventoryDisposition"]] = relationship("InventoryDisposition", back_populates="movements")


# 15. ReturnEvent (Audit Trail)
class ReturnEvent(Base):
    __tablename__ = "return_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True) # EVT-2026-000001
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False) # ReturnRequest, ReturnShipment, Inspection, Refund, InventoryDisposition
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_state: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_state: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actor: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


# 16. AnomalyRecord (Ground Truth & Monitored Anomalies)
class AnomalyRecord(Base):
    __tablename__ = "anomaly_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anomaly_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True) # ANOM-2026-000001
    issue_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    affected_entity: Mapped[str] = mapped_column(String(32), nullable=False)
    affected_business_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    expected_detection_result: Mapped[str] = mapped_column(String(64), nullable=False)
    expected_business_decision: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False) # CRITICAL, HIGH, MEDIUM
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    injected_in_dataset: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    detection_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
