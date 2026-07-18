# Import the core Streamlit library
import streamlit as st

# Read the raw CSS file content from disk
def load_css() -> str:
    # Open the style.css file with UTF-8 encoding
    with open("ui/style.css", "r", encoding="utf-8") as f:
        # Return the complete string contents
        return f.read()

# Inject the loaded CSS into the Streamlit DOM
def inject_custom_css():
    """Reads style.css and injects it into Streamlit via markdown."""
    # Fetch CSS string
    css = load_css()
    # Use unsafe_allow_html to embed the raw CSS into the browser
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Render the application's top navigation header
def render_navbar(active_page: str = "landing"):
    """Renders the top navigation bar with an enterprise tab-style underline."""
    
    # Add a spacer at the top of the page
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    
    # Define a 5-column layout for the navbar structure
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 3])
    
    # Place the main branding title in the leftmost column
    with col1:
        st.markdown("<div style='font-family: var(--font-heading); font-size: 1.25rem; font-weight: 700; color: var(--primary-green); padding-top: 0.5rem;'>AgroTech Vision</div>", unsafe_allow_html=True)
    
    # Helper function to render an individual navigation tab
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
        # Check if this tab is the currently active page
        if active_page == target_page:
            # Active tab: Render as static text with a green underline
            col.markdown(f"<div style='text-align:center; padding: 0.5rem; color: var(--primary-green); border-bottom: 2px solid var(--primary-green); font-weight: 600; cursor: default;'>{label}</div>", unsafe_allow_html=True)
        else:
            # Inactive tab: Render as a clickable Streamlit button
            if col.button(label, use_container_width=True):
                # Update session state if clicked
                st.session_state.page = target_page
                # Force an immediate page reload
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

    # Render Dashboard tab in column 2
    _nav_tab(col2, "Dashboard", "dashboard")
    # Render Simulation Setup tab in column 3
    _nav_tab(col3, "Simulation", "setup")
    # Render Node Inspector tab in column 4
    _nav_tab(col4, "Inspector", "inspector")
    
    # Add a light horizontal divider beneath the navbar
    st.markdown("<hr style='margin-top: 0; padding-top: 0; margin-bottom: 1.5rem; border-color: var(--border-color); opacity: 0.3;'>", unsafe_allow_html=True)

# Helper function to draw small KPI metric cards
def render_metric_card(container, title: str, value: str, color_hex: str = "#2E7D32"):
    """Compact KPI Card for dashboard."""
    # Define HTML payload for the metric card
    card_html = f"""
    <div class="sci-card-compact" style="border-top: 3px solid {color_hex}; text-align: center; padding: 0.75rem;">
        <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 0.25rem;">{title}</div>
        <div style="font-family: var(--font-mono); font-size: 1.5rem; font-weight: 500; color: var(--text-primary); line-height: 1.2;">{value}</div>
    </div>
    """
    # Write raw HTML block into the provided container
    container.markdown(card_html, unsafe_allow_html=True)

# Standardize Plotly chart aesthetics across the application
def apply_light_theme(fig):
    """Applies the Scientific Light design system tokens to a Plotly figure."""
    # Update global layout parameters for the figure
    fig.update_layout(
        # Set chart area background to transparent
        plot_bgcolor="rgba(0,0,0,0)", 
        # Set outer paper background to transparent
        paper_bgcolor="rgba(0,0,0,0)",
        # Set default font style
        font=dict(color="#111827", family="Inter"),
        # Adjust margins to fit tightly within containers
        margin=dict(l=0, r=0, t=24, b=0),
        # Configure X-axis gridlines and labels
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.15)", zeroline=False, title_font=dict(color="#111827", size=13), tickfont=dict(color="#111827", size=11)),
        # Configure Y-axis gridlines and labels
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.15)", zeroline=False, title_font=dict(color="#111827", size=13), tickfont=dict(color="#111827", size=11)),
        # Configure top-right horizontal legend style
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0.9)", bordercolor="#E5E7EB", borderwidth=1,
            font=dict(size=10, color="#1F2937")
        ),
        # Configure interactive hover tooltip style
        hoverlabel=dict(
            bgcolor="#FFFFFF", 
            font_size=12, 
            font_family="Inter", 
            bordercolor="#E5E7EB",
            font_color="#1F2937"
        )
    )
    # Return the updated figure object
    return fig
