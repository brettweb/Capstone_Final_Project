"""
Data models, default data, and JSON helpers for Hope's Caramels Traceability System.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

USERS_PATH = Path("hc_users.json")
SUPPLIERS_PATH = Path("hc_suppliers.json")
INGREDIENT_CODES_PATH = Path("hc_ingredient_codes.json")
FLAVOR_CODES_PATH = Path("hc_flavor_codes.json")
INGREDIENTS_PATH = Path("hc_ingredients.json")
BATCHES_PATH = Path("hc_batches.json")

def timestamp_now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def default_users() -> List[Dict[str, Any]]:
    now = timestamp_now()
    return [
        {
            "id": "U001",
            "full_name": "Owner",
            "email": "owner@hopescaramels.com",
            "password": "owner123",
            "role": "Owner",
            "created_at": now
        },
        {
            "id": "U002",
            "full_name": "Cook",
            "email": "cook@hopescaramels.com",
            "password": "cook123",
            "role": "Cook",
            "created_at": now
        }
    ]

def default_suppliers() -> List[Dict[str, Any]]:
    return [
        {"sup_code": "HPD", "supplier_name": "High Point Dairy"},
        {"sup_code": "CMC", "supplier_name": "Country Maid Creamery"},
        {"sup_code": "GBR", "supplier_name": "Golden Barrell"},
        {"sup_code": "CTF", "supplier_name": "Cargill TopFlo"},
        {"sup_code": "MPX", "supplier_name": "Morton's PureX"},
        {"sup_code": "FUL", "supplier_name": "Fulafrute"},
        {"sup_code": "GAL", "supplier_name": "Galloway Company"},
        {"sup_code": "TAR", "supplier_name": "Tartaros"},
        {"sup_code": "FAN", "supplier_name": "Fante's"},
        {"sup_code": "LAO", "supplier_name": "LorAnn Oils"},
        {"sup_code": "WEG", "supplier_name": "Wegman's"},
        {"sup_code": "GOY", "supplier_name": "Goya"},
        {"sup_code": "MCC", "supplier_name": "McCormick"},
        {"sup_code": "RSP", "supplier_name": "Regal Spice"},
        {"sup_code": "KRK", "supplier_name": "Kirkland"},
        {"sup_code": "LGU", "supplier_name": "Le Guerandais"},
        {"sup_code": "CBO", "supplier_name": "Cherry Bay Orchards"},
        {"sup_code": "GUI", "supplier_name": "Guinness"},
        {"sup_code": "TWN", "supplier_name": "Total Wine"},
        {"sup_code": "HMS", "supplier_name": "House-Made"},
        {"sup_code": "OTH", "supplier_name": "Other/Unknown"}
    ]

def default_ingredient_codes() -> List[Dict[str, Any]]:
    return [
        {"ingredient_name": "Cream", "ing_code": "CRM", "default_unit": "Qt"},
        {"ingredient_name": "Butter", "ing_code": "BTR", "default_unit": "Lb"},
        {"ingredient_name": "Brown Sugar", "ing_code": "BSG", "default_unit": "Lb"},
        {"ingredient_name": "Salt", "ing_code": "SLT", "default_unit": "Lb"},
        {"ingredient_name": "Corn Syrup", "ing_code": "CSY", "default_unit": "Gal"},
        {"ingredient_name": "Sweetened Condensed Milk", "ing_code": "SCM", "default_unit": "Gal"},
        {"ingredient_name": "Cream of Tartar", "ing_code": "COT", "default_unit": "Lb"},
        {"ingredient_name": "Vanilla Beans", "ing_code": "VNB", "default_unit": "Ea"},
        {"ingredient_name": "100% Ethanol", "ing_code": "ETH", "default_unit": "L"},
        {"ingredient_name": "Distilled Water", "ing_code": "DWT", "default_unit": "L"},
        {"ingredient_name": "Ground Cinnamon", "ing_code": "GCI", "default_unit": "Lb"},
        {"ingredient_name": "Ground Nutmeg", "ing_code": "GNT", "default_unit": "Lb"},
        {"ingredient_name": "Allspice", "ing_code": "ALS", "default_unit": "Lb"},
        {"ingredient_name": "Ground Cloves", "ing_code": "GCL", "default_unit": "Lb"},
        {"ingredient_name": "Ground Ginger", "ing_code": "GGI", "default_unit": "Lb"},
        {"ingredient_name": "Cardamom", "ing_code": "CAR", "default_unit": "Lb"},
        {"ingredient_name": "Black Pepper", "ing_code": "BPP", "default_unit": "Lb"},
        {"ingredient_name": "Blood Orange Juice", "ing_code": "BOJ", "default_unit": "Qt"},
        {"ingredient_name": "Blood Orange Zest", "ing_code": "BOZ", "default_unit": "Ea"},
        {"ingredient_name": "Coconut Flakes", "ing_code": "CFL", "default_unit": "Lb"},
        {"ingredient_name": "Lime Zest", "ing_code": "LMZ", "default_unit": "Ea"},
        {"ingredient_name": "Chocolate Chips", "ing_code": "CHC", "default_unit": "Lb"},
        {"ingredient_name": "Espresso Powder", "ing_code": "ESP", "default_unit": "Lb"},
        {"ingredient_name": "Chai Tea", "ing_code": "CHT", "default_unit": "Ea"},
        {"ingredient_name": "Ghost Pepper Salt", "ing_code": "GPS", "default_unit": "Lb"},
        {"ingredient_name": "Coarse Sea Salt", "ing_code": "CSS", "default_unit": "Lb"},
        {"ingredient_name": "Coconut Flavor", "ing_code": "COF", "default_unit": "Fl"},
        {"ingredient_name": "Creme of Coconut", "ing_code": "COC", "default_unit": "Can"},
        {"ingredient_name": "Blood Orange Flavor", "ing_code": "BOF", "default_unit": "Fl"},
        {"ingredient_name": "Pecan", "ing_code": "PCN", "default_unit": "Lb"},
        {"ingredient_name": "Cashew", "ing_code": "CSH", "default_unit": "Lb"},
        {"ingredient_name": "Tart Cherry Juice", "ing_code": "TCJ", "default_unit": "Qt"},
        {"ingredient_name": "Stout Concentrate", "ing_code": "STC", "default_unit": "Fl"},
        {"ingredient_name": "Vanilla Extract (House)", "ing_code": "VEX", "default_unit": "Fl"},
        {"ingredient_name": "Apple Pie Spice Mix", "ing_code": "APS", "default_unit": "Lb"},
        {"ingredient_name": "Chai Spice Mix", "ing_code": "CSM", "default_unit": "Lb"},
        {"ingredient_name": "Gingerbread Spice Mix", "ing_code": "GBS", "default_unit": "Lb"}
    ]

def default_flavor_codes() -> List[Dict[str, Any]]:
    return [
        {"flavor_name": "Classic", "flavor_code": "CL"},
        {"flavor_name": "Sea Salt", "flavor_code": "SS"},
        {"flavor_name": "Chocolate", "flavor_code": "CC"},
        {"flavor_name": "Chocolate Salted", "flavor_code": "CS"},
        {"flavor_name": "Chai", "flavor_code": "CH"},
        {"flavor_name": "Spicy", "flavor_code": "SP"},
        {"flavor_name": "Coffee", "flavor_code": "CO"},
        {"flavor_name": "Mocha", "flavor_code": "MO"},
        {"flavor_name": "Apple Pie", "flavor_code": "AP"},
        {"flavor_name": "Vanilla", "flavor_code": "VA"},
        {"flavor_name": "Blood Orange", "flavor_code": "BO"},
        {"flavor_name": "Coconut Lime", "flavor_code": "CLM"},
        {"flavor_name": "Gingerbread", "flavor_code": "GB"},
        {"flavor_name": "Tart Cherry", "flavor_code": "TC"},
        {"flavor_name": "Stout", "flavor_code": "ST"},
        {"flavor_name": "Turtle", "flavor_code": "TU"},
        {"flavor_name": "Cashew Square", "flavor_code": "CSQ"},
        {"flavor_name": "Seasonal Special", "flavor_code": "SPC"}
    ]

def default_ingredients() -> List[Dict[str, Any]]:
    return []

def default_batches() -> List[Dict[str, Any]]:
    return []

def ensure_json_file(path: Path, default_data: Any) -> None:
    if not path.exists():
        with open(path, "w") as f:
            json.dump(default_data, f, indent=4)

def load_json(path: Path, default_data: Any) -> Any:
    ensure_json_file(path, default_data)
    with open(path, "r") as f:
        return json.load(f)

def save_json(path: Path, data: Any) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def load_all_data():
    users = load_json(USERS_PATH, default_users())
    suppliers = load_json(SUPPLIERS_PATH, default_suppliers())
    ingredient_codes = load_json(INGREDIENT_CODES_PATH, default_ingredient_codes())
    flavor_codes = load_json(FLAVOR_CODES_PATH, default_flavor_codes())
    ingredients = load_json(INGREDIENTS_PATH, default_ingredients())
    # Ensure all ingredient lots have a status field
    for ing in ingredients:
        if "status" not in ing:
            ing["status"] = "unopened"
    batches = load_json(BATCHES_PATH, default_batches())
    return users, suppliers, ingredient_codes, flavor_codes, ingredients, batches
