from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, EmailStr

# Common Pagination
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

# Customer Schemas
class CustomerBase(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    segment: str
    risk_score: float

class CustomerRead(CustomerBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Product Schemas
class ProductRead(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    price: float
    cost: float
    is_returnable: bool
    default_return_window_days: int
    restockable: bool
    requires_serial_number: bool
    class Config:
        from_attributes = True

# Order Line Schemas
class OrderLineRead(BaseModel):
    id: int
    line_number: int
    product_id: int
    product: Optional[ProductRead] = None
    quantity: int
    unit_price: float
    line_subtotal: float
    allocated_discount: float
    line_tax: float
    total_line_amount: float
    returned_quantity: int
    class Config:
        from_attributes = True

# Order Schemas
class OrderRead(BaseModel):
    id: int
    order_id: str
    customer_id: int
    customer: Optional[CustomerRead] = None
    order_date: datetime
    delivery_date: Optional[datetime] = None
    status: str
    subtotal: float
    discount_amount: float
    tax_amount: float
    shipping_amount: float
    total_amount: float
    payment_method: str
    shipping_address: Optional[str] = None
    lines: List[OrderLineRead] = []
    class Config:
        from_attributes = True

# Return Line Create & Read
class ReturnLineCreate(BaseModel):
    order_line_id: int
    requested_quantity: int = Field(gt=0, description="Quantity to return")

class ReturnLineRead(BaseModel):
    id: int
    return_line_id: str
    order_line_id: int
    product_id: int
    product: Optional[ProductRead] = None
    requested_quantity: int
    eligible_quantity: int
    approved_quantity: int
    rejected_quantity: int
    eligibility_status: str
    ineligibility_reason: Optional[str] = None
    policy_code_applied: Optional[str] = None
    override_approved: bool
    override_reason: Optional[str] = None
    override_by: Optional[str] = None
    estimated_refund_amount: float
    actual_refund_amount: float
    disposition_status: str
    created_at: datetime
    class Config:
        from_attributes = True

# Return Authorization Read
class ReturnAuthorizationRead(BaseModel):
    id: int
    authorization_number: str
    authorized_date: datetime
    authorized_by: str
    authorized_quantity: int
    status: str
    valid_until: datetime
    notes: Optional[str] = None
    class Config:
        from_attributes = True

# Return Shipment Read
class ReturnShipmentRead(BaseModel):
    id: int
    shipment_id: str
    carrier: str
    tracking_number: str
    status: str
    shipped_date: Optional[datetime] = None
    received_date: Optional[datetime] = None
    destination_warehouse: str
    created_at: datetime
    class Config:
        from_attributes = True

# Inspection Read
class InspectionRead(BaseModel):
    id: int
    inspection_id: str
    inspected_quantity: int
    item_condition: str
    packaging_condition: str
    result: str
    damage_type: str
    missing_components: Optional[str] = None
    notes: Optional[str] = None
    inspector_id: str
    inspection_timestamp: datetime
    recommended_disposition: str
    class Config:
        from_attributes = True

# Refund Read
class RefundRead(BaseModel):
    id: int
    refund_id: str
    idempotency_key: str
    refund_method: str
    base_unit_refund: float
    tax_refund: float
    shipping_refund: float
    restocking_fee_deducted: float
    net_refund_amount: float
    status: str
    processed_at: datetime
    gateway_reference: str
    failure_reason: Optional[str] = None
    class Config:
        from_attributes = True

# ReturnRequest Create & Read
class ReturnRequestCreate(BaseModel):
    order_id: str = Field(description="Order public ID, e.g. ORD-2026-000001")
    customer_id: str = Field(description="Customer public ID, e.g. CUST-2026-000001")
    reason_category: str = Field(description="DEFECTIVE, WRONG_ITEM, SIZE_FIT, etc.")
    channel: str = Field(default="WEB")
    customer_comments: Optional[str] = None
    lines: List[ReturnLineCreate]

class ReturnRequestRead(BaseModel):
    id: int
    rma_number: str
    order_id: int
    order: Optional[OrderRead] = None
    customer_id: int
    customer: Optional[CustomerRead] = None
    status: str
    overall_eligibility: str
    requested_date: datetime
    channel: str
    reason_category: str
    customer_comments: Optional[str] = None
    lines: List[ReturnLineRead] = []
    authorization: Optional[ReturnAuthorizationRead] = None
    shipments: List[ReturnShipmentRead] = []
    refunds: List[RefundRead] = []
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# Operation Action Request Schemas
class AuthorizeReturnRequest(BaseModel):
    authorized_by: str = "MANAGER_DESK"
    validity_days: int = 14

class CreateShipmentRequest(BaseModel):
    carrier: str = "UPS"
    tracking_number: Optional[str] = None
    destination_warehouse: str = "WH-CENTRAL-01"

class ReceiveShipmentRequest(BaseModel):
    receiver_id: str = "WH_STATION_01"

class InspectShipmentRequest(BaseModel):
    return_line_id: str
    inspected_quantity: int = 1
    item_condition: str = "OPENED_LIKE_NEW"
    packaging_condition: str = "INTACT"
    damage_type: str = "NONE"
    missing_components: Optional[str] = None
    notes: Optional[str] = None
    inspector_id: str = "INSPECTOR_QA_01"
    allow_unreceived_override: bool = False

class ProcessRefundRequest(BaseModel):
    idempotency_key: str
    return_line_id: Optional[str] = None
    refund_method: str = "ORIGINAL_PAYMENT"
    apply_restocking_fee: bool = False

class ExecuteDispositionRequest(BaseModel):
    return_line_id: str
    disposition_type: str # RESTOCK, REFURBISH, QUARANTINE, SCRAP
    quantity: int = 1
    warehouse_location: str = "WH-BIN-A12"
    technician_id: str = "TECH_DISP_01"
    notes: Optional[str] = None

class LineOverrideRequest(BaseModel):
    override_by: str
    override_reason: str

class DataGenerationRequest(BaseModel):
    profile: str = "starter" # starter or full
    seed: int = 20261022

