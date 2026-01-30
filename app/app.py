"""
RAP Framework - Web Interface
Main entry point for the Streamlit application.

Identity Visual: SEK (Security Ecosystem Knowledge)
"""

import streamlit as st
from pathlib import Path

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="RAP Framework | SEK",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://sek.io",
        "Report a bug": "https://github.com/sek/rap/issues",
        "About": """
        ## RAP Framework
        **Resilience Acceleration Program**

        Framework de Quantificação de Risco Orientado à Resiliência Cibernética.

        Desenvolvido por SEK - Security Ecosystem Knowledge
        """
    }
)

# Load custom CSS
def load_css():
    """Load custom CSS for SEK branding."""
    css_file = Path(__file__).parent / "assets" / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Inline critical CSS for SEK branding
    st.markdown("""
    <style>
    /* SEK Brand Colors */
    :root {
        --sek-primary: #0A1628;
        --sek-secondary: #1B3A5F;
        --sek-accent: #00D4AA;
        --sek-accent-light: #00E5BB;
        --sek-text: #FFFFFF;
        --sek-text-muted: #A0AEC0;
        --sek-background: #0D1117;
        --sek-card: #161B22;
        --sek-border: #30363D;
        --sek-success: #00D4AA;
        --sek-warning: #FFA726;
        --sek-danger: #FF4757;
        --sek-info: #00B4D8;
    }

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0A1628 0%, #0D1117 50%, #1B3A5F 100%);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A1628 0%, #161B22 100%);
        border-right: 1px solid #30363D;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF;
    }

    /* Headers */
    h1, h2, h3 {
        color: #FFFFFF !important;
    }

    h1 {
        background: linear-gradient(90deg, #00D4AA, #00B4D8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Cards/Containers */
    [data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 1rem;
    }

    [data-testid="stMetricValue"] {
        color: #00D4AA !important;
    }

    [data-testid="stMetricLabel"] {
        color: #A0AEC0 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #00D4AA, #00B4D8);
        color: #0A1628;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #00E5BB, #00C5E9);
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.4);
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: #161B22;
        border: 1px solid #30363D;
        color: #FFFFFF;
        border-radius: 8px;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #00D4AA;
        box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.2);
    }

    /* Dataframes */
    .stDataFrame {
        border: 1px solid #30363D;
        border-radius: 12px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: #161B22;
        border-radius: 8px 8px 0 0;
        border: 1px solid #30363D;
        color: #A0AEC0;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00D4AA, #00B4D8);
        color: #0A1628;
        border-color: #00D4AA;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        color: #FFFFFF;
    }

    /* Success/Error/Warning messages */
    .stSuccess {
        background: rgba(0, 212, 170, 0.1);
        border-left: 4px solid #00D4AA;
    }

    .stError {
        background: rgba(255, 71, 87, 0.1);
        border-left: 4px solid #FF4757;
    }

    .stWarning {
        background: rgba(255, 167, 38, 0.1);
        border-left: 4px solid #FFA726;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00D4AA, #00B4D8);
    }

    /* Divider */
    hr {
        border-color: #30363D;
    }

    /* Custom classes */
    .sek-card {
        background: rgba(22, 27, 34, 0.9);
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
    }

    .sek-metric-card {
        background: linear-gradient(135deg, #161B22 0%, #1B3A5F 100%);
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }

    .sek-metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00D4AA;
        margin: 0.5rem 0;
    }

    .sek-metric-label {
        font-size: 0.875rem;
        color: #A0AEC0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .gap-critical { color: #FF4757; }
    .gap-high { color: #FF6B6B; }
    .gap-elevated { color: #FFA726; }
    .gap-moderate { color: #FFD93D; }
    .gap-low { color: #00D4AA; }

    /* Logo area */
    .logo-container {
        text-align: center;
        padding: 1rem 0 2rem 0;
        border-bottom: 1px solid #30363D;
        margin-bottom: 1rem;
    }

    .logo-text {
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00D4AA, #00B4D8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .logo-subtitle {
        font-size: 0.75rem;
        color: #A0AEC0;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        # Logo
        st.markdown("""
        <div class="logo-container">
            <div class="logo-text">🛡️ RAP</div>
            <div class="logo-subtitle">Resilience Acceleration Program</div>
            <div style="font-size: 0.65rem; color: #A0AEC0; margin-top: 0.5rem;">
                powered by <span style="color: #00D4AA; font-weight: 600;">SEK</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown("### Navegação")

        pages = {
            "🏠 Dashboard": "dashboard",
            "📋 Cenários": "scenarios",
            "📊 Avaliações (3 Camadas)": "assessments",
            "🎲 Simulação": "simulation",
            "📈 Relatórios": "reports",
            "📚 Taxonomia RAP": "taxonomy",
        }

        # Store selected page in session state
        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"

        for label, page_id in pages.items():
            if st.button(label, key=f"nav_{page_id}", use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()

        st.markdown("---")

        # Quick stats
        st.markdown("### Status Rápido")

        if "scenarios" in st.session_state and st.session_state.scenarios:
            n_scenarios = len(st.session_state.scenarios)
            st.metric("Cenários", n_scenarios)
        else:
            st.metric("Cenários", 0)

        if "last_simulation" in st.session_state:
            st.caption(f"Última simulação: {st.session_state.last_simulation}")

        st.markdown("---")

        # Footer
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; color: #A0AEC0; font-size: 0.75rem;">
            <div>RAP Framework v0.1.0</div>
            <div style="margin-top: 0.25rem;">
                <a href="https://sek.io" target="_blank" style="color: #00D4AA; text-decoration: none;">
                    sek.io
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    # Load CSS
    load_css()

    # Initialize session state
    if "scenarios" not in st.session_state:
        st.session_state.scenarios = []
    if "results" not in st.session_state:
        st.session_state.results = []
    if "assessments" not in st.session_state:
        st.session_state.assessments = {}

    # Render sidebar
    render_sidebar()

    # Route to current page
    page = st.session_state.get("current_page", "dashboard")

    if page == "dashboard":
        from app.pages.dashboard import render_dashboard
        render_dashboard()
    elif page == "scenarios":
        from app.pages.scenarios import render_scenarios
        render_scenarios()
    elif page == "assessments":
        from app.pages.assessments import render_assessments
        render_assessments()
    elif page == "simulation":
        from app.pages.simulation import render_simulation
        render_simulation()
    elif page == "reports":
        from app.pages.reports import render_reports
        render_reports()
    elif page == "taxonomy":
        from app.pages.taxonomy import render_taxonomy
        render_taxonomy()
    else:
        st.error(f"Página não encontrada: {page}")


if __name__ == "__main__":
    main()
