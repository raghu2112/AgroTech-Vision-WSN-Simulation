# Import Streamlit for web interface
import streamlit as st
# Import time for simulating loading delays
import time
# Import the main simulation engine
from simulation import WSNSimulation

# Main render function for the loading page
def render():
    # Fetch configuration settings from session state
    cfg = st.session_state.config

    # Vertical spacer
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    
    # Define layout columns to center content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Render loading UI in the center column
    with col2:
        # Display initialization header text
        st.markdown(
            """
            <div class="fade-in" style="text-align: center; margin-bottom: 2rem;">
                <h2 style="color: var(--primary-green) !important;">Initializing Environment</h2>
                <p style="color: var(--text-secondary);">Provisioning Wireless Sensor Network simulation...</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # A simple placeholder for progress text updates
        status_container = st.empty()
        # Initialize a progress bar at 0%
        progress_bar = st.progress(0)
        
        # Define the sequence of fake loading messages
        steps = [
            "Deploying sensor nodes across field...",
            "Computing neighbor adjacency graph...",
            "Running K-Means Clustering...",
            "Selecting optimal Cluster Heads...",
            "Building network topology...",
            "Preparing Analytics Dashboard..."
        ]
        
        # Loop over the simulated steps
        for i, step_text in enumerate(steps):
            # Calculate completion percentage
            progress_pct = int(((i + 1) / len(steps)) * 100)
            
            # Format HTML for the current step indicator
            status_html = f"""
            <div class="sci-card fade-in" style="margin-bottom: 1rem; border-left: 4px solid var(--accent-blue);">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-weight: 500;">Step {i+1}/6</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">{step_text}</span>
                </div>
            </div>
            """
            # Inject the current status HTML
            status_container.markdown(status_html, unsafe_allow_html=True)
            # Update the progress bar
            progress_bar.progress(progress_pct)
            
            # Perform actual initialization exactly halfway through
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
                    multi_hop=cfg.get("multi_hop", True),
                    event_driven=cfg.get("event_driven", True),
                    enable_3d=cfg.get("enable_3d", False),
                    field_size=(cfg.get("field_w", 100), cfg.get("field_h", 100))
                )
                # Run the initial clustering and setup
                sim.initialize()
                # Store the simulation instance in session state
                st.session_state.sim = sim
                # Small artificial delay for visual pacing
                time.sleep(0.5)
            # Other steps just wait briefly for visual effect
            else:
                time.sleep(0.4)
                
        # Final brief pause before transition
        time.sleep(0.5)
        # Advance to the dashboard page
        st.session_state.page = "dashboard"
        # Trigger page transition
        st.rerun()
