"""
Three-layer assessments page for RAP Framework.
Manage Business Strategy, GRC, and Offensive Security assessments.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional

from rap.core.model import LayerAssessment, RAPAssessment, AssessmentLayer
from rap.core.taxonomy import METRICS, get_metric
from rap.core.mapping_layers import calculate_gap_factor, create_pla_view
from app.components.charts import SEK_COLORS


def render_assessments():
    """Render the assessments page."""
    st.markdown("# Avaliações de Três Camadas")
    st.markdown("""
    O modelo RAP integra três perspectivas para cada métrica:
    - **Business Strategy**: Objetivos definidos pelo negócio
    - **Strategy & Risk Governance**: Maturidade de controles e processos
    - **Offensive Security**: Resultados reais de testes
    """)

    # Initialize assessments in session state
    if "assessments" not in st.session_state:
        st.session_state.assessments = {}

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Visão PLA", "➕ Nova Avaliação", "📋 Todas Avaliações"])

    with tab1:
        render_pla_view()

    with tab2:
        render_assessment_form()

    with tab3:
        render_all_assessments()


def render_pla_view():
    """Render the PLA (3-level) view for assessments."""
    assessments = st.session_state.get("assessments", {})

    if not assessments:
        st.info("Nenhuma avaliação cadastrada. Crie avaliações para visualizar a análise PLA.")

        if st.button("📝 Criar Avaliação de Exemplo", type="primary"):
            create_example_assessments()
            st.rerun()
        return

    st.markdown("### Análise de Gap por Métrica")

    # Select metric to view
    metric_options = list(assessments.keys())
    selected_metric = st.selectbox(
        "Selecione a métrica:",
        options=metric_options,
        format_func=lambda x: f"{x}: {get_metric(x).name if get_metric(x) else 'Desconhecida'}"
    )

    if selected_metric:
        rap_assessment = assessments[selected_metric]
        pla_view = create_pla_view(rap_assessment)

        # Metric info
        metric = get_metric(selected_metric)
        if metric:
            st.markdown(f"**Métrica:** {metric.name}")
            st.caption(metric.description)

        st.markdown("---")

        # Three columns for the three layers
        col1, col2, col3 = st.columns(3)

        with col1:
            render_layer_card(
                "Nível 1: Business Strategy",
                "🎯",
                rap_assessment.business_strategy,
                "#00D4AA",
                "Objetivo definido pelo negócio"
            )

        with col2:
            render_layer_card(
                "Nível 2: Strategy & Risk Governance",
                "📋",
                rap_assessment.strategy_risk_governance,
                "#00B4D8",
                "Maturidade de controles"
            )

        with col3:
            render_layer_card(
                "Nível 3: Offensive Security",
                "🎯",
                rap_assessment.offensive_security,
                "#FFA726",
                "Resultados reais de testes"
            )

        st.markdown("---")

        # Gap analysis
        st.markdown("### Análise de Gap")

        gap_factor = calculate_gap_factor(rap_assessment)

        col1, col2 = st.columns([1, 2])

        with col1:
            # Gap gauge
            fig = create_gap_gauge(gap_factor)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gap interpretation
            gap_class, gap_desc = get_gap_interpretation(gap_factor)

            st.markdown(f"""
            <div class="sek-card">
                <h4 style="color: #FFFFFF; margin-bottom: 1rem;">Fator de Gap: {gap_factor:.2f}</h4>
                <div class="{gap_class}" style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">
                    {gap_desc}
                </div>
                <p style="color: #A0AEC0; font-size: 0.875rem;">
                    {get_gap_recommendation(gap_factor)}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Gap details
            if pla_view["gap_analysis"]["objective_vs_reality_gap"] is not None:
                st.metric(
                    "Gap Objetivo vs Realidade",
                    f"{pla_view['gap_analysis']['objective_vs_reality_gap']:.1f} pontos"
                )

        # Visual comparison chart
        st.markdown("### Comparação Visual")
        fig = create_layer_comparison_chart(rap_assessment)
        st.plotly_chart(fig, use_container_width=True)


