# Import Streamlit for web interface
import streamlit as st
# Import Plotly for drawing the local network topology
import plotly.graph_objects as go
# Import custom components and theming functions
from ui.components import render_navbar, render_metric_card, apply_light_theme

# Main render function for the inspector view
def render():
    # Fetch the active simulation object from session state
    sim = st.session_state.sim
    # Redirect to the setup page if the simulation is not initialized
    if sim is None:
        st.session_state.page = "setup"
        st.rerun()

    # Render the top navigation bar, highlighting 'inspector'
    render_navbar("inspector")
    
    # ─── Header & Node Selection ───
    # Render the page title
    st.markdown("<h3 style='color: var(--primary-green) !important; margin-bottom: 0.25rem;'>Node Inspector</h3>", unsafe_allow_html=True)
    # Render the page subtitle
    st.markdown("<p style='color: var(--text-secondary); font-size: 0.9rem;'>Inspect individual sensor nodes and monitor their real-time network status.</p>", unsafe_allow_html=True)
    
    # Initialize the selected node ID in session state if missing
    if "selected_node_id" not in st.session_state:
        st.session_state.selected_node_id = 0
        
    # Generate a list of formatted node names for the dropdown
    node_opts = [f"Node {n.id}" for n in sim.nodes]
    # Handle edge case where selected ID exceeds the current node count
    if st.session_state.selected_node_id >= len(node_opts):
        st.session_state.selected_node_id = 0
        
    # Set up layout columns for the selection controls
    c1, c2, c3, c4 = st.columns([2, 1, 1, 4])
    # Render a dropdown select box for choosing a specific node
    selected = c1.selectbox("Select Node", options=node_opts, index=st.session_state.selected_node_id, label_visibility="collapsed")
    
    # Extract the integer ID from the selected dropdown string
    selected_id = int(selected.split(" ")[1])
    # If the selection changed via dropdown, update state and rerun
    if selected_id != st.session_state.selected_node_id:
        st.session_state.selected_node_id = selected_id
        st.rerun()
        
    # Render 'Previous Node' button
    if c2.button("← Previous", use_container_width=True):
        # Decrement node ID safely
        st.session_state.selected_node_id = max(0, st.session_state.selected_node_id - 1)
        st.rerun()
        
    # Render 'Next Node' button
    if c3.button("Next →", use_container_width=True):
        # Increment node ID safely
        st.session_state.selected_node_id = min(len(sim.nodes) - 1, st.session_state.selected_node_id + 1)
        st.rerun()

    # Fetch the actual node object corresponding to the current selection
    n = sim.nodes[st.session_state.selected_node_id]

    # Render a vertical spacer
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # ─── KPI Cards ───
    # Set up 6 columns for KPI cards
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    
    # Format the live status string
    status_str = "Alive" if n.is_alive else "Dead"
    # Select color based on live status
    status_color = "#16A34A" if n.is_alive else "#DC2626"
    # Format the current role string
    role_str = "CH" if n.is_ch else ("Dead" if not n.is_alive else "Sensor")
    # Format the assigned cluster ID
    cluster_str = str(n.cluster_id) if n.cluster_id >= 0 else "N/A"
    # Calculate physical distance to base station
    dist_bs = n.distance_to(sim.base_station)
    
    # Render Status KPI
    with k1: render_metric_card(st, "Status", status_str, status_color)
    # Render Role KPI
    with k2: render_metric_card(st, "Role", role_str, "#2563EB")
    # Render Energy Level KPI
    with k3: render_metric_card(st, "Energy", f"{n.energy:.4f}J", "#F59E0B")
    # Render Cluster ID KPI
    with k4: render_metric_card(st, "Cluster", cluster_str, "#6B7280")
    # Render Neighbor Count KPI
    with k5: render_metric_card(st, "Neighbors", f"{n.neighbors}", "#8B5CF6")
    # Render Distance to Base Station KPI
    with k6: render_metric_card(st, "Dist. to BS", f"{dist_bs:.1f}m", "#0EA5E9")

    # Render a vertical spacer
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # ─── Main Content Split ───
    # Split the main area into left (details/logs) and right (map)
    left, right = st.columns([1, 2], gap="medium")
    
    # Render left panel
    with left:
        # Open card container
        st.markdown("<div class='sci-card' style='padding: 1rem; height: 100%;'>", unsafe_allow_html=True)
        # Add Node Details header
        st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 1rem;'>Node Details</h4>", unsafe_allow_html=True)
        
        # Build HTML table for detailed node stats
        details_html = f"""
        <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
            <tr><td style="padding: 0.25rem 0; color: var(--text-secondary);">Node ID</td><td style="text-align: right; font-weight: 500; color: #111827;">{n.id}</td></tr>
            <tr><td style="padding: 0.25rem 0; color: var(--text-secondary);">Coordinates</td><td style="text-align: right; font-weight: 500; color: #111827;">({n.x:.1f}, {n.y:.1f})</td></tr>
            <tr><td style="padding: 0.25rem 0; color: var(--text-secondary);">Current CH</td><td style="text-align: right; font-weight: 500; color: #111827;">{cluster_str}</td></tr>
            <tr><td style="padding: 0.25rem 0; color: var(--text-secondary);">Initial Energy</td><td style="text-align: right; font-weight: 500; color: #111827;">{n.initial_energy:.2f} J</td></tr>
            <tr><td style="padding: 0.25rem 0; color: var(--text-secondary);">Consumed</td><td style="text-align: right; font-weight: 500; color: #111827;">{(n.initial_energy - n.energy):.4f} J</td></tr>
            <tr><td style="padding: 0.25rem 0; color: var(--text-secondary);">Packets Sent</td><td style="text-align: right; font-weight: 500; color: #111827;">{n.data_sent}</td></tr>
        </table>
        """
        # Inject HTML table
        st.markdown(details_html, unsafe_allow_html=True)
        
        # Add Activity Log header
        st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-top: 1.5rem; margin-bottom: 0.5rem;'>Activity Log</h4>", unsafe_allow_html=True)
        
        # Filter global logs for entries relevant to this specific node
        node_logs = [log for log in sim.logs if f"Node {n.id}" in log or f"CH {n.id}" in log]
        # Check if relevant logs exist
        if node_logs:
            # Accumulate formatted log entries
            log_entries = ""
            # Iterate backwards over the most recent 15 logs
            for log in reversed(node_logs[-15:]):
                # Append log item HTML
                log_entries += f'<div style="border-bottom: 1px solid var(--border-color); padding: 2px 0; color: #111827;">{log}</div>'
            # Inject log panel HTML
            st.markdown(f'<div class="log-panel-container">{log_entries}</div>', unsafe_allow_html=True)
        else:
            # Display fallback if no logs are found
            st.markdown('<div class="log-panel-container" style="color: #6B7280;">No specific events logged.</div>', unsafe_allow_html=True)
        
        # Close card container
        st.markdown("</div>", unsafe_allow_html=True)

    # Render right panel (Local Topology map)
    with right:
        # Open card container
        st.markdown("<div class='sci-card' style='padding: 1rem; height: 100%;'>", unsafe_allow_html=True)
        # Add Local Topology header
        st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0;'>Local Topology</h4>", unsafe_allow_html=True)
        
        # Initialize a new Plotly figure
        fig = go.Figure()
        # Draw the simulation field boundary box
        fig.add_shape(type="rect", x0=0, y0=0, x1=sim.field_w, y1=sim.field_h, line=dict(color="rgba(46, 125, 50, 0.2)", width=1, dash="dot"), fillcolor="rgba(248, 250, 245, 0.5)")
        
        # Plot the base station location
        fig.add_trace(go.Scatter(x=[sim.base_station[0]], y=[sim.base_station[1]], mode="markers+text", text=["BS"], textposition="top center", textfont=dict(color="#1F2937", size=10), marker=dict(size=14, color="#2563EB", symbol="square", opacity=0.8), name="Base Station", hoverinfo="skip"))
        
        # Gather coordinates of all OTHER nodes
        all_x = [node.x for node in sim.nodes if node.id != n.id]
        all_y = [node.y for node in sim.nodes if node.id != n.id]
        # Assign grey to alive and red to dead nodes
        all_colors = ["rgba(107, 114, 128, 0.6)" if node.is_alive else "rgba(220, 38, 38, 0.4)" for node in sim.nodes if node.id != n.id]
        
        # Plot all other nodes faintly in the background
        fig.add_trace(go.Scatter(x=all_x, y=all_y, mode="markers", marker=dict(size=8, color=all_colors), hoverinfo="skip", name="Other Nodes"))
        
        # Plot the selected node prominently
        fig.add_trace(go.Scatter(x=[n.x], y=[n.y], mode="markers+text", text=[f"Node {n.id}"], textposition="top center", textfont=dict(color="#1F2937", size=12, weight="bold"), marker=dict(size=16, color="#16A34A" if n.is_alive else "#DC2626", line=dict(width=2, color="#000")), name="Selected Node"))
        
        # If node is alive, draw its communication range ring
        if n.is_alive:
            fig.add_shape(type="circle", xref="x", yref="y", x0=n.x-sim.comm_range, y0=n.y-sim.comm_range, x1=n.x+sim.comm_range, y1=n.y+sim.comm_range, line_color="rgba(46, 125, 50, 0.4)", line_dash="dot")
        
        # Draw connectivity arrows if the node is alive
        if n.is_alive:
            # If the node is a Cluster Head, draw an arrow to the Base Station
            if n.is_ch:
                fig.add_annotation(x=sim.base_station[0], y=sim.base_station[1], ax=n.x, ay=n.y, xref='x', yref='y', axref='x', ayref='y', showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="#2563EB")
            # If it's a normal node in a cluster, draw an arrow to its Cluster Head
            elif n.cluster_id >= 0:
                # Find the assigned Cluster Head object
                local_ch = next((ch for ch in sim.current_chs if ch.id == n.cluster_id), None)
                if local_ch:
                    # Highlight the assigned Cluster Head
                    fig.add_trace(go.Scatter(x=[local_ch.x], y=[local_ch.y], mode="markers+text", text=[f"CH {local_ch.id}"], textposition="bottom center", textfont=dict(color="#1F2937", size=11), marker=dict(size=12, color="#2E7D32", symbol="diamond"), name="Assigned CH"))
                    # Draw a directional arrow to the Cluster Head
                    fig.add_annotation(x=local_ch.x, y=local_ch.y, ax=n.x, ay=n.y, xref='x', yref='y', axref='x', ayref='y', showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#16A34A")
        
        # Configure the layout of the local topology chart
        fig.update_layout(
            xaxis=dict(range=[-5, sim.field_w + 15], visible=False, fixedrange=True),
            yaxis=dict(range=[-5, sim.field_h + 25], scaleanchor="x", visible=False, fixedrange=True),
            height=450,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False
        )
        # Apply the global light theme to the chart
        fig = apply_light_theme(fig)
        # Display the chart via Streamlit
        st.plotly_chart(fig, use_container_width=True, theme=None, config={'displayModeBar': False})
        # Close the card container
        st.markdown("</div>", unsafe_allow_html=True)
