"""
Cook dashboard page rendering for Hope's Caramels Traceability System.
"""
import streamlit as st
import pandas as pd
from app.pages import render_scan_lot_tab
from app.search import batch_lookup, ingredient_lookup, find_batches_using_lot

def render_cook_dashboard(users, suppliers, ingredient_codes, flavor_codes, ingredients, batches, current_user):
    st.title("Cook Dashboard")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "View Data",
        "Batch Lookup",
        "Lot Lookup",
        "Scan Lot From Photo",
        "Add Batch",
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
            current_user_name=current_user["full_name"]
        )

    with tab5:
        st.subheader("Add New Batch")
        from app.utils import generate_batch_id
        from app.data import save_json, BATCHES_PATH, timestamp_now
        from app.ocr import extract_lot_from_image
        col1, col2 = st.columns(2)
        with col1:
            selected_flavor = st.selectbox(
                "Select Flavor",
                options=flavor_codes,
                format_func=lambda x: f'{x["flavor_code"]} - {x["flavor_name"]}'
            )
            flavor_code = selected_flavor["flavor_code"]
            flavor_name = selected_flavor["flavor_name"]
            date_produced = st.date_input("Date Produced", value=pd.to_datetime("today"))
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
            lot_options = [i["lot_number"] for i in ingredients if i["ingredient_name"].lower() == code.lower()]
            col_lot, col_cam = st.columns([5,1])
            # Use session state to store OCR result for each ingredient
            ocr_key = f"cook_batch_{key}_ocr"
            selected_lots = col_lot.multiselect(f"{code} Lots", options=lot_options, key=f"cook_batch_{key}_lots")
            uploaded_file = col_cam.file_uploader(" ", type=["png","jpg","jpeg","webp"], key=f"cook_batch_{key}_upload", label_visibility="collapsed")
            if uploaded_file is not None:
                extracted_lot, raw_lines, error_message = extract_lot_from_image(uploaded_file)
                if error_message:
                    col_cam.error(error_message)
                elif extracted_lot:
                    # Add OCR result to dropdown if not present
                    if extracted_lot not in lot_options:
                        lot_options.append(extracted_lot)
                    # Add to selected lots if not already selected
                    if extracted_lot not in selected_lots:
                        selected_lots.append(extracted_lot)
                    # Update the multiselect value in session state
                    st.session_state[f"cook_batch_{key}_lots"] = selected_lots
                    col_cam.success(f"Read: {extracted_lot}")
            ingredient_lots[key] = st.session_state.get(f"cook_batch_{key}_lots", selected_lots)
        if st.button("Add Batch", key="cook_add_batch_btn", type="primary", use_container_width=True):
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
