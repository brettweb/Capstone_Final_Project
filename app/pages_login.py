"""
Login and registration page rendering for Hope's Caramels Traceability System.
"""
import streamlit as st
import time
from app.auth import authenticate_user, register_user

def render_login_page(users):
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

def render_register_page(users):
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
