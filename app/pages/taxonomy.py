"""
Taxonomy viewer page for RAP Framework.
Browse the 7 dimensions and 25+ metrics.
"""

import streamlit as st

from rap.core.taxonomy import (
    DIMENSIONS,
    METRICS,
    get_dimension,
    get_metric,
    get_metrics_by_dimension,
    get_dimension_summary,
)
from app.components.charts import SEK_COLORS


def render_taxonomy():
    """Render the taxonomy viewer page."""
    st.markdown("# Taxonomia RAP")
    st.markdown("""
    O framework RAP organiza o risco cibernético em **7 Dimensões de Risco Digital**
    e **25+ Métricas de Resiliência**, alinhadas aos principais frameworks de mercado.
    """)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🗂️ Dimensões", "📏 Métricas", "📚 Referências"])

    with tab1:
        render_dimensions_view()

    with tab2:
        render_metrics_view()

    with tab3:
        render_references()


def render_dimensions_view():
    """Render the dimensions overview."""
    st.markdown("### As 7 Dimensões de Risco Digital")

    # Dimension colors
    dim_colors = {
        1: "#00D4AA",
        2: "#00B4D8",
        3: "#9B59B6",
        4: "#E74C3C",
        5: "#F39C12",
        6: "#1ABC9C",
        7: "#3498DB",
    }

    # Create grid of dimension cards
    for dim_id in range(1, 8, 2):
        col1, col2 = st.columns(2)

        with col1:
            dim = DIMENSIONS.get(dim_id)
            if dim:
                render_dimension_card(dim, dim_colors.get(dim_id, "#FFFFFF"))

        with col2:
            if dim_id + 1 <= 7:
                dim = DIMENSIONS.get(dim_id + 1)
                if dim:
                    render_dimension_card(dim, dim_colors.get(dim_id + 1, "#FFFFFF"))

    # Dimension summary table
    st.markdown("---")
    st.markdown("### Resumo das Dimensões")

    summary = get_dimension_summary()

    rows = []
    for dim_id, info in summary.items():
        dim = DIMENSIONS.get(dim_id)
        rows.append({
            "ID": f"D{dim_id}",
            "Nome": info["name"],
            "Nome (EN)": info["name_en"],
            "Métricas": info["metric_count"],
            "IDs das Métricas": ", ".join(info["metric_ids"]),
        })

    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_dimension_card(dim, color):
    """Render a single dimension card."""
    metrics = get_metrics_by_dimension(dim.id)

    st.markdown(f"""
    <div class="sek-card" style="border-left: 4px solid {color}; min-height: 200px;">
        <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
            <span style="background: {color}; color: #0A1628; padding: 0.25rem 0.75rem; border-radius: 4px; font-weight: 700; margin-right: 0.75rem;">
                D{dim.id}
            </span>
            <span style="color: #FFFFFF; font-weight: 600; font-size: 1rem;">
                {dim.name}
            </span>
        </div>
        <div style="color: #A0AEC0; font-size: 0.75rem; margin-bottom: 0.5rem;">
            {dim.name_en}
        </div>
        <div style="color: #FFFFFF; font-size: 0.875rem; margin-bottom: 0.75rem;">
            {dim.description[:150]}...
        </div>
        <div style="color: #A0AEC0; font-size: 0.75rem;">
            <strong>Frameworks:</strong> {', '.join(dim.frameworks[:3])}
        </div>
        <div style="color: {color}; font-size: 0.875rem; margin-top: 0.5rem;">
            <strong>{len(metrics)} métricas</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics_view():
    """Render the metrics browser."""
    st.markdown("### Navegador de Métricas")

    # Filter by dimension
    col1, col2 = st.columns([1, 3])

    with col1:
        dim_options = {f"D{d.id}: {d.name[:20]}...": d.id for d in DIMENSIONS.values()}
        dim_options = {"Todas as Dimensões": None, **dim_options}

        selected_dim = st.selectbox(
            "Filtrar por Dimensão:",
            options=list(dim_options.keys())
        )
        filter_dim = dim_options[selected_dim]

    with col2:
        search = st.text_input(
            "Buscar métrica:",
            placeholder="Digite para buscar por nome ou descrição..."
        )

    st.markdown("---")

    # Get metrics based on filter
    if filter_dim:
        metrics_list = get_metrics_by_dimension(filter_dim)
    else:
        metrics_list = list(METRICS.values())

    # Apply search filter
    if search:
        search_lower = search.lower()
        metrics_list = [
            m for m in metrics_list
            if search_lower in m.name.lower() or search_lower in m.description.lower()
        ]

    st.markdown(f"**{len(metrics_list)} métrica(s) encontrada(s)**")

    # Display metrics
    for metric in metrics_list:
        render_metric_card(metric)


def render_metric_card(metric):
    """Render a single metric card with expandable details."""
    dim = DIMENSIONS.get(metric.dimension_id)
    dim_name = dim.name if dim else "Desconhecida"

    # Color based on dimension
    dim_colors = {
        1: "#00D4AA", 2: "#00B4D8", 3: "#9B59B6",
        4: "#E74C3C", 5: "#F39C12", 6: "#1ABC9C", 7: "#3498DB"
    }
    color = dim_colors.get(metric.dimension_id, "#FFFFFF")

    with st.expander(f"**{metric.id}** - {metric.name}"):
        st.markdown(f"""
        <div style="padding: 0.5rem 0;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span style="background: {color}20; color: {color}; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; margin-right: 0.5rem;">
                    D{metric.dimension_id}: {dim_name[:20]}
                </span>
                <span style="background: {'#00D4AA' if metric.higher_is_better else '#FFA726'}20; color: {'#00D4AA' if metric.higher_is_better else '#FFA726'}; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem;">
                    {'↑ Maior = Melhor' if metric.higher_is_better else '↓ Menor = Melhor'}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**Descrição:** {metric.description}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Tipo de Medição:** {metric.measurement_type}")
            st.markdown(f"**Unidade:** {metric.target_unit}")

        with col2:
            if metric.frameworks:
                st.markdown(f"**Frameworks Relacionados:**")
                for fw in metric.frameworks:
                    st.markdown(f"- {fw}")


def render_references():
    """Render framework references."""
    st.markdown("### Frameworks e Referências")

    st.markdown("""
    O RAP foi projetado para **complementar** frameworks existentes,
    não para substituí-los. Abaixo estão os principais frameworks de referência:
    """)

    # Framework cards
    frameworks = [
        {
            "name": "Open FAIR",
            "description": "Factor Analysis of Information Risk - Metodologia de quantificação de risco que serve como base conceitual do RAP.",
            "url": "https://www.opengroup.org/forum/open-fair-forum",
            "use": "Modelo de frequência × impacto, distribuições PERT"
        },
        {
            "name": "NIST CSF",
            "description": "Cybersecurity Framework - Estrutura de funções de segurança (Identify, Protect, Detect, Respond, Recover).",
            "url": "https://www.nist.gov/cyberframework",
            "use": "Organização de controles, funções de segurança"
        },
        {
            "name": "ISO 27001",
            "description": "Sistema de Gestão de Segurança da Informação - Controles de segurança amplamente adotados.",
            "url": "https://www.iso.org/isoiec-27001-information-security.html",
            "use": "Anexo A como referência de controles"
        },
        {
            "name": "CIS Controls",
            "description": "Center for Internet Security Controls - Conjunto priorizado de ações de segurança.",
            "url": "https://www.cisecurity.org/controls",
            "use": "Controles técnicos específicos"
        },
        {
            "name": "MITRE ATT&CK",
            "description": "Base de conhecimento de táticas, técnicas e procedimentos adversários.",
            "url": "https://attack.mitre.org",
            "use": "Modelagem de ameaças, cenários de ataque"
        },
        {
            "name": "IEC 62443",
            "description": "Série de normas para segurança de sistemas de automação industrial e controle.",
            "url": "https://www.iec.ch",
            "use": "Dimensão 5 - Segurança OT/IoT/Industrial"
        },
    ]

    for fw in frameworks:
        st.markdown(f"""
        <div class="sek-card" style="margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="color: #00D4AA; font-weight: 600; font-size: 1.1rem;">{fw['name']}</div>
                    <div style="color: #FFFFFF; font-size: 0.875rem; margin: 0.5rem 0;">{fw['description']}</div>
                    <div style="color: #A0AEC0; font-size: 0.75rem;">
                        <strong>Uso no RAP:</strong> {fw['use']}
                    </div>
                </div>
                <a href="{fw['url']}" target="_blank" style="color: #00B4D8; text-decoration: none; font-size: 0.875rem;">
                    🔗 Link
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Tools reference
    st.markdown("### Ferramentas de Referência (Open Source)")

    tools = [
        {
            "name": "pyfair",
            "description": "Open Source FAIR Toolkit em Python",
            "url": "https://github.com/Hive-Systems/pyfair",
        },
        {
            "name": "riskquant",
            "description": "Biblioteca de quantificação de risco da Netflix",
            "url": "https://github.com/Netflix-Skunkworks/riskquant",
        },
        {
            "name": "evaluator",
            "description": "Quantified Risk Assessment Toolkit (R)",
            "url": "https://github.com/davidski/evaluator",
        },
    ]

    col1, col2, col3 = st.columns(3)

    for i, tool in enumerate(tools):
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <div class="sek-card" style="text-align: center; min-height: 120px;">
                <div style="color: #00D4AA; font-weight: 600;">{tool['name']}</div>
                <div style="color: #A0AEC0; font-size: 0.75rem; margin: 0.5rem 0;">{tool['description']}</div>
                <a href="{tool['url']}" target="_blank" style="color: #00B4D8; text-decoration: none; font-size: 0.75rem;">
                    GitHub →
                </a>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Bibliography
    st.markdown("### Bibliografia")

    st.markdown("""
    1. Freund, J., & Jones, J. (2015). *Measuring and Managing Information Risk: A FAIR Approach*. Butterworth-Heinemann.

    2. Hubbard, D. W. (2014). *How to Measure Anything in Cybersecurity Risk*. Wiley.

    3. The Open Group. (2017). *Open FAIR Risk Taxonomy (O-RT) Standard*.

    4. NIST. (2018). *Framework for Improving Critical Infrastructure Cybersecurity*.

    5. Gartner. (2023). *Digital Risk Management Framework*.
    """)
