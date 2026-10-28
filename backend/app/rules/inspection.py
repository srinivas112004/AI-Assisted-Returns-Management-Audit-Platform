from typing import Tuple

def evaluate_inspection_outcome(
    item_condition: str,
    packaging_condition: str,
    damage_type: str = "NONE",
    is_received: bool = True
) -> Tuple[str, str, bool]:
    """
    Returns (inspection_result, recommended_disposition, apply_restocking_fee)
    """
    if not is_received:
        return "NOT_RECEIVED", "QUARANTINE", False

    # Counterfeit or Tampered -> Quarantine immediately
    if item_condition == "COUNTERFEIT" or damage_type == "TAMPERED":
        return "QUARANTINE_REQUIRED", "QUARANTINE", False

    # Destroyed or Water Damage -> Scrap
    if item_condition == "DESTROYED" or packaging_condition == "DESTROYED" or damage_type == "WATER":
        return "REJECT_SCRAP", "SCRAP", False

    # Perfect Unopened -> Restock (no fee)
    if item_condition == "UNOPENED" and packaging_condition == "INTACT" and damage_type == "NONE":
        return "PASS", "RESTOCK", False

    # Opened Like New or Packaging Only damage -> Restock with Restocking Fee
    if (
        item_condition in ["OPENED_LIKE_NEW", "UNOPENED"]
        and packaging_condition in ["INTACT", "DAMAGED_REPAIRABLE"]
        and damage_type in ["NONE", "PACKAGING_ONLY"]
    ):
        return "PASS_WITH_RESTOCKING_FEE", "RESTOCK", True

    # Slight wear or repairable electrical/cosmetic -> Refurbish
    if (
        item_condition in ["SLIGHT_WEAR", "SIGNIFICANT_DAMAGE"]
        and damage_type in ["COSMETIC", "ELECTRICAL", "IMPACT"]
    ):
        return "REFURBISHABLE", "REFURBISH", False

    # Irreparable or severe wear
    if item_condition == "SIGNIFICANT_DAMAGE":
        return "REJECT_SCRAP", "SCRAP", False

    # Default safe fallback: Quarantine for manual evaluation
    return "QUARANTINE_REQUIRED", "QUARANTINE", False

