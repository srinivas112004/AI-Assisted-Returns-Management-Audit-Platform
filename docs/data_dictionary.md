# Data Dictionary & Schema Specifications

This comprehensive data dictionary details all database tables, columns, data types, constraints, and validation rules.

---

## 1. Customer (`customers`)
Represents an individual or business customer account.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal unique database key |
| `customer_id` | VARCHAR(32) | UK | No | None | Deterministic public ID (`CUST-2026-000001`) |
| `first_name` | VARCHAR(64) | - | No | None | Customer given name |
| `last_name` | VARCHAR(64) | - | No | None | Customer family name |
| `email` | VARCHAR(128) | UK | No | None | Contact email address |
| `phone` | VARCHAR(32) | - | Yes | NULL | Contact phone number |
| `segment` | VARCHAR(32) | - | No | 'STANDARD' | Loyalty tier: `STANDARD`, `VIP`, `WHOLESALE` |
| `risk_score` | FLOAT | - | No | 0.0 | Calculated fraud/returns risk index (0.00 to 1.00) |
| `created_at` | DATETIME | - | No | UTC Now | Account creation timestamp |

---

## 2. Product (`products`)
Catalog items available for purchase and reverse logistics.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal product key |
| `sku` | VARCHAR(64) | UK | No | None | Stock Keeping Unit identifier (`SKU-ELEC-001`) |
| `name` | VARCHAR(255) | - | No | None | Marketing product title |
| `category` | VARCHAR(64) | INDEX | No | None | Category: `Electronics`, `Apparel`, `Home & Kitchen`, `Food & Beverage` |
| `price` | NUMERIC(10,2) | - | No | None | Standard retail selling price (USD) |
| `cost` | NUMERIC(10,2) | - | No | None | Inventory procurement cost (USD) |
| `is_returnable`| BOOLEAN | - | No | True | Whether product allows customer returns |
| `default_return_window_days` | INTEGER | - | No | 30 | Base allowable return window (days) |
| `restockable` | BOOLEAN | - | No | True | Whether product can be re-shelved |
| `requires_serial_number` | BOOLEAN | - | No | False | Serial number verification flag |
| `created_at` | DATETIME | - | No | UTC Now | Catalog registration timestamp |

---

## 3. Return Policy (`return_policies`)
Configurable governance rules applied to product categories.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal policy key |
| `policy_code`| VARCHAR(32) | UK | No | None | Public code (`POL-STD-30`, `POL-ELEC-14`, `POL-NON-RET`) |
| `name` | VARCHAR(128) | - | No | None | Human-readable policy title |
| `category` | VARCHAR(64) | INDEX | No | None | Target category |
| `return_window_days` | INTEGER | - | No | 30 | Allowable days elapsed between delivery and request |
| `restocking_fee_percent` | NUMERIC(5,2)| - | No | 0.00 | Restocking fee percentage deducted for opened items |
| `requires_original_packaging` | BOOLEAN | - | No | False | Original packaging required flag |
| `allow_opened_box` | BOOLEAN | - | No | True | Accept opened/unsealed packaging |
| `is_active` | BOOLEAN | - | No | True | Policy active flag |
| `effective_from` | DATETIME | - | No | None | Policy validity start timestamp |
| `description`| TEXT | - | Yes | NULL | Summary of policy terms |

---

