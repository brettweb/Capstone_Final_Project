import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import time
import pandas as pd

import re
import numpy as np
from PIL import Image

try:
    import easyocr
except ImportError:
    easyocr = None

# APP CONFIG
st.set_page_config(
    page_title="Hope's Caramels Traceability System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FILE PATHS
USERS_PATH = Path("hc_users.json")
SUPPLIERS_PATH = Path("hc_suppliers.json")
INGREDIENT_CODES_PATH = Path("hc_ingredient_codes.json")
FLAVOR_CODES_PATH = Path("hc_flavor_codes.json")
INGREDIENTS_PATH = Path("hc_ingredients.json")
BATCHES_PATH = Path("hc_batches.json")


# TIMESTAMP HELPER
def timestamp_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# DEFAULT DATA
def default_users():
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


def default_suppliers():
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


def default_ingredient_codes():
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


def default_flavor_codes():
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


def default_ingredients():
    return []


def default_batches():
    return []


# JSON HELPERS
def ensure_json_file(path, default_data):
    if not path.exists():
        with open(path, "w") as f:
            json.dump(default_data, f, indent=4)


def load_json(path, default_data):
    ensure_json_file(path, default_data)
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


# LOAD DATA
def load_all_data():
    users = load_json(USERS_PATH, default_users())
    suppliers = load_json(SUPPLIERS_PATH, default_suppliers())
    ingredient_codes = load_json(INGREDIENT_CODES_PATH, default_ingredient_codes())
    flavor_codes = load_json(FLAVOR_CODES_PATH, default_flavor_codes())
    ingredients = load_json(INGREDIENTS_PATH, default_ingredients())
    batches = load_json(BATCHES_PATH, default_batches())
    return users, suppliers, ingredient_codes, flavor_codes, ingredients, batches


# ID / SEARCH HELPERS
def generate_user_id(users):
    if len(users) == 0:
        return "U001"
    last_id = max(int(user["id"][1:]) for user in users)
    return f"U{last_id + 1:03d}"


def generate_batch_id(date_produced, flavor_code, batches):
    date_str = pd.to_datetime(date_produced).strftime("%y%m%d")
    prefix = flavor_code.strip().upper()

    same_day_batches = [
        b for b in batches
        if b["date_produced"] == pd.to_datetime(date_produced).strftime("%Y-%m-%d")
        and b["flavor_code"] == prefix
    ]

    seq = len(same_day_batches) + 1
    return f"{prefix}-{date_str}-{seq:03d}"


def authenticate_user(email, password, users):
    for user in users:
        if user["email"].lower() == email.lower() and user["password"] == password:
            return user
    return None


def register_user(full_name, email, password, role, users):
    for user in users:
        if user["email"].lower() == email.lower():
            return False, "An account with this email already exists."

    new_user = {
        "id": generate_user_id(users),
        "full_name": full_name,
        "email": email,
        "password": password,
        "role": role,
        "created_at": timestamp_now()
    }

    users.append(new_user)
    save_json(USERS_PATH, users)
    return True, "Registration successful."


def supplier_lookup(suppliers, sup_code):
    return [s for s in suppliers if s["sup_code"].strip().lower() == sup_code.strip().lower()]


def ingredient_lookup(ingredients, lot_number):
    return [i for i in ingredients if i["lot_number"].strip().lower() == lot_number.strip().lower()]


def batch_lookup(batches, batch_id):
    return [b for b in batches if b["batch_id"].strip().lower() == batch_id.strip().lower()]


def find_batches_using_lot(batches, lot_number):
    matches = []
    target = lot_number.strip().lower()

    for batch in batches:
        ingredient_lots = batch.get("ingredient_lots", {})
        for lot_list in ingredient_lots.values():
            if any(str(lot).strip().lower() == target for lot in lot_list):
                matches.append(batch)
                break

    return matches


def low_stock_ingredients(ingredients, threshold=2):
    low_items = []
    for item in ingredients:
        qty_text = str(item.get("quantity", ""))
        digits = "".join(ch for ch in qty_text if ch.isdigit())
        if digits:
            qty_num = int(digits)
            if qty_num <= threshold:
                low_items.append(item)
    return low_items



def ingredient_to_batch_key(ingredient_name):
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


@st.cache_resource
def get_ocr_reader():
    if easyocr is None:
        return None
    return easyocr.Reader(["en"], gpu=False)


def normalize_lot_text(text):
    cleaned = str(text).upper().strip()
    cleaned = cleaned.replace("—", "-").replace("_", "-")
    cleaned = re.sub(r"\s+", "", cleaned)
    cleaned = re.sub(r"[^A-Z0-9\-]", "", cleaned)
    return cleaned


def extract_lot_from_image(uploaded_file):
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


def save_scanned_lot(ingredients, batches, ingredient_record, selected_batch_ids, user_name):
    lot_number = ingredient_record["lot_number"]

    if not any(i["lot_number"] == lot_number for i in ingredients):
        ingredients.append(ingredient_record)
        save_json(INGREDIENTS_PATH, ingredients)

    batch_key = ingredient_to_batch_key(ingredient_record["ingredient_name"])
    updated_any_batch = False

    for batch in batches:
        if batch["batch_id"] in selected_batch_ids:
            if "ingredient_lots" not in batch:
                batch["ingredient_lots"] = {}
            if batch_key not in batch["ingredient_lots"]:
                batch["ingredient_lots"][batch_key] = []
            if lot_number not in batch["ingredient_lots"][batch_key]:
                batch["ingredient_lots"][batch_key].append(lot_number)
                batch["updated_at"] = timestamp_now()
                batch["updated_by"] = user_name
                updated_any_batch = True

    if updated_any_batch:
        save_json(BATCHES_PATH, batches)


def render_scan_lot_tab(tab_key_prefix, ingredients, batches, ingredient_codes, suppliers, current_user_name):
    st.subheader("Scan Lot Number From Photo")
    st.caption("Upload a picture of a lot label. AI will read the lot number, let you confirm it, save it to the ingredient JSON, and optionally link it to one or more caramel batches.")

    if easyocr is None:
        st.warning("OCR package missing. Install: pip install easyocr pillow numpy")

    col1, col2 = st.columns(2)

    with col1:
        selected_ing = st.selectbox(
            "Ingredient",
            options=ingredient_codes,
            format_func=lambda x: x["ingredient_name"],
            key=f"{tab_key_prefix}_scan_ing"
        )

        selected_supplier = st.selectbox(
            "Supplier",
            options=suppliers,
            format_func=lambda x: f'{x["sup_code"]} - {x["supplier_name"]}',
            key=f"{tab_key_prefix}_scan_supplier"
        )

        quantity_value = st.number_input(
            "Quantity",
            min_value=0.0,
            step=0.5,
            key=f"{tab_key_prefix}_scan_qty"
        )

        date_received = st.date_input(
            "Date Received",
            value=datetime.today(),
            key=f"{tab_key_prefix}_scan_date"
        )

        expiration_date = st.text_input(
            "Expiration Date (optional)",
            key=f"{tab_key_prefix}_scan_exp"
        )

        storage_location = st.text_input(
            "Storage Location",
            value="Cooler",
            key=f"{tab_key_prefix}_scan_storage"
        )

        notes = st.text_area("Notes", key=f"{tab_key_prefix}_scan_notes")

    with col2:
        batch_options = [b["batch_id"] for b in batches]
        selected_batch_ids = st.multiselect(
            "Link this lot to batch(es)",
            options=batch_options,
            key=f"{tab_key_prefix}_scan_batches"
        )

        uploaded_file = st.file_uploader(
            "Upload lot label image",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"{tab_key_prefix}_scan_upload"
        )

        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded lot label image", use_container_width=True)

        if st.button("Read Lot Number From Photo", key=f"{tab_key_prefix}_read_btn", use_container_width=True):
            if uploaded_file is None:
                st.error("Please upload an image first.")
            else:
                extracted_lot, raw_lines, error_message = extract_lot_from_image(uploaded_file)
                if error_message:
                    st.error(error_message)
                else:
                    st.session_state[f"{tab_key_prefix}_ocr_lot"] = extracted_lot
                    st.session_state[f"{tab_key_prefix}_ocr_lines"] = raw_lines
                    st.success("Lot number read from image.")

        extracted_lot = st.session_state.get(f"{tab_key_prefix}_ocr_lot", "")
        raw_lines = st.session_state.get(f"{tab_key_prefix}_ocr_lines", [])

        if extracted_lot:
            st.markdown("### OCR Result")
            st.code(extracted_lot)

            if raw_lines:
                st.write("Other detected text:")
                st.write(raw_lines)

            edited_lot = st.text_input(
                "Confirm or edit lot number before saving",
                value=extracted_lot,
                key=f"{tab_key_prefix}_edited_lot"
            )

            if st.button("Save Scanned Lot", key=f"{tab_key_prefix}_save_btn", type="primary", use_container_width=True):
                if not edited_lot.strip():
                    st.error("Lot number cannot be blank.")
                else:
                    ingredient_name = selected_ing["ingredient_name"]
                    ingredient_code = selected_ing["ing_code"]
                    unit = selected_ing["default_unit"]
                    supplier_code = selected_supplier["sup_code"]
                    supplier_name = selected_supplier["supplier_name"]
                    quantity_text = f"{quantity_value:g}{unit}"

                    new_ingredient = {
                        "lot_number": normalize_lot_text(edited_lot),
                        "ingredient_code": ingredient_code,
                        "ingredient_name": ingredient_name,
                        "supplier_code": supplier_code,
                        "supplier_name": supplier_name,
                        "quantity": quantity_text,
                        "unit": unit,
                        "date_received": pd.to_datetime(date_received).strftime("%Y-%m-%d"),
                        "expiration_date": expiration_date.strip(),
                        "storage_location": storage_location.strip(),
                        "notes": notes.strip(),
                        "created_at": timestamp_now(),
                        "created_by": current_user_name,
                        "source": "image_scan"
                    }

                    if any(i["lot_number"] == new_ingredient["lot_number"] for i in ingredients):
                        st.warning("That lot already exists in hc_ingredients.json. It will still be linked to any selected batches.")

                    save_scanned_lot(
                        ingredients=ingredients,
                        batches=batches,
                        ingredient_record=new_ingredient,
                        selected_batch_ids=selected_batch_ids,
                        user_name=current_user_name
                    )

                    st.success("Scanned lot saved successfully.")
                    st.rerun()


# AI ASSISTANT
def ai_traceability_response(user_prompt, suppliers, ingredients, batches):
    prompt = user_prompt.strip().lower()
    tokens = user_prompt.replace("?", "").replace(",", " ").split()

    if "help" in prompt:
        return (
            "Try asking one of these:\n"
            "- Find batch CL-250318-001\n"
            "- Search lot CRM-HPD-8Qt-03172025\n"
            "- Which batches used CRM-HPD-8Qt-03172025?\n"
            "- Show suppliers\n"
            "- What ingredients are low stock?"
        )

    if "show suppliers" in prompt or "supplier list" in prompt:
        if len(suppliers) == 0:
            return "There are no suppliers in the system."
        response = "Suppliers:\n"
        for s in suppliers:
            response += f"- {s['sup_code']} | {s['supplier_name']}\n"
        return response

    if "low stock" in prompt:
        low_items = low_stock_ingredients(ingredients)
        if len(low_items) == 0:
            return "There are currently no low-stock ingredient lots based on the simple quantity check."
        response = "Low-stock ingredient lots:\n"
        for item in low_items:
            response += f"- {item['ingredient_name']} | {item['lot_number']} | Qty: {item['quantity']}\n"
        return response

    if "find batch" in prompt or prompt.startswith("batch"):
        possible_batch = None
        for token in tokens:
            if "-" in token and any(ch.isdigit() for ch in token):
                possible_batch = token
                break
        if possible_batch:
            result = batch_lookup(batches, possible_batch)
            if len(result) == 0:
                return f"No batch was found for {possible_batch}."
            return json.dumps(result[0], indent=2)

    if "search lot" in prompt or "used" in prompt or "lot" in prompt:
        possible_lot = None
        for token in tokens:
            if "-" in token and any(ch.isdigit() for ch in token):
                possible_lot = token
        if possible_lot:
            ingredient_matches = ingredient_lookup(ingredients, possible_lot)
            batch_matches = find_batches_using_lot(batches, possible_lot)

            response_parts = []
            if len(ingredient_matches) > 0:
                response_parts.append("Lot record:\n" + json.dumps(ingredient_matches[0], indent=2))
            if len(batch_matches) > 0:
                response_parts.append(
                    "Batches using this lot:\n" +
                    "\n".join([f"- {b['batch_id']} | {b['flavor_name']} | {b['date_produced']}" for b in batch_matches])
                )
            if len(response_parts) == 0:
                return f"I could not find lot {possible_lot} in the system."
            return "\n\n".join(response_parts)

    return "I support batch lookup, lot lookup, supplier review, low stock review, and help."


# SESSION STATE
if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I’m the Hope’s Caramels traceability assistant. Ask me about batches, lot numbers, suppliers, low stock, or type help."
        }
    ]


