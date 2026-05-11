import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from simulation import WSNSimulation
from utils import get_alive_nodes, get_dead_nodes
import time

# ─── Page Config ───
st.set_page_config(
    page_title="AgroTech Vision | WSN Simulation",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Session State Routing ───
if "page" not in st.session_state: st.session_state.page = "landing"
if "sim" not in st.session_state: st.session_state.sim = None
if "config" not in st.session_state: st.session_state.config = {}

def navigate_to(page_name): st.session_state.page = page_name

# ─── Custom CSS Injection ───
no_scroll_css = ""
if st.session_state.page in ["landing", "setup", "loading"]:
    no_scroll_css = """
    html, body, .stApp {
        overflow: hidden !important;
    }
    ::-webkit-scrollbar { display: none; }
    """

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@500;700&display=swap');

    /* Hide Streamlit Chrome */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    {no_scroll_css}

    /* Global Typography & Background */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Space Grotesk', sans-serif !important;
        color: #f8fafc !important;
        letter-spacing: -0.5px;
    }}
    .stApp {{ 
        background: radial-gradient(circle at top left, #0f172a, #064e3b 80%, #022c22); 
    }}
    .block-container {{ 
        padding-top: 1rem !important; 
        padding-bottom: 1rem !important;
        max-width: 1400px;
    }}
    
    /* Glassmorphism Cards */
    .glass-card {{
        background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px; 
        padding: 2rem; 
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    /* Metric Cards */
    .metric-card {{
        background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; 
        padding: 1.5rem 1rem; 
        text-align: center;
        backdrop-filter: blur(16px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .metric-card::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #10b981, #3b82f6);
        opacity: 0; transition: opacity 0.3s;
    }}
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px -8px rgba(0,0,0,0.5);
        border-color: rgba(255,255,255,0.2);
    }}
    .metric-card:hover::before {{ opacity: 1; }}
    
    .metric-value {{ font-size: 2.5rem; font-weight: 700; color: #34d399; font-family: 'Space Grotesk', sans-serif; line-height: 1.1; margin-bottom: 0.2rem; }}
    .metric-label {{ font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }}
    
    /* Alert Pulses */
    @keyframes pulse-critical {{
        0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); border-color: rgba(239, 68, 68, 0.8); }}
        70% {{ box-shadow: 0 0 0 15px rgba(239, 68, 68, 0); border-color: rgba(239, 68, 68, 0.2); }}
        100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); border-color: rgba(239, 68, 68, 0.8); }}
    }}
    .alert-pulse {{
        animation: pulse-critical 2s infinite !important;
        border: 1px solid rgba(239, 68, 68, 0.8) !important;
    }}
    .alert-pulse .metric-value {{ color: #ef4444 !important; }}

    /* Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, #059669, #10b981) !important;
        color: #ffffff !important; 
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important; 
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        transition: all 0.2s ease !important;
        height: 3.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.4) !important;
        background: linear-gradient(135deg, #047857, #059669) !important;
    }}
    .stButton>button:active {{ transform: translateY(0); }}
    
    /* Secondary Buttons */
    .btn-secondary>div>button {{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }}
    .btn-secondary>div>button:hover {{ background: rgba(255,255,255,0.1) !important; }}
    
    /* Headers & Dividers */
    hr {{ border-color: rgba(255,255,255,0.1) !important; margin: 2rem 0; }}
    .section-title {{ font-size: 1.25rem; color: #e2e8f0; margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; }}

    /* Loader */
    .loader-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; }}
    .spinner {{
        width: 60px; height: 60px;
        border: 4px solid rgba(16, 185, 129, 0.2);
        border-radius: 50%;
        border-top-color: #10b981;
        animation: spin 1s ease-in-out infinite;
        margin-bottom: 2rem;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
</style>
""", unsafe_allow_html=True)

# ─── Page 1: Landing ───
if st.session_state.page == "landing":
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='glass-card' style='text-align: center; padding: 4rem 3rem;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>🌍</div>
            <h1 style='font-size: 3.5rem; margin-bottom: 0.5rem; background: -webkit-linear-gradient(#fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>AgroTech Vision</h1>
            <p style='font-size: 1.2rem; color: #10b981 !important; font-weight: 500; letter-spacing: 1px; text-transform: uppercase;'>WSN Simulation Platform</p>
            <p style='color: #94a3b8 !important; line-height: 1.6; margin: 2rem 0;'>
                A production-grade environment for simulating energy-efficient Wireless Sensor Networks in smart agriculture. Monitor dynamic cluster head selections, routing protocols, and edge computing topologies in real-time.
            </p>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Initialize Environment Setup", use_container_width=True):
            navigate_to("setup")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ─── Page 2: Configuration Setup ───
elif st.session_state.page == "setup":
    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Simulation Parameters</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8 !important; margin-bottom:3rem;'>Define network topology and scoring algorithms before deployment.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.markdown("<div class='section-title'>🌐 Topology</div>", unsafe_allow_html=True)
        num_nodes = st.number_input("Total Sensor Nodes", min_value=10, max_value=100, value=40, step=5, help="Number of nodes randomly deployed in the field.")
        comm_range = st.number_input("Communication Range (m)", min_value=15, max_value=80, value=35, step=5, help="Maximum transmission distance between nodes.")
    with col2:
        st.markdown("<div class='section-title'>⚡ Energy constraints</div>", unsafe_allow_html=True)
        energy_threshold = st.number_input("CH Energy Threshold (J)", min_value=0.1, max_value=1.0, value=0.3, step=0.05, help="Minimum energy required to become a Cluster Head.")
    with col3:
        st.markdown("<div class='section-title'>⚖️ CH Selection Algorithm</div>", unsafe_allow_html=True)
        w1 = st.number_input("Energy Weight (w1)", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
        w2 = st.number_input("Proximity Weight (w2)", min_value=0.0, max_value=1.0, value=0.3, step=0.1)
        w3 = st.number_input("Neighbor Weight (w3)", min_value=0.0, max_value=1.0, value=0.2, step=0.1)
        
    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns([1, 2, 1])
    with cc2:
        if st.button("🚀 Deploy Network", use_container_width=True):
            st.session_state.config = {
                "num_nodes": num_nodes, "energy_threshold": energy_threshold,
                "comm_range": comm_range, "w1": w1, "w2": w2, "w3": w3
            }
            navigate_to("loading")
            st.rerun()

# ─── Page 3: Loading ───
elif st.session_state.page == "loading":
    st.markdown("""
        <div class="loader-container">
            <div class="spinner"></div>
            <h2 style="color: #fff; margin-bottom: 0.5rem;">Provisioning Network</h2>
            <p style="color: #10b981;">Establishing mesh topology & assigning initial energy...</p>
        </div>
    """, unsafe_allow_html=True)
    
    cfg = st.session_state.config
    sim = WSNSimulation(
        num_nodes=cfg["num_nodes"], energy_threshold=cfg["energy_threshold"],
        comm_range=cfg["comm_range"], w1=cfg["w1"], w2=cfg["w2"], w3=cfg["w3"]
    )
    sim.initialize()
    st.session_state.sim = sim
    
    time.sleep(1.5)
    navigate_to("dashboard")
    st.rerun()

# ─── Page 4: Dashboard ───
elif st.session_state.page == "dashboard":
    sim = st.session_state.sim
    stats = sim.get_stats()
    
    # Header area
    head1, head2 = st.columns([4, 1])
    with head1:
        st.markdown("<h2 style='margin-top:0;'>📡 Network Operations Center</h2>", unsafe_allow_html=True)
    with head2:
        st.markdown("<div class='btn-secondary'>", unsafe_allow_html=True)
        if st.button("⚙️ Reconfigure", use_container_width=True):
            navigate_to("setup")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── Metrics Row ───
    m1, m2, m3, m4, m5 = st.columns(5)
    def metric_card(col, label, value, color="#34d399", extra_class=""):
        col.markdown(f"""
        <div class="metric-card {extra_class}">
            <div class="metric-value" style="color:{color}">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    dead_alert = "alert-pulse" if stats["dead_nodes"] >= sim.num_nodes * 0.25 else ""

    metric_card(m1, "Simulation Round", stats["round"], "#f8fafc")
    metric_card(m2, "Alive Nodes", stats["alive_nodes"], "#34d399")
    metric_card(m3, "Dead Nodes", stats["dead_nodes"], "#94a3b8" if not dead_alert else "#ef4444", dead_alert)
    metric_card(m4, "Active Clusters", f"{stats.get('num_chs', 0)}", "#fbbf24")
    metric_card(m5, "Data Packets", f"{stats.get('total_data_sent', 0)}", "#a78bfa")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ─── Main Visualizations & Controls ───
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown("<div class='section-title'>Live Topology Map</div>", unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(color="rgba(100,100,200,0.2)", width=1, dash="dot"), fillcolor="rgba(0,0,0,0.2)")

        fig.add_trace(go.Scatter(x=[sim.base_station[0]], y=[sim.base_station[1]], mode="markers+text", text=["Base Station"], textposition="top center", textfont=dict(color="#f8fafc", size=11, family="Inter"), marker=dict(size=18, color="#f97316", symbol="square", line=dict(width=2, color="#fff")), name="Base Station", hovertemplate="Base Station<extra></extra>"))

        dead = get_dead_nodes(sim.nodes)
        if dead:
            fig.add_trace(go.Scatter(x=[n.x for n in dead], y=[n.y for n in dead], mode="markers", marker=dict(size=8, color="#475569", symbol="x"), name="Dead Nodes", hovertemplate="<b>Node %{customdata[0]}</b><br>Status: Dead<br>Energy: 0.00J<extra></extra>", customdata=[[n.id] for n in dead]))

        alive = [n for n in get_alive_nodes(sim.nodes) if not n.is_ch]
        if alive:
            c_ids = [n.cluster_id for n in alive]
            fig.add_trace(go.Scatter(x=[n.x for n in alive], y=[n.y for n in alive], mode="markers", marker=dict(size=10, color=c_ids, colorscale="Viridis", showscale=False, line=dict(width=1, color="rgba(255,255,255,0.3)")), name="Sensor Nodes", hovertemplate="<b>Node %{customdata[0]}</b><br>Role: Member<br>Cluster ID: %{customdata[3]}<br>Energy: %{customdata[1]:.3f}J<br>Neighbors: %{customdata[2]}<extra></extra>", customdata=[[n.id, n.energy, n.neighbors, n.cluster_id] for n in alive]))

        if sim.current_chs:
            # Draw CHs
            ch_ids = [ch.cluster_id for ch in sim.current_chs]
            fig.add_trace(go.Scatter(x=[ch.x for ch in sim.current_chs], y=[ch.y for ch in sim.current_chs], mode="markers+text", text=[f"CH {ch.id}" for ch in sim.current_chs], textposition="top right", textfont=dict(color="#f8fafc", size=11, family="Inter", weight="bold"), marker=dict(size=16, color=ch_ids, colorscale="Viridis", symbol="diamond", line=dict(width=2, color="#fff")), name="Cluster Heads", hovertemplate="<b>Node %{customdata[0]}</b><br>Role: Cluster Head<br>Energy: %{customdata[1]:.3f}J<br>Neighbors: %{customdata[2]}<extra></extra>", customdata=[[ch.id, ch.energy, ch.neighbors] for ch in sim.current_chs]))
            
            # Draw Connections: Member -> Local CH
            for n in alive:
                local_ch = next((ch for ch in sim.current_chs if ch.id == n.cluster_id), None)
                if local_ch:
                    fig.add_trace(go.Scatter(x=[n.x, local_ch.x], y=[n.y, local_ch.y], mode="lines", line=dict(color="rgba(255,255,255,0.1)", width=1), showlegend=False, hoverinfo="skip"))
            
            # Draw Connections: CH -> Base Station
            for ch in sim.current_chs:
                fig.add_trace(go.Scatter(x=[ch.x, sim.base_station[0]], y=[ch.y, sim.base_station[1]], mode="lines", line=dict(color="rgba(249,115,22,0.4)", width=2, dash="dash"), showlegend=False, hoverinfo="skip"))

        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", family="Inter"),
            xaxis=dict(range=[-5, 115], gridcolor="rgba(255,255,255,0.05)", zeroline=False, visible=False, fixedrange=True),
            yaxis=dict(range=[-5, 125], gridcolor="rgba(255,255,255,0.05)", zeroline=False, scaleanchor="x", visible=False, fixedrange=True),
            height=450, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)", font=dict(size=10), itemclick=False, itemdoubleclick=False),
            hoverlabel=dict(bgcolor="rgba(15, 23, 42, 0.95)", font_size=13, font_family="Inter", bordercolor="rgba(255,255,255,0.1)")
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with right:
        st.markdown("<div class='section-title'>Simulation Controls</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        if c1.button("▶️ Step Forward (1)", use_container_width=True): sim.run_round(); st.rerun()
        if c2.button("⏩ Fast Forward (10)", use_container_width=True): sim.run_n_rounds(10); st.rerun()
        
        st.markdown("<div class='section-title' style='margin-top:2.5rem;'>Network Trends</div>", unsafe_allow_html=True)
        
        if len(sim.energy_history) > 1:
            df = pd.DataFrame({"Round": range(len(sim.energy_history)), "Energy": sim.energy_history, "Alive": sim.alive_history, "CHs": sim.ch_count_history})
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=df["Round"], y=df["Energy"], name="Energy (J)", mode="lines", fill="tozeroy", line=dict(color="#10b981", width=2), fillcolor="rgba(16,185,129,0.1)", yaxis="y1"))
            fig_trend.add_trace(go.Scatter(x=df["Round"], y=df["Alive"], name="Alive Nodes", mode="lines", line=dict(color="#3b82f6", width=2, dash="dot"), yaxis="y2"))
            fig_trend.add_trace(go.Scatter(x=df["Round"], y=df["CHs"], name="Active CHs", mode="lines", line=dict(color="#fbbf24", width=2), yaxis="y2"))
            
            fig_trend.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=10),
                height=250, margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(title="Energy (J)", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                yaxis2=dict(title="Nodes", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        else:
            st.markdown("<p style='color:#64748b; font-size:0.9rem; text-align:center; padding:2rem 0;'>Run simulation to generate analytics data.</p>", unsafe_allow_html=True)

    # ─── Node Analytics Detail Section ───
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Node Introspection</div>", unsafe_allow_html=True)
    
    sel_col, _ = st.columns([1, 2])
    with sel_col:
        node_opts = [f"Node {n.id}" for n in sim.nodes]
        selected = st.selectbox("Select Node for Detailed Telemetry", node_opts, label_visibility="collapsed")
    
    if selected:
        n = sim.nodes[int(selected.split(" ")[1])]
        nc1, nc2, nc3, nc4 = st.columns(4)
        
        status_color = "#10b981" if n.is_alive else "#ef4444"
        role = "Cluster Head" if n.is_ch else ("Dead" if not n.is_alive else "Sensor Node")
        
        nc1.markdown(f"<div class='glass-card' style='padding: 1.5rem;'><strong>Identity</strong><br><span style='color:#f8fafc; font-size:1.2rem;'>Node #{n.id}</span></div>", unsafe_allow_html=True)
        nc2.markdown(f"<div class='glass-card' style='padding: 1.5rem;'><strong>Current Role</strong><br><span style='color:{status_color}; font-size:1.2rem; font-weight:600;'>{role}</span></div>", unsafe_allow_html=True)
        nc3.markdown(f"<div class='glass-card' style='padding: 1.5rem;'><strong>Residual Energy</strong><br><span style='color:#fbbf24; font-size:1.2rem;'>{n.energy:.4f} J</span></div>", unsafe_allow_html=True)
        nc4.markdown(f"<div class='glass-card' style='padding: 1.5rem;'><strong>Topology Data</strong><br><span style='color:#cbd5e1;'>{n.neighbors} Neighbors • {n.data_sent} Pkts</span></div>", unsafe_allow_html=True)