## 4. Order (`orders`)
Customer purchase transaction record.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal order key |
| `order_id` | VARCHAR(32) | UK | No | None | Public order identifier (`ORD-2026-000001`) |
| `customer_id`| INTEGER | FK | No | None | References `customers.id` |
| `order_date` | DATETIME | - | No | None | Purchase transaction timestamp |
| `delivery_date` | DATETIME | - | Yes | NULL | Carrier confirmed delivery timestamp |
| `status` | VARCHAR(32) | - | No | 'DELIVERED' | `PENDING`, `DELIVERED`, `PARTIALLY_RETURNED`, `FULLY_RETURNED` |
| `subtotal` | NUMERIC(10,2) | - | No | None | Sum of order line item costs |
| `discount_amount` | NUMERIC(10,2) | - | No | 0.00 | Order-level promotional discount |
| `tax_amount` | NUMERIC(10,2) | - | No | 0.00 | Total calculated sales tax |
| `shipping_amount` | NUMERIC(10,2) | - | No | 0.00 | Freight shipping charge |
| `total_amount` | NUMERIC(10,2) | - | No | None | Net invoice settled amount |
| `payment_method` | VARCHAR(32) | - | No | 'CREDIT_CARD' | Payment instrument used |
| `shipping_address` | TEXT | - | Yes | NULL | Destination delivery address |
| `created_at` | DATETIME | - | No | UTC Now | Order creation timestamp |
| `updated_at` | DATETIME | - | No | UTC Now | Order status update timestamp |

---

## 5. Order Line (`order_lines`)
Itemized product purchase within an order.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal line key |
| `order_id` | INTEGER | FK | No | None | References `orders.id` |
| `product_id` | INTEGER | FK | No | None | References `products.id` |
| `line_number`| INTEGER | - | No | None | Sequential item index within order |
| `quantity` | INTEGER | - | No | None | Purchased unit count |
| `unit_price` | NUMERIC(10,2) | - | No | None | Retail unit price at transaction |
| `line_subtotal` | NUMERIC(10,2) | - | No | None | `unit_price * quantity` |
| `allocated_discount` | NUMERIC(10,2) | - | No | 0.00 | Proportional promo discount |
| `line_tax` | NUMERIC(10,2) | - | No | 0.00 | Proportional sales tax |
| `total_line_amount` | NUMERIC(10,2) | - | No | None | Net line paid amount |
| `returned_quantity` | INTEGER | - | No | 0 | Count of units returned/authorized |
| `created_at` | DATETIME | - | No | UTC Now | Line creation timestamp |

---

## 6. Return Request (`return_requests`)
Customer Return Merchandise Authorization (RMA) ticket.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal RMA key |
| `rma_number` | VARCHAR(32) | UK | No | None | Public identifier (`RMA-2026-000001`) |
| `order_id` | INTEGER | FK | No | None | References `orders.id` |
| `customer_id`| INTEGER | FK | No | None | References `customers.id` |
| `status` | VARCHAR(32) | INDEX | No | 'SUBMITTED' | Lifecycle status |
| `overall_eligibility` | VARCHAR(32) | - | No | 'PENDING_REVIEW' | Rule verdict |
| `requested_date` | DATETIME | - | No | None | RMA submission timestamp |
| `channel` | VARCHAR(32) | - | No | 'WEB' | `WEB`, `MOBILE`, `SUPPORT_PORTAL`, `IN_STORE` |
| `reason_category` | VARCHAR(64) | - | No | None | `DEFECTIVE`, `WRONG_ITEM`, `SIZE_FIT`, etc. |
| `customer_comments` | TEXT | - | Yes | NULL | Customer notes |
| `created_at` | DATETIME | - | No | UTC Now | RMA creation timestamp |
| `updated_at` | DATETIME | - | No | UTC Now | RMA status update timestamp |

---

