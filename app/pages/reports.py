"""
Reports page for RAP Framework.
Generate and export risk reports.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO

from rap.engine.analytics import calculate_risk_metrics, rank_scenarios
from rap.core.taxonomy import DIMENSIONS, get_metric
from app.components.charts import SEK_COLORS


def render_reports():
    """Render the reports page."""
    st.markdown("# Relatórios e Exportação")
    st.markdown("Gere relatórios executivos e exporte dados para análise.")

    results = st.session_state.get("results", [])
    scenarios = st.session_state.get("scenarios", [])

    if not results:
        st.warning("⚠️ Nenhum resultado de simulação disponível. Execute uma simulação primeiro.")

        if st.button("🎲 Ir para Simulação", type="primary"):
            st.session_state.current_page = "simulation"
            st.rerun()
        return

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Relatório Executivo", "📥 Exportar Dados", "🎨 Gráficos"])

    with tab1:
        render_executive_report(results, scenarios)

    with tab2:
        render_export_options(results, scenarios)

    with tab3:
        render_charts(results, scenarios)


def render_executive_report(results, scenarios):
    """Render executive summary report."""
    st.markdown("### Relatório Executivo de Risco")

    # Calculate all metrics
    all_metrics = [calculate_risk_metrics(r) for r in results]

    # Report header
    report_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.caption(f"Gerado em: {report_date}")

    st.markdown("---")

    # 1. Portfolio Summary
    st.markdown("## 1. Resumo do Portfólio de Risco")

    total_mean = sum(m.mean_loss for m in all_metrics)
    total_var95 = sum(m.var_95 for m in all_metrics)
    total_var99 = sum(m.var_99 for m in all_metrics)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Cenários Analisados", len(scenarios))
    with col2:
        st.metric("Exposição Anual Esperada", f"R$ {total_mean:,.0f}")
    with col3:
        st.metric("VaR 95%", f"R$ {total_var95:,.0f}")
    with col4:
        st.metric("VaR 99%", f"R$ {total_var99:,.0f}")

    # Key insights box
    st.markdown("""
    <div class="sek-card">
        <h4 style="color: #00D4AA; margin-bottom: 1rem;">📌 Insights Principais</h4>
        <ul style="color: #FFFFFF; margin: 0; padding-left: 1.5rem;">
            <li>A organização enfrenta uma <strong>exposição anual esperada</strong> de R$ {:,.0f}</li>
            <li>Em <strong>95% dos cenários simulados</strong>, as perdas não excedem R$ {:,.0f}</li>
            <li>O <strong>pior cenário (1%)</strong> pode resultar em perdas superiores a R$ {:,.0f}</li>
        </ul>
    </div>
    """.format(total_mean, total_var95, total_var99), unsafe_allow_html=True)

    st.markdown("---")

    # 2. Top Risks
    st.markdown("## 2. Principais Riscos")

    rankings = rank_scenarios(results, "var_95")
    top_5 = rankings[:5]

    st.markdown("### Top 5 Cenários por VaR 95%")

    for i, (scenario_id, name, var95) in enumerate(top_5, 1):
        # Find the full metrics
        for m in all_metrics:
            if m.scenario_name == name:
                metrics = m
                break

        # Risk level color
        if var95 > 1_000_000:
            risk_color = "#FF4757"
            risk_level = "CRÍTICO"
        elif var95 > 500_000:
            risk_color = "#FFA726"
            risk_level = "ALTO"
        else:
            risk_color = "#FFD93D"
            risk_level = "MODERADO"

        st.markdown(f"""
        <div class="sek-card" style="border-left: 4px solid {risk_color}; margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #A0AEC0; font-size: 0.875rem;">#{i}</span>
                    <span style="color: #FFFFFF; font-weight: 600; margin-left: 0.5rem;">{name}</span>
                    <span style="color: {risk_color}; font-size: 0.75rem; margin-left: 0.5rem; padding: 0.125rem 0.5rem; background: {risk_color}20; border-radius: 4px;">{risk_level}</span>
                </div>
                <div style="text-align: right;">
                    <div style="color: {risk_color}; font-weight: 700;">VaR 95%: R$ {var95:,.0f}</div>
                    <div style="color: #A0AEC0; font-size: 0.75rem;">Média: R$ {metrics.mean_loss:,.0f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. Distribution by Dimension
    st.markdown("## 3. Distribuição por Dimensão de Risco")

    # Group by dimension
    dim_data = {}
    for scenario, metric in zip(scenarios, all_metrics):
        dim_id = scenario.dimension_id
        dim_name = DIMENSIONS.get(dim_id)
        dim_label = f"D{dim_id}: {dim_name.name if dim_name else 'Desconhecida'}"

        if dim_label not in dim_data:
            dim_data[dim_label] = {"mean": 0, "var95": 0, "count": 0}

        dim_data[dim_label]["mean"] += metric.mean_loss
        dim_data[dim_label]["var95"] += metric.var_95
        dim_data[dim_label]["count"] += 1

    # Create DataFrame
    dim_df = pd.DataFrame([
        {
            "Dimensão": dim,
            "Cenários": data["count"],
            "Exposição Média": data["mean"],
            "VaR 95%": data["var95"],
            "% do Total": data["mean"] / total_mean * 100 if total_mean > 0 else 0,
        }
        for dim, data in dim_data.items()
    ])

    dim_df = dim_df.sort_values("Exposição Média", ascending=False)

    st.dataframe(
        dim_df.style.format({
            "Exposição Média": "R$ {:,.0f}",
            "VaR 95%": "R$ {:,.0f}",
            "% do Total": "{:.1f}%",
        }).background_gradient(subset=["% do Total"], cmap="YlOrRd"),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # 4. Recommendations
    st.markdown("## 4. Recomendações")

    # Generate recommendations based on data
    recommendations = generate_recommendations(scenarios, all_metrics, rankings)

    for i, rec in enumerate(recommendations, 1):
        priority_colors = {"ALTA": "#FF4757", "MÉDIA": "#FFA726", "BAIXA": "#00D4AA"}
        color = priority_colors.get(rec["priority"], "#A0AEC0")

        st.markdown(f"""
        <div class="sek-card" style="margin-bottom: 0.5rem;">
            <div style="display: flex; align-items: flex-start;">
                <span style="color: {color}; font-weight: 700; margin-right: 1rem; font-size: 1.25rem;">{i}.</span>
                <div>
                    <div style="color: #FFFFFF; font-weight: 600;">{rec['title']}</div>
                    <div style="color: #A0AEC0; font-size: 0.875rem; margin-top: 0.25rem;">{rec['description']}</div>
                    <span style="color: {color}; font-size: 0.75rem; padding: 0.125rem 0.5rem; background: {color}20; border-radius: 4px; margin-top: 0.5rem; display: inline-block;">
                        Prioridade: {rec['priority']}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def generate_recommendations(scenarios, metrics, rankings):
    """Generate recommendations based on analysis."""
    recommendations = []

    # Top risk recommendation
    if rankings:
        top_risk = rankings[0]
        recommendations.append({
            "title": f"Priorizar mitigação do cenário '{top_risk[1]}'",
            "description": f"Este cenário representa o maior risco com VaR 95% de R$ {top_risk[2]:,.0f}. Avalie controles adicionais.",
            "priority": "ALTA"
        })

    # High concentration in single dimension
    dim_exposure = {}
    total_mean = sum(m.mean_loss for m in metrics)
    for scenario, metric in zip(scenarios, metrics):
        dim_id = scenario.dimension_id
        dim_exposure[dim_id] = dim_exposure.get(dim_id, 0) + metric.mean_loss

    for dim_id, exposure in dim_exposure.items():
        if total_mean > 0 and exposure / total_mean > 0.4:
            dim_name = DIMENSIONS.get(dim_id)
            recommendations.append({
                "title": f"Concentração de risco na Dimensão {dim_id}",
                "description": f"Mais de 40% da exposição está em '{dim_name.name if dim_name else 'Desconhecida'}'. Diversifique controles.",
                "priority": "MÉDIA"
            })

    # General recommendations
    recommendations.append({
        "title": "Revisar avaliações das três camadas",
        "description": "Atualize as avaliações de Business Strategy, GRC e Offensive Security para refinar os parâmetros de risco.",
        "priority": "MÉDIA"
    })

    recommendations.append({
        "title": "Acompanhar evolução dos indicadores",
        "description": "Execute simulações periodicamente (mensal/trimestral) para acompanhar a evolução da postura de risco.",
        "priority": "BAIXA"
    })

    return recommendations


def render_export_options(results, scenarios):
    """Render data export options."""
    st.markdown("### Exportar Dados")

    all_metrics = [calculate_risk_metrics(r) for r in results]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Resultados da Simulação (CSV)")

        df = pd.DataFrame([
            {
                "scenario_id": m.scenario_id,
                "scenario_name": m.scenario_name,
                "mean_loss": m.mean_loss,
                "median_loss": m.median_loss,
                "var_90": m.var_90,
                "var_95": m.var_95,
                "var_99": m.var_99,
                "min_loss": m.min_loss,
                "max_loss": m.max_loss,
                "std_loss": m.std_loss,
                "probability_of_loss": m.probability_of_loss,
                "currency": m.currency,
                "n_iterations": m.n_iterations,
            }
            for m in all_metrics
        ])

        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Resultados CSV",
            data=csv,
            file_name="rap_simulation_results.csv",
            mime="text/csv",
            type="primary",
        )

        st.markdown("#### Preview:")
        st.dataframe(df.head(), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### Cenários Completos (CSV)")

        scenarios_df = pd.DataFrame([
            {
                "scenario_id": s.scenario_id,
                "scenario_name": s.name,
                "metric_id": s.metric_id,
                "dimension_id": s.dimension_id,
                "asset": s.asset,
                "threat": s.threat,
                "freq_min": s.frequency.min_value,
                "freq_most": s.frequency.most_likely,
                "freq_max": s.frequency.max_value,
                "impact_min": s.impact.min_value,
                "impact_most": s.impact.most_likely,
                "impact_max": s.impact.max_value,
                "currency": s.impact.currency,
            }
            for s in scenarios
        ])

        scenarios_csv = scenarios_df.to_csv(index=False)
        st.download_button(
            "📥 Download Cenários CSV",
            data=scenarios_csv,
            file_name="rap_scenarios.csv",
            mime="text/csv",
        )

        st.markdown("#### Preview:")
        st.dataframe(scenarios_df.head(), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Excel export
    st.markdown("#### Relatório Completo (Excel)")
    st.caption("Inclui múltiplas abas: Resumo, Cenários, Resultados, Recomendações")

    if st.button("📥 Gerar Relatório Excel", type="primary"):
        # Create Excel file in memory
        buffer = BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            # Summary sheet
            summary_data = {
                "Métrica": ["Total de Cenários", "Exposição Anual Esperada", "VaR 95%", "VaR 99%"],
                "Valor": [
                    len(scenarios),
                    f"R$ {sum(m.mean_loss for m in all_metrics):,.0f}",
                    f"R$ {sum(m.var_95 for m in all_metrics):,.0f}",
                    f"R$ {sum(m.var_99 for m in all_metrics):,.0f}",
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Resumo", index=False)

            # Scenarios sheet
            scenarios_df.to_excel(writer, sheet_name="Cenários", index=False)

            # Results sheet
            df.to_excel(writer, sheet_name="Resultados", index=False)

        buffer.seek(0)

        st.download_button(
            "📥 Download Excel",
            data=buffer,
            file_name="rap_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def render_charts(results, scenarios):
    """Render exportable charts."""
    st.markdown("### Gráficos para Apresentação")

    all_metrics = [calculate_risk_metrics(r) for r in results]

    # Chart 1: Top risks bar chart
    st.markdown("#### Top 10 Riscos por VaR 95%")

    sorted_metrics = sorted(all_metrics, key=lambda m: m.var_95, reverse=True)[:10]

    fig = go.Figure(data=[
        go.Bar(
            x=[m.var_95 for m in sorted_metrics],
            y=[m.scenario_name[:30] for m in sorted_metrics],
            orientation="h",
            marker_color=SEK_COLORS["accent"],
            text=[f"R$ {m.var_95:,.0f}" for m in sorted_metrics],
            textposition="outside",
        )
    ])

    fig.update_layout(
        paper_bgcolor="#0A1628",
        plot_bgcolor="#0A1628",
        font_color="#FFFFFF",
        xaxis=dict(showgrid=True, gridcolor="rgba(48, 54, 61, 0.5)", title="VaR 95% (R$)"),
        yaxis=dict(showgrid=False, autorange="reversed"),
        height=400,
        margin=dict(t=20, b=40, l=200, r=100),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Chart 2: Pie chart by dimension
    st.markdown("#### Distribuição de Exposição por Dimensão")

    dim_exposure = {}
    for scenario, metric in zip(scenarios, all_metrics):
        dim_id = scenario.dimension_id
        dim_name = DIMENSIONS.get(dim_id)
        label = f"D{dim_id}: {dim_name.name[:15] if dim_name else 'N/A'}..."
        dim_exposure[label] = dim_exposure.get(label, 0) + metric.mean_loss

    fig = go.Figure(data=[go.Pie(
        labels=list(dim_exposure.keys()),
        values=list(dim_exposure.values()),
        hole=0.4,
        marker_colors=[SEK_COLORS["accent"], SEK_COLORS["info"], "#9B59B6", "#E74C3C", "#F39C12", "#1ABC9C", "#3498DB"],
        textinfo="percent+label",
        textposition="outside",
    )])

    fig.update_layout(
        paper_bgcolor="#0A1628",
        plot_bgcolor="#0A1628",
        font_color="#FFFFFF",
        showlegend=False,
        height=400,
        margin=dict(t=20, b=20, l=20, r=20),
    )

    st.plotly_chart(fig, use_container_width=True)
