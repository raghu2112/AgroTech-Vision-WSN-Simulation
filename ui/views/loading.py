import streamlit as st
import time
from simulation import WSNSimulation

def render():
    cfg = st.session_state.config

    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            <div class="fade-in" style="text-align: center; margin-bottom: 2rem;">
                <h2 style="color: var(--primary-green) !important;">Initializing Environment</h2>
                <p style="color: var(--text-secondary);">Provisioning Wireless Sensor Network simulation...</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # A simple placeholder for progress updates
        status_container = st.empty()
        progress_bar = st.progress(0)
        
        steps = [
            "Deploying sensor nodes across field...",
            "Computing neighbor adjacency graph...",
            "Running K-Means Clustering...",
            "Selecting optimal Cluster Heads...",
            "Building network topology...",
            "Preparing Analytics Dashboard..."
        ]
        
        # Fake loading steps for UI polish, and actual instantiation at step 3
        for i, step_text in enumerate(steps):
            progress_pct = int(((i + 1) / len(steps)) * 100)
            
            # HTML for the current step
            status_html = f"""
            <div class="sci-card fade-in" style="margin-bottom: 1rem; border-left: 4px solid var(--accent-blue);">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-weight: 500;">Step {i+1}/6</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">{step_text}</span>
                </div>
            </div>
            """
            status_container.markdown(status_html, unsafe_allow_html=True)
            progress_bar.progress(progress_pct)
            
            if i == 2:
                # Instantiate simulation logic here
                sim = WSNSimulation(
                    num_nodes=cfg.get("num_nodes", 50), 
                    energy_threshold=cfg.get("energy_threshold", 0.3),
                    comm_range=cfg.get("comm_range", 35.0), 
                    w1=cfg.get("w1", 0.5), 
                    w2=cfg.get("w2", 0.3), 
                    w3=cfg.get("w3", 0.2),
                    rotation_interval=cfg.get("rotation_interval", 5),
                    auto_recluster=cfg.get("auto_recluster", True),
                    field_size=(cfg.get("field_w", 100), cfg.get("field_h", 100))
                )
                sim.initialize()
                st.session_state.sim = sim
                time.sleep(0.5)
            else:
                time.sleep(0.4)
                
        time.sleep(0.5)
        st.session_state.page = "dashboard"
        st.rerun()