## 7. Return Line (`return_lines`)
Individual itemized unit requested for return within an RMA.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal line key |
| `return_line_id` | VARCHAR(48) | UK | No | None | Public identifier (`RMAL-RMA-2026-000001-01`) |
| `return_request_id` | INTEGER | FK | No | None | References `return_requests.id` |
| `order_line_id` | INTEGER | FK | No | None | References `order_lines.id` |
| `product_id` | INTEGER | FK | No | None | References `products.id` |
| `requested_quantity` | INTEGER | - | No | None | Customer requested return units |
| `eligible_quantity` | INTEGER | - | No | 0 | Rule engine eligible units |
| `approved_quantity` | INTEGER | - | No | 0 | Authorized return units |
| `rejected_quantity` | INTEGER | - | No | 0 | Rejected return units |
| `eligibility_status` | VARCHAR(32) | - | No | 'PENDING_REVIEW' | `ELIGIBLE`, `INELIGIBLE`, `OVERRIDDEN` |
| `ineligibility_reason` | VARCHAR(255)| - | Yes | NULL | Rule rejection reason |
| `policy_code_applied` | VARCHAR(32) | - | Yes | NULL | Policy code evaluated |
| `override_approved` | BOOLEAN | - | No | False | Supervisor override flag |
| `override_reason` | VARCHAR(255)| - | Yes | NULL | Exception override explanation |
| `override_by` | VARCHAR(64) | - | Yes | NULL | Authorizing supervisor identifier |
| `estimated_refund_amount` | NUMERIC(10,2)| - | No | 0.00 | Projected customer payout |
| `actual_refund_amount` | NUMERIC(10,2)| - | No | 0.00 | Actual settled customer payout |
| `disposition_status` | VARCHAR(32) | - | No | 'PENDING' | `PENDING`, `RESTOCKED`, `REFURBISHED`, `QUARANTINED`, `SCRAPPED`, `SPLIT` |
| `created_at` | DATETIME | - | No | UTC Now | Line creation timestamp |

---

## 8. Return Authorization (`return_authorizations`)
Official reverse logistics authorization token.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal authorization key |
| `authorization_number`| VARCHAR(32) | UK | No | None | Token (`RMA-AUTH-2026-000001`) |
| `return_request_id` | INTEGER | FK, UK| No | None | References `return_requests.id` (1:1) |
| `authorized_date` | DATETIME | - | No | None | Issuance timestamp |
| `authorized_by` | VARCHAR(64) | - | No | None | Operator or SYSTEM_RULES_ENGINE |
| `authorized_quantity` | INTEGER | - | No | None | Sum of approved units |
| `status` | VARCHAR(32) | - | No | 'ISSUED' | `ISSUED`, `IN_USE`, `EXPIRED`, `CANCELLED` |
| `valid_until` | DATETIME | - | No | None | Authorization expiration timestamp |
| `notes` | TEXT | - | Yes | NULL | Authorization remarks |
| `created_at` | DATETIME | - | No | UTC Now | Token creation timestamp |

---

## 9. Return Shipment (`return_shipments`)
Inbound parcel logistics tracking.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal shipment key |
| `shipment_id` | VARCHAR(32) | UK | No | None | Public identifier (`RTS-2026-000001`) |
| `return_request_id` | INTEGER | FK | No | None | References `return_requests.id` |
| `return_authorization_id`| INTEGER | FK | Yes | NULL | References `return_authorizations.id` |
| `carrier` | VARCHAR(32) | - | No | 'UPS' | `UPS`, `FEDEX`, `USPS`, `DHL` |
| `tracking_number` | VARCHAR(64) | INDEX | No | None | Carrier tracking code |
| `status` | VARCHAR(32) | - | No | 'LABEL_CREATED' | `LABEL_CREATED`, `IN_TRANSIT`, `DELIVERED`, `MISSING`, `CANCELLED` |
| `shipped_date` | DATETIME | - | Yes | NULL | Carrier intake scan timestamp |
| `received_date` | DATETIME | - | Yes | NULL | Warehouse dock delivery scan timestamp |
| `destination_warehouse` | VARCHAR(64)| - | No | 'WH-CENTRAL-01'| Destination intake facility |
| `created_at` | DATETIME | - | No | UTC Now | Shipment registration timestamp |
| `updated_at` | DATETIME | - | No | UTC Now | Status update timestamp |

---

