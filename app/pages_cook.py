"""
Cook dashboard page rendering for Hope's Caramels Traceability System.
"""
import streamlit as st
import pandas as pd
from app.pages import render_scan_lot_tab
from app.search import batch_lookup, ingredient_lookup, find_batches_using_lot

def render_cook_dashboard(users, suppliers, ingredient_codes, flavor_codes, ingredients, batches, current_user):
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
            current_user_name=current_user["full_name"]
        )
    # AI Assistant tab can be added here as needed
