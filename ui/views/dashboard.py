# Import Streamlit for web interface
import streamlit as st
# Import Plotly for 2D/3D visualizations
import plotly.graph_objects as go
# Import Pandas for data manipulation in analytics
import pandas as pd
# Import time for auto-run delays
import time
# Import custom UI components
from ui.components import render_navbar, render_metric_card, apply_light_theme
# Import helper functions
from utils import get_alive_nodes, get_dead_nodes

# Main render function for the dashboard view
def render():
    # Fetch the simulation instance from session state
    sim = st.session_state.sim
    # Redirect to setup if simulation hasn't been initialized
    if sim is None:
        st.session_state.page = "setup"
        st.rerun()
    
    # Retrieve current simulation statistics
    stats = sim.get_stats()

    # Render the top navigation bar, highlighting 'dashboard'
    render_navbar("dashboard")

    # Create 6 columns for KPI metric cards
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    # Get initial energy to calculate percentage
    initial_total_energy = sim.energy_history[0] if sim.energy_history else 1
    # Calculate residual energy percentage
    energy_pct = (stats["total_energy"] / initial_total_energy * 100) if initial_total_energy > 0 else 0
    
    # Display Alive Nodes KPI
    with m1:
        render_metric_card(st, "Alive Nodes", f"{stats['alive_nodes']}/{sim.num_nodes}", "#2E7D32")
    # Display Dead Nodes KPI
    with m2:
        render_metric_card(st, "Dead Nodes", f"{sim.num_nodes - stats['alive_nodes']}", "#DC2626")
    # Display Active Clusters KPI
    with m3:
        render_metric_card(st, "Active Clusters", f"{stats.get('num_chs', 0)}", "#2563EB")
    # Display Residual Energy KPI
    with m4:
        render_metric_card(st, "Residual Energy", f"{energy_pct:.1f}%", "#F59E0B")
    # Display Current Round KPI
    with m5:
        render_metric_card(st, "Current Round", f"{stats['round']}", "#6B7280")
    # Display Total Packets Sent KPI
    with m6:
        render_metric_card(st, "Packets Sent", f"{stats.get('total_data_sent', 0)}", "#16A34A")

    # Add a spacer
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Core Layout: Topology (Left) | Controls & Logs (Right)
    left, right = st.columns([7, 3], gap="medium")

    # Render Topology section
    with left:
        # Wrap topology in a styled card
        st.markdown("<div class='sci-card' style='padding: 1rem; height: 100%;'>", unsafe_allow_html=True)
        # Add topology section header
        st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'>Live Network Topology</h4>", unsafe_allow_html=True)
        
        # Default view mode
        view_mode = "3D"
        # Offer toggle if 3D is enabled
        if getattr(sim, 'enable_3d', False):
            # Render radio buttons to toggle 2D/3D
            view_mode = st.radio("Topology View", ["3D", "2D"], horizontal=True, label_visibility="collapsed")
        
        # Initialize a new Plotly figure
        fig = go.Figure()

        # Render 3D Topology
        if getattr(sim, 'enable_3d', False) and view_mode == "3D":
            import numpy as np
            from utils import get_elevation

            # ── High-Res Terrain Grid ──────────────────────────
            # Set terrain resolution
            res = 50
            # Generate X grid values
            x_range = np.linspace(0, sim.field_w, res)
            # Generate Y grid values
            y_range = np.linspace(0, sim.field_h, res)
            # Create 2D meshgrid
            x_grid, y_grid = np.meshgrid(x_range, y_range)
            # Initialize Z array
            z_grid = np.zeros_like(x_grid)
            # Calculate procedural elevation for every grid point
            for i in range(res):
                for j in range(res):
                    z_grid[i, j] = get_elevation(x_grid[i, j], y_grid[i, j], sim.field_w, sim.field_h)

            # Find maximum elevation for layout scaling
            z_max = float(np.max(z_grid))
            # Define floor height
            z_floor = -1.0

            # ── Layer 1: Solid Terrain (dark topo) ────────────
            # Define dark green colorscale
            topo_colors = [
                [0.0,  'rgb(10, 25, 15)'],
                [0.25, 'rgb(20, 55, 30)'],
                [0.5,  'rgb(35, 90, 45)'],
                [0.75, 'rgb(55, 130, 60)'],
                [1.0,  'rgb(80, 170, 80)']
            ]
            # Add shaded surface plot
            fig.add_trace(go.Surface(
                x=x_grid, y=y_grid, z=z_grid,
                colorscale=topo_colors, showscale=False, opacity=0.92,
                lighting=dict(ambient=0.35, diffuse=0.7, roughness=0.9, specular=0.15, fresnel=0.15),
                lightposition=dict(x=50, y=-50, z=200),
                hoverinfo='skip', name='Terrain'
            ))

            # ── Layer 2: Glowing Wireframe Grid ───────────────
            # Set grid line spacing
            wire_step = 5
            # Draw horizontal wireframe lines
            for i in range(0, res, wire_step):
                fig.add_trace(go.Scatter3d(
                    x=x_grid[i, :], y=y_grid[i, :], z=z_grid[i, :] + 0.15,
                    mode='lines', line=dict(color='rgba(0, 255, 140, 0.12)', width=1),
                    hoverinfo='skip', showlegend=False
                ))
            # Draw vertical wireframe lines
            for j in range(0, res, wire_step):
                fig.add_trace(go.Scatter3d(
                    x=x_grid[:, j], y=y_grid[:, j], z=z_grid[:, j] + 0.15,
                    mode='lines', line=dict(color='rgba(0, 255, 140, 0.12)', width=1),
                    hoverinfo='skip', showlegend=False
                ))

            # ── Base Station ──────────────────────────────────
            # Determine Base Station Z coordinate
            bs_z = sim.base_station[2] if len(sim.base_station) > 2 else 40.0
            # Determine Base Station X, Y coordinates
            bs_x, bs_y = sim.base_station[0], sim.base_station[1]
            # Calculate terrain height below Base Station
            bs_ground_z = get_elevation(bs_x, min(bs_y, sim.field_h), sim.field_w, sim.field_h)
            # Draw vertical pillar line from ground to BS
            fig.add_trace(go.Scatter3d(
                x=[bs_x, bs_x], y=[bs_y, bs_y], z=[bs_ground_z, bs_z],
                mode='lines', line=dict(color='rgba(59,130,246,0.5)', width=3, dash='dot'),
                hoverinfo='skip', showlegend=False
            ))
            # Draw Base Station marker
            fig.add_trace(go.Scatter3d(
                x=[bs_x], y=[bs_y], z=[bs_z],
                mode='markers+text', text=['⬡ BASE'], textposition='top center',
                textfont=dict(color='#93C5FD', size=13),
                marker=dict(size=10, color='#3B82F6', symbol='square',
                            line=dict(width=2, color='#93C5FD')),
                name='Base Station'
            ))

            # ── Event Zone ────────────────────────────────────
            # Render event anomaly indicator if active
            if getattr(sim, 'event_driven', False) and getattr(sim, 'current_event_zone', None):
                # Unpack event details
                ex, ey, er = sim.current_event_zone
                # Calculate ground elevation at event
                ez = get_elevation(ex, ey, sim.field_w, sim.field_h)
                # Create angular array for circle
                theta = np.linspace(0, 2 * np.pi, 40)
                # Generate ring X coordinates
                ring_x = ex + er * np.cos(theta)
                # Generate ring Y coordinates
                ring_y = ey + er * np.sin(theta)
                # Generate ring Z coordinates
                ring_z = np.full_like(theta, ez + 0.5)
                # Draw event boundary ring
                fig.add_trace(go.Scatter3d(
                    x=ring_x, y=ring_y, z=ring_z,
                    mode='lines', line=dict(color='rgba(239, 68, 68, 0.6)', width=3),
                    hoverinfo='skip', showlegend=False
                ))
                # Draw central event marker
                fig.add_trace(go.Scatter3d(
                    x=[ex], y=[ey], z=[ez + 3],
                    mode='markers+text', text=['⚠ EVENT'], textposition='top center',
                    textfont=dict(color='#FCA5A5', size=11),
                    marker=dict(size=7, color='#EF4444', symbol='diamond', opacity=0.9),
                    name='Event Anomaly'
                ))

            # ── Dead Nodes ────────────────────────────────────
            # Fetch dead nodes
            dead = get_dead_nodes(sim.nodes)
            if dead:
                # Plot dead nodes as red X's
                fig.add_trace(go.Scatter3d(
                    x=[n.x for n in dead], y=[n.y for n in dead], z=[n.z for n in dead],
                    mode='markers', marker=dict(size=4, color='#991B1B', symbol='x', opacity=0.6),
                    name='Dead Nodes', hoverinfo='skip'
                ))

            # ── Alive Sensor Nodes ────────────────────────────
            # Fetch alive normal nodes
            alive = [n for n in get_alive_nodes(sim.nodes) if not n.is_ch]
            if alive:
                # Calculate energy percentages for color mapping
                energies = [n.energy / n.initial_energy for n in alive]
                # Plot alive nodes
                fig.add_trace(go.Scatter3d(
                    x=[n.x for n in alive], y=[n.y for n in alive],
                    z=[n.z + 0.5 for n in alive],
                    mode='markers',
                    marker=dict(size=5, color=energies, colorscale='Turbo',
                                cmin=0, cmax=1, showscale=False,
                                line=dict(width=0.5, color='rgba(255,255,255,0.3)')),
                    name='Sensor Nodes',
                    hovertemplate='<b>Node %{customdata[0]}</b><br>Energy: %{customdata[1]:.2f}J<extra></extra>',
                    customdata=[[n.id, n.energy] for n in alive]
                ))

            # ── Cluster Heads (elevated with pillars) ─────────
            # Render cluster heads if present
            if sim.current_chs:
                # Offset to float CHs above the terrain
                ch_float_offset = 4.0
                # Draw vertical pillars for each CH
                for ch in sim.current_chs:
                    fig.add_trace(go.Scatter3d(
                        x=[ch.x, ch.x], y=[ch.y, ch.y],
                        z=[ch.z, ch.z + ch_float_offset],
                        mode='lines',
                        line=dict(color='rgba(250, 204, 21, 0.4)', width=2, dash='dot'),
                        hoverinfo='skip', showlegend=False
                    ))
                # Plot Cluster Head markers
                fig.add_trace(go.Scatter3d(
                    x=[ch.x for ch in sim.current_chs],
                    y=[ch.y for ch in sim.current_chs],
                    z=[ch.z + ch_float_offset for ch in sim.current_chs],
                    mode='markers+text',
                    text=[f'CH{ch.id}' for ch in sim.current_chs],
                    textposition='top center',
                    textfont=dict(color='#FDE68A', size=11),
                    marker=dict(size=9, color='#FACC15', symbol='diamond',
                                line=dict(width=1.5, color='#FEF08A')),
                    name='Cluster Heads',
                    hovertemplate='<b>CH %{customdata[0]}</b><br>Energy: %{customdata[1]:.3f}J<extra></extra>',
                    customdata=[[ch.id, ch.energy] for ch in sim.current_chs]
                ))

                # ── Member-to-CH Links ────────────────────────
                # Create arrays for line segments
                edge_x, edge_y, edge_z = [], [], []
                # Build line segments between members and their CH
                for n in alive:
                    local_ch = next((ch for ch in sim.current_chs if ch.id == n.cluster_id), None)
                    if local_ch:
                        edge_x.extend([n.x, local_ch.x, None])
                        edge_y.extend([n.y, local_ch.y, None])
                        edge_z.extend([n.z + 0.5, local_ch.z + ch_float_offset, None])
                        
                # Draw member links
                fig.add_trace(go.Scatter3d(
                    x=edge_x, y=edge_y, z=edge_z,
                    mode='lines', line=dict(color='rgba(148, 163, 184, 0.2)', width=1.5),
                    name='Member Links', hoverinfo='none', showlegend=False
                ))

                # ── CH-to-BS Routing Arcs ─────────────────────
                # Draw routing paths for each CH
                for ch in sim.current_chs:
                    # Check if routing to next hop or BS
                    has_hop = getattr(ch, 'next_hop', None) and ch.next_hop.is_alive
                    # Set target X
                    tx = ch.next_hop.x if has_hop else bs_x
                    # Set target Y
                    ty = ch.next_hop.y if has_hop else bs_y
                    # Set target Z
                    tz = (ch.next_hop.z + ch_float_offset) if has_hop else bs_z
                    # Source Z
                    src_z = ch.z + ch_float_offset

                    # Determine number of interpolation points for smooth arc
                    num_pts = 10
                    arc_x, arc_y, arc_z = [], [], []
                    # Compute arc points
                    for k in range(num_pts + 1):
                        # Interpolation fraction
                        t = k / num_pts
                        # Interpolated X
                        px = ch.x + t * (tx - ch.x)
                        # Interpolated Y
                        py = ch.y + t * (ty - ch.y)
                        # Interpolated Z
                        pz = src_z + t * (tz - src_z)
                        # Apply parabolic bulge
                        bulge = 12.0 * t * (1.0 - t)
                        arc_x.append(px)
                        arc_y.append(py)
                        arc_z.append(pz + bulge)
                    # Add breaks between paths
                    arc_x.append(None); arc_y.append(None); arc_z.append(None)

                    # Use orange for multi-hop, blue for direct to BS
                    line_color = 'rgba(251, 146, 60, 0.85)' if has_hop else 'rgba(96, 165, 250, 0.85)'
                    # Draw routing arcs
                    fig.add_trace(go.Scatter3d(
                        x=arc_x, y=arc_y, z=arc_z,
                        mode='lines', line=dict(color=line_color, width=5),
                        hoverinfo='none', showlegend=False
                    ))

            # ── Scene Layout (Dark Holographic Theme) ─────────
            # Update 3D specific layout parameters
            fig.update_layout(
                scene=dict(
                    xaxis=dict(visible=False, range=[-5, sim.field_w + 5]),
                    yaxis=dict(visible=False, range=[-5, sim.field_h * 1.2]),
                    zaxis=dict(visible=False, range=[z_floor, max(55, bs_z + 15)]),
                    aspectratio=dict(x=1, y=1.15, z=0.35),
                    camera=dict(
                        eye=dict(x=1.5, y=-1.8, z=1.0),
                        up=dict(x=0, y=0, z=1)
                    ),
                    bgcolor='rgb(8, 12, 18)'
                ),
                height=550,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False,
                paper_bgcolor='rgb(8, 12, 18)'
            )
        # Render 2D Topology
        else:
            # Draw simulation field boundary
            fig.add_shape(type="rect", x0=0, y0=0, x1=sim.field_w, y1=sim.field_h, line=dict(color="rgba(46, 125, 50, 0.2)", width=1, dash="dot"), fillcolor="rgba(248, 250, 245, 0.5)")
            # Plot Base Station
            fig.add_trace(go.Scatter(x=[sim.base_station[0]], y=[sim.base_station[1]], mode="markers+text", text=["BS"], textposition="top center", textfont=dict(color="#1F2937", size=10, family="Inter"), marker=dict(size=14, color="#2563EB", symbol="square", line=dict(width=2, color="#fff")), name="Base Station", hovertemplate="Base Station<extra></extra>"))
            # Render event anomaly if active
            if getattr(sim, 'event_driven', False) and getattr(sim, 'current_event_zone', None):
                ex, ey, er = sim.current_event_zone
                # Draw event boundary circle
                fig.add_shape(type="circle", xref="x", yref="y", x0=ex-er, y0=ey-er, x1=ex+er, y1=ey+er, fillcolor="rgba(239, 68, 68, 0.1)", line_color="rgba(239, 68, 68, 0.5)", line_dash="dash")
                # Plot event center marker
                fig.add_trace(go.Scatter(x=[ex], y=[ey], mode="markers+text", text=["Event"], textposition="top center", textfont=dict(color="#DC2626", size=10, family="Inter"), marker=dict(size=8, color="#DC2626", symbol="star"), name="Event Anomaly", hoverinfo="skip"))
            # Plot Dead Nodes
            dead = get_dead_nodes(sim.nodes)
            if dead:
                fig.add_trace(go.Scatter(x=[n.x for n in dead], y=[n.y for n in dead], mode="markers", marker=dict(size=6, color="#DC2626", symbol="x"), name="Dead Nodes", hovertemplate="<b>Node %{customdata[0]}</b><br>Status: Dead<br>Energy: 0.00J<extra></extra>", customdata=[[n.id] for n in dead]))
            # Plot Alive Nodes
            alive = [n for n in get_alive_nodes(sim.nodes) if not n.is_ch]
            if alive:
                c_ids = [n.cluster_id for n in alive]
                fig.add_trace(go.Scatter(x=[n.x for n in alive], y=[n.y for n in alive], mode="markers", marker=dict(size=9, color=c_ids, colorscale="Rainbow", showscale=False, line=dict(width=1, color="#111827")), name="Sensor Nodes", hovertemplate="<b>Node %{customdata[0]}</b><br>Role: Member<br>Cluster ID: %{customdata[3]}<br>Energy: %{customdata[1]:.3f}J<br>Neighbors: %{customdata[2]}<extra></extra>", customdata=[[n.id, n.energy, n.neighbors, n.cluster_id] for n in alive]))
            # Plot Cluster Heads and Routing
            if sim.current_chs:
                ch_ids = [ch.cluster_id for ch in sim.current_chs]
                # Plot Cluster Heads
                fig.add_trace(go.Scatter(x=[ch.x for ch in sim.current_chs], y=[ch.y for ch in sim.current_chs], mode="markers+text", text=[f"CH {ch.id}" for ch in sim.current_chs], textposition="top right", textfont=dict(color="#111827", size=11, family="Inter", weight="bold"), marker=dict(size=14, color=ch_ids, colorscale="Rainbow", symbol="diamond", line=dict(width=2, color="#111827")), name="Cluster Heads", hovertemplate="<b>Node %{customdata[0]}</b><br>Role: Cluster Head<br>Energy: %{customdata[1]:.3f}J<br>Neighbors: %{customdata[2]}<extra></extra>", customdata=[[ch.id, ch.energy, ch.neighbors] for ch in sim.current_chs]))
                # Draw lines from members to their CH
                for n in alive:
                    local_ch = next((ch for ch in sim.current_chs if ch.id == n.cluster_id), None)
                    if local_ch:
                        fig.add_annotation(x=local_ch.x, y=local_ch.y, ax=n.x, ay=n.y, xref='x', yref='y', axref='x', ayref='y', showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=1.5, arrowcolor="rgba(75, 85, 99, 0.6)")
                # Draw routing paths from CHs to BS
                for ch in sim.current_chs:
                    target_x = ch.next_hop.x if getattr(ch, 'next_hop', None) and ch.next_hop.is_alive else sim.base_station[0]
                    target_y = ch.next_hop.y if getattr(ch, 'next_hop', None) and ch.next_hop.is_alive else sim.base_station[1]
                    arrow_color = "rgba(217, 119, 6, 0.6)" if getattr(ch, 'next_hop', None) and ch.next_hop.is_alive else "rgba(37, 99, 235, 0.4)"
                    arrow_head = 2 if getattr(ch, 'next_hop', None) and ch.next_hop.is_alive else 3
                    fig.add_annotation(x=target_x, y=target_y, ax=ch.x, ay=ch.y, xref='x', yref='y', axref='x', ayref='y', showarrow=True, arrowhead=arrow_head, arrowsize=1, arrowwidth=1.5, arrowcolor=arrow_color)
            # Apply 2D layout parameters
            fig.update_layout(
                xaxis=dict(range=[-5, sim.field_w + 15], visible=False, fixedrange=True),
                yaxis=dict(range=[-5, sim.field_h + 15], scaleanchor="x", visible=False, fixedrange=True),
                height=500,
                margin=dict(l=0, r=0, t=10, b=0)
            )
        # Check if 3D is active for configuration
        is_3d_active = getattr(sim, 'enable_3d', False) and view_mode == "3D"
        # Apply light theme if using 2D
        if not is_3d_active:
            fig = apply_light_theme(fig)
        # Display the Plotly chart in Streamlit
        st.plotly_chart(fig, use_container_width=True, theme=None, config={'displayModeBar': is_3d_active, 'scrollZoom': is_3d_active})
        # Close topology card container
        st.markdown("</div>", unsafe_allow_html=True)

    # Render Controls & Logs section
    with right:
        # Wrap controls in styled card
        st.markdown("<div class='sci-card' style='padding: 1rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        # Add controls section header
        st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 1rem;'>Controls</h4>", unsafe_allow_html=True)
        
        # Split controls into two columns
        c1, c2 = st.columns(2)
        # Render single step button
        step_clicked = c1.button("Step (1)", use_container_width=True)
        # Render fast forward button
        ff_clicked = c2.button("Fast (10)", use_container_width=True)
        
        # Add spacer
        st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
        
        # Render auto-run checkbox linked to session state
        st.checkbox("Auto-Run", key="auto_run")
        
        # Execute single round if clicked
        if step_clicked:
            sim.run_round()
            st.rerun()
        # Execute 10 rounds if clicked
        if ff_clicked:
            sim.run_n_rounds(10)
            st.rerun()
        # Close controls card container
        st.markdown("</div>", unsafe_allow_html=True)

        # Wrap logs in styled card
        st.markdown("<div class='sci-card' style='padding: 1rem;'>", unsafe_allow_html=True)
        # Add logs section header
        st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'>Simulation Log</h4>", unsafe_allow_html=True)
        # Check if logs exist
        if sim.logs:
            # Accumulate HTML string for logs
            log_entries = ""
            # Iterate through the last 20 logs
            for log in sim.logs[-20:]:
                # Add each log entry formatted in HTML
                log_entries += f'<div style="border-bottom: 1px solid var(--border-color); padding: 2px 0; color: #111827;">{log}</div>'
            # Render the log container
            st.markdown(f'<div class="log-panel-container">{log_entries}</div>', unsafe_allow_html=True)
        else:
            # Render placeholder if no logs
            st.markdown('<div class="log-panel-container" style="color: #6B7280;">Awaiting simulation start...</div>', unsafe_allow_html=True)
        # Close logs card container
        st.markdown("</div>", unsafe_allow_html=True)

    # Add spacer before analytics
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Bottom Analytics Section
    # Wrap analytics in styled card
    st.markdown("<div class='sci-card' style='padding: 1rem;'>", unsafe_allow_html=True)
    # Add analytics section header
    st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'>Performance Analytics</h4>", unsafe_allow_html=True)
    
    # Check if there is enough data to plot
    if len(sim.energy_history) > 1:
        # Create a dataframe of historical metrics
        df = pd.DataFrame({"Round": range(len(sim.energy_history)), "Energy": sim.energy_history, "Alive": sim.alive_history, "CHs": sim.ch_count_history})
        # Split into 3 columns for charts
        ac1, ac2, ac3 = st.columns(3)
        
        # Render Network Lifetime chart
        with ac1:
            # Initialize Network Lifetime Figure
            fig1 = go.Figure()
            # Plot alive node counts over time
            fig1.add_trace(go.Scatter(x=df["Round"], y=df["Alive"], name="Alive Nodes", line=dict(color="#16A34A", width=2)))
            # Configure layout
            fig1.update_layout(title="Network Lifetime", xaxis_title="Round", yaxis_title="Nodes", height=200, margin=dict(l=0, r=0, t=30, b=0))
            # Apply light theme styling
            fig1 = apply_light_theme(fig1)
            # Render chart
            st.plotly_chart(fig1, use_container_width=True, theme=None, config={'displayModeBar': False})
            
        # Render Energy Depletion chart
        with ac2:
            # Initialize Energy Depletion Figure
            fig2 = go.Figure()
            # Plot total energy over time
            fig2.add_trace(go.Scatter(x=df["Round"], y=df["Energy"], name="Total Energy", fill="tozeroy", line=dict(color="#2E7D32", width=2), fillcolor="rgba(46, 125, 50, 0.1)"))
            # Configure layout
            fig2.update_layout(title="Energy Depletion", xaxis_title="Round", yaxis_title="Joules", height=200, margin=dict(l=0, r=0, t=30, b=0))
            # Apply light theme styling
            fig2 = apply_light_theme(fig2)
            # Render chart
            st.plotly_chart(fig2, use_container_width=True, theme=None, config={'displayModeBar': False})
            
        # Render Data Throughput chart
        with ac3:
            # Initialize Data Throughput Figure
            fig3 = go.Figure()
            # Plot cumulative data packets sent over time
            fig3.add_trace(go.Scatter(x=df["Round"], y=sim.packets_history, name="Packets", fill="tozeroy", line=dict(color="#2563EB", width=2), fillcolor="rgba(37, 99, 235, 0.1)"))
            # Configure layout
            fig3.update_layout(title="Data Throughput", xaxis_title="Round", yaxis_title="Packets", height=200, margin=dict(l=0, r=0, t=30, b=0))
            # Apply light theme styling
            fig3 = apply_light_theme(fig3)
            # Render chart
            st.plotly_chart(fig3, use_container_width=True, theme=None, config={'displayModeBar': False})
    else:
        # Placeholder text if no data
        st.markdown("<p style='color: var(--text-secondary); font-size: 0.9rem; margin-top: 1rem;'>Run simulation to generate analytics data.</p>", unsafe_allow_html=True)
    # Close analytics card container
    st.markdown("</div>", unsafe_allow_html=True)

    # Process auto-run logic
    if st.session_state.auto_run and sim.is_running:
        # Run one round automatically
        sim.run_round()
        # Pause slightly to throttle loop
        time.sleep(1.0)
        # Rerun Streamlit page
        st.rerun()
