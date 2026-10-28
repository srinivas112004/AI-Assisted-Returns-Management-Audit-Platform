from typing import Optional, Tuple

class DispositionValidationResult:
    def __init__(self, is_valid: bool, error_message: Optional[str] = None):
        self.is_valid = is_valid
        self.error_message = error_message

def validate_disposition_action(
    disposition_type: str,
    inspection_id: Optional[int],
    inspection_result: Optional[str],
    shipment_status: str,
    already_disposed_quantity: int,
    line_approved_quantity: int,
    disposition_quantity: int
) -> DispositionValidationResult:
    """
    Validates inventory disposition rules:
    - Never restock an item before receipt and inspection.
    - Restock only items with acceptable inspection result (PASS, PASS_WITH_RESTOCKING_FEE).
    - Prevent total disposition quantity from exceeding approved return line quantity.
    """
    # 1. Quantity bounds
    if disposition_quantity <= 0:
        return DispositionValidationResult(False, "Disposition quantity must be greater than zero.")

    if (already_disposed_quantity + disposition_quantity) > line_approved_quantity:
        return DispositionValidationResult(
            False,
            f"DISPOSITION_QTY_EXCEEDS_APPROVED (Approved: {line_approved_quantity}, Already Disposed: {already_disposed_quantity}, Requested: {disposition_quantity})"
        )

    # 2. Restock-specific rules
    if disposition_type == "RESTOCK":
        if shipment_status != "DELIVERED":
            return DispositionValidationResult(
                False,
                f"RESTOCK_BEFORE_RECEIPT (Shipment status is '{shipment_status}', expected 'DELIVERED')"
            )

        if not inspection_id or not inspection_result:
            return DispositionValidationResult(
                False,
                "RESTOCK_BEFORE_INSPECTION (Cannot restock without completed inspection)"
            )

        if inspection_result not in ["PASS", "PASS_WITH_RESTOCKING_FEE"]:
            return DispositionValidationResult(
                False,
                f"INVALID_RESTOCK_CONDITION (Inspection result was '{inspection_result}', cannot RESTOCK damaged/defective goods directly)"
            )

    # 3. Refurbish rules
    if disposition_type == "REFURBISH":
        if not inspection_id:
            return DispositionValidationResult(False, "REFURBISH requires inspection verification.")

    # 4. Valid
    return DispositionValidationResult(True, None)
