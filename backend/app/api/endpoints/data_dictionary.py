from fastapi import APIRouter

router = APIRouter()

DATA_DICTIONARY_ENTITIES = [
    {
        "entity_name": "Customer",
        "table_name": "customers",
        "description": "Represents an individual or business purchaser with risk profile and lifetime tracking.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Internal auto-increment primary key."},
            {"name": "customer_id", "type": "VARCHAR(32)", "required": True, "key": "UK", "description": "Deterministic public identifier (CUST-2026-000001)."},
            {"name": "first_name", "type": "VARCHAR(64)", "required": True, "key": "-", "description": "Customer given name."},
            {"name": "last_name", "type": "VARCHAR(64)", "required": True, "key": "-", "description": "Customer family name."},
            {"name": "email", "type": "VARCHAR(128)", "required": True, "key": "UK", "description": "Unique email address for contact and notification."},
            {"name": "phone", "type": "VARCHAR(32)", "required": False, "key": "-", "description": "Contact telephone number."},
            {"name": "segment", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "Customer tier: STANDARD, VIP, WHOLESALE."},
            {"name": "risk_score", "type": "FLOAT", "required": True, "key": "-", "description": "Calculated returns fraud risk index (0.00 - 1.00)."},
            {"name": "created_at", "type": "DATETIME", "required": True, "key": "-", "description": "Timestamp of account registration."}
        ]
    },
    {
        "entity_name": "Product",
        "table_name": "products",
        "description": "Catalog items eligible or excluded from returns.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Internal product ID."},
            {"name": "sku", "type": "VARCHAR(64)", "required": True, "key": "UK", "description": "Stock Keeping Unit identifier."},
            {"name": "name", "type": "VARCHAR(255)", "required": True, "key": "-", "description": "Marketing product title."},
            {"name": "category", "type": "VARCHAR(64)", "required": True, "key": "INDEX", "description": "Product category (Electronics, Apparel, Home & Kitchen, Food)."},
            {"name": "price", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Retail catalog selling price."},
            {"name": "cost", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Internal procurement inventory cost."},
            {"name": "is_returnable", "type": "BOOLEAN", "required": True, "key": "-", "description": "Whether returns are permitted by law/policy."},
            {"name": "default_return_window_days", "type": "INTEGER", "required": True, "key": "-", "description": "Standard allowable days since delivery."},
            {"name": "restockable", "type": "BOOLEAN", "required": True, "key": "-", "description": "Whether item can return to active inventory."},
            {"name": "requires_serial_number", "type": "BOOLEAN", "required": True, "key": "-", "description": "Serial tracking verification flag."}
        ]
    },
    {
        "entity_name": "ReturnPolicy",
        "table_name": "return_policies",
        "description": "Configurable governance rules per category.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Internal policy identifier."},
            {"name": "policy_code", "type": "VARCHAR(32)", "required": True, "key": "UK", "description": "Unique policy identifier code (e.g. POL-ELEC-14)."},
            {"name": "name", "type": "VARCHAR(128)", "required": True, "key": "-", "description": "Descriptive human policy title."},
            {"name": "category", "type": "VARCHAR(64)", "required": True, "key": "INDEX", "description": "Category to which rule applies."},
            {"name": "return_window_days", "type": "INTEGER", "required": True, "key": "-", "description": "Maximum days elapsed between delivery and request."},
            {"name": "restocking_fee_percent", "type": "NUMERIC(5,2)", "required": True, "key": "-", "description": "Fee percentage deducted upon opened box return."},
            {"name": "requires_original_packaging", "type": "BOOLEAN", "required": True, "key": "-", "description": "Condition requirement flag."},
            {"name": "allow_opened_box", "type": "BOOLEAN", "required": True, "key": "-", "description": "Permit opened product acceptance."}
        ]
    },
    {
        "entity_name": "Order",
        "table_name": "orders",
        "description": "Customer purchase transaction record.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Primary key."},
            {"name": "order_id", "type": "VARCHAR(32)", "required": True, "key": "UK", "description": "Public purchase ID (ORD-2026-000001)."},
            {"name": "customer_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References customers.id."},
            {"name": "order_date", "type": "DATETIME", "required": True, "key": "-", "description": "Purchase transaction timestamp."},
            {"name": "delivery_date", "type": "DATETIME", "required": False, "key": "-", "description": "Carrier confirmed delivery timestamp."},
            {"name": "status", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "DELIVERED, PENDING, PARTIALLY_RETURNED, FULLY_RETURNED."},
            {"name": "subtotal", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Gross items aggregate amount."},
            {"name": "discount_amount", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Total order promo coupons applied."},
            {"name": "tax_amount", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Calculated sales tax."},
            {"name": "shipping_amount", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Outbound freight charged."},
            {"name": "total_amount", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Final paid customer invoice amount."}
        ]
    },
    {
        "entity_name": "OrderLine",
        "table_name": "order_lines",
        "description": "Individual product item purchase within an order.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Primary key."},
            {"name": "order_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References orders.id."},
            {"name": "product_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References products.id."},
            {"name": "line_number", "type": "INTEGER", "required": True, "key": "-", "description": "Sequential line position."},
            {"name": "quantity", "type": "INTEGER", "required": True, "key": "-", "description": "Purchased unit count."},
            {"name": "unit_price", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Charged price per unit."},
            {"name": "line_subtotal", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "unit_price * quantity."},
            {"name": "allocated_discount", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Proportional discount allocation."},
            {"name": "line_tax", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Sales tax on line."},
            {"name": "total_line_amount", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Net paid amount for line."},
            {"name": "returned_quantity", "type": "INTEGER", "required": True, "key": "-", "description": "Quantity currently returned/authorized."}
        ]
    },
    {
        "entity_name": "ReturnRequest",
        "table_name": "return_requests",
        "description": "RMA initiating the return lifecycle workflow.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Primary key."},
            {"name": "rma_number", "type": "VARCHAR(32)", "required": True, "key": "UK", "description": "Deterministic business RMA identifier (RMA-2026-000001)."},
            {"name": "order_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References orders.id."},
            {"name": "customer_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References customers.id."},
            {"name": "status", "type": "VARCHAR(32)", "required": True, "key": "INDEX", "description": "Lifecycle state: SUBMITTED, ELIGIBLE, AUTHORIZED, IN_TRANSIT, RECEIVED, INSPECTED, COMPLETED, REJECTED."},
            {"name": "overall_eligibility", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "Rule verdict: FULLY_ELIGIBLE, PARTIALLY_ELIGIBLE, INELIGIBLE, PENDING_REVIEW."},
            {"name": "requested_date", "type": "DATETIME", "required": True, "key": "-", "description": "Customer return submission timestamp."},
            {"name": "channel", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "Intake portal: WEB, MOBILE, SUPPORT_PORTAL, IN_STORE."},
            {"name": "reason_category", "type": "VARCHAR(64)", "required": True, "key": "-", "description": "DEFECTIVE, WRONG_ITEM, SIZE_FIT, CHANGED_MIND, etc."}
        ]
    },
    {
        "entity_name": "ReturnLine",
        "table_name": "return_lines",
        "description": "Line item within a return request.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Primary key."},
            {"name": "return_line_id", "type": "VARCHAR(48)", "required": True, "key": "UK", "description": "RMAL-RMA-2026-000001-01."},
            {"name": "return_request_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References return_requests.id."},
            {"name": "order_line_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References order_lines.id."},
            {"name": "product_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References products.id."},
            {"name": "requested_quantity", "type": "INTEGER", "required": True, "key": "-", "description": "Customer requested return units."},
            {"name": "eligible_quantity", "type": "INTEGER", "required": True, "key": "-", "description": "Units determined eligible by rule engine."},
            {"name": "approved_quantity", "type": "INTEGER", "required": True, "key": "-", "description": "Authorized return quantity."},
            {"name": "rejected_quantity", "type": "INTEGER", "required": True, "key": "-", "description": "Rejected return quantity."},
            {"name": "eligibility_status", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "ELIGIBLE, INELIGIBLE, OVERRIDDEN."},
            {"name": "ineligibility_reason", "type": "VARCHAR(255)", "required": False, "key": "-", "description": "Explaining rejection reason."},
            {"name": "override_approved", "type": "BOOLEAN", "required": True, "key": "-", "description": "Whether manager exception override was applied."},
            {"name": "estimated_refund_amount", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Projected payout balance."},
            {"name": "actual_refund_amount", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Executed payout balance."},
            {"name": "disposition_status", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "PENDING, RESTOCKED, REFURBISHED, QUARANTINED, SCRAPPED, SPLIT."}
        ]
    },
    {
        "entity_name": "ReturnAuthorization",
        "table_name": "return_authorizations",
        "description": "Official authorization token granting reverse logistics acceptance.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Primary key."},
            {"name": "authorization_number", "type": "VARCHAR(32)", "required": True, "key": "UK", "description": "RMA-AUTH-2026-000001."},
            {"name": "return_request_id", "type": "INTEGER", "required": True, "key": "FK, UK", "description": "References return_requests.id (1:1)."},
            {"name": "authorized_date", "type": "DATETIME", "required": True, "key": "-", "description": "Issuance timestamp."},
            {"name": "authorized_by", "type": "VARCHAR(64)", "required": True, "key": "-", "description": "Operator or SYSTEM_RULES_ENGINE."},
            {"name": "authorized_quantity", "type": "INTEGER", "required": True, "key": "-", "description": "Total approved unit count."},
            {"name": "status", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "ISSUED, IN_USE, EXPIRED, CANCELLED."},
            {"name": "valid_until", "type": "DATETIME", "required": True, "key": "-", "description": "Expiration timestamp for reverse shipping."}
        ]
    },
    {
        "entity_name": "ReturnShipment",
        "table_name": "return_shipments",
        "description": "Reverse logistics transport parcel record.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Primary key."},
            {"name": "shipment_id", "type": "VARCHAR(32)", "required": True, "key": "UK", "description": "RTS-2026-000001."},
            {"name": "return_request_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References return_requests.id."},
            {"name": "carrier", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "Carrier: UPS, FEDEX, USPS, DHL."},
            {"name": "tracking_number", "type": "VARCHAR(64)", "required": True, "key": "INDEX", "description": "Carrier tracking identifier."},
            {"name": "status", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "LABEL_CREATED, IN_TRANSIT, DELIVERED, MISSING, CANCELLED."},
            {"name": "shipped_date", "type": "DATETIME", "required": False, "key": "-", "description": "Carrier intake scan timestamp."},
            {"name": "received_date", "type": "DATETIME", "required": False, "key": "-", "description": "Warehouse dock arrival scan timestamp."},
            {"name": "destination_warehouse", "type": "VARCHAR(64)", "required": True, "key": "-", "description": "Warehouse intake facility identifier."}
        ]
    },
    {
        "entity_name": "Inspection",
        "table_name": "inspections",
        "description": "Quality assurance evaluation performed upon physical receipt.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Primary key."},
            {"name": "inspection_id", "type": "VARCHAR(32)", "required": True, "key": "UK", "description": "INS-2026-000001."},
            {"name": "return_shipment_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References return_shipments.id."},
            {"name": "return_line_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References return_lines.id."},
            {"name": "inspected_quantity", "type": "INTEGER", "required": True, "key": "-", "description": "Number of units evaluated."},
            {"name": "item_condition", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "UNOPENED, OPENED_LIKE_NEW, SLIGHT_WEAR, SIGNIFICANT_DAMAGE, DESTROYED, COUNTERFEIT."},
            {"name": "packaging_condition", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "INTACT, DAMAGED_REPAIRABLE, MISSING, DESTROYED."},
            {"name": "result", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "PASS, PASS_WITH_RESTOCKING_FEE, REFURBISHABLE, QUARANTINE_REQUIRED, REJECT_SCRAP, NOT_RECEIVED."},
            {"name": "damage_type", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "NONE, COSMETIC, ELECTRICAL, WATER, IMPACT, PACKAGING_ONLY, TAMPERED."},
            {"name": "recommended_disposition", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "RESTOCK, REFURBISH, QUARANTINE, SCRAP."}
        ]
    },
    {
        "entity_name": "Refund",
        "table_name": "refunds",
        "description": "Financial reimbursement disbursed to the customer.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Primary key."},
            {"name": "refund_id", "type": "VARCHAR(32)", "required": True, "key": "UK", "description": "REF-2026-000001."},
            {"name": "return_request_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References return_requests.id."},
            {"name": "idempotency_key", "type": "VARCHAR(64)", "required": True, "key": "UK", "description": "Unique cryptographic token preventing duplicate payment."},
            {"name": "base_unit_refund", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Item purchase cost refunded."},
            {"name": "tax_refund", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Proportional tax reimbursed."},
            {"name": "restocking_fee_deducted", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Policy fee withheld."},
            {"name": "net_refund_amount", "type": "NUMERIC(10,2)", "required": True, "key": "-", "description": "Final paid disbursement."},
            {"name": "status", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "COMPLETED, PENDING, BLOCKED_DUPLICATE."},
            {"name": "gateway_reference", "type": "VARCHAR(64)", "required": True, "key": "-", "description": "Simulated payment processor reference."}
        ]
    },
    {
        "entity_name": "InventoryDisposition",
        "table_name": "inventory_dispositions",
        "description": "Routing decisions assigning physical returned inventory to destination bays.",
        "fields": [
            {"name": "id", "type": "INTEGER", "required": True, "key": "PK", "description": "Primary key."},
            {"name": "disposition_id", "type": "VARCHAR(32)", "required": True, "key": "UK", "description": "DISP-2026-000001."},
            {"name": "return_line_id", "type": "INTEGER", "required": True, "key": "FK", "description": "References return_lines.id."},
            {"name": "inspection_id", "type": "INTEGER", "required": False, "key": "FK", "description": "References inspections.id."},
            {"name": "disposition_type", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "RESTOCK, REFURBISH, QUARANTINE, SCRAP."},
            {"name": "quantity", "type": "INTEGER", "required": True, "key": "-", "description": "Quantity routed to disposition."},
            {"name": "warehouse_location", "type": "VARCHAR(64)", "required": True, "key": "-", "description": "Warehouse bin/bay designation."},
            {"name": "status", "type": "VARCHAR(32)", "required": True, "key": "-", "description": "COMPLETED, PENDING, REJECTED."}
        ]
    }
]

@router.get("")
def get_data_dictionary():
    return {
        "title": "Returns Management & Audit Platform Data Dictionary",
        "version": "1.0.0",
        "total_entities": len(DATA_DICTIONARY_ENTITIES),
        "entities": DATA_DICTIONARY_ENTITIES
    }

