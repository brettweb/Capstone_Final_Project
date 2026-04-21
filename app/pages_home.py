"""
Home page rendering for Hope's Caramels Traceability System.
"""
import streamlit as st
import pandas as pd

def render_home_page(users, suppliers, ingredients, batches, flavor_codes, role):
    st.title("Home")
    st.success(f"Welcome, {st.session_state.user['full_name']} ({role})")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Users", len(users))
    c2.metric("Suppliers", len(suppliers))
    c3.metric("Ingredient Lots", len(ingredients))
    c4.metric("Batches", len(batches))
    if role == "Owner":
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
