from datetime import datetime, timezone
from decimal import Decimal

ANCHOR_DATE = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)

PRODUCT_CATALOG = [
    # Electronics (14-day window, 15% restock fee)
    {"sku": "SKU-ELEC-001", "name": "Aura Ultra Wireless Headphones", "category": "Electronics", "price": Decimal("199.99"), "cost": Decimal("85.00"), "is_returnable": True, "default_return_window_days": 14},
    {"sku": "SKU-ELEC-002", "name": "Vortex 4K Action Camera", "category": "Electronics", "price": Decimal("249.50"), "cost": Decimal("110.00"), "is_returnable": True, "default_return_window_days": 14},
    {"sku": "SKU-ELEC-003", "name": "PulseFit Pro Smartwatch", "category": "Electronics", "price": Decimal("149.00"), "cost": Decimal("60.00"), "is_returnable": True, "default_return_window_days": 14},
    {"sku": "SKU-ELEC-004", "name": "SonicBeam Soundbar 2.1", "category": "Electronics", "price": Decimal("129.99"), "cost": Decimal("52.00"), "is_returnable": True, "default_return_window_days": 14},
    {"sku": "SKU-ELEC-005", "name": "Zenith Mechanical Keyboard", "category": "Electronics", "price": Decimal("89.95"), "cost": Decimal("35.00"), "is_returnable": True, "default_return_window_days": 14},
    
    # Apparel (30-day window, 0% restock fee)
    {"sku": "SKU-APPR-001", "name": "Apex Merino Wool Sweater", "category": "Apparel", "price": Decimal("78.00"), "cost": Decimal("24.00"), "is_returnable": True, "default_return_window_days": 30},
    {"sku": "SKU-APPR-002", "name": "Strata Technical Trench Coat", "category": "Apparel", "price": Decimal("185.00"), "cost": Decimal("65.00"), "is_returnable": True, "default_return_window_days": 30},
    {"sku": "SKU-APPR-003", "name": "FlexForm Stretch Chinos", "category": "Apparel", "price": Decimal("54.50"), "cost": Decimal("18.00"), "is_returnable": True, "default_return_window_days": 30},
    {"sku": "SKU-APPR-004", "name": "AeroRun Lightweight Running Shoes", "category": "Apparel", "price": Decimal("110.00"), "cost": Decimal("42.00"), "is_returnable": True, "default_return_window_days": 30},

    # Home & Kitchen (30-day window, 10% restock fee)
    {"sku": "SKU-HOME-001", "name": "Barista Touch Espresso Machine", "category": "Home & Kitchen", "price": Decimal("349.99"), "cost": Decimal("160.00"), "is_returnable": True, "default_return_window_days": 30},
    {"sku": "SKU-HOME-002", "name": "Cast Iron Dutch Oven 6-Qt", "category": "Home & Kitchen", "price": Decimal("95.00"), "cost": Decimal("38.00"), "is_returnable": True, "default_return_window_days": 30},
    {"sku": "SKU-HOME-003", "name": "Smart Pure HEPA Air Purifier", "category": "Home & Kitchen", "price": Decimal("139.00"), "cost": Decimal("58.00"), "is_returnable": True, "default_return_window_days": 30},

    # Non-Returnable / Perishable or Hygiene Categories
    {"sku": "SKU-FOOD-001", "name": "Artisan Dark Roast Coffee Beans 2lb", "category": "Food & Beverage", "price": Decimal("28.00"), "cost": Decimal("10.00"), "is_returnable": False, "default_return_window_days": 0},
    {"sku": "SKU-FOOD-002", "name": "Organic Ceremonial Grade Matcha", "category": "Food & Beverage", "price": Decimal("36.00"), "cost": Decimal("14.00"), "is_returnable": False, "default_return_window_days": 0},
    {"sku": "SKU-HYGN-001", "name": "Precision Electric Sonic Toothbrush Head 4-Pack", "category": "Personal Care", "price": Decimal("24.99"), "cost": Decimal("8.00"), "is_returnable": False, "default_return_window_days": 0},
]

POLICIES = [
    {
        "policy_code": "POL-ELEC-14",
        "name": "Consumer Electronics Policy",
        "category": "Electronics",
        "return_window_days": 14,
        "restocking_fee_percent": Decimal("15.00"),
        "requires_original_packaging": True,
        "allow_opened_box": True,
        "description": "14-day return window with 15% restocking fee for opened items. Serial numbers must match."
    },
    {
        "policy_code": "POL-APPR-30",
        "name": "Apparel & Fashion Policy",
        "category": "Apparel",
        "return_window_days": 30,
        "restocking_fee_percent": Decimal("0.00"),
        "requires_original_packaging": False,
        "allow_opened_box": True,
        "description": "30-day standard return window. Tags must be attached for full refund."
    },
    {
        "policy_code": "POL-HOME-30",
        "name": "Home & Kitchen Appliance Policy",
        "category": "Home & Kitchen",
        "return_window_days": 30,
        "restocking_fee_percent": Decimal("10.00"),
        "requires_original_packaging": True,
        "allow_opened_box": True,
        "description": "30-day window. 10% restocking fee on kitchen electrics if packaging opened."
    },
    {
        "policy_code": "POL-NON-RET",
        "name": "Non-Returnable Perishables & Hygiene Policy",
        "category": "Food & Beverage",
        "return_window_days": 0,
        "restocking_fee_percent": Decimal("0.00"),
        "requires_original_packaging": True,
        "allow_opened_box": False,
        "description": "Strictly non-returnable due to health and safety regulations."
    },
]

REASON_CATEGORIES = [
    "DEFECTIVE",
    "WRONG_ITEM",
    "SIZE_FIT",
    "CHANGED_MIND",
    "NOT_AS_DESCRIBED",
    "ARRIVED_LATE",
    "MISSING_PARTS",
]

CHANNELS = ["WEB", "MOBILE", "SUPPORT_PORTAL", "IN_STORE"]
