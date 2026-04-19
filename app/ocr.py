"""
OCR and image processing for Hope's Caramels Traceability System.
"""
import re
import numpy as np
from PIL import Image
from datetime import datetime
from typing import Any, List, Tuple, Dict
import streamlit as st

try:
    import easyocr
except ImportError:
    easyocr = None

from .utils import normalize_lot_text

def get_ocr_reader():
    if easyocr is None:
        return None
    return easyocr.Reader(["en"], gpu=False)

def parse_lot_number(lot_number: str, ingredient_codes: List[Dict[str, Any]], suppliers: List[Dict[str, Any]]) -> Dict[str, Any]:
    lot_number = normalize_lot_text(lot_number)
    parts = lot_number.split("-")
    info = {}
    if len(parts) >= 4:
        info["ingredient_code"] = parts[0]
        info["supplier_code"] = parts[1]
        info["quantity_text"] = parts[2]
        match = re.match(r"^(\d+(?:\.\d+)?)([A-Z]+)$", parts[2])
        if match:
            info["quantity_value"] = float(match.group(1))
            info["quantity_unit"] = match.group(2)
        else:
            info["quantity_value"] = 0.0
            info["quantity_unit"] = ""
        try:
            info["date_received"] = datetime.strptime(parts[3], "%m%d%Y").date()
        except ValueError:
            pass
    if "ingredient_code" in info:
        for item in ingredient_codes:
            if item["ing_code"].upper() == info["ingredient_code"]:
                info["ingredient_name"] = item["ingredient_name"]
                info["default_unit"] = item["default_unit"]
                break
    if "supplier_code" in info:
        for supplier in suppliers:
            if supplier["sup_code"].upper() == info["supplier_code"]:
                info["supplier_name"] = supplier["supplier_name"]
                break
    return info

def extract_lot_from_image(uploaded_file) -> Tuple[Any, List[str], Any]:
    reader = get_ocr_reader()
    if reader is None:
        return None, [], "easyocr is not installed. Run: pip install easyocr pillow numpy"
    image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)
    raw_results = reader.readtext(image_np, detail=0)
    cleaned_lines = [normalize_lot_text(x) for x in raw_results if normalize_lot_text(x)]
    combined_text = " ".join(cleaned_lines)
    pattern = r"[A-Z0-9]{2,5}-[A-Z0-9]{2,5}-[A-Z0-9]{1,10}-\d{8}"
    matches = re.findall(pattern, combined_text)
    if matches:
        return matches[0], cleaned_lines, None
    if cleaned_lines:
        return cleaned_lines[0], cleaned_lines, None
    return None, [], "No readable text found in the image."
