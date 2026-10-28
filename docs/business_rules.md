# Business Rules & Financial Settlement Specifications

This document defines the deterministic business rules, eligibility criteria, financial formulas, and inventory constraints implemented across the platform.

---

## 1. Return Eligibility Rules Engine

Return eligibility is evaluated on a per-line basis using strict deterministic checks:

### 1.1 Verification Invariants
1. **Order Existence**: The referenced `order_id` must exist in the database.
2. **Customer Ownership**: The order's `customer_id` must match the requesting customer's ID.
3. **Delivery Status**: The order must have reached `DELIVERED` status with a recorded `delivery_date`. Requests prior to delivery are rejected with `ORDER_NOT_YET_DELIVERED`.
4. **Date Ordering**: `request_date` must be on or after `delivery_date`. If $t_{\text{request}} < t_{\text{delivery}}$, request is rejected.
5. **Quantity Bounds**:
   $$\text{requested\_quantity} \le (\text{purchased\_quantity} - \text{already\_returned\_quantity})$$
   Requests attempting to return more units than available are rejected with `RETURN_QTY_EXCEEDS_AVAILABLE`.
6. **Category Exclusion**: Products classified in non-returnable categories (`Food & Beverage`, `Perishable`, `Personal Care`, `Hazardous`) or flagged `is_returnable = False` are immediately rejected with `CATEGORY_EXCLUDED`.

### 1.2 Category Policy Windows
- **Consumer Electronics**: 14 calendar days from delivery date.
- **Apparel & Fashion**: 30 calendar days from delivery date.
- **Home & Kitchen**: 30 calendar days from delivery date.
- **Perishables / Hygiene**: 0 days (Strictly non-returnable).

### 1.3 Exception Override Workflow
If a return request is submitted after the policy window has elapsed:
- **Default Verdict**: `INELIGIBLE` with reason `RETURN_AFTER_WINDOW`.
- **Authorized Override**: Permitted only when explicitly authorized by an authorized supervisor. An override records:
  - `override_approved = True`
  - `override_by` (e.g. `MGR_RET_99`)
  - `override_reason` (e.g. "Customer satisfaction courtesy exception authorized by supervisor")
  - Audit event in `return_events` with type `EXCEPTION_OVERRIDDEN`

---

## 2. Return Authorization Rules

1. **Only Eligible Units**: Authorizations can only be issued for requests with status `FULLY_ELIGIBLE` or `PARTIALLY_ELIGIBLE`.
2. **Quantity Lock**: `approved_quantity` is set to `eligible_quantity`. Ineligible lines receive `approved_quantity = 0`.
3. **Double-Authorization Guard**: Exactly one `ReturnAuthorization` token can be issued per RMA. Subsequent authorization requests are blocked with HTTP 400.
4. **Order Line Reservation**: When an authorization is issued, the parent `OrderLine.returned_quantity` is immediately incremented by the authorized quantity, preventing concurrent duplicate returns from other RMAs.

---

## 3. Reverse Logistics & Shipment Rules

1. **Deterministic Shipment ID**: Format `RTS-2026-XXXXXX`.
2. **Delivery Before Inspection Invariant**: Physical items must be delivered and received at the intake dock (`shipment.status == 'DELIVERED'`) before an inspection can be recorded. Inspecting unreceived parcels is strictly blocked unless an explicit documented override is provided.

---

## 4. Inspection & Disposition Recommendation Matrix

Warehouse quality assurance records item condition, packaging condition, and damage classification:

