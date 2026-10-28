from datetime import datetime, timezone, timedelta
from decimal import Decimal
import pytest
from app.models.entities import Customer, Product, ReturnPolicy, Order, OrderLine, AnomalyRecord
from app.core.config import settings

def setup_baseline_entities(db):
    now = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)
    
    # Policy
    pol = ReturnPolicy(
        policy_code="POL-ELEC-14",
        name="Electronics Policy",
        category="Electronics",
        return_window_days=14,
        restocking_fee_percent=Decimal("15.00"),
        requires_original_packaging=True,
        allow_opened_box=True,
        is_active=True,
        effective_from=now - timedelta(days=60)
    )
    db.add(pol)

    # Product
    prod = Product(
        sku="SKU-ELEC-TEST-01",
        name="Test Headphones",
        category="Electronics",
        price=Decimal("100.00"),
        cost=Decimal("40.00"),
        is_returnable=True,
        default_return_window_days=14,
        restockable=True,
        requires_serial_number=True,
        created_at=now - timedelta(days=60)
    )
    db.add(prod)
    db.flush()

    # Customer
    cust = Customer(
        customer_id="CUST-TEST-000001",
        first_name="Jane",
        last_name="Doe",
        email="jane.doe.test@example.com",
        segment="VIP",
        risk_score=0.05,
        created_at=now - timedelta(days=60)
    )
    db.add(cust)
    db.flush()

    # Order
    order = Order(
        order_id="ORD-TEST-000001",
        customer_id=cust.id,
        order_date=now - timedelta(days=5),
        delivery_date=now - timedelta(days=3),
        status="DELIVERED",
        subtotal=Decimal("200.00"),
        discount_amount=Decimal("20.00"),
        tax_amount=Decimal("14.40"),
        shipping_amount=Decimal("0.00"),
        total_amount=Decimal("194.40"),
        payment_method="CREDIT_CARD",
        shipping_address="123 Tech Way, Austin, TX",
        created_at=now - timedelta(days=5),
        updated_at=now - timedelta(days=3)
    )
    db.add(order)
    db.flush()

    ol = OrderLine(
        order_id=order.id,
        product_id=prod.id,
        line_number=1,
        quantity=2,
        unit_price=Decimal("100.00"),
        line_subtotal=Decimal("200.00"),
        allocated_discount=Decimal("20.00"),
        line_tax=Decimal("14.40"),
        total_line_amount=Decimal("194.40"),
        returned_quantity=0,
        created_at=now - timedelta(days=5)
    )
    db.add(ol)

    # Anomaly record
    anom = AnomalyRecord(
        anomaly_id="ANOM-TEST-000001",
        issue_type="RETURN_QTY_EXCEEDS_PURCHASED",
        affected_entity="ReturnLine",
        affected_business_id="RMAL-TEST-01",
        expected_detection_result="FAIL",
        expected_business_decision="REJECT",
        severity="CRITICAL",
        rationale="Unit test ground truth fixture",
        injected_in_dataset=True,
        detected=True
    )
    db.add(anom)

    db.commit()
    return cust, prod, order, ol

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_end_to_end_return_api_workflow(client, db_session):
    cust, prod, order, ol = setup_baseline_entities(db_session)

    # 1. Dashboard summary
    dash_res = client.get("/api/dashboard/summary")
    assert dash_res.status_code == 200
    assert dash_res.json()["cards"]["total_orders"] >= 1

    # 2. Submit Return Request
    create_payload = {
        "order_id": order.order_id,
        "customer_id": cust.customer_id,
        "reason_category": "DEFECTIVE",
        "channel": "WEB",
        "customer_comments": "Audio buzzing in right earbud",
        "lines": [
            {
                "order_line_id": ol.id,
                "requested_quantity": 1
            }
        ]
    }
    submit_res = client.post("/api/returns", json=create_payload)
    assert submit_res.status_code == 200
    rma_number = submit_res.json()["rma_number"]
    assert submit_res.json()["overall_eligibility"] == "FULLY_ELIGIBLE"

    # 3. Get Return Details
    detail_res = client.get(f"/api/returns/{rma_number}")
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["rma_number"] == rma_number
    assert len(data["lines"]) == 1
    return_line_id = data["lines"][0]["return_line_id"]

    # 4. Authorize Return
    auth_res = client.post(f"/api/returns/{rma_number}/authorize", json={
        "authorized_by": "MANAGER_TEST",
        "validity_days": 14
    })
    assert auth_res.status_code == 200
    assert "authorization_number" in auth_res.json()

    # 5. Prevent Duplicate Authorization
    dup_auth_res = client.post(f"/api/returns/{rma_number}/authorize", json={
        "authorized_by": "MANAGER_TEST"
    })
    assert dup_auth_res.status_code == 400
    assert "already authorized" in dup_auth_res.json()["detail"]

    # 6. Create Return Shipment
    ship_res = client.post(f"/api/returns/{rma_number}/shipments", json={
        "carrier": "UPS",
        "destination_warehouse": "WH-CENTRAL-01"
    })
    assert ship_res.status_code == 200
    shipment_id = ship_res.json()["shipment_id"]

    # 7. Restock Before Receipt blocked
    disp_blocked = client.post(f"/api/returns/{rma_number}/disposition", json={
        "return_line_id": return_line_id,
        "disposition_type": "RESTOCK",
        "quantity": 1
    })
    assert disp_blocked.status_code == 400
    assert "RESTOCK_BEFORE_RECEIPT" in disp_blocked.json()["detail"]

    # 8. Receive Shipment
    rec_res = client.post(f"/api/shipments/{shipment_id}/receive", json={
        "receiver_id": "WH_STATION_TEST"
    })
    assert rec_res.status_code == 200
    assert rec_res.json()["status"] == "DELIVERED"

    # 9. Warehouse Inspection
    insp_res = client.post(f"/api/shipments/{shipment_id}/inspect", json={
        "return_line_id": return_line_id,
        "inspected_quantity": 1,
        "item_condition": "OPENED_LIKE_NEW",
        "packaging_condition": "INTACT",
        "damage_type": "NONE",
        "inspector_id": "QA_INSP_01"
    })
    assert insp_res.status_code == 200
    assert insp_res.json()["result"] == "PASS_WITH_RESTOCKING_FEE"
    assert insp_res.json()["recommended_disposition"] == "RESTOCK"

    # 10. Execute Disposition (RESTOCK)
    disp_res = client.post(f"/api/returns/{rma_number}/disposition", json={
        "return_line_id": return_line_id,
        "disposition_type": "RESTOCK",
        "quantity": 1,
        "warehouse_location": "WH-BIN-A12",
        "technician_id": "TECH_01"
    })
    assert disp_res.status_code == 200
    assert disp_res.json()["disposition_type"] == "RESTOCK"

    # 11. Process Refund
    idempotency_key = f"IDEMP-TEST-{rma_number}"
    refund_res = client.post(f"/api/returns/{rma_number}/refund", json={
        "idempotency_key": idempotency_key,
        "return_line_id": return_line_id,
        "refund_method": "ORIGINAL_PAYMENT",
        "apply_restocking_fee": True
    })
    assert refund_res.status_code == 200
    assert refund_res.json()["status"] == "COMPLETED"
    assert refund_res.json()["blocked"] is False
    assert refund_res.json()["net_refund_amount"] > 0

    # 12. Idempotent Duplicate Payment Block
    dup_refund_res = client.post(f"/api/returns/{rma_number}/refund", json={
        "idempotency_key": idempotency_key,
        "return_line_id": return_line_id
    })
    assert dup_refund_res.status_code == 200
    assert dup_refund_res.json()["blocked"] is True
    assert dup_refund_res.json()["status"] == "BLOCKED_DUPLICATE"

    # 13. Verify Audit Events
    audit_res = client.get("/api/audit-events")
    assert audit_res.status_code == 200
    assert len(audit_res.json()["items"]) > 0

    # 14. Verify Exceptions
    exc_res = client.get("/api/exceptions")
    assert exc_res.status_code == 200
    assert exc_res.json()["summary"]["blocked_duplicates_count"] >= 1

    # 15. Verify Validation Report
    val_res = client.get("/api/validation/report")
    assert val_res.status_code == 200
    assert val_res.json()["overall_status"] == "PASS"

    # 16. Admin Endpoint Security
    gen_no_auth = client.post("/api/admin/generate-data", json={"profile": "starter"})
    assert gen_no_auth.status_code == 403

    gen_auth = client.post(
        "/api/admin/generate-data",
        json={"profile": "starter", "seed": 20261022},
        headers={"X-Admin-Key": settings.ADMIN_API_KEY}
    )
    assert gen_auth.status_code == 200
    assert gen_auth.json()["summary"]["status"] == "SUCCESS"
