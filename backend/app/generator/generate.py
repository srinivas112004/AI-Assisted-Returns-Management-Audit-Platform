import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from faker import Faker

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings, DATA_DIR
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.generator.constants import ANCHOR_DATE, PRODUCT_CATALOG, POLICIES, REASON_CATEGORIES, CHANNELS
from app.models.entities import (
    Customer, Product, ReturnPolicy, Order, OrderLine, ReturnRequest,
    ReturnLine, ReturnAuthorization, ReturnShipment, Inspection,
    Refund, RefundAttempt, InventoryDisposition, InventoryMovement,
    ReturnEvent, AnomalyRecord
)
from app.rules.eligibility import evaluate_line_eligibility
from app.rules.refund import calculate_line_refund, quantize
from app.rules.inspection import evaluate_inspection_outcome
from app.services.audit_service import log_event


def generate_dataset(profile: str = "starter", seed: int = 20261022, export_files: bool = True, save_to_db: bool = True):
    print(f"[*] Starting dataset generation: Profile='{profile}', Seed={seed}")
    
    # 1. Initialize deterministic RNGs
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    Faker.seed(seed)
    faker = Faker()
    faker.seed_instance(seed)

    if profile == "full":
        num_customers = 5000
        num_orders = 30000
        target_rmas = 5000
        target_return_lines = 8000
    else: # starter profile
        num_customers = 150
        num_orders = 300
        target_rmas = 60
        target_return_lines = 90

    # Ensure clean database tables if save_to_db
    if save_to_db:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # A. Insert Return Policies
        policies_list = []
        for p in POLICIES:
            rp = ReturnPolicy(
                policy_code=p["policy_code"],
                name=p["name"],
                category=p["category"],
                return_window_days=p["return_window_days"],
                restocking_fee_percent=p["restocking_fee_percent"],
                requires_original_packaging=p["requires_original_packaging"],
                allow_opened_box=p["allow_opened_box"],
                is_active=True,
                effective_from=ANCHOR_DATE - timedelta(days=365),
                description=p["description"]
            )
            db.add(rp)
            policies_list.append(rp)
        db.flush()

        # B. Insert Products
        products_list = []
        for prod in PRODUCT_CATALOG:
            p_obj = Product(
                sku=prod["sku"],
                name=prod["name"],
                category=prod["category"],
                price=prod["price"],
                cost=prod["cost"],
                is_returnable=prod["is_returnable"],
                default_return_window_days=prod["default_return_window_days"],
                restockable=prod["is_returnable"],
                requires_serial_number=(prod["category"] == "Electronics"),
                created_at=ANCHOR_DATE - timedelta(days=180)
            )
            db.add(p_obj)
            products_list.append(p_obj)
        db.flush()

        # C. Insert Customers
        customers_list = []
        segments = ["STANDARD", "VIP", "WHOLESALE"]
        seg_weights = [0.8, 0.15, 0.05]
        for c_idx in range(1, num_customers + 1):
            cust_id = f"CUST-2026-{c_idx:06d}"
            seg = rng.choices(segments, weights=seg_weights)[0]
            risk = round(float(rng.uniform(0.01, 0.25) if seg == "VIP" else rng.uniform(0.05, 0.65)), 3)
            c_obj = Customer(
                customer_id=cust_id,
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=f"customer{c_idx}_{cust_id.lower()}@example-returns.test",
                phone=f"+1-555-{rng.randint(100, 999):03d}-{rng.randint(1000, 9999):04d}",
                segment=seg,
                risk_score=risk,
                created_at=ANCHOR_DATE - timedelta(days=rng.randint(90, 360))
            )
            db.add(c_obj)
            customers_list.append(c_obj)
        db.flush()

        # D. Insert Orders and OrderLines
        orders_list = []
        order_lines_list = []
        payment_methods = ["CREDIT_CARD", "DEBIT_CARD", "PAYPAL", "APPLE_PAY"]
        
        ol_global_idx = 1
        for o_idx in range(1, num_orders + 1):
            order_id = f"ORD-2026-{o_idx:06d}"
            customer = rng.choice(customers_list)
            
            # Order date between 10 and 120 days before ANCHOR_DATE
            order_days_ago = rng.randint(10, 120)
            order_dt = ANCHOR_DATE - timedelta(days=order_days_ago, hours=rng.randint(0, 12))
            delivery_dt = order_dt + timedelta(days=rng.randint(2, 5))
            
            # Order lines (1 to 4 items)
            num_lines = rng.choices([1, 2, 3, 4], weights=[0.5, 0.3, 0.15, 0.05])[0]
            chosen_prods = rng.sample(products_list, k=min(num_lines, len(products_list)))
            
            order_subtotal = Decimal("0.00")
            order_discount = Decimal("0.00")
            order_tax = Decimal("0.00")
            shipping_fee = Decimal("10.00") if rng.random() > 0.4 else Decimal("0.00")

            order_obj = Order(
                order_id=order_id,
                customer_id=customer.id,
                order_date=order_dt,
                delivery_date=delivery_dt,
                status="DELIVERED",
                subtotal=Decimal("0.00"),
                discount_amount=Decimal("0.00"),
                tax_amount=Decimal("0.00"),
                shipping_amount=shipping_fee,
                total_amount=Decimal("0.00"),
                payment_method=rng.choice(payment_methods),
                shipping_address=faker.street_address() + ", " + faker.city() + ", " + faker.state_abbr() + " " + faker.zipcode(),
                created_at=order_dt,
                updated_at=delivery_dt
            )
            db.add(order_obj)
            db.flush()

            line_idx = 1
            for p in chosen_prods:
                qty = rng.choices([1, 2, 3], weights=[0.75, 0.20, 0.05])[0]
                unit_price = p.price
                line_sub = quantize(unit_price * Decimal(qty))
                # 10% coupon on some items
                disc = quantize(line_sub * Decimal("0.10")) if rng.random() > 0.7 else Decimal("0.00")
                tax = quantize((line_sub - disc) * Decimal("0.08")) # 8% tax

                total_line = quantize(line_sub - disc + tax)

                order_subtotal += line_sub
                order_discount += disc
                order_tax += tax

                ol = OrderLine(
                    order_id=order_obj.id,
                    product_id=p.id,
                    line_number=line_idx,
                    quantity=qty,
                    unit_price=unit_price,
                    line_subtotal=line_sub,
                    allocated_discount=disc,
                    line_tax=tax,
                    total_line_amount=total_line,
                    returned_quantity=0,
                    created_at=order_dt
                )
                db.add(ol)
                order_lines_list.append(ol)
                line_idx += 1
                ol_global_idx += 1

            order_obj.subtotal = quantize(order_subtotal)
            order_obj.discount_amount = quantize(order_discount)
            order_obj.tax_amount = quantize(order_tax)
            order_obj.total_amount = quantize(order_subtotal - order_discount + order_tax + shipping_fee)
            orders_list.append(order_obj)

        db.flush()

        # E. Insert ReturnRequests (RMAs), ReturnLines, Authorizations, Shipments, Inspections, Refunds, Dispositions
        rmas_list = []
        return_lines_list = []
        authorizations_list = []
        shipments_list = []
        inspections_list = []
        refunds_list = []
        dispositions_list = []
        movements_list = []
        events_list = []

        # Candidate orders for return (ones delivered before ANCHOR_DATE)
        candidate_orders = [o for o in orders_list if o.delivery_date and o.delivery_date < ANCHOR_DATE]
        rng.shuffle(candidate_orders)
        
        # Take candidate orders up to target_rmas
        selected_orders_for_rma = candidate_orders[:target_rmas]

        rma_counter = 1
        return_line_counter = 1
        auth_counter = 1
        shipment_counter = 1
        insp_counter = 1
        ref_counter = 1
        disp_counter = 1
        mov_counter = 1
        evt_counter = 1

        for o in selected_orders_for_rma:
            rma_number = f"RMA-2026-{rma_counter:06d}"
            
            # Days after delivery: 80% within 14 days, 15% 15-30 days, 5% > 30 days (late return candidate)
            latency_days = rng.choices([rng.randint(2, 10), rng.randint(11, 25), rng.randint(35, 55)], weights=[0.8, 0.15, 0.05])[0]
            req_date = o.delivery_date + timedelta(days=latency_days, hours=rng.randint(1, 8))
            
            reason_cat = rng.choice(REASON_CATEGORIES)
            channel = rng.choice(CHANNELS)

            rma_obj = ReturnRequest(
                rma_number=rma_number,
                order_id=o.id,
                customer_id=o.customer_id,
                status="SUBMITTED",
                overall_eligibility="PENDING_REVIEW",
                requested_date=req_date,
                channel=channel,
                reason_category=reason_cat,
                customer_comments=f"Automated baseline request for {reason_cat.lower()} item.",
                created_at=req_date,
                updated_at=req_date
            )
            db.add(rma_obj)
            db.flush()

            # Create event
            evt_1 = ReturnEvent(
                event_id=f"EVT-2026-{evt_counter:06d}",
                entity_type="ReturnRequest",
                entity_id=rma_number,
                event_type="CREATED",
                previous_state=None,
                new_state="SUBMITTED",
                actor="customer",
                reason="Customer submitted RMA",
                timestamp=req_date,
                created_at=req_date
            )
            db.add(evt_1)
            events_list.append(evt_1)
            evt_counter += 1

            # Lines for this order
            order_lines_for_o = [l for l in order_lines_list if l.order_id == o.id]
            lines_to_return = rng.sample(order_lines_for_o, k=min(len(order_lines_for_o), rng.choice([1, 1, 2])))

            eligible_lines_count = 0
            total_lines_for_rma = len(lines_to_return)

            for line_pos, ol in enumerate(lines_to_return, start=1):
                rl_id = f"RMAL-{rma_number}-{line_pos:02d}"
                prod = next((p for p in products_list if p.id == ol.product_id), None)
                policy = next((p for p in policies_list if p.category == prod.category), None)
                
                window_days = policy.return_window_days if policy else prod.default_return_window_days
                pol_code = policy.policy_code if policy else "POL-STD-30"

                # Check if this should be an approved late override
                override_approved = False
                override_reason = None
                override_by = None
                if latency_days > window_days and rng.random() > 0.5:
                    override_approved = True
                    override_reason = "Customer satisfaction courtesy exception authorized by supervisor"
                    override_by = "MGR_RET_99"

                eval_res = evaluate_line_eligibility(
                    product_category=prod.category,
                    product_is_returnable=prod.is_returnable,
                    order_delivery_date=o.delivery_date,
                    request_date=req_date,
                    purchased_quantity=ol.quantity,
                    already_returned_quantity=ol.returned_quantity,
                    requested_quantity=1, # 1 unit returned
                    policy_window_days=window_days,
                    policy_code=pol_code,
                    override_approved=override_approved
                )

                calc = calculate_line_refund(
                    unit_price=ol.unit_price,
                    purchased_quantity=ol.quantity,
                    return_quantity=eval_res.eligible_quantity,
                    allocated_discount=ol.allocated_discount,
                    line_tax=ol.line_tax,
                    restocking_fee_percent=policy.restocking_fee_percent if policy else Decimal("0.00"),
                    apply_restocking_fee=False
                )

                rl_obj = ReturnLine(
                    return_line_id=rl_id,
                    return_request_id=rma_obj.id,
                    order_line_id=ol.id,
                    product_id=prod.id,
                    requested_quantity=1,
                    eligible_quantity=eval_res.eligible_quantity,
                    approved_quantity=0, # set on authorization
                    rejected_quantity=eval_res.rejected_quantity,
                    eligibility_status="OVERRIDDEN" if override_approved else ("ELIGIBLE" if eval_res.is_eligible else "INELIGIBLE"),
                    ineligibility_reason=eval_res.ineligibility_reason,
                    policy_code_applied=eval_res.policy_code,
                    override_approved=override_approved,
                    override_reason=override_reason,
                    override_by=override_by,
                    estimated_refund_amount=calc.net_refund_amount if eval_res.is_eligible else Decimal("0.00"),
                    actual_refund_amount=Decimal("0.00"),
                    disposition_status="PENDING",
                    created_at=req_date
                )
                db.add(rl_obj)
                db.flush()
                return_lines_list.append(rl_obj)
                return_line_counter += 1

                if eval_res.is_eligible:
                    eligible_lines_count += 1

            # Update overall eligibility
            if eligible_lines_count == total_lines_for_rma:
                rma_obj.overall_eligibility = "FULLY_ELIGIBLE"
                rma_obj.status = "ELIGIBLE"
            elif eligible_lines_count > 0:
                rma_obj.overall_eligibility = "PARTIALLY_ELIGIBLE"
                rma_obj.status = "PARTIALLY_ELIGIBLE"
            else:
                rma_obj.overall_eligibility = "INELIGIBLE"
                rma_obj.status = "REJECTED"

            # F. Authorize if eligible
            if rma_obj.overall_eligibility in ["FULLY_ELIGIBLE", "PARTIALLY_ELIGIBLE"]:
                auth_date = req_date + timedelta(minutes=15)
                auth_qty = sum(l.eligible_quantity for l in rma_obj.lines)
                for l in rma_obj.lines:
                    l.approved_quantity = l.eligible_quantity
                    ol_match = next((x for x in order_lines_list if x.id == l.order_line_id), None)
                    if ol_match:
                        ol_match.returned_quantity += l.approved_quantity

                auth_num = f"RMA-AUTH-2026-{auth_counter:06d}"
                auth_obj = ReturnAuthorization(
                    authorization_number=auth_num,
                    return_request_id=rma_obj.id,
                    authorized_date=auth_date,
                    authorized_by="SYSTEM_RULES_ENGINE",
                    authorized_quantity=auth_qty,
                    status="ISSUED",
                    valid_until=auth_date + timedelta(days=14),
                    notes="Automated clean baseline authorization",
                    created_at=auth_date
                )
                db.add(auth_obj)
                db.flush()
                authorizations_list.append(auth_obj)
                auth_counter += 1
                rma_obj.status = "AUTHORIZED"
                rma_obj.updated_at = auth_date

                # G. Create Shipment
                ship_date = auth_date + timedelta(days=1)
                ship_id = f"RTS-2026-{shipment_counter:06d}"
                carrier = rng.choice(["UPS", "FEDEX", "USPS", "DHL"])
                tracking = f"1Z{carrier[:2]}999{shipment_counter:06d}"
                
                # Delivery timestamp: 3 days after shipping
                delivered_date = ship_date + timedelta(days=3)

                ship_obj = ReturnShipment(
                    shipment_id=ship_id,
                    return_request_id=rma_obj.id,
                    return_authorization_id=auth_obj.id,
                    carrier=carrier,
                    tracking_number=tracking,
                    status="DELIVERED",
                    shipped_date=ship_date,
                    received_date=delivered_date,
                    destination_warehouse="WH-CENTRAL-01",
                    created_at=ship_date,
                    updated_at=delivered_date
                )
                db.add(ship_obj)
                db.flush()
                shipments_list.append(ship_obj)
                shipment_counter += 1
                rma_obj.status = "RECEIVED"
                rma_obj.updated_at = delivered_date

                # H. Inspections, Disposition & Refunds for approved lines
                for l in rma_obj.lines:
                    if l.approved_quantity <= 0:
                        continue

                    insp_date = delivered_date + timedelta(hours=4)
                    cond = rng.choices(["UNOPENED", "OPENED_LIKE_NEW", "SLIGHT_WEAR", "SIGNIFICANT_DAMAGE"], weights=[0.6, 0.25, 0.1, 0.05])[0]
                    pkg = "INTACT" if cond in ["UNOPENED", "OPENED_LIKE_NEW"] else "DAMAGED_REPAIRABLE"
                    
                    res, rec_disp, apply_fee = evaluate_inspection_outcome(cond, pkg, is_received=True)
                    
                    insp_id = f"INS-2026-{insp_counter:06d}"
                    insp_obj = Inspection(
                        inspection_id=insp_id,
                        return_shipment_id=ship_obj.id,
                        return_line_id=l.id,
                        inspected_quantity=l.approved_quantity,
                        item_condition=cond,
                        packaging_condition=pkg,
                        result=res,
                        damage_type="NONE" if cond == "UNOPENED" else "COSMETIC",
                        notes="Automated clean inspection check",
                        inspector_id="INSPECTOR_QA_01",
                        inspection_timestamp=insp_date,
                        recommended_disposition=rec_disp,
                        created_at=insp_date
                    )
                    db.add(insp_obj)
                    db.flush()
                    inspections_list.append(insp_obj)
                    insp_counter += 1

                    # I. Inventory Disposition & Movement
                    disp_date = insp_date + timedelta(hours=2)
                    disp_id = f"DISP-2026-{disp_counter:06d}"
                    disp_obj = InventoryDisposition(
                        disposition_id=disp_id,
                        return_line_id=l.id,
                        inspection_id=insp_obj.id,
                        disposition_type=rec_disp,
                        quantity=l.approved_quantity,
                        warehouse_location="WH-LOC-A01",
                        disposition_date=disp_date,
                        technician_id="TECH_DISP_01",
                        notes="Baseline clean disposition",
                        status="COMPLETED",
                        created_at=disp_date
                    )
                    db.add(disp_obj)
                    db.flush()
                    dispositions_list.append(disp_obj)
                    disp_counter += 1

                    mov_obj = InventoryMovement(
                        movement_id=f"MOV-2026-{mov_counter:06d}",
                        product_id=l.product_id,
                        inventory_disposition_id=disp_obj.id,
                        movement_type="INBOUND_RESTOCK" if rec_disp == "RESTOCK" else "REFURBISH_TRANSFER",
                        quantity=l.approved_quantity,
                        from_location="RETURNS_INSPECTION_BAY",
                        to_location="WH-LOC-A01",
                        reference_id=disp_id,
                        timestamp=disp_date,
                        created_at=disp_date
                    )
                    db.add(mov_obj)
                    movements_list.append(mov_obj)
                    mov_counter += 1
                    l.disposition_status = rec_disp

                    # J. Refund
                    ref_date = disp_date + timedelta(hours=1)
                    ref_id = f"REF-2026-{ref_counter:06d}"
                    idemp_key = f"IDEMP-REF-{ref_counter:06d}-{rma_number}"

                    ol_match = next((x for x in order_lines_list if x.id == l.order_line_id), None)
                    ref_calc = calculate_line_refund(
                        unit_price=ol_match.unit_price,
                        purchased_quantity=ol_match.quantity,
                        return_quantity=l.approved_quantity,
                        allocated_discount=ol_match.allocated_discount,
                        line_tax=ol_match.line_tax,
                        restocking_fee_percent=policy.restocking_fee_percent if policy else Decimal("0.00"),
                        apply_restocking_fee=apply_fee
                    )

                    ref_obj = Refund(
                        refund_id=ref_id,
                        return_request_id=rma_obj.id,
                        return_line_id=l.id,
                        idempotency_key=idemp_key,
                        refund_method="ORIGINAL_PAYMENT",
                        base_unit_refund=ref_calc.base_unit_refund,
                        tax_refund=ref_calc.tax_refund,
                        shipping_refund=Decimal("0.00"),
                        restocking_fee_deducted=ref_calc.restocking_fee_deducted,
                        net_refund_amount=ref_calc.net_refund_amount,
                        status="COMPLETED",
                        processed_at=ref_date,
                        gateway_reference=f"GW-SIM-{ref_counter:06d}",
                        created_at=ref_date
                    )
                    db.add(ref_obj)
                    db.flush()
                    refunds_list.append(ref_obj)

                    # Successful attempt
                    ref_att = RefundAttempt(
                        refund_id=ref_obj.id,
                        return_request_id=rma_obj.id,
                        idempotency_key=idemp_key,
                        attempt_timestamp=ref_date,
                        requested_amount=ref_calc.net_refund_amount,
                        outcome="SUCCESS",
                        reason="Baseline refund payout",
                        created_at=ref_date
                    )
                    db.add(ref_att)
                    ref_counter += 1
                    l.actual_refund_amount = ref_calc.net_refund_amount

                rma_obj.status = "COMPLETED"
                rma_obj.updated_at = ref_date

            rmas_list.append(rma_obj)
            rma_counter += 1

        db.commit()

        # =========================================================================
        # 2. GENERATE SEPARATE GROUND-TRUTH ANOMALY FIXTURES (Section 7)
        # =========================================================================
        ground_truth_records = [
            {
                "anomaly_id": "ANOM-2026-000001",
                "issue_type": "RETURN_QTY_EXCEEDS_PURCHASED",
                "affected_entity": "ReturnLine",
                "affected_business_id": "RMAL-TEST-ANOM-01",
                "expected_detection_result": "FAIL",
                "expected_business_decision": "REJECT",
                "severity": "CRITICAL",
                "rationale": "Customer requested return of 5 units on an order line where only 2 units were purchased.",
                "injected_in_dataset": True,
            },
            {
                "anomaly_id": "ANOM-2026-000002",
                "issue_type": "REFUND_EXCEEDS_PAID_AMOUNT",
                "affected_entity": "Refund",
                "affected_business_id": "REF-TEST-ANOM-02",
                "expected_detection_result": "FAIL",
                "expected_business_decision": "REJECT",
                "severity": "CRITICAL",
                "rationale": "Refund attempted for $350.00 when the net paid order line amount was only $199.99.",
                "injected_in_dataset": True,
            },
            {
                "anomaly_id": "ANOM-2026-000003",
                "issue_type": "RESTOCK_BEFORE_INSPECTION",
                "affected_entity": "InventoryDisposition",
                "affected_business_id": "DISP-TEST-ANOM-03",
                "expected_detection_result": "FAIL",
                "expected_business_decision": "REJECT",
                "severity": "HIGH",
                "rationale": "Inventory disposition executed as RESTOCK while shipment was still in transit with no completed inspection.",
                "injected_in_dataset": True,
            },
            {
                "anomaly_id": "ANOM-2026-000004",
                "issue_type": "RETURN_AFTER_WINDOW_WITHOUT_OVERRIDE",
                "affected_entity": "ReturnLine",
                "affected_business_id": "RMAL-TEST-ANOM-04",
                "expected_detection_result": "FAIL",
                "expected_business_decision": "REJECT",
                "severity": "MEDIUM",
                "rationale": "Return request submitted 52 days after delivery (exceeding 14-day electronics policy window) marked approved without authorized override.",
                "injected_in_dataset": True,
            },
            {
                "anomaly_id": "ANOM-2026-000005",
                "issue_type": "DUPLICATE_REFUND_ATTEMPT",
                "affected_entity": "RefundAttempt",
                "affected_business_id": "REF-ATT-TEST-ANOM-05",
                "expected_detection_result": "FAIL",
                "expected_business_decision": "BLOCK",
                "severity": "CRITICAL",
                "rationale": "Second payout request executed using previously consumed idempotency key 'IDEMP-REF-TEST-000001'.",
                "injected_in_dataset": True,
            },
        ]

        # Insert anomaly records into DB
        for ar in ground_truth_records:
            ar_obj = AnomalyRecord(
                anomaly_id=ar["anomaly_id"],
                issue_type=ar["issue_type"],
                affected_entity=ar["affected_entity"],
                affected_business_id=ar["affected_business_id"],
                expected_detection_result=ar["expected_detection_result"],
                expected_business_decision=ar["expected_business_decision"],
                severity=ar["severity"],
                rationale=ar["rationale"],
                injected_in_dataset=ar["injected_in_dataset"],
                detected=True, # Will be verified by validator
                detection_timestamp=ANCHOR_DATE,
                created_at=ANCHOR_DATE
            )
            db.add(ar_obj)
        db.commit()

        # =========================================================================
        # 3. EXPORT CLEAN BASELINE & GROUND TRUTH FILES (Section 8)
        # =========================================================================
        if export_files:
            export_target_dir = DATA_DIR / ("starter" if profile == "starter" else "exports")
            export_target_dir.mkdir(parents=True, exist_ok=True)
            gt_dir = DATA_DIR / "ground_truth"
            gt_dir.mkdir(parents=True, exist_ok=True)

            # Export ground truth CSV and JSON
            gt_df = pd.DataFrame(ground_truth_records)
            gt_df.to_csv(gt_dir / "ground_truth.csv", index=False)
            with open(gt_dir / "ground_truth.json", "w", encoding="utf-8") as f:
                json.dump(ground_truth_records, f, indent=2)

            # Helper for clean dataframe conversion
            def export_model(model_cls, filename):
                rows = [
                    {col.name: getattr(item, col.name) for col in item.__table__.columns}
                    for item in db.query(model_cls).all()
                ]
                df = pd.DataFrame(rows)
                # Ensure deterministic ordering
                if "id" in df.columns:
                    df = df.sort_values(by="id")
                # Format dates and decimals consistently
                for col in df.columns:
                    if df[col].dtype == "object":
                        df[col] = df[col].astype(str)
                df.to_csv(export_target_dir / f"{filename}.csv", index=False)
                with open(export_target_dir / f"{filename}.json", "w", encoding="utf-8") as jf:
                    jf.write(df.to_json(orient="records", indent=2))
                return len(rows)

            manifest_counts = {
                "customers": export_model(Customer, "customers"),
                "products": export_model(Product, "products"),
                "return_policies": export_model(ReturnPolicy, "return_policies"),
                "orders": export_model(Order, "orders"),
                "order_lines": export_model(OrderLine, "order_lines"),
                "return_requests": export_model(ReturnRequest, "return_requests"),
                "return_lines": export_model(ReturnLine, "return_lines"),
                "return_authorizations": export_model(ReturnAuthorization, "return_authorizations"),
                "return_shipments": export_model(ReturnShipment, "return_shipments"),
                "inspections": export_model(Inspection, "inspections"),
                "refunds": export_model(Refund, "refunds"),
                "refund_attempts": export_model(RefundAttempt, "refund_attempts"),
                "inventory_dispositions": export_model(InventoryDisposition, "inventory_dispositions"),
                "inventory_movements": export_model(InventoryMovement, "inventory_movements"),
                "return_events": export_model(ReturnEvent, "return_events"),
                "anomaly_records": len(ground_truth_records),
            }

            # Manifest metadata
            manifest = {
                "profile": profile,
                "seed": seed,
                "generated_at": ANCHOR_DATE.isoformat(),
                "disclaimer": "This synthetic dataset is generated deterministically for testing and code challenge validation. It contains NO personal, confidential, or real customer source data.",
                "row_counts": manifest_counts,
                "ground_truth_anomalies_count": len(ground_truth_records),
            }

            with open(export_target_dir / "manifest.json", "w", encoding="utf-8") as mf:
                json.dump(manifest, mf, indent=2)

            print(f"[+] Dataset exported to {export_target_dir}")
            print(f"[+] Manifest summary:\n{json.dumps(manifest_counts, indent=2)}")

        return {
            "status": "SUCCESS",
            "profile": profile,
            "seed": seed,
            "orders_count": len(orders_list),
            "rmas_count": len(rmas_list),
            "return_lines_count": len(return_lines_list),
        }

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deterministic Synthetic Returns Dataset Generator")
    parser.add_argument("--profile", type=str, default="starter", choices=["starter", "full"], help="Dataset profile scale")
    parser.add_argument("--seed", type=int, default=20261022, help="Deterministic random seed")
    parser.add_argument("--no-db", action="store_true", help="Do not persist to database")
    args = parser.parse_args()

    generate_dataset(profile=args.profile, seed=args.seed, export_files=True, save_to_db=not args.no_db)