## 10. Inspection (`inspections`)
Physical quality assurance evaluation performed upon delivery.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal inspection key |
| `inspection_id` | VARCHAR(32) | UK | No | None | Public identifier (`INS-2026-000001`) |
| `return_shipment_id`| INTEGER | FK | No | None | References `return_shipments.id` |
| `return_line_id` | INTEGER | FK | No | None | References `return_lines.id` |
| `inspected_quantity`| INTEGER | - | No | None | Inspected unit count |
| `item_condition` | VARCHAR(32) | - | No | None | `UNOPENED`, `OPENED_LIKE_NEW`, `SLIGHT_WEAR`, `SIGNIFICANT_DAMAGE`, `DESTROYED`, `COUNTERFEIT` |
| `packaging_condition`| VARCHAR(32)| - | No | None | `INTACT`, `DAMAGED_REPAIRABLE`, `MISSING`, `DESTROYED` |
| `result` | VARCHAR(32) | - | No | None | `PASS`, `PASS_WITH_RESTOCKING_FEE`, `REFURBISHABLE`, `QUARANTINE_REQUIRED`, `REJECT_SCRAP` |
| `damage_type` | VARCHAR(32) | - | No | 'NONE' | `NONE`, `COSMETIC`, `ELECTRICAL`, `WATER`, `IMPACT`, `PACKAGING_ONLY`, `TAMPERED` |
| `missing_components`| VARCHAR(255)| - | Yes | NULL | Notes on missing cords, accessories |
| `inspector_id` | VARCHAR(64) | - | No | None | QA technician badge identifier |
| `inspection_timestamp`| DATETIME | - | No | None | Inspection completion timestamp |
| `recommended_disposition`| VARCHAR(32)| - | No | None | `RESTOCK`, `REFURBISH`, `QUARANTINE`, `SCRAP` |
| `created_at` | DATETIME | - | No | UTC Now | Record timestamp |

---

## 11. Refund (`refunds`)
Financial payout disbursed to the customer.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal refund key |
| `refund_id` | VARCHAR(32) | UK | No | None | Public identifier (`REF-2026-000001`) |
| `return_request_id` | INTEGER | FK | No | None | References `return_requests.id` |
| `return_line_id` | INTEGER | FK | Yes | NULL | References `return_lines.id` |
| `idempotency_key` | VARCHAR(64) | UK | No | None | Unique cryptographic token |
| `refund_method` | VARCHAR(32) | - | No | 'ORIGINAL_PAYMENT'| Payment method |
| `base_unit_refund` | NUMERIC(10,2)| - | No | None | Item gross refund balance |
| `tax_refund` | NUMERIC(10,2)| - | No | 0.00 | Proportional tax refund |
| `shipping_refund` | NUMERIC(10,2)| - | No | 0.00 | Shipping refund |
| `restocking_fee_deducted`| NUMERIC(10,2)| -| No | 0.00 | Deducted policy restocking fee |
| `net_refund_amount`| NUMERIC(10,2)| - | No | None | Net customer payout |
| `status` | VARCHAR(32) | - | No | 'COMPLETED' | `COMPLETED`, `PENDING`, `BLOCKED_DUPLICATE` |
| `processed_at` | DATETIME | - | No | None | Execution timestamp |
| `gateway_reference`| VARCHAR(64) | - | No | None | Payment gateway reference |
| `created_at` | DATETIME | - | No | UTC Now | Record timestamp |

---

## 12. Refund Attempt (`refund_attempts`)
Audit log for payment duplicate attempts.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal attempt key |
| `refund_id` | INTEGER | FK | Yes | NULL | References `refunds.id` |
| `return_request_id` | INTEGER | FK | No | None | References `return_requests.id` |
| `idempotency_key` | VARCHAR(64) | INDEX | No | None | Token supplied |
| `attempt_timestamp` | DATETIME | - | No | None | Attempt timestamp |
| `requested_amount` | NUMERIC(10,2)| - | No | None | Requested payout |
| `outcome` | VARCHAR(32) | - | No | None | `SUCCESS`, `BLOCKED_DUPLICATE`, `REJECTED_OVERLIMIT` |
| `reason` | VARCHAR(255)| - | No | None | Guard outcome reason |

---

