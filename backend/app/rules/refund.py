from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional

TWO_PLACES = Decimal("0.01")

def quantize(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

class RefundCalculationResult:
    def __init__(
        self,
        base_unit_refund: Decimal,
        tax_refund: Decimal,
        shipping_refund: Decimal,
        restocking_fee_deducted: Decimal,
        net_refund_amount: Decimal,
        max_allowable_refund: Decimal,
        is_valid: bool,
        error_message: Optional[str] = None
    ):
        self.base_unit_refund = quantize(base_unit_refund)
        self.tax_refund = quantize(tax_refund)
        self.shipping_refund = quantize(shipping_refund)
        self.restocking_fee_deducted = quantize(restocking_fee_deducted)
        self.net_refund_amount = quantize(net_refund_amount)
        self.max_allowable_refund = quantize(max_allowable_refund)
        self.is_valid = is_valid
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_unit_refund": float(self.base_unit_refund),
            "tax_refund": float(self.tax_refund),
            "shipping_refund": float(self.shipping_refund),
            "restocking_fee_deducted": float(self.restocking_fee_deducted),
            "net_refund_amount": float(self.net_refund_amount),
            "max_allowable_refund": float(self.max_allowable_refund),
            "is_valid": self.is_valid,
            "error_message": self.error_message,
        }


def calculate_line_refund(
    unit_price: Decimal,
    purchased_quantity: int,
    return_quantity: int,
    allocated_discount: Decimal,
    line_tax: Decimal,
    restocking_fee_percent: Decimal = Decimal("0.00"),
    include_shipping: bool = False,
    shipping_amount: Decimal = Decimal("0.00"),
    previously_refunded_amount: Decimal = Decimal("0.00"),
    apply_restocking_fee: bool = False
) -> RefundCalculationResult:
    """
    Computes exact proportional refund amounts using Decimal arithmetic.
    Formula:
      effective_unit_subtotal = (unit_price * return_quantity)
      proportional_discount = (allocated_discount / purchased_quantity) * return_quantity
      base_net_item = effective_unit_subtotal - proportional_discount
      proportional_tax = (line_tax / purchased_quantity) * return_quantity
      proportional_shipping = (shipping_amount / purchased_quantity) * return_quantity if include_shipping else 0.00
      restocking_fee = (base_net_item * (restocking_fee_percent / 100)) if apply_restocking_fee else 0.00
      net_refund = base_net_item + proportional_tax + proportional_shipping - restocking_fee
    """
    if return_quantity <= 0 or purchased_quantity <= 0:
        return RefundCalculationResult(
            base_unit_refund=Decimal("0.00"),
            tax_refund=Decimal("0.00"),
            shipping_refund=Decimal("0.00"),
            restocking_fee_deducted=Decimal("0.00"),
            net_refund_amount=Decimal("0.00"),
            max_allowable_refund=Decimal("0.00"),
            is_valid=False,
            error_message="Quantity must be greater than zero."
        )

    qty_ratio = Decimal(return_quantity) / Decimal(purchased_quantity)
    
    # Gross unit cost
    gross_item_total = quantize(unit_price * Decimal(return_quantity))
    proportional_discount = quantize(allocated_discount * qty_ratio)
    base_net_item = gross_item_total - proportional_discount
    if base_net_item < Decimal("0.00"):
        base_net_item = Decimal("0.00")

    proportional_tax = quantize(line_tax * qty_ratio)
    proportional_shipping = quantize(shipping_amount * qty_ratio) if include_shipping else Decimal("0.00")

    # Restocking fee deduction
    restocking_fee = Decimal("0.00")
    if apply_restocking_fee and restocking_fee_percent > Decimal("0.00"):
        restocking_fee = quantize(base_net_item * (restocking_fee_percent / Decimal("100.00")))

    net_refund = quantize(base_net_item + proportional_tax + proportional_shipping - restocking_fee)

    # Maximum refundable for this portion of the order line
    max_line_paid = quantize(gross_item_total - proportional_discount + proportional_tax + proportional_shipping)
    max_allowable = quantize(max_line_paid - previously_refunded_amount)
    if max_allowable < Decimal("0.00"):
        max_allowable = Decimal("0.00")

    # Invariant: net_refund cannot exceed max_allowable
    if net_refund > max_allowable:
        return RefundCalculationResult(
            base_unit_refund=base_net_item,
            tax_refund=proportional_tax,
            shipping_refund=proportional_shipping,
            restocking_fee_deducted=restocking_fee,
            net_refund_amount=net_refund,
            max_allowable_refund=max_allowable,
            is_valid=False,
            error_message=f"REFUND_EXCEEDS_PAID_AMOUNT (Calculated: {net_refund} > Max Allowable: {max_allowable})"
        )

    return RefundCalculationResult(
        base_unit_refund=base_net_item,
        tax_refund=proportional_tax,
        shipping_refund=proportional_shipping,
        restocking_fee_deducted=restocking_fee,
        net_refund_amount=net_refund,
        max_allowable_refund=max_allowable,
        is_valid=True,
        error_message=None
    )
