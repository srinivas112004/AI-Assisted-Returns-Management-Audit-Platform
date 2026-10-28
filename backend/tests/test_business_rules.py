from datetime import datetime, timezone, timedelta
from decimal import Decimal
import pytest

from app.rules.eligibility import evaluate_line_eligibility
from app.rules.refund import calculate_line_refund, quantize
from app.rules.inspection import evaluate_inspection_outcome
from app.rules.disposition import validate_disposition_action

def test_eligible_return():
    now = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)
    delivery = now - timedelta(days=5)

    res = evaluate_line_eligibility(
        product_category="Apparel",
        product_is_returnable=True,
        order_delivery_date=delivery,
        request_date=now,
        purchased_quantity=2,
        already_returned_quantity=0,
        requested_quantity=1,
        policy_window_days=30
    )
    assert res.is_eligible is True
    assert res.eligible_quantity == 1
    assert res.rejected_quantity == 0
    assert res.requires_override is False

def test_ineligible_return_category_exclusion():
    now = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)
    delivery = now - timedelta(days=2)

    res = evaluate_line_eligibility(
        product_category="Food",
        product_is_returnable=False,
        order_delivery_date=delivery,
        request_date=now,
        purchased_quantity=1,
        already_returned_quantity=0,
        requested_quantity=1,
        policy_window_days=0
    )
    assert res.is_eligible is False
    assert res.rejected_quantity == 1
    assert "CATEGORY_EXCLUDED" in res.ineligibility_reason

def test_late_return_without_override():
    now = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)
    delivery = now - timedelta(days=45) # 45 days > 30-day window

    res = evaluate_line_eligibility(
        product_category="Electronics",
        product_is_returnable=True,
        order_delivery_date=delivery,
        request_date=now,
        purchased_quantity=1,
        already_returned_quantity=0,
        requested_quantity=1,
        policy_window_days=14,
        override_approved=False
    )
    assert res.is_eligible is False
    assert res.requires_override is True
    assert "RETURN_AFTER_WINDOW" in res.ineligibility_reason

def test_late_return_with_authorized_override():
    now = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)
    delivery = now - timedelta(days=45)

    res = evaluate_line_eligibility(
        product_category="Electronics",
        product_is_returnable=True,
        order_delivery_date=delivery,
        request_date=now,
        purchased_quantity=1,
        already_returned_quantity=0,
        requested_quantity=1,
        policy_window_days=14,
        override_approved=True
    )
    assert res.is_eligible is True
    assert res.eligible_quantity == 1
    assert res.requires_override is True

def test_quantity_exceeding_purchased():
    now = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)
    delivery = now - timedelta(days=5)

    res = evaluate_line_eligibility(
        product_category="Apparel",
        product_is_returnable=True,
        order_delivery_date=delivery,
        request_date=now,
        purchased_quantity=2,
        already_returned_quantity=0,
        requested_quantity=5, # Requested 5 > Purchased 2
        policy_window_days=30
    )
    assert res.is_eligible is False
    assert "RETURN_QTY_EXCEEDS_AVAILABLE" in res.ineligibility_reason

def test_partial_return_and_remaining_limit():
    now = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)
    delivery = now - timedelta(days=5)

    # 1 of 2 already returned, requesting 1
    res1 = evaluate_line_eligibility(
        product_category="Apparel",
        product_is_returnable=True,
        order_delivery_date=delivery,
        request_date=now,
        purchased_quantity=2,
        already_returned_quantity=1,
        requested_quantity=1,
        policy_window_days=30
    )
    assert res1.is_eligible is True
    assert res1.eligible_quantity == 1

    # 2 of 2 already returned, requesting 1 more
    res2 = evaluate_line_eligibility(
        product_category="Apparel",
        product_is_returnable=True,
        order_delivery_date=delivery,
        request_date=now,
        purchased_quantity=2,
        already_returned_quantity=2,
        requested_quantity=1,
        policy_window_days=30
    )
    assert res2.is_eligible is False
    assert "ALL_PURCHASED_UNITS_ALREADY_RETURNED" in res2.ineligibility_reason

