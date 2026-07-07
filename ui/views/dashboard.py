import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time
from ui.components import render_navbar, render_metric_card, apply_light_theme
from utils import get_alive_nodes, get_dead_nodes

def render():
    sim = st.session_state.sim
    if sim is None:
        st.session_state.page = "setup"
        st.rerun()
    
    stats = sim.get_stats()

    # Nav
    render_navbar("dashboard")

    # KPIs Row
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    initial_total_energy = sim.energy_history[0] if sim.energy_history else 1
    energy_pct = (stats["total_energy"] / initial_total_energy * 100) if initial_total_energy > 0 else 0
    
    with m1:
        render_metric_card(st, "Alive Nodes", f"{stats['alive_nodes']}/{sim.num_nodes}", "#2E7D32")
    with m2:
        render_metric_card(st, "Dead Nodes", f"{sim.num_nodes - stats['alive_nodes']}", "#DC2626")
    with m3:
        render_metric_card(st, "Active Clusters", f"{stats.get('num_chs', 0)}", "#2563EB")
    with m4:
        render_metric_card(st, "Residual Energy", f"{energy_pct:.1f}%", "#F59E0B")
    with m5:
        render_metric_card(st, "Current Round", f"{stats['round']}", "#6B7280")
    with m6:
        render_metric_card(st, "Packets Sent", f"{stats.get('total_data_sent', 0)}", "#16A34A")

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Core Layout: Topology (Left) | Controls & Logs (Right)
    left, right = st.columns([7, 3], gap="medium")

    with left:
        st.markdown("<div class='sci-card' style='padding: 1rem; height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0;'>Live Network Topology</h4>", unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_shape(type="rect", x0=0, y0=0, x1=sim.field_w, y1=sim.field_h, line=dict(color="rgba(46, 125, 50, 0.2)", width=1, dash="dot"), fillcolor="rgba(248, 250, 245, 0.5)")

        fig.add_trace(go.Scatter(x=[sim.base_station[0]], y=[sim.base_station[1]], mode="markers+text", text=["BS"], textposition="top center", textfont=dict(color="#1F2937", size=10, family="Inter"), marker=dict(size=14, color="#2563EB", symbol="square", line=dict(width=2, color="#fff")), name="Base Station", hovertemplate="Base Station<extra></extra>"))

        dead = get_dead_nodes(sim.nodes)
        if dead:
            fig.add_trace(go.Scatter(x=[n.x for n in dead], y=[n.y for n in dead], mode="markers", marker=dict(size=6, color="#DC2626", symbol="x"), name="Dead Nodes", hovertemplate="<b>Node %{customdata[0]}</b><br>Status: Dead<br>Energy: 0.00J<extra></extra>", customdata=[[n.id] for n in dead]))

        alive = [n for n in get_alive_nodes(sim.nodes) if not n.is_ch]
        if alive:
            c_ids = [n.cluster_id for n in alive]
            fig.add_trace(go.Scatter(x=[n.x for n in alive], y=[n.y for n in alive], mode="markers", marker=dict(size=9, color=c_ids, colorscale="Rainbow", showscale=False, line=dict(width=1, color="#111827")), name="Sensor Nodes", hovertemplate="<b>Node %{customdata[0]}</b><br>Role: Member<br>Cluster ID: %{customdata[3]}<br>Energy: %{customdata[1]:.3f}J<br>Neighbors: %{customdata[2]}<extra></extra>", customdata=[[n.id, n.energy, n.neighbors, n.cluster_id] for n in alive]))

        if sim.current_chs:
            ch_ids = [ch.cluster_id for ch in sim.current_chs]
            fig.add_trace(go.Scatter(x=[ch.x for ch in sim.current_chs], y=[ch.y for ch in sim.current_chs], mode="markers+text", text=[f"CH {ch.id}" for ch in sim.current_chs], textposition="top right", textfont=dict(color="#111827", size=11, family="Inter", weight="bold"), marker=dict(size=14, color=ch_ids, colorscale="Rainbow", symbol="diamond", line=dict(width=2, color="#111827")), name="Cluster Heads", hovertemplate="<b>Node %{customdata[0]}</b><br>Role: Cluster Head<br>Energy: %{customdata[1]:.3f}J<br>Neighbors: %{customdata[2]}<extra></extra>", customdata=[[ch.id, ch.energy, ch.neighbors] for ch in sim.current_chs]))
            
            for n in alive:
                local_ch = next((ch for ch in sim.current_chs if ch.id == n.cluster_id), None)
                if local_ch:
                    fig.add_annotation(x=local_ch.x, y=local_ch.y, ax=n.x, ay=n.y, xref='x', yref='y', axref='x', ayref='y', showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=1.5, arrowcolor="rgba(75, 85, 99, 0.6)")
            
            for ch in sim.current_chs:
                fig.add_annotation(x=sim.base_station[0], y=sim.base_station[1], ax=ch.x, ay=ch.y, xref='x', yref='y', axref='x', ayref='y', showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=1.5, arrowcolor="rgba(37, 99, 235, 0.4)")

        fig.update_layout(
            xaxis=dict(range=[-5, sim.field_w + 15], visible=False, fixedrange=True),
            yaxis=dict(range=[-5, sim.field_h + 15], scaleanchor="x", visible=False, fixedrange=True),
            height=500,
            margin=dict(l=0, r=0, t=10, b=0)
        )
        fig = apply_light_theme(fig)
        st.plotly_chart(fig, use_container_width=True, theme=None, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='sci-card' style='padding: 1rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 1rem;'>Controls</h4>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        step_clicked = c1.button("Step (1)", use_container_width=True)
        ff_clicked = c2.button("Fast (10)", use_container_width=True)
        
        st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
        
        st.checkbox("Auto-Run", key="auto_run")
        
        if step_clicked:
            sim.run_round()
            st.rerun()
        if ff_clicked:
            sim.run_n_rounds(10)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='sci-card' style='padding: 1rem;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'>Simulation Log</h4>", unsafe_allow_html=True)
        if sim.logs:
            log_entries = ""
            for log in sim.logs[-20:]:
                log_entries += f'<div style="border-bottom: 1px solid var(--border-color); padding: 2px 0; color: #111827;">{log}</div>'
            st.markdown(f'<div class="log-panel-container">{log_entries}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="log-panel-container" style="color: #6B7280;">Awaiting simulation start...</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Bottom Analytics Section
    st.markdown("<div class='sci-card' style='padding: 1rem;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size:1rem; color:var(--primary-green) !important; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'>Performance Analytics</h4>", unsafe_allow_html=True)
    
    if len(sim.energy_history) > 1:
        df = pd.DataFrame({"Round": range(len(sim.energy_history)), "Energy": sim.energy_history, "Alive": sim.alive_history, "CHs": sim.ch_count_history})
        ac1, ac2, ac3 = st.columns(3)
        
        with ac1:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=df["Round"], y=df["Alive"], name="Alive Nodes", line=dict(color="#16A34A", width=2)))
            fig1.update_layout(title="Network Lifetime", xaxis_title="Round", yaxis_title="Nodes", height=200, margin=dict(l=0, r=0, t=30, b=0))
            fig1 = apply_light_theme(fig1)
            st.plotly_chart(fig1, use_container_width=True, theme=None, config={'displayModeBar': False})
            
        with ac2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df["Round"], y=df["Energy"], name="Total Energy", fill="tozeroy", line=dict(color="#2E7D32", width=2), fillcolor="rgba(46, 125, 50, 0.1)"))
            fig2.update_layout(title="Energy Depletion", xaxis_title="Round", yaxis_title="Joules", height=200, margin=dict(l=0, r=0, t=30, b=0))
            fig2 = apply_light_theme(fig2)
            st.plotly_chart(fig2, use_container_width=True, theme=None, config={'displayModeBar': False})
            
        with ac3:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=df["Round"], y=sim.packets_history, name="Packets", fill="tozeroy", line=dict(color="#2563EB", width=2), fillcolor="rgba(37, 99, 235, 0.1)"))
            fig3.update_layout(title="Data Throughput", xaxis_title="Round", yaxis_title="Packets", height=200, margin=dict(l=0, r=0, t=30, b=0))
            fig3 = apply_light_theme(fig3)
            st.plotly_chart(fig3, use_container_width=True, theme=None, config={'displayModeBar': False})
    else:
        st.markdown("<p style='color: var(--text-secondary); font-size: 0.9rem; margin-top: 1rem;'>Run simulation to generate analytics data.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.auto_run and sim.is_running:
        sim.run_round()
        time.sleep(1.0)
        st.rerun()
