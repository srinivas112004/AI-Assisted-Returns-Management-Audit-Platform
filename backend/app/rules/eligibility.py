from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple

class EligibilityRuleResult:
    def __init__(
        self,
        is_eligible: bool,
        eligible_quantity: int,
        rejected_quantity: int,
        ineligibility_reason: Optional[str] = None,
        policy_code: Optional[str] = None,
        requires_override: bool = False
    ):
        self.is_eligible = is_eligible
        self.eligible_quantity = eligible_quantity
        self.rejected_quantity = rejected_quantity
        self.ineligibility_reason = ineligibility_reason
        self.policy_code = policy_code
        self.requires_override = requires_override

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_eligible": self.is_eligible,
            "eligible_quantity": self.eligible_quantity,
            "rejected_quantity": self.rejected_quantity,
            "ineligibility_reason": self.ineligibility_reason,
            "policy_code": self.policy_code,
            "requires_override": self.requires_override,
        }


def evaluate_line_eligibility(
    product_category: str,
    product_is_returnable: bool,
    order_delivery_date: Optional[datetime],
    request_date: datetime,
    purchased_quantity: int,
    already_returned_quantity: int,
    requested_quantity: int,
    policy_window_days: int = 30,
    policy_code: str = "POL-STD-30",
    allow_override: bool = False,
    override_approved: bool = False
) -> EligibilityRuleResult:
    """
    Evaluates return eligibility for an order line following strict deterministic business rules.
    """
    # 1. Quantity Validation
    available_to_return = purchased_quantity - already_returned_quantity
    if available_to_return <= 0:
        return EligibilityRuleResult(
            is_eligible=False,
            eligible_quantity=0,
            rejected_quantity=requested_quantity,
            ineligibility_reason="ALL_PURCHASED_UNITS_ALREADY_RETURNED",
            policy_code=policy_code
        )

    if requested_quantity > available_to_return:
        return EligibilityRuleResult(
            is_eligible=False,
            eligible_quantity=0,
            rejected_quantity=requested_quantity,
            ineligibility_reason=f"RETURN_QTY_EXCEEDS_AVAILABLE (Requested: {requested_quantity}, Available: {available_to_return})",
            policy_code=policy_code
        )

    # 2. Product Returnability Exclusion
    if not product_is_returnable or product_category in ["Perishable", "Food", "Intimates", "Hazardous"]:
        return EligibilityRuleResult(
            is_eligible=False,
            eligible_quantity=0,
            rejected_quantity=requested_quantity,
            ineligibility_reason=f"CATEGORY_EXCLUDED ({product_category} is non-returnable)",
            policy_code="POL-NON-RET"
        )

    # 3. Delivery Date & Return Window
    if not order_delivery_date:
        return EligibilityRuleResult(
            is_eligible=False,
            eligible_quantity=0,
            rejected_quantity=requested_quantity,
            ineligibility_reason="ORDER_NOT_YET_DELIVERED",
            policy_code=policy_code
        )

    # Calculate days since delivery
    days_elapsed = (request_date.date() - order_delivery_date.date()).days
    if days_elapsed < 0:
        return EligibilityRuleResult(
            is_eligible=False,
            eligible_quantity=0,
            rejected_quantity=requested_quantity,
            ineligibility_reason="REQUEST_DATE_BEFORE_DELIVERY_DATE",
            policy_code=policy_code
        )

    if days_elapsed > policy_window_days:
        if override_approved:
            return EligibilityRuleResult(
                is_eligible=True,
                eligible_quantity=requested_quantity,
                rejected_quantity=0,
                ineligibility_reason=None,
                policy_code=policy_code,
                requires_override=True
            )
        else:
            return EligibilityRuleResult(
                is_eligible=False,
                eligible_quantity=0,
                rejected_quantity=requested_quantity,
                ineligibility_reason=f"RETURN_AFTER_WINDOW (Elapsed {days_elapsed} days > {policy_window_days} days limit)",
                policy_code=policy_code,
                requires_override=True
            )

    # 4. Fully Eligible
    return EligibilityRuleResult(
        is_eligible=True,
        eligible_quantity=requested_quantity,
        rejected_quantity=0,
        ineligibility_reason=None,
        policy_code=policy_code,
        requires_override=False
    )