def test_refund_arithmetic_precision():
    calc = calculate_line_refund(
        unit_price=Decimal("199.99"),
        purchased_quantity=2,
        return_quantity=1,
        allocated_discount=Decimal("20.00"),
        line_tax=Decimal("14.40"),
        restocking_fee_percent=Decimal("15.00"),
        apply_restocking_fee=True
    )
    assert calc.is_valid is True
    # 1 unit net base = 199.99 - 10.00 = 189.99
    assert calc.base_unit_refund == Decimal("189.99")
    # Proportional tax (half of 14.40) = 7.20
    assert calc.tax_refund == Decimal("7.20")
    # Restocking fee 15% of 189.99 = 28.50
    assert calc.restocking_fee_deducted == Decimal("28.50")
    # Net refund = 189.99 + 7.20 - 28.50 = 168.69
    assert calc.net_refund_amount == Decimal("168.69")

def test_refund_exceeding_paid_amount_rejection():
    calc = calculate_line_refund(
        unit_price=Decimal("100.00"),
        purchased_quantity=1,
        return_quantity=1,
        allocated_discount=Decimal("0.00"),
        line_tax=Decimal("8.00"),
        previously_refunded_amount=Decimal("108.00") # Already refunded in full
    )
    assert calc.is_valid is False
    assert "REFUND_EXCEEDS_PAID_AMOUNT" in calc.error_message

def test_inspection_outcomes():
    # Perfect condition -> RESTOCK with no fee
    res, disp, fee = evaluate_inspection_outcome(
        item_condition="UNOPENED",
        packaging_condition="INTACT",
        damage_type="NONE"
    )
    assert res == "PASS"
    assert disp == "RESTOCK"
    assert fee is False

    # Opened like new -> RESTOCK with restocking fee
    res, disp, fee = evaluate_inspection_outcome(
        item_condition="OPENED_LIKE_NEW",
        packaging_condition="INTACT",
        damage_type="NONE"
    )
    assert res == "PASS_WITH_RESTOCKING_FEE"
    assert disp == "RESTOCK"
    assert fee is True

    # Repairable electrical -> REFURBISH
    res, disp, fee = evaluate_inspection_outcome(
        item_condition="SLIGHT_WEAR",
        packaging_condition="DAMAGED_REPAIRABLE",
        damage_type="ELECTRICAL"
    )
    assert res == "REFURBISHABLE"
    assert disp == "REFURBISH"

    # Counterfeit -> QUARANTINE
    res, disp, fee = evaluate_inspection_outcome(
        item_condition="COUNTERFEIT",
        packaging_condition="INTACT",
        damage_type="TAMPERED"
    )
    assert res == "QUARANTINE_REQUIRED"
    assert disp == "QUARANTINE"

    # Destroyed -> SCRAP
    res, disp, fee = evaluate_inspection_outcome(
        item_condition="DESTROYED",
        packaging_condition="DESTROYED",
        damage_type="WATER"
    )
    assert res == "REJECT_SCRAP"
    assert disp == "SCRAP"

def test_disposition_invariants():
    # Restock before receipt blocked
    val1 = validate_disposition_action(
        disposition_type="RESTOCK",
        inspection_id=None,
        inspection_result=None,
        shipment_status="IN_TRANSIT",
        already_disposed_quantity=0,
        line_approved_quantity=1,
        disposition_quantity=1
    )
    assert val1.is_valid is False
    assert "RESTOCK_BEFORE_RECEIPT" in val1.error_message

    # Restock before inspection blocked
    val2 = validate_disposition_action(
        disposition_type="RESTOCK",
        inspection_id=None,
        inspection_result=None,
        shipment_status="DELIVERED",
        already_disposed_quantity=0,
        line_approved_quantity=1,
        disposition_quantity=1
    )
    assert val2.is_valid is False
    assert "RESTOCK_BEFORE_INSPECTION" in val2.error_message

    # Restock of damaged goods blocked
    val3 = validate_disposition_action(
        disposition_type="RESTOCK",
        inspection_id=1,
        inspection_result="REJECT_SCRAP",
        shipment_status="DELIVERED",
        already_disposed_quantity=0,
        line_approved_quantity=1,
        disposition_quantity=1
    )
    assert val3.is_valid is False
    assert "INVALID_RESTOCK_CONDITION" in val3.error_message

    # Disposition exceeding approved quantity blocked
    val4 = validate_disposition_action(
        disposition_type="SCRAP",
        inspection_id=1,
        inspection_result="REJECT_SCRAP",
        shipment_status="DELIVERED",
        already_disposed_quantity=1,
        line_approved_quantity=1,
        disposition_quantity=1
    )
    assert val4.is_valid is False
    assert "DISPOSITION_QTY_EXCEEDS_APPROVED" in val4.error_message

