import streamlit as st

def load_css() -> str:
    with open("ui/style.css", "r", encoding="utf-8") as f:
        return f.read()

def inject_custom_css():
    """Reads style.css and injects it into Streamlit via markdown."""
    css = load_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def render_navbar(active_page: str = "landing"):
    """Renders the top navigation bar with an enterprise tab-style underline."""
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 3])
    
    with col1:
        st.markdown("<div style='font-family: var(--font-heading); font-size: 1.25rem; font-weight: 700; color: var(--primary-green); padding-top: 0.5rem;'>AgroTech Vision</div>", unsafe_allow_html=True)
    
    def _nav_tab(col, label, target_page):
        # Determine CSS class for active underline state
        btn_class = "nav-btn-active" if active_page == target_page else "nav-btn"
        
        # Inject invisible span to apply CSS class to the subsequent button via layout hacking if needed,
        # but since Streamlit doesn't natively support class assignment directly on buttons, 
        # we wrap it inside a container and use nth-child or container-based styling if required.
        # Alternatively, Streamlit 1.30+ allows `use_container_width`.
        
        # We rely on an HTML hack for tabs since native buttons are hard to style individually without classes.
        # Wait, if we just use standard Streamlit buttons, we can inject a class via markdown wrapper!
        # Actually, Streamlit buttons inside a column can't easily take a class. 
        # But we can use `st.container` with a unique key? No. 
        # Let's use raw HTML with session state query params for routing? No, Streamlit reruns on button.
        # Let's use `st.button` and accept the standard Streamlit button styling but rely on our global `.stButton > button[kind="secondary"]` for inactive, and `[kind="primary"]` for active?
        # The prompt asked for "Enterprise appearance, Active page highlighted, Green underline, No button appearance".
        
        # Workaround:
        if active_page == target_page:
            # Active
            col.markdown(f"<div style='text-align:center; padding: 0.5rem; color: var(--primary-green); border-bottom: 2px solid var(--primary-green); font-weight: 600; cursor: default;'>{label}</div>", unsafe_allow_html=True)
        else:
            # Inactive (using Streamlit button styled as a clean link via CSS globally applied to all buttons in these specific columns? Hard to isolate. 
            # Easiest is to use the `type="secondary"` and style it cleanly.
            if col.button(label, use_container_width=True):
                st.session_state.page = target_page
                st.rerun()

    # Apply the hack to strip button backgrounds for these columns in CSS
    st.markdown("""
        <style>
            /* Strip background for buttons in the nav area */
            div[data-testid="column"]:nth-of-type(2) .stButton > button,
            div[data-testid="column"]:nth-of-type(3) .stButton > button,
            div[data-testid="column"]:nth-of-type(4) .stButton > button {
                background: transparent !important;
                border: none !important;
                border-radius: 0 !important;
                color: var(--text-secondary) !important;
                border-bottom: 2px solid transparent !important;
            }
            div[data-testid="column"]:nth-of-type(2) .stButton > button:hover,
            div[data-testid="column"]:nth-of-type(3) .stButton > button:hover,
            div[data-testid="column"]:nth-of-type(4) .stButton > button:hover {
                color: var(--primary-green) !important;
                background: rgba(46, 125, 50, 0.05) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    _nav_tab(col2, "Dashboard", "dashboard")
    _nav_tab(col3, "Simulation", "setup")
    _nav_tab(col4, "Inspector", "inspector")
    
    st.markdown("<hr style='margin-top: 0; padding-top: 0; margin-bottom: 1.5rem; border-color: var(--border-color); opacity: 0.3;'>", unsafe_allow_html=True)

def render_metric_card(container, title: str, value: str, color_hex: str = "#2E7D32"):
    """Compact KPI Card for dashboard."""
    card_html = f"""
    <div class="sci-card-compact" style="border-top: 3px solid {color_hex}; text-align: center; padding: 0.75rem;">
        <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 0.25rem;">{title}</div>
        <div style="font-family: var(--font-mono); font-size: 1.5rem; font-weight: 500; color: var(--text-primary); line-height: 1.2;">{value}</div>
    </div>
    """
    container.markdown(card_html, unsafe_allow_html=True)

def apply_light_theme(fig):
    """Applies the Scientific Light design system tokens to a Plotly figure."""
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#111827", family="Inter"),
        margin=dict(l=0, r=0, t=24, b=0),
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.15)", zeroline=False, title_font=dict(color="#111827", size=13), tickfont=dict(color="#111827", size=11)),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.15)", zeroline=False, title_font=dict(color="#111827", size=13), tickfont=dict(color="#111827", size=11)),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0.9)", bordercolor="#E5E7EB", borderwidth=1,
            font=dict(size=10, color="#1F2937")
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF", 
            font_size=12, 
            font_family="Inter", 
            bordercolor="#E5E7EB",
            font_color="#1F2937"
        )
    )
    return fig
