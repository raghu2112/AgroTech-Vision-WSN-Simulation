# Import Streamlit for web interface
import streamlit as st
# Import common navbar component
from ui.components import render_navbar

# Main render function for the setup configuration page
def render():
    # Render the top navigation bar, highlighting 'setup'
    render_navbar("setup")
    
    # Render the page header and description
    st.markdown("""
        <div class="fade-in" style="text-align: center; margin-bottom: 1.5rem;">
            <h2 style="color: var(--primary-green) !important; margin-bottom: 0.25rem;">Simulation Configuration</h2>
            <p style="color: var(--text-secondary); max-width: 600px; margin: 0 auto; font-size: 0.9rem;">
                Configure the Wireless Sensor Network topology, clustering parameters, and simulation settings.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Helper function to render a label alongside an interactive tooltip
    def label_with_tooltip(label, tooltip):
        # Inject HTML for custom label with CSS-driven hover tooltip
        st.markdown(f'''
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem; margin-top: 0.5rem;">
            <span style="font-weight: 500; color: var(--text-primary); font-size: 0.9rem;">{label}</span>
            <div class="custom-tooltip" style="margin-left: 0.5rem; position: relative; display: inline-block; cursor: help;">
                <span style="background-color: var(--primary-green); color: white; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold;">?</span>
                <div class="tooltip-text" style="visibility: hidden; width: 250px; background-color: #111827; color: #fff; text-align: center; border-radius: 6px; padding: 0.5rem; position: absolute; z-index: 1000; bottom: 125%; left: 50%; margin-left: -125px; opacity: 0; transition: opacity 0.2s; font-size: 0.8rem; box-shadow: 0 4px 6px rgba(0,0,0,0.3); font-weight: normal; line-height: 1.4;">
                    {tooltip}
                    <div style="position: absolute; top: 100%; left: 50%; margin-left: -5px; border-width: 5px; border-style: solid; border-color: #111827 transparent transparent transparent;"></div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Create the main configuration form
    with st.form("simulation_config", border=False):
        # Split configuration options into 4 columns
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        # Render Topology settings in column 1
        with col1:
            # Topology header
            st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'>🌐 Topology</h4>", unsafe_allow_html=True)
            # Label for number of nodes
            label_with_tooltip("Total Sensor Nodes", "The total number of sensor nodes randomly deployed in the simulation area.")
            # Slider for number of nodes
            num_nodes = st.slider("Total Sensor Nodes", min_value=10, max_value=200, value=50, step=10, label_visibility="collapsed")
            # Label for communication range
            label_with_tooltip("Comm Range (m)", "The maximum distance a node can reliably communicate with other nodes or the Base Station.")
            # Slider for communication range
            comm_range = st.slider("Comm Range (m)", min_value=15.0, max_value=100.0, value=35.0, step=5.0, label_visibility="collapsed")
            # Label for field width
            label_with_tooltip("Field Width (m)", "The horizontal dimension of the simulation field in meters.")
            # Slider for field width
            field_w = st.slider("Field Width (m)", min_value=50, max_value=500, value=100, step=10, label_visibility="collapsed")
            # Label for field height
            label_with_tooltip("Field Height (m)", "The vertical dimension of the simulation field in meters.")
            # Slider for field height
            field_h = st.slider("Field Height (m)", min_value=50, max_value=500, value=100, step=10, label_visibility="collapsed")
            
        # Render Clustering settings in column 2
        with col2:
            # Clustering header
            st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'>⚡ Clustering</h4>", unsafe_allow_html=True)
            # Label for energy threshold
            label_with_tooltip("CH Energy Threshold (J)", "Minimum residual energy required for a node to be eligible for election as a Cluster Head.")
            # Slider for energy threshold
            energy_threshold = st.slider("CH Energy Threshold (J)", min_value=0.1, max_value=1.0, value=0.3, step=0.05, label_visibility="collapsed")
            # Label for rotation interval
            label_with_tooltip("Rotation Interval (Rounds)", "Number of simulation rounds before the network triggers a new Cluster Head election phase.")
            # Slider for rotation interval
            rotation_interval = st.slider("Rotation Interval (Rounds)", min_value=1, max_value=20, value=5, step=1, label_visibility="collapsed")
            # Vertical spacer
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            # Label for auto re-clustering checkbox
            label_with_tooltip("Enable Auto Re-clustering", "If enabled, the simulation automatically rebuilds clusters when the rotation interval is reached.")
            # Checkbox for auto re-clustering
            auto_recluster = st.checkbox("Enable Auto Re-clustering", value=True, label_visibility="collapsed")
            
        # Render Advanced Network settings in column 3
        with col3:
            # Network settings header
            st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'>📡 Adv. Network</h4>", unsafe_allow_html=True)
            # Label for multi-hop routing
            label_with_tooltip("Multi-Hop Routing", "If enabled, Cluster Heads route data through other closer Cluster Heads instead of directly to the Base Station.")
            # Checkbox for multi-hop routing
            multi_hop = st.checkbox("Multi-Hop Routing", value=True, label_visibility="collapsed")
            # Label for event-driven sensing
            label_with_tooltip("Event-Driven Sensing", "If enabled, sensors only transmit data when a random spatial event occurs, significantly reducing energy consumption.")
            # Checkbox for event-driven sensing
            event_driven = st.checkbox("Event-Driven Sensing", value=True, label_visibility="collapsed")
            # Label for 3D terrain
            label_with_tooltip("3D Topography & Obstacles", "If enabled, the simulation generates mathematical terrain that blocks Line-of-Sight, forcing nodes to route around hills.")
            # Checkbox for 3D terrain
            enable_3d = st.checkbox("3D Topography & Obstacles", value=False, label_visibility="collapsed")
            
        # Render Algorithm Weights settings in column 4
        with col4:
            # Algorithm Weights header
            st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'>⚖️ Algorithm Weights</h4>", unsafe_allow_html=True)
            # Label for energy weight
            label_with_tooltip("w1 (Residual Energy)", "Fitness weight for remaining energy. Higher values prioritize nodes with more battery left.")
            # Slider for energy weight
            w1 = st.slider("w1 (Residual Energy)", min_value=0.0, max_value=1.0, value=0.5, step=0.1, label_visibility="collapsed")
            # Label for distance weight
            label_with_tooltip("w2 (Distance to BS)", "Fitness weight for distance to Base Station. Higher values prioritize nodes physically closer to the BS.")
            # Slider for distance weight
            w2 = st.slider("w2 (Distance to BS)", min_value=0.0, max_value=1.0, value=0.3, step=0.1, label_visibility="collapsed")
            # Label for neighbor density weight
            label_with_tooltip("w3 (Neighbor Density)", "Fitness weight for node density. Higher values prioritize nodes surrounded by many other sensors.")
            # Slider for neighbor density weight
            w3 = st.slider("w3 (Neighbor Density)", min_value=0.0, max_value=1.0, value=0.2, step=0.1, label_visibility="collapsed")

        # Vertical spacer before submit button
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # Center the submit button in the middle column
        submit_col1, submit_col2, submit_col3 = st.columns([1, 1, 1])
        with submit_col2:
            # Render the form submit button
            submitted = st.form_submit_button("Launch Simulation", use_container_width=True, type="primary")
            
    # Process form submission
    if submitted:
        # Save all selected configuration parameters to session state
        st.session_state.config = {
            "num_nodes": num_nodes,
            "field_w": field_w,
            "field_h": field_h,
            "comm_range": comm_range,
            "energy_threshold": energy_threshold,
            "rotation_interval": rotation_interval,
            "auto_recluster": auto_recluster,
            "multi_hop": multi_hop,
            "event_driven": event_driven,
            "enable_3d": enable_3d,
            "w1": w1,
            "w2": w2,
            "w3": w3
        }
        # Route the user to the loading screen
        st.session_state.page = "loading"
        # Trigger an immediate Streamlit rerun
        st.rerun()
