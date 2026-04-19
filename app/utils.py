"""
Utility functions for Hope's Caramels Traceability System.
"""
from datetime import datetime
import pandas as pd
import re
from typing import List, Dict, Any

def generate_user_id(users: List[Dict[str, Any]]) -> str:
    if len(users) == 0:
        return "U001"
    last_id = max(int(user["id"][1:]) for user in users)
    return f"U{last_id + 1:03d}"

def generate_batch_id(date_produced, flavor_code, batches) -> str:
    date_str = pd.to_datetime(date_produced).strftime("%y%m%d")
    prefix = flavor_code.strip().upper()
    same_day_batches = [
        b for b in batches
        if b["date_produced"] == pd.to_datetime(date_produced).strftime("%Y-%m-%d")
        and b["flavor_code"] == prefix
    ]
    seq = len(same_day_batches) + 1
    return f"{prefix}-{date_str}-{seq:03d}"

def ingredient_to_batch_key(ingredient_name: str) -> str:
    mapping = {
        "Cream": "cream",
        "Butter": "butter",
        "Brown Sugar": "brown_sugar",
        "Salt": "salt",
        "Corn Syrup": "corn_syrup",
        "Sweetened Condensed Milk": "sweetened_condensed_milk",
        "Cream of Tartar": "cream_of_tartar",
        "Coarse Sea Salt": "salt",
        "Pecan": "nuts",
        "Cashew": "nuts"
    }
    return mapping.get(ingredient_name, "flavoring")

def normalize_lot_text(text: str) -> str:
    cleaned = str(text).upper().strip()
    cleaned = cleaned.replace("—", "-").replace("_", "-")
    cleaned = re.sub(r"\s+", "", cleaned)
    cleaned = re.sub(r"[^A-Z0-9\-]", "", cleaned)
    return cleaned
