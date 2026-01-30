"""
Simulation page for RAP Framework.
Run Monte Carlo simulations on risk scenarios.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

from rap.engine.monte_carlo import (
    simulate_scenarios,
    simulate_scenario,
    SimulationConfig,
    aggregate_results,
)
from rap.engine.analytics import (
    calculate_risk_metrics,
    calculate_loss_exceedance_curve,
    rank_scenarios,
)
from app.components.charts import SEK_COLORS


def render_simulation():
    """Render the simulation page."""
    st.markdown("# Simulação Monte Carlo")
    st.markdown("Execute simulações para quantificar o risco dos cenários cadastrados.")

    scenarios = st.session_state.get("scenarios", [])

    if not scenarios:
        st.warning("⚠️ Nenhum cenário cadastrado. Crie cenários primeiro.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Criar Cenários", type="primary"):
                st.session_state.current_page = "scenarios"
                st.rerun()
        with col2:
            if st.button("🔬 Carregar Exemplos"):
                from app.pages.dashboard import load_example_scenarios
                load_example_scenarios()
                st.rerun()
        return

    # Tabs
    tab1, tab2 = st.tabs(["🎲 Executar Simulação", "📊 Resultados"])

    with tab1:
        render_simulation_config(scenarios)

    with tab2:
        render_simulation_results()


def render_simulation_config(scenarios):
    """Render simulation configuration and execution."""
    st.markdown("### Configuração da Simulação")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Cenários Selecionados")
        st.info(f"**{len(scenarios)} cenário(s)** serão simulados")

        # Show scenario summary
        df = pd.DataFrame([
            {
                "ID": s.scenario_id,
                "Nome": s.name[:30] + "..." if len(s.name) > 30 else s.name,
                "EAL Est.": f"R$ {s.get_expected_annual_loss():,.0f}",
            }
            for s in scenarios
        ])
        st.dataframe(df, use_container_width=True, hide_index=True, height=200)

    with col2:
        st.markdown("#### Parâmetros")

        iterations = st.select_slider(
            "Número de Iterações",
            options=[1_000, 5_000, 10_000, 20_000, 50_000, 100_000],
            value=10_000,
            help="Mais iterações = maior precisão, mas mais tempo de processamento"
        )

        seed = st.number_input(
            "Seed (opcional)",
            min_value=0,
            max_value=999999,
            value=42,
            help="Use o mesmo seed para resultados reproduzíveis"
        )

        use_seed = st.checkbox("Usar seed para reprodutibilidade", value=True)

        distribution = st.selectbox(
            "Tipo de Distribuição",
            options=["PERT (Recomendado)", "Triangular"],
            help="PERT é mais suave e geralmente preferido para análise de risco"
        )

    st.markdown("---")

    # Execution
    st.markdown("### Executar Simulação")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        run_button = st.button(
            "🎲 Executar Simulação Monte Carlo",
            type="primary",
            use_container_width=True
        )

    with col2:
        st.metric("Cenários", len(scenarios))

    with col3:
        st.metric("Iterações", f"{iterations:,}")

    if run_button:
        run_simulation(scenarios, iterations, seed if use_seed else None)


def run_simulation(scenarios, iterations, seed):
    """Execute the Monte Carlo simulation with progress bar."""
    st.markdown("---")
    st.markdown("### Executando Simulação...")

    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Config
    config = SimulationConfig(
        n_iterations=iterations,
        random_seed=seed,
    )

    results = []
    total = len(scenarios)

    start_time = time.time()

    for i, scenario in enumerate(scenarios):
        status_text.text(f"Simulando: {scenario.name} ({i + 1}/{total})")

        # Simulate
        result = simulate_scenario(scenario, config)
        results.append(result)

        # Update progress
        progress_bar.progress((i + 1) / total)

    elapsed = time.time() - start_time

    # Store results
    st.session_state.results = results
    st.session_state.last_simulation = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.simulation_config = {
        "iterations": iterations,
        "seed": seed,
        "elapsed": elapsed,
    }

    # Success message
    progress_bar.progress(1.0)
    status_text.empty()

    st.success(f"""
    ✅ **Simulação concluída com sucesso!**

    - **{total} cenário(s)** simulados
    - **{iterations:,} iterações** por cenário
    - **Tempo total:** {elapsed:.2f} segundos
    """)

    # Show quick summary
    st.markdown("---")
    st.markdown("### Resumo Rápido")

    all_metrics = [calculate_risk_metrics(r) for r in results]

    total_mean = sum(m.mean_loss for m in all_metrics)
    total_var95 = sum(m.var_95 for m in all_metrics)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Exposição Anual Esperada", f"R$ {total_mean:,.0f}")
    with col2:
        st.metric("VaR 95% Total", f"R$ {total_var95:,.0f}")
    with col3:
        st.metric("Cenários Analisados", len(scenarios))

    st.info("Veja os resultados detalhados na aba **Resultados** ou no **Dashboard**.")


def render_simulation_results():
    """Render simulation results."""
    results = st.session_state.get("results", [])

    if not results:
        st.info("Nenhum resultado de simulação disponível. Execute uma simulação primeiro.")
        return

    config = st.session_state.get("simulation_config", {})

    # Simulation info
    st.markdown("### Informações da Simulação")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Iterações", f"{config.get('iterations', 'N/A'):,}")
    with col2:
        st.metric("Seed", config.get("seed", "N/A"))
    with col3:
        st.metric("Tempo", f"{config.get('elapsed', 0):.2f}s")
    with col4:
        st.metric("Data", st.session_state.get("last_simulation", "N/A"))

    st.markdown("---")

    # Calculate metrics for all results
    all_metrics = [calculate_risk_metrics(r) for r in results]

    # Portfolio summary
    st.markdown("### Métricas do Portfólio")

    total_mean = sum(m.mean_loss for m in all_metrics)
    total_var90 = sum(m.var_90 for m in all_metrics)
    total_var95 = sum(m.var_95 for m in all_metrics)
    total_var99 = sum(m.var_99 for m in all_metrics)

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
            <div class="sek-metric-label">VaR 90%</div>
            <div class="sek-metric-value" style="color: #FFD93D;">R$ {total_var90:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="sek-metric-card">
            <div class="sek-metric-label">VaR 95%</div>
            <div class="sek-metric-value" style="color: #FFA726;">R$ {total_var95:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="sek-metric-card">
            <div class="sek-metric-label">VaR 99%</div>
            <div class="sek-metric-value" style="color: #FF4757;">R$ {total_var99:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Distribuição de Perdas (Agregado)")
        fig = create_loss_distribution_chart(results)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Curva de Excedência de Perdas")
        fig = create_exceedance_curve(results)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Detailed table
    st.markdown("### Detalhamento por Cenário")

    df = pd.DataFrame([
        {
            "Cenário": m.scenario_name,
            "Média": m.mean_loss,
            "Mediana": m.median_loss,
            "VaR 90%": m.var_90,
            "VaR 95%": m.var_95,
            "VaR 99%": m.var_99,
            "P(Loss)": m.probability_of_loss,
            "Desvio Padrão": m.std_loss,
        }
        for m in all_metrics
    ])

    # Sort by VaR 95%
    df = df.sort_values("VaR 95%", ascending=False)

    st.dataframe(
        df.style.format({
            "Média": "R$ {:,.0f}",
            "Mediana": "R$ {:,.0f}",
            "VaR 90%": "R$ {:,.0f}",
            "VaR 95%": "R$ {:,.0f}",
            "VaR 99%": "R$ {:,.0f}",
            "P(Loss)": "{:.1%}",
            "Desvio Padrão": "R$ {:,.0f}",
        }).background_gradient(subset=["VaR 95%"], cmap="YlOrRd"),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # Individual scenario analysis
    st.markdown("### Análise Individual de Cenário")

    scenario_names = [r.scenario_name for r in results]
    selected_scenario = st.selectbox(
        "Selecione um cenário para análise detalhada:",
        options=scenario_names
    )

    if selected_scenario:
        idx = scenario_names.index(selected_scenario)
        result = results[idx]
        metrics = all_metrics[idx]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"#### {selected_scenario}")
            st.markdown(f"""
            - **Média:** R$ {metrics.mean_loss:,.0f}
            - **Mediana:** R$ {metrics.median_loss:,.0f}
            - **Desvio Padrão:** R$ {metrics.std_loss:,.0f}
            - **Mínimo:** R$ {metrics.min_loss:,.0f}
            - **Máximo:** R$ {metrics.max_loss:,.0f}
            - **P(Loss > 0):** {metrics.probability_of_loss:.1%}
            """)

        with col2:
            # Mini histogram
            fig = go.Figure(data=[go.Histogram(
                x=result.annual_losses,
                nbinsx=50,
                marker_color=SEK_COLORS["accent"],
                opacity=0.7,
            )])

            fig.add_vline(x=metrics.mean_loss, line_dash="dash", line_color="#FFFFFF",
                          annotation_text="Média")
            fig.add_vline(x=metrics.var_95, line_dash="dash", line_color="#FFA726",
                          annotation_text="VaR 95%")

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#FFFFFF",
                xaxis=dict(showgrid=True, gridcolor="rgba(48, 54, 61, 0.5)", title="Perda Anual (R$)"),
                yaxis=dict(showgrid=True, gridcolor="rgba(48, 54, 61, 0.5)", title="Frequência"),
                height=250,
                margin=dict(t=20, b=40, l=40, r=20),
            )

            st.plotly_chart(fig, use_container_width=True)


def create_loss_distribution_chart(results) -> go.Figure:
    """Create aggregated loss distribution histogram."""
    # Aggregate all losses
    all_losses = np.sum([r.annual_losses for r in results], axis=0)

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=all_losses,
        nbinsx=100,
        marker_color=SEK_COLORS["accent"],
        opacity=0.7,
        name="Distribuição",
    ))

    # Add VaR lines
    mean_loss = np.mean(all_losses)
    var_95 = np.percentile(all_losses, 95)
    var_99 = np.percentile(all_losses, 99)

    fig.add_vline(x=mean_loss, line_dash="dash", line_color="#FFFFFF",
                  annotation_text="Média", annotation_position="top")
    fig.add_vline(x=var_95, line_dash="dash", line_color="#FFA726",
                  annotation_text="VaR 95%", annotation_position="top")
    fig.add_vline(x=var_99, line_dash="dash", line_color="#FF4757",
                  annotation_text="VaR 99%", annotation_position="top")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FFFFFF",
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(48, 54, 61, 0.5)",
            title="Perda Anual Agregada (R$)",
            tickformat=",.0f",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(48, 54, 61, 0.5)",
            title="Frequência",
        ),
        showlegend=False,
        height=350,
        margin=dict(t=40, b=40, l=40, r=20),
    )

    return fig


def create_exceedance_curve(results) -> go.Figure:
    """Create loss exceedance curve."""
    # Aggregate losses
    all_losses = np.sum([r.annual_losses for r in results], axis=0)
    sorted_losses = np.sort(all_losses)

    # Calculate exceedance probabilities
    n = len(sorted_losses)
    exceedance_probs = 1 - np.arange(1, n + 1) / n

    # Sample points for smoother curve
    sample_indices = np.linspace(0, n - 1, 200, dtype=int)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sorted_losses[sample_indices],
        y=exceedance_probs[sample_indices],
        mode="lines",
        line=dict(color=SEK_COLORS["accent"], width=2),
        fill="tozeroy",
        fillcolor="rgba(0, 212, 170, 0.1)",
        name="Excedência",
    ))

    # Add reference lines
    var_95 = np.percentile(sorted_losses, 95)
    fig.add_hline(y=0.05, line_dash="dash", line_color="#FFA726",
                  annotation_text="5% (VaR 95%)")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FFFFFF",
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(48, 54, 61, 0.5)",
            title="Perda Anual (R$)",
            tickformat=",.0f",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(48, 54, 61, 0.5)",
            title="Probabilidade de Excedência",
            tickformat=".0%",
            range=[0, 1],
        ),
        showlegend=False,
        height=350,
        margin=dict(t=20, b=40, l=40, r=20),
    )

    return fig
