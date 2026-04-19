"""
Page rendering functions for Hope's Caramels Traceability System.
Each function renders a specific page or tab in the Streamlit app.
"""
import streamlit as st
import pandas as pd
import time
from datetime import datetime, date
from app.data import save_json, USERS_PATH, INGREDIENTS_PATH, BATCHES_PATH, timestamp_now
from app.utils import generate_batch_id, ingredient_to_batch_key, normalize_lot_text
from app.auth import authenticate_user, register_user
from app.search import supplier_lookup, ingredient_lookup, batch_lookup, find_batches_using_lot, low_stock_ingredients
from app.ocr import extract_lot_from_image, parse_lot_number

# --- Helper for saving scanned lot (used in scan lot tab) ---
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

# --- Scan Lot Tab ---
def render_scan_lot_tab(tab_key_prefix, ingredients, batches, ingredient_codes, suppliers, current_user_name):
    st.subheader("Scan Lot Number From Photo")
    st.caption("Upload a picture of a lot label. AI will read the lot number, let you confirm it, save it to the ingredient JSON, and optionally link it to one or more caramel batches.")
    try:
        import easyocr
    except ImportError:
        st.warning("OCR package missing. Install: pip install easyocr pillow numpy")
    extracted_lot = st.session_state.get(f"{tab_key_prefix}_ocr_lot", "")
    lot_info = parse_lot_number(extracted_lot, ingredient_codes, suppliers) if extracted_lot else {}
    if extracted_lot:
        if st.session_state.get(f"{tab_key_prefix}_edited_lot", "") != extracted_lot:
            st.session_state[f"{tab_key_prefix}_edited_lot"] = extracted_lot
        if "ingredient_name" in lot_info:
            st.session_state[f"{tab_key_prefix}_scan_ingredient_name"] = lot_info["ingredient_name"]
            st.session_state[f"{tab_key_prefix}_scan_ingredient_code"] = lot_info.get("ingredient_code", "")
        if "supplier_name" in lot_info:
            st.session_state[f"{tab_key_prefix}_scan_supplier_name"] = lot_info["supplier_name"]
            st.session_state[f"{tab_key_prefix}_scan_supplier_code"] = lot_info.get("supplier_code", "")
        if "quantity_text" in lot_info:
            st.session_state[f"{tab_key_prefix}_scan_quantity_text"] = lot_info["quantity_text"]
            st.session_state[f"{tab_key_prefix}_scan_quantity_value"] = lot_info.get("quantity_value", 0.0)
        if "default_unit" in lot_info:
            st.session_state[f"{tab_key_prefix}_scan_default_unit"] = lot_info["default_unit"]
        if "date_received" in lot_info:
            st.session_state[f"{tab_key_prefix}_scan_date"] = lot_info["date_received"]
        if "default_unit" in lot_info and f"{tab_key_prefix}_scan_storage" not in st.session_state:
            pass
    col1, col2 = st.columns(2)
    with col2:
        ingredient_name = st.session_state.get(f"{tab_key_prefix}_scan_ingredient_name", "")
        ingredient_code = st.session_state.get(f"{tab_key_prefix}_scan_ingredient_code", "")
        selected_supplier_name = st.session_state.get(f"{tab_key_prefix}_scan_supplier_name", "")
        supplier_code = st.session_state.get(f"{tab_key_prefix}_scan_supplier_code", "")
        quantity_text = st.session_state.get(f"{tab_key_prefix}_scan_quantity_text", "")
        quantity_value = st.session_state.get(f"{tab_key_prefix}_scan_quantity_value", 0.0)
        date_received_value = st.session_state.get(f"{tab_key_prefix}_scan_date", datetime.today())
        st.text_input(
            "Ingredient",
            value=f"{ingredient_name} ({ingredient_code})" if ingredient_name else "",
            disabled=True
        )
        st.text_input(
            "Supplier",
            value=f"{selected_supplier_name} ({supplier_code})" if selected_supplier_name else "",
            disabled=True
        )
        st.text_input(
            "Quantity",
            value=quantity_text,
            disabled=True
        )
        st.text_input(
            "Date Received",
            value=date_received_value.strftime("%Y-%m-%d") if isinstance(date_received_value, (datetime, date)) else str(date_received_value),
            disabled=True
        )
        expiration_date = st.text_input(
            "Expiration Date (optional)",
            key=f"{tab_key_prefix}_scan_exp"
        )
        storage_location = st.text_input(
            "Storage Location",
            value=st.session_state.get(f"{tab_key_prefix}_scan_storage", "Cooler"),
            key=f"{tab_key_prefix}_scan_storage"
        )
        notes = st.text_area("Notes", key=f"{tab_key_prefix}_scan_notes")
        batch_options = [b["batch_id"] for b in batches]
        selected_batch_ids = st.multiselect(
            "Link this lot to batch(es)",
            options=batch_options,
            key=f"{tab_key_prefix}_scan_batches"
        )
    with col1:
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
            if st.session_state.get(f"{tab_key_prefix}_edited_lot", "") != extracted_lot:
                st.session_state[f"{tab_key_prefix}_edited_lot"] = extracted_lot
            edited_lot = st.text_input(
                "Confirm or edit lot number before saving",
                key=f"{tab_key_prefix}_edited_lot"
            )
            if st.button("Save Scanned Lot", key=f"{tab_key_prefix}_save_btn", type="primary", use_container_width=True):
                if not edited_lot.strip():
                    st.error("Lot number cannot be blank.")
                else:
                    edited_lot_norm = normalize_lot_text(edited_lot)
                    parsed_edit = parse_lot_number(edited_lot_norm, ingredient_codes, suppliers)
                    ingredient_name = parsed_edit.get("ingredient_name", st.session_state.get(f"{tab_key_prefix}_scan_ingredient_name", ""))
                    ingredient_code = parsed_edit.get("ingredient_code", st.session_state.get(f"{tab_key_prefix}_scan_ingredient_code", ""))
                    unit = parsed_edit.get("default_unit", st.session_state.get(f"{tab_key_prefix}_scan_default_unit", ""))
                    supplier_code = parsed_edit.get("supplier_code", st.session_state.get(f"{tab_key_prefix}_scan_supplier_code", ""))
                    supplier_name = parsed_edit.get("supplier_name", st.session_state.get(f"{tab_key_prefix}_scan_supplier_name", ""))
                    quantity_text = parsed_edit.get("quantity_text", st.session_state.get(f"{tab_key_prefix}_scan_quantity_text", ""))
                    quantity_value = parsed_edit.get("quantity_value", st.session_state.get(f"{tab_key_prefix}_scan_quantity_value", 0.0))
                    if "date_received" in parsed_edit:
                        date_received_value = parsed_edit["date_received"]
                    if not ingredient_name or not ingredient_code or not supplier_code or not supplier_name:
                        st.error("Unable to save scanned lot: missing ingredient or supplier information.")
                    else:
                        if not quantity_text and unit:
                            quantity_text = f"{quantity_value:g}{unit}"
                        st.session_state[f"{tab_key_prefix}_scan_ingredient_name"] = ingredient_name
                        st.session_state[f"{tab_key_prefix}_scan_ingredient_code"] = ingredient_code
                        st.session_state[f"{tab_key_prefix}_scan_supplier_name"] = supplier_name
                        st.session_state[f"{tab_key_prefix}_scan_supplier_code"] = supplier_code
                        st.session_state[f"{tab_key_prefix}_scan_quantity_text"] = quantity_text
                        st.session_state[f"{tab_key_prefix}_scan_quantity_value"] = quantity_value
                        if "date_received" in parsed_edit:
                            st.session_state[f"{tab_key_prefix}_scan_date"] = parsed_edit["date_received"]
                        new_ingredient = {
                            "lot_number": edited_lot_norm,
                            "ingredient_code": ingredient_code,
                            "ingredient_name": ingredient_name,
                            "supplier_code": supplier_code,
                            "supplier_name": supplier_name,
                            "quantity": quantity_text,
                            "unit": unit,
                            "date_received": pd.to_datetime(date_received_value).strftime("%Y-%m-%d"),
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