## 13. Inventory Disposition (`inventory_dispositions`)
Routing decision assigning physical returned inventory to destination bays.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal disposition key |
| `disposition_id` | VARCHAR(32) | UK | No | None | Public identifier (`DISP-2026-000001`) |
| `return_line_id` | INTEGER | FK | No | None | References `return_lines.id` |
| `inspection_id` | INTEGER | FK | Yes | NULL | References `inspections.id` |
| `disposition_type` | VARCHAR(32) | - | No | None | `RESTOCK`, `REFURBISH`, `QUARANTINE`, `SCRAP` |
| `quantity` | INTEGER | - | No | None | Units routed |
| `warehouse_location`| VARCHAR(64) | - | No | None | Warehouse bin/bay code |
| `disposition_date` | DATETIME | - | No | None | Execution timestamp |
| `technician_id` | VARCHAR(64) | - | No | None | Technician identifier |
| `status` | VARCHAR(32) | - | No | 'COMPLETED' | `COMPLETED`, `PENDING`, `REJECTED` |

---

## 14. Inventory Movement (`inventory_movements`)
Auditable stock transfer transaction ledger.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal movement key |
| `movement_id` | VARCHAR(32) | UK | No | None | Public identifier (`MOV-2026-000001`) |
| `product_id` | INTEGER | FK | No | None | References `products.id` |
| `inventory_disposition_id` | INTEGER | FK | Yes | NULL | References `inventory_dispositions.id` |
| `movement_type` | VARCHAR(32) | - | No | None | `INBOUND_RESTOCK`, `REFURBISH_TRANSFER`, `QUARANTINE_HOLD`, `SCRAP_WRITE_OFF` |
| `quantity` | INTEGER | - | No | None | Units transferred |
| `from_location` | VARCHAR(64) | - | No | None | Source intake bay |
| `to_location` | VARCHAR(64) | - | No | None | Destination warehouse bin |
| `reference_id` | VARCHAR(64) | - | No | None | Linked disposition identifier |
| `timestamp` | DATETIME | - | No | None | Movement timestamp |

---

## 15. Return Event (`return_events`)
Append-only immutable audit trail.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal event key |
| `event_id` | VARCHAR(32) | UK | No | None | Public identifier (`EVT-2026-000001`) |
| `entity_type` | VARCHAR(32) | - | No | None | Entity class name |
| `entity_id` | VARCHAR(64) | INDEX | No | None | Business public ID |
| `event_type` | VARCHAR(64) | - | No | None | Action/Transition type |
| `previous_state` | TEXT | - | Yes | NULL | State prior to event |
| `new_state` | TEXT | - | Yes | NULL | State following event |
| `actor` | VARCHAR(64) | - | No | None | Initiator identifier |
| `reason` | VARCHAR(255)| - | Yes | NULL | Event rationale |
| `timestamp` | DATETIME | - | No | None | Chronological event timestamp |

---

## 16. Anomaly Record (`anomaly_records`)
Ground-truth labelled anomalies for detector evaluation.

| Field Name | Type | Key | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK | No | Auto | Internal record key |
| `anomaly_id` | VARCHAR(32) | UK | No | None | Identifier (`ANOM-2026-000001`) |
| `issue_type` | VARCHAR(64) | INDEX | No | None | Classification type |
| `affected_entity` | VARCHAR(32) | - | No | None | Target model |
| `affected_business_id` | VARCHAR(64)| INDEX | No | None | Target business ID |
| `expected_detection_result` | VARCHAR(64)| - | No | 'FAIL' | Anticipated invariant check result |
| `expected_business_decision` | VARCHAR(64)| - | No | 'REJECT' | Anticipated business decision |
| `severity` | VARCHAR(16) | - | No | 'CRITICAL'| `CRITICAL`, `HIGH`, `MEDIUM` |
| `rationale` | TEXT | - | No | None | Technical scenario description |
| `injected_in_dataset` | BOOLEAN | - | No | True | Ground truth flag |
| `detected` | BOOLEAN | - | No | True | Detection status flag |

