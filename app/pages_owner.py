"""
Owner dashboard page rendering for Hope's Caramels Traceability System.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from app.utils import generate_batch_id
from app.pages import render_scan_lot_tab
from app.data import save_json, INGREDIENTS_PATH, BATCHES_PATH, timestamp_now

def render_owner_dashboard(users, suppliers, ingredient_codes, flavor_codes, ingredients, batches, current_user):
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
                "created_by": current_user["full_name"],
                "status": "unopened"
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
            current_user_name=current_user["full_name"]
        )

    with tab4:
        st.subheader("Add New Batch")
        col1, col2 = st.columns(2)
        with col1:
            selected_flavor = st.selectbox(
                "Select Flavor",
                options=flavor_codes,
                format_func=lambda x: f'{x["flavor_code"]} - {x["flavor_name"]}'
            )
            flavor_code = selected_flavor["flavor_code"]
            flavor_name = selected_flavor["flavor_name"]
            date_produced = st.date_input("Date Produced", value=datetime.today())
            batch_id = generate_batch_id(date_produced, flavor_code, batches)
            st.write(f"Batch ID: {batch_id}")
        with col2:
            st.write(f"Flavor: {flavor_name}")
            st.write(f"Date: {pd.to_datetime(date_produced).strftime('%Y-%m-%d')}")
            notes = st.text_area("Batch Notes")
            wholesale = st.checkbox("Wholesale Batch?", value=False)
        st.markdown("### Link Ingredient Lots")
        ingredient_lots = {}
        for code in ["Cream", "Butter", "Brown Sugar", "Salt", "Corn Syrup", "Sweetened Condensed Milk", "Cream of Tartar", "Flavoring", "Nuts"]:
            key = code.lower().replace(" ", "_")
            lot_options = [i["lot_number"] for i in ingredients if i["ingredient_name"].lower() == code.lower() and i.get("status", "unopened") == "opened"]
            col_lot, col_cam = st.columns([5,1])
            multiselect_key = f"batch_{key}_lots"
            from app.ocr import extract_lot_from_image
            uploaded_file = col_cam.file_uploader(" ", type=["png","jpg","jpeg","webp"], key=f"owner_batch_{key}_upload", label_visibility="collapsed")
            # Use a flag to trigger OCR update
            ocr_flag_key = f"owner_batch_{key}_ocr_flag"
            if ocr_flag_key not in st.session_state:
                st.session_state[ocr_flag_key] = False
            # If OCR flag is set, update the multiselect default and reset flag
            if st.session_state[ocr_flag_key]:
                extracted_lot = st.session_state.get(f"owner_batch_{key}_ocr_result", None)
                prev_selected = st.session_state.get(multiselect_key, [])
                if extracted_lot and extracted_lot not in prev_selected:
                    new_selected = prev_selected + [extracted_lot]
                    st.session_state[multiselect_key] = new_selected
                st.session_state[ocr_flag_key] = False
            selected_lots = col_lot.multiselect(f"{code} Lots", options=lot_options, key=multiselect_key)
            if uploaded_file is not None:
                extracted_lot, raw_lines, error_message = extract_lot_from_image(uploaded_file)
                if error_message:
                    col_cam.error(error_message)
                elif extracted_lot:
                    if extracted_lot not in lot_options:
                        lot_options.append(extracted_lot)
                    st.session_state[f"owner_batch_{key}_ocr_result"] = extracted_lot
                    st.session_state[ocr_flag_key] = True
                    col_cam.success(f"Read: {extracted_lot}. Added to selection.")
                    st.rerun()
            ingredient_lots[key] = st.session_state.get(multiselect_key, selected_lots)
        if st.button("Add Batch", key="add_batch_btn", type="primary", use_container_width=True):
            if any(b["batch_id"] == batch_id for b in batches):
                st.error("That batch ID already exists.")
            else:
                new_batch = {
                    "batch_id": batch_id,
                    "date_produced": pd.to_datetime(date_produced).strftime("%Y-%m-%d"),
                    "flavor_code": flavor_code,
                    "flavor_name": flavor_name,
                    "ingredient_lots": ingredient_lots,
                    "wholesale": wholesale,
                    "notes": notes.strip(),
                    "created_at": timestamp_now(),
                    "created_by": current_user["full_name"]
                }
                batches.append(new_batch)
                save_json(BATCHES_PATH, batches)
                st.success(f"Batch {batch_id} added successfully.")
                st.rerun()

    with tab5:
        st.subheader("Traceability Search")
        search_type = st.radio("Search for", ["Batch", "Lot"], horizontal=True)
        if search_type == "Batch":
            batch_id = st.text_input("Enter Batch ID", key="owner_search_batch_id")
            if st.button("Lookup Batch", key="owner_lookup_batch", use_container_width=True):
                from app.search import batch_lookup
                batch_result = batch_lookup(batches, batch_id)
                if len(batch_result) == 0:
                    st.warning("No batch found.")
                else:
                    st.dataframe(pd.DataFrame(batch_result), use_container_width=True)
        else:
            lot_number = st.text_input("Enter Lot Number", key="owner_search_lot_number")
            if st.button("Lookup Lot", key="owner_lookup_lot", use_container_width=True):
                from app.search import ingredient_lookup, find_batches_using_lot
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

    with tab6:
        st.subheader("AI Assistant")
        st.info("Ask the AI assistant about batches, lot numbers, suppliers, low stock, or type 'help'.")
        messages = st.session_state.get("messages", [])
        for msg in messages:
            st.chat_message(msg["role"]).write(msg["content"])
        user_input = st.chat_input("Ask a question...")
        if user_input:
            # Placeholder: In production, connect to an LLM or backend
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, the AI assistant is not yet implemented in this demo."})
            st.rerun()

    with tab7:
        st.subheader("Manage Data")
        st.markdown("### Download Data")
        st.download_button("Download Users", pd.DataFrame(users).to_csv(index=False), file_name="users.csv")
        st.download_button("Download Suppliers", pd.DataFrame(suppliers).to_csv(index=False), file_name="suppliers.csv")
        st.download_button("Download Ingredients", pd.DataFrame(ingredients).to_csv(index=False), file_name="ingredients.csv")
        st.download_button("Download Batches", pd.DataFrame(batches).to_csv(index=False), file_name="batches.csv")
        st.markdown("### Ingredient Status Management")
        status_options = ["unopened", "opened", "empty"]
        for ing in ingredients:
            col1, col2, col3 = st.columns([4, 2, 2])
            with col1:
                st.write(f"{ing['lot_number']} ({ing['ingredient_name']})")
            with col2:
                new_status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_options.index(ing.get("status", "unopened")),
                    key=f"status_{ing['lot_number']}"
                )
            with col3:
                if new_status != ing.get("status", "unopened"):
                    ing["status"] = new_status
                    save_json(INGREDIENTS_PATH, ingredients)
                    st.success(f"Status for {ing['lot_number']} set to {new_status}")
                    st.rerun()
        st.markdown("### Danger Zone")
        if st.button("Delete All Batches", key="delete_batches_btn", type="secondary", use_container_width=True):
            batches.clear()
            save_json(BATCHES_PATH, batches)
            st.success("All batches deleted.")
            st.rerun()
        if st.button("Delete All Ingredients", key="delete_ingredients_btn", type="secondary", use_container_width=True):
            ingredients.clear()
            save_json(INGREDIENTS_PATH, ingredients)
            st.success("All ingredients deleted.")
            st.rerun()