| Item Condition | Packaging Condition | Damage Type | QA Result | Recommended Disposition | Restocking Fee Applied |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **UNOPENED** | INTACT | NONE | `PASS` | `RESTOCK` | No |
| **OPENED_LIKE_NEW** | INTACT | NONE | `PASS_WITH_RESTOCKING_FEE` | `RESTOCK` | Yes |
| **OPENED_LIKE_NEW** | DAMAGED_REPAIRABLE | PACKAGING_ONLY | `PASS_WITH_RESTOCKING_FEE` | `RESTOCK` | Yes |
| **SLIGHT_WEAR** | DAMAGED_REPAIRABLE | COSMETIC / IMPACT | `REFURBISHABLE` | `REFURBISH` | No |
| **SIGNIFICANT_DAMAGE**| ANY | ELECTRICAL / IMPACT | `REFURBISHABLE` | `REFURBISH` | No |
| **COUNTERFEIT** | ANY | TAMPERED | `QUARANTINE_REQUIRED` | `QUARANTINE` | No |
| **DESTROYED** | DESTROYED | WATER / CRUSHED | `REJECT_SCRAP` | `SCRAP` | No |

---

## 5. Refund Arithmetic & Idempotency Safeguards

Refunds are calculated using fixed-point `Decimal` arithmetic rounded to 2 decimal places (`ROUND_HALF_UP`).

### 5.1 Refund Formula
For a returned quantity $q_r$ from an order line with purchased quantity $q_p$, unit price $P$, allocated discount $D$, line tax $T$, and restocking fee percentage $F_{\text{pct}}$:

$$\text{gross\_item} = P \times q_r$$

$$\text{proportional\_discount} = \left(\frac{D}{q_p}\right) \times q_r$$

$$\text{base\_net} = \text{gross\_item} - \text{proportional\_discount}$$

$$\text{proportional\_tax} = \left(\frac{T}{q_p}\right) \times q_r$$

$$\text{restocking\_fee} = \begin{cases} \text{base\_net} \times \left(\frac{F_{\text{pct}}}{100}\right) & \text{if fee applied} \\ 0.00 & \text{otherwise} \end{cases}$$

$$\text{net\_refund} = \text{base\_net} + \text{proportional\_tax} - \text{restocking\_fee}$$

### 5.2 Maximum Refundable Limit
$$\text{max\_line\_paid} = \text{gross\_item} - \text{proportional\_discount} + \text{proportional\_tax}$$

$$\text{max\_allowable} = \text{max\_line\_paid} - \text{previously\_refunded}$$

**Invariant**:
$$\text{net\_refund} \le \text{max\_allowable}$$
Any refund attempt where $\text{net\_refund} > \text{max\_allowable}$ is rejected with `REFUND_EXCEEDS_PAID_AMOUNT`.

### 5.3 Idempotency Key Duplicate Prevention
- Every payout request requires a unique `idempotency_key` (e.g. `IDEMP-REF-000001-RMA-2026-000001`).
- If an idempotency key has already been settled, the platform:
  1. Immediately blocks payout execution.
  2. Records an entry in `refund_attempts` with `outcome = 'BLOCKED_DUPLICATE'`.
  3. Returns the original refund record with `blocked = True`.
  4. Never creates a duplicate disbursement record.

---

## 6. Inventory Disposition Rules

Supported destinations:
- **RESTOCK**: Re-enters active available inventory.
- **REFURBISH**: Routed to technical repair bench for restoration.
- **QUARANTINE**: Isolated for warranty investigation or fraud review.
- **SCRAP**: Written off for recycling or certified destruction.

### 6.1 Invariants
1. **Never Restock Uninspected Goods**: An item cannot have disposition `RESTOCK` without an associated `inspection_id` with result `PASS` or `PASS_WITH_RESTOCKING_FEE`.
2. **Never Exceed Approved Quantity**: Total disposed quantity across all dispositions for a return line cannot exceed `approved_quantity`.
3. **Auditable Movement**: Every completed disposition writes an immutable record to `inventory_movements` with `movement_id`, `from_location`, `to_location`, and timestamp.
4. **Split Dispositions**: Return lines with multiple units can be split into different dispositions (e.g. 1 unit `RESTOCK`, 1 unit `REFURBISH`), in which case the line status is marked `SPLIT`.