def render_layer_card(title: str, icon: str, assessment: Optional[LayerAssessment], color: str, description: str):
    """Render a card for a single layer assessment."""
    if assessment:
        score = assessment.score
        target = assessment.target_value
        actual = assessment.actual_value
        notes = assessment.notes or ""

        st.markdown(f"""
        <div class="sek-card" style="border-left: 4px solid {color};">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <span style="font-size: 0.875rem; color: #A0AEC0;">{title}</span>
            </div>
            <div style="font-size: 2.5rem; font-weight: 700; color: {color}; margin-bottom: 0.5rem;">
                {score:.1f}/10
            </div>
            <div style="color: #A0AEC0; font-size: 0.75rem; margin-bottom: 0.5rem;">
                {description}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if target is not None:
            st.caption(f"🎯 Target: {target}")
        if actual is not None:
            st.caption(f"📊 Actual: {actual}")
        if notes:
            with st.expander("Ver notas"):
                st.write(notes)
    else:
        st.markdown(f"""
        <div class="sek-card" style="border-left: 4px solid #30363D; opacity: 0.6;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <span style="font-size: 0.875rem; color: #A0AEC0;">{title}</span>
            </div>
            <div style="font-size: 1.5rem; color: #A0AEC0; margin-bottom: 0.5rem;">
                Não avaliado
            </div>
            <div style="color: #A0AEC0; font-size: 0.75rem;">
                {description}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_assessment_form():
    """Render form for creating new assessments."""
    st.markdown("### Nova Avaliação")

    with st.form("assessment_form"):
        # Metric selection
        metric_options = {f"{m.id}: {m.name}": m.id for m in METRICS.values()}
        selected_metric = st.selectbox(
            "Métrica RAP *",
            options=list(metric_options.keys()),
            help="Selecione a métrica a ser avaliada"
        )
        metric_id = metric_options[selected_metric]

        st.markdown("---")

        # Three columns for three layers
        st.markdown("### Avaliação por Camada")
        st.caption("Preencha as informações disponíveis para cada camada. Nem todas são obrigatórias.")

        col1, col2, col3 = st.columns(3)

        # Business Strategy
        with col1:
            st.markdown("#### 🎯 Business Strategy")
            bs_score = st.slider(
                "Score (0-10)",
                min_value=0.0,
                max_value=10.0,
                value=5.0,
                step=0.5,
                key="bs_score",
                help="Nível de definição do objetivo"
            )
            bs_target = st.number_input(
                "Valor Target",
                value=0.0,
                key="bs_target",
                help="Ex: RTO em horas, % máximo aceitável"
            )
            bs_notes = st.text_area(
                "Notas",
                key="bs_notes",
                placeholder="Contexto do objetivo de negócio...",
                height=100
            )
            bs_enabled = st.checkbox("Incluir Business Strategy", value=True, key="bs_enabled")

        # GRC
        with col2:
            st.markdown("#### 📋 Strategy & Risk Governance")
            grc_score = st.slider(
                "Score (0-10)",
                min_value=0.0,
                max_value=10.0,
                value=5.0,
                step=0.5,
                key="grc_score",
                help="Nível de maturidade de controles"
            )
            grc_evidence = st.text_input(
                "Evidências",
                key="grc_evidence",
                placeholder="Ex: Plano de DR v2.0, Política de Backup"
            )
            grc_notes = st.text_area(
                "Notas",
                key="grc_notes",
                placeholder="Descrição dos controles implementados...",
                height=100
            )
            grc_enabled = st.checkbox("Incluir GRC", value=True, key="grc_enabled")

        # Offensive Security
        with col3:
            st.markdown("#### 🔴 Offensive Security")
            os_score = st.slider(
                "Score (0-10)",
                min_value=0.0,
                max_value=10.0,
                value=5.0,
                step=0.5,
                key="os_score",
                help="Resultado real em testes"
            )
            os_actual = st.number_input(
                "Valor Real Medido",
                value=0.0,
                key="os_actual",
                help="Ex: Tempo real de recuperação, % de sucesso"
            )
            os_evidence = st.text_input(
                "Evidências",
                key="os_evidence",
                placeholder="Ex: Relatório de Pentest 2024-01"
            )
            os_notes = st.text_area(
                "Notas",
                key="os_notes",
                placeholder="Achados do teste...",
                height=100
            )
            os_enabled = st.checkbox("Incluir Offensive Security", value=True, key="os_enabled")

        st.markdown("---")

        submitted = st.form_submit_button("💾 Salvar Avaliação", type="primary", use_container_width=True)

        if submitted:
            # Create assessments
            bs_assessment = None
            grc_assessment = None
            os_assessment = None

            if bs_enabled:
                bs_assessment = LayerAssessment(
                    layer=AssessmentLayer.BUSINESS_STRATEGY,
                    metric_id=metric_id,
                    score=bs_score,
                    target_value=bs_target if bs_target > 0 else None,
                    notes=bs_notes if bs_notes else None,
                )

            if grc_enabled:
                grc_assessment = LayerAssessment(
                    layer=AssessmentLayer.STRATEGY_RISK_GOVERNANCE,
                    metric_id=metric_id,
                    score=grc_score,
                    evidence=grc_evidence if grc_evidence else None,
                    notes=grc_notes if grc_notes else None,
                )

            if os_enabled:
                os_assessment = LayerAssessment(
                    layer=AssessmentLayer.OFFENSIVE_SECURITY,
                    metric_id=metric_id,
                    score=os_score,
                    actual_value=os_actual if os_actual > 0 else None,
                    evidence=os_evidence if os_evidence else None,
                    notes=os_notes if os_notes else None,
                )

            # Create RAP Assessment
            rap_assessment = RAPAssessment(
                metric_id=metric_id,
                business_strategy=bs_assessment,
                strategy_risk_governance=grc_assessment,
                offensive_security=os_assessment,
            )

            # Save to session state
            st.session_state.assessments[metric_id] = rap_assessment

            st.success(f"✅ Avaliação para métrica {metric_id} salva com sucesso!")
            st.balloons()


def render_all_assessments():
    """Render list of all assessments."""
    assessments = st.session_state.get("assessments", {})

    if not assessments:
        st.info("Nenhuma avaliação cadastrada.")
        return

    st.markdown(f"### {len(assessments)} Avaliação(ões)")

    # Create summary table
    rows = []
    for metric_id, rap in assessments.items():
        metric = get_metric(metric_id)
        gap = calculate_gap_factor(rap)

        rows.append({
            "Métrica": f"{metric_id}: {metric.name if metric else 'Desconhecida'}",
            "Business Strategy": f"{rap.business_strategy.score:.1f}" if rap.business_strategy else "-",
            "GRC": f"{rap.strategy_risk_governance.score:.1f}" if rap.strategy_risk_governance else "-",
            "Offensive Security": f"{rap.offensive_security.score:.1f}" if rap.offensive_security else "-",
            "Gap Factor": gap,
            "Status": get_gap_interpretation(gap)[1],
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df.style.format({"Gap Factor": "{:.2f}"}).background_gradient(
            subset=["Gap Factor"],
            cmap="RdYlGn_r",
            vmin=0.5,
            vmax=2.0
        ),
        use_container_width=True,
        hide_index=True,
    )

    # Actions
    st.markdown("---")
    if st.button("🗑️ Limpar Todas Avaliações", type="secondary"):
        st.session_state.assessments = {}
        st.rerun()


def create_example_assessments():
    """Create example assessments for demonstration."""
    examples = [
        ("01", 8.0, 2.0, 7.0, 5.0, 4.0),  # metric_id, bs_score, bs_target, grc_score, os_score, os_actual
        ("07", 7.0, 5.0, 6.5, 4.0, 15.0),
        ("22", 8.0, None, 5.0, 4.5, 3.0),
    ]

    for metric_id, bs_score, bs_target, grc_score, os_score, os_actual in examples:
        bs = LayerAssessment(
            layer=AssessmentLayer.BUSINESS_STRATEGY,
            metric_id=metric_id,
            score=bs_score,
            target_value=bs_target,
            notes="Objetivo definido no BIA",
        )
        grc = LayerAssessment(
            layer=AssessmentLayer.STRATEGY_RISK_GOVERNANCE,
            metric_id=metric_id,
            score=grc_score,
            evidence="Documentação e controles",
        )
        os_sec = LayerAssessment(
            layer=AssessmentLayer.OFFENSIVE_SECURITY,
            metric_id=metric_id,
            score=os_score,
            actual_value=os_actual,
            evidence="Teste de simulação",
        )

        rap = RAPAssessment(
            metric_id=metric_id,
            business_strategy=bs,
            strategy_risk_governance=grc,
            offensive_security=os_sec,
        )
        st.session_state.assessments[metric_id] = rap


def create_gap_gauge(gap_factor: float) -> go.Figure:
    """Create a gauge chart for gap factor."""
    # Determine color based on gap
    if gap_factor < 0.7:
        color = SEK_COLORS["success"]
    elif gap_factor < 1.0:
        color = "#FFD93D"
    elif gap_factor < 1.3:
        color = SEK_COLORS["warning"]
    else:
        color = SEK_COLORS["danger"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=gap_factor,
        number={"suffix": "x", "font": {"color": "#FFFFFF"}},
        gauge={
            "axis": {"range": [0.5, 2.0], "tickcolor": "#A0AEC0"},
            "bar": {"color": color},
            "bgcolor": "#161B22",
            "borderwidth": 2,
            "bordercolor": "#30363D",
            "steps": [
                {"range": [0.5, 0.7], "color": "rgba(0, 212, 170, 0.3)"},
                {"range": [0.7, 1.0], "color": "rgba(255, 217, 61, 0.3)"},
                {"range": [1.0, 1.3], "color": "rgba(255, 167, 38, 0.3)"},
                {"range": [1.3, 2.0], "color": "rgba(255, 71, 87, 0.3)"},
            ],
            "threshold": {
                "line": {"color": "#FFFFFF", "width": 2},
                "thickness": 0.75,
                "value": gap_factor
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#FFFFFF"},
        height=200,
        margin=dict(t=20, b=20, l=20, r=20),
    )

    return fig


def create_layer_comparison_chart(rap_assessment: RAPAssessment) -> go.Figure:
    """Create a radar/bar chart comparing the three layers."""
    categories = ["Business Strategy", "GRC", "Offensive Security"]
    values = [
        rap_assessment.business_strategy.score if rap_assessment.business_strategy else 0,
        rap_assessment.strategy_risk_governance.score if rap_assessment.strategy_risk_governance else 0,
        rap_assessment.offensive_security.score if rap_assessment.offensive_security else 0,
    ]

    colors = [SEK_COLORS["accent"], SEK_COLORS["info"], SEK_COLORS["warning"]]

    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f"{v:.1f}" for v in values],
            textposition="outside",
        )
    ])

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FFFFFF",
        yaxis=dict(
            range=[0, 10],
            showgrid=True,
            gridcolor="rgba(48, 54, 61, 0.5)",
            title="Score",
        ),
        xaxis=dict(showgrid=False),
        height=300,
        margin=dict(t=40, b=40, l=40, r=40),
    )

    return fig


def get_gap_interpretation(gap_factor: float) -> tuple[str, str]:
    """Get CSS class and description for gap factor."""
    if gap_factor < 0.7:
        return "gap-low", "BAIXO"
    elif gap_factor < 1.0:
        return "gap-moderate", "MODERADO"
    elif gap_factor < 1.3:
        return "gap-elevated", "ELEVADO"
    elif gap_factor < 1.6:
        return "gap-high", "ALTO"
    else:
        return "gap-critical", "CRÍTICO"


def get_gap_recommendation(gap_factor: float) -> str:
    """Get recommendation based on gap factor."""
    if gap_factor < 0.7:
        return "Excelente! A realidade excede as expectativas. Considere documentar as práticas como referência."
    elif gap_factor < 1.0:
        return "Bom resultado. Pequenos ajustes podem alinhar completamente objetivo e realidade."
    elif gap_factor < 1.3:
        return "Gap moderado identificado. Revise controles e processos para aproximar a realidade do objetivo."
    elif gap_factor < 1.6:
        return "Gap significativo! Priorize ações de melhoria e acompanhe de perto a evolução."
    else:
        return "Gap crítico! Desvio maior requer atenção imediata. Reavalie objetivos e implemente correções urgentes."
