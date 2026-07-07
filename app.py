import streamlit as st
from ui.components import inject_custom_css
import ui.components# Import views
from ui.views import landing, setup, loading, dashboard, inspector
import importlib
importlib.reload(landing)
importlib.reload(setup)
importlib.reload(loading)
importlib.reload(dashboard)
importlib.reload(inspector)
importlib.reload(ui.components)

# ─── Page Config ───
st.set_page_config(
    page_title="AgroTech Vision | WSN Simulation",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Session State Initialization ───
if "page" not in st.session_state: st.session_state.page = "landing"
if "sim" not in st.session_state: st.session_state.sim = None
if "config" not in st.session_state: st.session_state.config = {}
if "auto_run" not in st.session_state: st.session_state.auto_run = False

# ─── Custom CSS Injection ───
inject_custom_css()

# If we are on landing, setup, or loading pages, we prevent scrolling globally
if st.session_state.page in ["landing", "setup", "loading"]:
    st.markdown("""
    <style>
        html, body, .stApp { overflow: hidden !important; }
        ::-webkit-scrollbar { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ─── Routing ───
page = st.session_state.page

if page == "landing":
    landing.render()
elif page == "setup":
    setup.render()
elif page == "loading":
    loading.render()
elif page == "dashboard":
    dashboard.render()
elif page == "inspector":
    inspector.render()

else:



    st.error("Page not found.")
    
# Force reload
















