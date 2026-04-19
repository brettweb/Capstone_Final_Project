
import streamlit as st
import socket
import logging
from app.data import load_all_data
from app.pages_login import render_login_page, render_register_page
from app.pages_home import render_home_page
from app.pages_owner import render_owner_dashboard
from app.pages_cook import render_cook_dashboard


st.set_page_config(
    page_title="Hope's Caramels Traceability System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Log server info for debugging
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return "127.0.0.1"

local_ip = get_local_ip()
st.info(f"[DEBUG] Streamlit running. If accessing from another device, use: http://{local_ip}:8501")
logging.basicConfig(level=logging.INFO)
logging.info(f"[DEBUG] Streamlit running. Access: http://{local_ip}:8501")

# Session state setup
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

# Load data
users, suppliers, ingredient_codes, flavor_codes, ingredients, batches = load_all_data()

# Sidebar
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
                st.session_state.page = "cook"
                st.rerun()
        if st.button("Logout", key="logout_btn", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.role = None
            st.session_state.page = "login"
            st.rerun()

# Page routing
if st.session_state.page == "login":
    render_login_page(users)
elif st.session_state.page == "register":
    render_register_page(users)
elif st.session_state.page == "home":
    if not st.session_state.logged_in:
        st.warning("Please log in first.")
        st.stop()
    render_home_page(users, suppliers, ingredients, batches, flavor_codes, st.session_state.role)
elif st.session_state.page == "owner":
    if not st.session_state.logged_in or st.session_state.role != "Owner":
        st.error("You do not have permission to view this page.")
        st.stop()
    render_owner_dashboard(users, suppliers, ingredient_codes, flavor_codes, ingredients, batches, st.session_state.user)
elif st.session_state.page == "cook":
    if not st.session_state.logged_in or st.session_state.role != "Cook":
        st.error("You do not have permission to view this page.")
        st.stop()
    render_cook_dashboard(users, suppliers, ingredient_codes, flavor_codes, ingredients, batches, st.session_state.user)
