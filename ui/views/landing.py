import streamlit as st

import base64

import base64
import os

def render():
    """Renders the landing page view. Fits completely inside one viewport."""
    
    # Detailed Agricultural WSN Background Image
    bg_path = r"C:\Users\raghu\.gemini\antigravity-ide\brain\025e1b7d-43e2-41d5-9281-ff5efbcdc5cb\agrotech_landing_bg_outline_1783397086799.png"
    bg_url = ""
    if os.path.exists(bg_path):
        with open(bg_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode("utf-8")
        bg_url = f"data:image/png;base64,{b64_img}"
    
    st.markdown(f"""
        <style>
            /* Apply beautiful detailed WSN agriculture background exclusively */
            .stApp {{
                background-color: var(--bg-color) !important;
                background-image: 
                    linear-gradient(to bottom, rgba(248, 250, 245, 0.2) 0%, rgba(248, 250, 245, 0) 50%),
                    url("{bg_url}") !important;
                background-size: cover !important;
                background-position: center 30% !important;
                background-repeat: no-repeat !important;
            }}
            
            /* Premium Call-to-Action Button Styling */
            div[data-testid="stButton"] button[kind="primary"] {{
                background: linear-gradient(135deg, var(--primary-green) 0%, #1b4d1e 100%) !important;
                border: none !important;
                box-shadow: 0 8px 20px rgba(46, 125, 50, 0.3) !important;
                transition: all 0.3s ease !important;
                text-transform: uppercase !important;
                letter-spacing: 1.5px !important;
                font-weight: 700 !important;
                padding: 1.5rem !important;
                border-radius: 50px !important;
                font-size: 1.1rem !important;
            }}
            
            div[data-testid="stButton"] button[kind="primary"]:hover {{
                transform: translateY(-3px) !important;
                box-shadow: 0 12px 25px rgba(46, 125, 50, 0.5) !important;
                background: linear-gradient(135deg, #36953A 0%, var(--primary-green) 100%) !important;
                color: white !important;
            }}
        </style>
        <div style='height: 10vh;'></div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 2.5rem; background: rgba(255, 255, 255, 0.5); backdrop-filter: blur(20px); padding: 3rem 2rem; border-radius: 1.5rem; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.6);" class="fade-in">
                <h1 style="font-size: 3.5rem; color: var(--primary-green) !important; margin-bottom: 1rem; letter-spacing: -0.05em; line-height: 1.1; text-shadow: 0 2px 4px rgba(255,255,255,0.8);">AgroTech Vision</h1>
                <h3 style="font-size: 1.25rem; color: #374151 !important; font-weight: 600; max-width: 700px; margin: 0 auto; line-height: 1.5; text-shadow: 0 1px 2px rgba(255,255,255,0.8);">
                    Production-Grade Wireless Sensor Network Simulation Platform for Smart Agriculture.
                </h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Single Primary CTA
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        with btn_col2:
            if st.button("Initialize Simulation", use_container_width=True, type="primary"):
                st.session_state.page = "setup"
                st.rerun()

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # Compact Feature Highlights
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem; display: flex; justify-content: center;" class="fade-in">
            <div style="display: inline-flex; justify-content: center; gap: 3rem; color: #111827; font-size: 1rem; font-weight: 700; background: rgba(255, 255, 255, 0.5); backdrop-filter: blur(20px); padding: 1rem 2.5rem; border-radius: 100px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.6); text-shadow: 0 1px 2px rgba(255,255,255,0.8);">
                <span style="display: flex; align-items: center; gap: 0.5rem;">🎯 K-Means Clustering</span>
                <span style="display: flex; align-items: center; gap: 0.5rem;">🔄 Dynamic CH Rotation</span>
                <span style="display: flex; align-items: center; gap: 0.5rem;">⚡ Energy Analytics</span>
                <span style="display: flex; align-items: center; gap: 0.5rem;">📊 Interactive Topology</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
