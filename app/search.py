"""
Search and lookup helpers for Hope's Caramels Traceability System.
"""
from typing import List, Dict, Any

def supplier_lookup(suppliers: List[Dict[str, Any]], sup_code: str) -> List[Dict[str, Any]]:
    return [s for s in suppliers if s["sup_code"].strip().lower() == sup_code.strip().lower()]

def ingredient_lookup(ingredients: List[Dict[str, Any]], lot_number: str) -> List[Dict[str, Any]]:
    return [i for i in ingredients if i["lot_number"].strip().lower() == lot_number.strip().lower()]

def batch_lookup(batches: List[Dict[str, Any]], batch_id: str) -> List[Dict[str, Any]]:
    return [b for b in batches if b["batch_id"].strip().lower() == batch_id.strip().lower()]

def find_batches_using_lot(batches: List[Dict[str, Any]], lot_number: str) -> List[Dict[str, Any]]:
    matches = []
    target = lot_number.strip().lower()
    for batch in batches:
        ingredient_lots = batch.get("ingredient_lots", {})
        for lot_list in ingredient_lots.values():
            if any(str(lot).strip().lower() == target for lot in lot_list):
                matches.append(batch)
                break
    return matches

def low_stock_ingredients(ingredients: List[Dict[str, Any]], threshold: int = 2) -> List[Dict[str, Any]]:
    low_items = []
    for item in ingredients:
        qty_text = str(item.get("quantity", ""))
        digits = "".join(ch for ch in qty_text if ch.isdigit())
        if digits:
            qty_num = int(digits)
            if qty_num <= threshold:
                low_items.append(item)
    return low_items