users, suppliers, ingredient_codes, flavor_codes, ingredients, batches = load_all_data()


# SIDEBAR
with st.sidebar:
    st.title("Navigation")

    if not st.session_state.logged_in:
        if st.button("Login", key="login_btn", type="primary", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

        if st.button("Register", key="register_btn", type="primary", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

    if st.session_state.logged_in:
        if st.button("Home", key="home_btn", type="primary", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

        if st.session_state.role == "Owner":
            if st.button("Owner Dashboard", key="owner_btn", type="primary", use_container_width=True):
                st.session_state.page = "owner"
                st.rerun()

        if st.session_state.role == "Cook":
            if st.button("Cook Dashboard", key="cook_btn", type="primary", use_container_width=True):
                st.session_state.page = "employee"
                st.rerun()

        if st.button("Logout", key="logout_btn", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.role = None
            st.session_state.page = "login"
            st.rerun()

# LOGIN PAGE
if st.session_state.page == "login":
    st.title("Hope's Caramels Traceability System")
    st.subheader("Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login Now", key="login_submit", use_container_width=True):
        user = authenticate_user(email, password, users)

        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.role = user["role"]
            st.session_state.page = "home"
            st.success("Login successful.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Invalid email or password.")


# REGISTER PAGE
elif st.session_state.page == "register":
    st.title("Register New Account")

    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Select Role", ["Owner", "Employee"])

    if st.button("Create Account", key="create_account_btn", use_container_width=True):
        if full_name.strip() == "" or email.strip() == "" or password.strip() == "":
            st.warning("Please fill in all fields.")
        else:
            success, message = register_user(full_name, email, password, role, users)
            if success:
                st.success(message)
                time.sleep(1)
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error(message)


# HOME PAGE
elif st.session_state.page == "home":
    if not st.session_state.logged_in:
        st.warning("Please log in first.")
        st.stop()

    st.title("Home")
    st.success(f"Welcome, {st.session_state.user['full_name']} ({st.session_state.role})")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Users", len(users))
    c2.metric("Suppliers", len(suppliers))
    c3.metric("Ingredient Lots", len(ingredients))
    c4.metric("Batches", len(batches))

    if st.session_state.role == "Owner":
        options = ["Batches", "Ingredients", "Suppliers", "Users"]
    else:
        options = ["Batches", "Ingredients", "Suppliers"]

    selected_category = st.radio("Select Category", options, horizontal=True)

    if selected_category == "Batches":
        st.markdown("## Batch Records")
        st.dataframe(pd.DataFrame(batches), use_container_width=True)
    elif selected_category == "Ingredients":
        st.markdown("## Ingredient Lots")
        st.dataframe(pd.DataFrame(ingredients), use_container_width=True)
    elif selected_category == "Suppliers":
        st.markdown("## Supplier List")
        st.dataframe(pd.DataFrame(suppliers), use_container_width=True)
    else:
        safe_users = []
        for user in users:
            safe_users.append({
                "id": user["id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "role": user["role"],
                "created_at": user["created_at"]
            })
        st.markdown("## Registered Users")
        st.dataframe(pd.DataFrame(safe_users), use_container_width=True)


# OWNER DASHBOARD
elif st.session_state.page == "owner":
    if not st.session_state.logged_in or st.session_state.role != "Owner":
        st.error("You do not have permission to view this page.")
        st.stop()

    st.title("Owner Dashboard")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview",
    "Add Ingredient Lot",
    "Scan Lot From Photo",
    "Add Batch",
    "Traceability Search",
    "AI Assistant",
    "Manage Data"
])

    with tab1:
        st.subheader("System Overview")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Users", len(users))
        k2.metric("Suppliers", len(suppliers))
        k3.metric("Ingredient Lots", len(ingredients))
        k4.metric("Batches", len(batches))

        st.markdown("### Recent Batch Records")
        if len(batches) > 0:
            st.dataframe(pd.DataFrame(batches).tail(10), use_container_width=True)
        else:
            st.warning("No batches found.")

    with tab2:
        st.subheader("Add New Ingredient Lot")

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_ing = st.selectbox(
                "Select Ingredient",
                options=ingredient_codes,
                format_func=lambda x: x["ingredient_name"]
            )

            ingredient_name = selected_ing["ingredient_name"]
            ingredient_code = selected_ing["ing_code"]
            unit = selected_ing["default_unit"]

            st.write(f"Ingredient Code: {ingredient_code}")
            st.write(f"Default Unit: {unit}")

            selected_supplier = st.selectbox(
                "Select Supplier",
                options=suppliers,
                format_func=lambda x: f'{x["sup_code"]} - {x["supplier_name"]}'
            )

            supplier_code = selected_supplier["sup_code"]
            supplier_name = selected_supplier["supplier_name"]

            st.write(f"Supplier Code: {supplier_code}")

        with col2:
            quantity_value = st.number_input("Quantity", min_value=0.0, step=0.5)
            date_received = st.date_input("Date Received", value=datetime.today())
            expiration_date = st.text_input("Expiration Date (optional)")
            storage_location = st.text_input("Storage Location", value="Cooler")

        with col3:
            notes = st.text_area("Notes")

            lot_date = pd.to_datetime(date_received).strftime("%m%d%Y")
            quantity_text = f"{quantity_value:g}{unit}"
            generated_lot = f"{ingredient_code}-{supplier_code}-{quantity_text}-{lot_date}"

            st.markdown("### Generated Lot Number")
            st.code(generated_lot)

        if st.button("Add Ingredient Lot", key="add_ingredient_btn", type="primary", use_container_width=True):
            new_ingredient = {
                "lot_number": generated_lot,
                "ingredient_code": ingredient_code,
                "ingredient_name": ingredient_name,
                "supplier_code": supplier_code,
                "supplier_name": supplier_name,
                "quantity": quantity_text,
                "unit": unit,
                "date_received": pd.to_datetime(date_received).strftime("%Y-%m-%d"),
                "expiration_date": expiration_date.strip(),
                "storage_location": storage_location.strip(),
                "notes": notes.strip(),
                "created_at": timestamp_now(),
                "created_by": st.session_state.user["full_name"]
            }

            if any(i["lot_number"] == generated_lot for i in ingredients):
                st.error("That lot number already exists.")
            else:
                ingredients.append(new_ingredient)
                save_json(INGREDIENTS_PATH, ingredients)
                st.success(f"Ingredient lot {generated_lot} added successfully.")
                st.rerun()
    with tab3:
        render_scan_lot_tab(
            tab_key_prefix="owner",
            ingredients=ingredients,
            batches=batches,
            ingredient_codes=ingredient_codes,
            suppliers=suppliers,
            current_user_name=st.session_state.user["full_name"]
        )
    with tab4:
        st.subheader("Add New Batch Record")

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_flavor = st.selectbox(
                "Select Flavor",
                options=flavor_codes,
                format_func=lambda x: x["flavor_name"]
            )

            flavor_name = selected_flavor["flavor_name"]
            flavor_code = selected_flavor["flavor_code"]
            date_produced = st.date_input("Date Produced", value=datetime.today())
            wholesale = st.selectbox("Wholesale?", [False, True])

            st.write(f"Flavor Code: {flavor_code}")

        ingredient_lot_options = [item["lot_number"] for item in ingredients]

        with col2:
            cream_lots = st.multiselect("Cream Lots", ingredient_lot_options)
            butter_lots = st.multiselect("Butter Lots", ingredient_lot_options)
            brown_sugar_lots = st.multiselect("Brown Sugar Lots", ingredient_lot_options)
            salt_lots = st.multiselect("Salt Lots", ingredient_lot_options)
            corn_syrup_lots = st.multiselect("Corn Syrup Lots", ingredient_lot_options)

        with col3:
            scmilk_lots = st.multiselect("Sweetened Condensed Milk Lots", ingredient_lot_options)
            crtartar_lots = st.multiselect("Cream of Tartar Lots", ingredient_lot_options)
            flavoring_lots = st.multiselect("Flavoring Lots", ingredient_lot_options)
            nuts_lots = st.multiselect("Nuts Lots", ingredient_lot_options)
            notes = st.text_area("Notes", key="batch_notes")

        preview_batch_id = generate_batch_id(date_produced, flavor_code, batches)
        st.markdown("### Generated Batch ID")
        st.code(preview_batch_id)

        if st.button("Add Batch Record", key="add_batch_btn", type="primary", use_container_width=True):
            new_batch = {
                "batch_id": preview_batch_id,
                "date_produced": pd.to_datetime(date_produced).strftime("%Y-%m-%d"),
                "flavor_code": flavor_code,
                "flavor_name": flavor_name,
                "ingredient_lots": {
                    "cream": cream_lots,
                    "butter": butter_lots,
                    "brown_sugar": brown_sugar_lots,
                    "salt": salt_lots,
                    "corn_syrup": corn_syrup_lots,
                    "sweetened_condensed_milk": scmilk_lots,
                    "cream_of_tartar": crtartar_lots,
                    "flavoring": flavoring_lots,
                    "nuts": nuts_lots
                },
                "wholesale": wholesale,
                "notes": notes.strip(),
                "created_at": timestamp_now(),
                "created_by": st.session_state.user["full_name"]
            }

            if any(b["batch_id"] == preview_batch_id for b in batches):
                st.error("That batch ID already exists.")
            else:
                batches.append(new_batch)
                save_json(BATCHES_PATH, batches)
                st.success(f"Batch {preview_batch_id} added successfully.")
                st.rerun()

    with tab5:
        st.subheader("Traceability Search")

        search_type = st.radio("Search by", ["Lot Number", "Batch ID", "Supplier Code"], horizontal=True)

        if search_type == "Lot Number":
            lot_input = st.text_input("Enter Lot Number")
            if st.button("Search Lot", key="search_lot_btn", use_container_width=True):
                lot_matches = ingredient_lookup(ingredients, lot_input)
                batch_matches = find_batches_using_lot(batches, lot_input)

                st.markdown("### Ingredient Lot Record")
                if len(lot_matches) == 0:
                    st.info("No matching lot found.")
                else:
                    st.dataframe(pd.DataFrame(lot_matches), use_container_width=True)

                st.markdown("### Batches Using This Lot")
                if len(batch_matches) == 0:
                    st.info("No matching batches found.")
                else:
                    st.dataframe(pd.DataFrame(batch_matches), use_container_width=True)

        elif search_type == "Batch ID":
            batch_input = st.text_input("Enter Batch ID")
            if st.button("Search Batch", key="search_batch_btn", use_container_width=True):
                batch_result = batch_lookup(batches, batch_input)
                if len(batch_result) == 0:
                    st.warning("No matching batch was found.")
                else:
                    st.dataframe(pd.DataFrame(batch_result), use_container_width=True)

        else:
            sup_input = st.text_input("Enter Supplier Code")
            if st.button("Search Supplier", key="search_supplier_btn", use_container_width=True):
                supplier_result = supplier_lookup(suppliers, sup_input)
                if len(supplier_result) == 0:
                    st.warning("No matching supplier was found.")
                else:
                    st.dataframe(pd.DataFrame(supplier_result), use_container_width=True)

    with tab6:
        st.subheader("AI Assistant")
        col11, col22 = st.columns([3, 1])

        with col11:
            st.caption("Try asking: Which batches used CRM-HPD-8Qt-03172025?")

        with col22:
            if st.button("Clear Messages", key="clear_owner_messages"):
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "Hi! I’m the Hope’s Caramels traceability assistant. Ask me about batches, lot numbers, suppliers, low stock, or type help."
                    }
                ]
                st.rerun()

        with st.container(border=True, height=300):
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        user_input = st.chat_input("Type your message here...", key="owner_chat_input")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = ai_traceability_response(user_input, suppliers, ingredients, batches)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    with tab7:
        st.subheader("Manage JSON Data")
        st.write("Users")
        st.dataframe(pd.DataFrame(users), use_container_width=True)
        st.write("Suppliers")
        st.dataframe(pd.DataFrame(suppliers), use_container_width=True)
        st.write("Ingredient Codes")
        st.dataframe(pd.DataFrame(ingredient_codes), use_container_width=True)
        st.write("Flavor Codes")
        st.dataframe(pd.DataFrame(flavor_codes), use_container_width=True)
        st.write("Ingredients")
        st.dataframe(pd.DataFrame(ingredients), use_container_width=True)
        st.write("Batches")
        st.dataframe(pd.DataFrame(batches), use_container_width=True)


# COOK DASHBOARD
elif st.session_state.page in ["cook"]:
    if not st.session_state.logged_in or st.session_state.role not in ["Cook"]:
        st.error("You do not have permission to view this page.")
        st.stop()

    st.title("Cook Dashboard")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "View Data",
    "Batch Lookup",
    "Lot Lookup",
    "Scan Lot From Photo",
    "AI Assistant"
])

    with tab1:
        st.subheader("Current System Data")
        view_choice = st.selectbox("Choose Data to View", ["Batches", "Ingredients", "Suppliers"])
        if view_choice == "Batches":
            st.dataframe(pd.DataFrame(batches), use_container_width=True)
        elif view_choice == "Ingredients":
            st.dataframe(pd.DataFrame(ingredients), use_container_width=True)
        else:
            st.dataframe(pd.DataFrame(suppliers), use_container_width=True)

    with tab2:
        st.subheader("Find a Batch")
        batch_id = st.text_input("Enter Batch ID", key="employee_batch_id")
        if st.button("Lookup Batch", key="employee_lookup_batch", use_container_width=True):
            batch_result = batch_lookup(batches, batch_id)
            if len(batch_result) == 0:
                st.warning("No batch found.")
            else:
                st.dataframe(pd.DataFrame(batch_result), use_container_width=True)

    with tab3:
        st.subheader("Find a Lot")
        lot_number = st.text_input("Enter Lot Number", key="employee_lot_number")
        if st.button("Lookup Lot", key="employee_lookup_lot", use_container_width=True):
            lot_matches = ingredient_lookup(ingredients, lot_number)
            batch_matches = find_batches_using_lot(batches, lot_number)

            st.markdown("### Lot Record")
            if len(lot_matches) == 0:
                st.info("No matching lot found.")
            else:
                st.dataframe(pd.DataFrame(lot_matches), use_container_width=True)

            st.markdown("### Batches Using This Lot")
            if len(batch_matches) == 0:
                st.info("No matching batch records found.")
            else:
                st.dataframe(pd.DataFrame(batch_matches), use_container_width=True)
  
    with tab4:
        render_scan_lot_tab(
            tab_key_prefix="cook",
            ingredients=ingredients,
            batches=batches,
            ingredient_codes=ingredient_codes,
            suppliers=suppliers,
            current_user_name=st.session_state.user["full_name"]
        )

    with tab5:
        st.subheader("AI Assistant")
        col11, col22 = st.columns([3, 1])

        with col11:
            st.caption("Try asking: Find batch CL-250318-001")

        with col22:
            if st.button("Clear Messages", key="clear_employee_messages"):
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "Hi! I’m the Hope’s Caramels traceability assistant. Ask me about batches, lot numbers, suppliers, low stock, or type help."
                    }
                ]
                st.rerun()

        with st.container(border=True, height=300):
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        user_input = st.chat_input("Type your message here...", key="employee_chat_input")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = ai_traceability_response(user_input, suppliers, ingredients, batches)
            st.session_state.messages.append({"role": "assistant", "content": response})
            time.sleep(1)
            st.rerun()
