# Import the main Streamlit library for the web app UI
import streamlit as st
# Import custom CSS injection function to style the app
from ui.components import inject_custom_css
# Import all page views for the application routing
from ui.views import landing, setup, loading, dashboard, inspector

# ─── Page Config ───
# Configure the browser tab title, icon, and default layout settings
st.set_page_config(
    page_title="AgroTech Vision | WSN Simulation",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Session State Initialization ───
# Initialize the current page to landing on first load
if "page" not in st.session_state: st.session_state.page = "landing"
# Initialize the simulation instance placeholder
if "sim" not in st.session_state: st.session_state.sim = None
# Initialize the user configuration dictionary
if "config" not in st.session_state: st.session_state.config = {}
# Initialize the auto-run toggle for the simulation
if "auto_run" not in st.session_state: st.session_state.auto_run = False

# ─── Custom CSS Injection ───
# Apply the global CSS styles to the application
inject_custom_css()

# Prevent scrolling on landing & loading pages only (setup needs scroll for 4 columns)
# Hide the scrollbar globally for clean transitions
if st.session_state.page in ["landing", "loading"]:
    st.markdown("""
    <style>
        /* Force body to not overflow */
        html, body, .stApp { overflow: hidden !important; }
        /* Hide webkit scrollbar */
        ::-webkit-scrollbar { display: none; }
    </style>
    """, unsafe_allow_html=True)

# Reset any leftover landing-page background on non-landing pages
# Ensures clean background transition after leaving landing page
if st.session_state.page != "landing":
    st.markdown("""
    <style>
        /* Remove the background image on standard pages */
        .stApp {
            background-image: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ─── Routing ───
# Retrieve the current active page
page = st.session_state.page

# Route to the appropriate render function based on the active page state
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
    # Fallback error message if page is invalid
    st.error("Page not found.")

