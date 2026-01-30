"""
Dashboard page for RAP Framework.
Displays risk overview, top scenarios, and key metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

from app.components.charts import (
    create_risk_gauge,
    create_dimension_chart,
    create_loss_distribution_chart,
    SEK_COLORS,
)


def render_dashboard():
    """Render the main dashboard."""
    st.markdown("# Dashboard de Risco")
    st.markdown("Visão geral da exposição ao risco cibernético da organização.")

    # Check if we have data
    has_scenarios = "scenarios" in st.session_state and len(st.session_state.scenarios) > 0
    has_results = "results" in st.session_state and len(st.session_state.results) > 0

    if not has_scenarios:
        render_empty_state()
        return

    if has_results:
        render_full_dashboard()
    else:
        render_scenarios_only_dashboard()


def render_empty_state():
    """Render empty state when no data is available."""
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="sek-card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
            <h3 style="color: #FFFFFF; margin-bottom: 0.5rem;">Criar Cenários</h3>
            <p style="color: #A0AEC0; font-size: 0.875rem;">
                Defina cenários de risco com frequência e impacto estimados.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="sek-card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎲</div>
            <h3 style="color: #FFFFFF; margin-bottom: 0.5rem;">Executar Simulação</h3>
            <p style="color: #A0AEC0; font-size: 0.875rem;">
                Execute simulações Monte Carlo para quantificar o risco.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="sek-card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📈</div>
            <h3 style="color: #FFFFFF; margin-bottom: 0.5rem;">Analisar Resultados</h3>
            <p style="color: #A0AEC0; font-size: 0.875rem;">
                Visualize métricas de risco como VaR e exposição anual.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick actions
    st.markdown("### Começar Agora")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("➕ Criar Primeiro Cenário", use_container_width=True):
            st.session_state.current_page = "scenarios"
            st.rerun()

    with col2:
        if st.button("📤 Importar CSV", use_container_width=True):
            st.session_state.current_page = "scenarios"
            st.session_state.show_import = True
            st.rerun()

    with col3:
        if st.button("📚 Ver Taxonomia RAP", use_container_width=True):
            st.session_state.current_page = "taxonomy"
            st.rerun()

    # Sample data option
    st.markdown("---")
    st.markdown("### Dados de Exemplo")

    if st.button("🔬 Carregar Cenários de Exemplo", use_container_width=False):
        load_example_scenarios()
        st.success("Cenários de exemplo carregados!")
        st.rerun()


def load_example_scenarios():
    """Load example scenarios into session state."""
    from rap.core.model import RiskScenario, FrequencyParams, ImpactParams

    examples = [
        RiskScenario(
            scenario_id="R001",
            name="Ransomware Attack on ERP",
            description="Ransomware encrypts critical ERP database",
            metric_id="01",
            dimension_id=1,
            asset="ERP System",
            threat="Ransomware",
            frequency=FrequencyParams(0.1, 0.3, 0.7),
            impact=ImpactParams(100_000, 500_000, 3_000_000, "BRL"),
        ),
        RiskScenario(
            scenario_id="R002",
            name="Data Breach via Phishing",
            description="Employee compromised via spear phishing",
            metric_id="07",
            dimension_id=2,
            asset="Customer Database",
            threat="Phishing",
            frequency=FrequencyParams(0.2, 0.5, 1.5),
            impact=ImpactParams(50_000, 200_000, 1_000_000, "BRL"),
        ),
        RiskScenario(
            scenario_id="R003",
            name="Supply Chain Compromise",
            description="Malicious code via compromised dependency",
            metric_id="22",
            dimension_id=7,
            asset="Software Dependencies",
            threat="Supply Chain",
            frequency=FrequencyParams(0.05, 0.15, 0.4),
            impact=ImpactParams(200_000, 800_000, 5_000_000, "BRL"),
        ),
        RiskScenario(
            scenario_id="R004",
            name="Cloud Misconfiguration",
            description="Sensitive data exposed via misconfigured S3",
            metric_id="06",
            dimension_id=3,
            asset="Cloud Storage",
            threat="Misconfiguration",
            frequency=FrequencyParams(0.1, 0.25, 0.6),
            impact=ImpactParams(100_000, 400_000, 2_000_000, "BRL"),
        ),
        RiskScenario(
            scenario_id="R005",
            name="Privileged Account Compromise",
            description="Domain admin credentials stolen",
            metric_id="03",
            dimension_id=2,
            asset="Domain Admin",
            threat="Credential Theft",
            frequency=FrequencyParams(0.2, 0.4, 1.0),
            impact=ImpactParams(200_000, 600_000, 2_500_000, "BRL"),
        ),
    ]

    st.session_state.scenarios = examples


def render_scenarios_only_dashboard():
    """Render dashboard when scenarios exist but no simulation yet."""
    scenarios = st.session_state.scenarios

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Cenários", len(scenarios))

    with col2:
        # Count dimensions
        dimensions = set(s.dimension_id for s in scenarios)
        st.metric("Dimensões Cobertas", f"{len(dimensions)}/7")

    with col3:
        # Estimated exposure (simple calculation)
        total_exposure = sum(s.get_expected_annual_loss() for s in scenarios)
        st.metric("Exposição Estimada", f"R$ {total_exposure:,.0f}")

    with col4:
        st.metric("Simulações", "0", delta="Pendente")

    st.markdown("---")

    # Prompt to run simulation
    st.warning("⚠️ Execute uma simulação Monte Carlo para obter métricas detalhadas de risco.")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🎲 Executar Simulação", type="primary", use_container_width=True):
            st.session_state.current_page = "simulation"
            st.rerun()

    st.markdown("---")

    # Scenarios table
    st.markdown("### Cenários Cadastrados")

    df = pd.DataFrame([
        {
            "ID": s.scenario_id,
            "Nome": s.name,
            "Ativo": s.asset,
            "Ameaça": s.threat,
            "Dimensão": s.dimension_id,
            "Exposição Est.": f"R$ {s.get_expected_annual_loss():,.0f}",
        }
        for s in scenarios
    ])

    st.dataframe(df, use_container_width=True, hide_index=True)


def render_full_dashboard():
    """Render full dashboard with simulation results."""
    scenarios = st.session_state.scenarios
    results = st.session_state.results

    from rap.engine.analytics import calculate_risk_metrics

    # Calculate metrics for all results
    all_metrics = [calculate_risk_metrics(r) for r in results]

    # Total exposure
    total_mean = sum(m.mean_loss for m in all_metrics)
    total_var95 = sum(m.var_95 for m in all_metrics)
    total_var99 = sum(m.var_99 for m in all_metrics)

    # Header metrics
    st.markdown("### Exposição Total do Portfólio")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="sek-metric-card">
            <div class="sek-metric-label">Exposição Anual Esperada</div>
            <div class="sek-metric-value">R$ {total_mean:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="sek-metric-card">
            <div class="sek-metric-label">VaR 95%</div>
            <div class="sek-metric-value" style="color: #FFA726;">R$ {total_var95:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="sek-metric-card">
            <div class="sek-metric-label">VaR 99%</div>
            <div class="sek-metric-value" style="color: #FF4757;">R$ {total_var99:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="sek-metric-card">
            <div class="sek-metric-label">Cenários Analisados</div>
            <div class="sek-metric-value" style="color: #00B4D8;">{len(scenarios)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Distribuição por Dimensão")
        fig = create_dimension_distribution(scenarios, all_metrics)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Top 5 Riscos por VaR 95%")
        fig = create_top_risks_chart(all_metrics)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Risk table
    st.markdown("### Detalhamento por Cenário")

    df = pd.DataFrame([
        {
            "Cenário": m.scenario_name,
            "Média": m.mean_loss,
            "VaR 90%": m.var_90,
            "VaR 95%": m.var_95,
            "VaR 99%": m.var_99,
            "P(Loss)": m.probability_of_loss,
        }
        for m in all_metrics
    ])

    # Sort by VaR 95%
    df = df.sort_values("VaR 95%", ascending=False)

    # Format columns
    st.dataframe(
        df.style.format({
            "Média": "R$ {:,.0f}",
            "VaR 90%": "R$ {:,.0f}",
            "VaR 95%": "R$ {:,.0f}",
            "VaR 99%": "R$ {:,.0f}",
            "P(Loss)": "{:.1%}",
        }).background_gradient(subset=["VaR 95%"], cmap="YlOrRd"),
        use_container_width=True,
        hide_index=True,
    )


def create_dimension_distribution(scenarios, metrics) -> go.Figure:
    """Create dimension distribution chart."""
    from rap.core.taxonomy import DIMENSIONS

    # Group by dimension
    dim_data = {}
    for scenario, metric in zip(scenarios, metrics):
        dim_id = scenario.dimension_id
        if dim_id not in dim_data:
            dim_data[dim_id] = 0
        dim_data[dim_id] += metric.mean_loss

    # Create data for chart
    labels = []
    values = []
    colors = [
        SEK_COLORS["accent"],
        SEK_COLORS["info"],
        "#9B59B6",
        "#E74C3C",
        "#F39C12",
        "#1ABC9C",
        "#3498DB",
    ]

    for dim_id in sorted(dim_data.keys()):
        dim_name = DIMENSIONS.get(dim_id)
        if dim_name:
            labels.append(f"D{dim_id}: {dim_name.name[:20]}...")
        else:
            labels.append(f"Dimensão {dim_id}")
        values.append(dim_data[dim_id])

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=colors[:len(labels)],
        textinfo="percent+label",
        textposition="outside",
    )])

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FFFFFF",
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=350,
    )

    return fig


def create_top_risks_chart(metrics) -> go.Figure:
    """Create horizontal bar chart for top risks."""
    # Sort by VaR 95% and take top 5
    sorted_metrics = sorted(metrics, key=lambda m: m.var_95, reverse=True)[:5]

    names = [m.scenario_name[:30] + "..." if len(m.scenario_name) > 30 else m.scenario_name
             for m in sorted_metrics]
    values = [m.var_95 for m in sorted_metrics]

    # Reverse for horizontal bar chart
    names = names[::-1]
    values = values[::-1]

    fig = go.Figure(data=[go.Bar(
        y=names,
        x=values,
        orientation="h",
        marker_color=SEK_COLORS["accent"],
        text=[f"R$ {v:,.0f}" for v in values],
        textposition="outside",
    )])

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FFFFFF",
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(48, 54, 61, 0.5)",
            tickformat=",.0f",
            title="VaR 95% (R$)",
        ),
        yaxis=dict(showgrid=False),
        margin=dict(t=20, b=40, l=10, r=80),
        height=350,
    )

    return fig
