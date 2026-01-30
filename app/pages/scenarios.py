"""
Scenarios management page for RAP Framework.
Create, edit, import, and export risk scenarios.
"""

import streamlit as st
import pandas as pd
from io import StringIO
from typing import Optional

from rap.core.model import RiskScenario, FrequencyParams, ImpactParams
from rap.core.taxonomy import DIMENSIONS, METRICS, get_metrics_by_dimension
from rap.data.io import read_scenarios_csv, scenarios_to_csv


def render_scenarios():
    """Render the scenarios management page."""
    st.markdown("# Gestão de Cenários")
    st.markdown("Crie, edite e gerencie cenários de risco para simulação.")

    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["📋 Cenários", "➕ Novo Cenário", "📤 Importar/Exportar"])

    with tab1:
        render_scenarios_list()

    with tab2:
        render_scenario_form()

    with tab3:
        render_import_export()


def render_scenarios_list():
    """Render the list of existing scenarios."""
    scenarios = st.session_state.get("scenarios", [])

    if not scenarios:
        st.info("Nenhum cenário cadastrado. Crie um novo cenário ou importe de um CSV.")
        return

    st.markdown(f"### {len(scenarios)} Cenário(s) Cadastrado(s)")

    # Create dataframe for display
    df = pd.DataFrame([
        {
            "ID": s.scenario_id,
            "Nome": s.name,
            "Dimensão": f"D{s.dimension_id}",
            "Métrica": s.metric_id,
            "Ativo": s.asset,
            "Ameaça": s.threat,
            "Freq (min/ml/max)": f"{s.frequency.min_value:.2f} / {s.frequency.most_likely:.2f} / {s.frequency.max_value:.2f}",
            "Impacto (min/ml/max)": f"R$ {s.impact.min_value:,.0f} / R$ {s.impact.most_likely:,.0f} / R$ {s.impact.max_value:,.0f}",
            "EAL Estimado": f"R$ {s.get_expected_annual_loss():,.0f}",
        }
        for s in scenarios
    ])

    st.dataframe(df, use_container_width=True, hide_index=True)

    # Actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ Limpar Todos", type="secondary"):
            st.session_state.scenarios = []
            st.session_state.results = []
            st.rerun()

    with col2:
        # Select scenario to edit
        scenario_names = [f"{s.scenario_id}: {s.name}" for s in scenarios]
        selected = st.selectbox("Selecionar para editar:", [""] + scenario_names, key="edit_select")

        if selected:
            idx = scenario_names.index(selected)
            st.session_state.editing_scenario = idx

    with col3:
        if st.button("✏️ Editar Selecionado", disabled=not st.session_state.get("edit_select")):
            st.info("Função de edição em desenvolvimento.")

    # Delete individual scenarios
    st.markdown("---")
    st.markdown("#### Remover Cenário")

    col1, col2 = st.columns([3, 1])
    with col1:
        delete_select = st.selectbox(
            "Selecionar para remover:",
            [""] + scenario_names,
            key="delete_select"
        )
    with col2:
        if st.button("🗑️ Remover", disabled=not delete_select, type="secondary"):
            if delete_select:
                idx = scenario_names.index(delete_select)
                st.session_state.scenarios.pop(idx)
                # Also remove result if exists
                if idx < len(st.session_state.get("results", [])):
                    st.session_state.results.pop(idx)
                st.success(f"Cenário removido: {delete_select}")
                st.rerun()


def render_scenario_form(scenario: Optional[RiskScenario] = None):
    """Render form for creating/editing a scenario."""
    st.markdown("### Criar Novo Cenário")

    is_edit = scenario is not None

    with st.form("scenario_form"):
        # Basic info
        col1, col2 = st.columns(2)

        with col1:
            scenario_id = st.text_input(
                "ID do Cenário",
                value=scenario.scenario_id if is_edit else f"R{len(st.session_state.get('scenarios', [])) + 1:03d}",
                help="Identificador único do cenário"
            )
            name = st.text_input(
                "Nome do Cenário *",
                value=scenario.name if is_edit else "",
                placeholder="Ex: Ransomware no ERP"
            )
            description = st.text_area(
                "Descrição",
                value=scenario.description if is_edit else "",
                placeholder="Descreva o cenário de risco...",
                height=100
            )

        with col2:
            asset = st.text_input(
                "Ativo Afetado *",
                value=scenario.asset if is_edit else "",
                placeholder="Ex: Sistema ERP, Banco de Dados"
            )
            threat = st.text_input(
                "Tipo de Ameaça *",
                value=scenario.threat if is_edit else "",
                placeholder="Ex: Ransomware, Phishing, Insider"
            )

        st.markdown("---")

        # Dimension and Metric selection
        col1, col2 = st.columns(2)

        with col1:
            dimension_options = {f"D{d.id}: {d.name}": d.id for d in DIMENSIONS.values()}
            default_dim = f"D{scenario.dimension_id}: {DIMENSIONS[scenario.dimension_id].name}" if is_edit else list(dimension_options.keys())[0]

            selected_dim = st.selectbox(
                "Dimensão de Risco *",
                options=list(dimension_options.keys()),
                index=list(dimension_options.keys()).index(default_dim) if is_edit else 0,
                help="Selecione a dimensão de risco RAP"
            )
            dimension_id = dimension_options[selected_dim]

        with col2:
            # Filter metrics by dimension
            dim_metrics = get_metrics_by_dimension(dimension_id)
            metric_options = {f"{m.id}: {m.name}": m.id for m in dim_metrics}

            if metric_options:
                selected_metric = st.selectbox(
                    "Métrica RAP",
                    options=list(metric_options.keys()),
                    help="Selecione a métrica relacionada"
                )
                metric_id = metric_options[selected_metric]
            else:
                st.warning("Nenhuma métrica encontrada para esta dimensão.")
                metric_id = "00"

        st.markdown("---")
        st.markdown("### Parâmetros de Frequência (eventos/ano)")
        st.caption("Use distribuição PERT: mínimo ≤ mais provável ≤ máximo")

        col1, col2, col3 = st.columns(3)

        with col1:
            freq_min = st.number_input(
                "Frequência Mínima",
                min_value=0.0,
                max_value=100.0,
                value=scenario.frequency.min_value if is_edit else 0.1,
                step=0.1,
                format="%.2f",
                help="Estimativa otimista de eventos/ano"
            )

        with col2:
            freq_ml = st.number_input(
                "Frequência Mais Provável",
                min_value=0.0,
                max_value=100.0,
                value=scenario.frequency.most_likely if is_edit else 0.3,
                step=0.1,
                format="%.2f",
                help="Estimativa mais provável de eventos/ano"
            )

        with col3:
            freq_max = st.number_input(
                "Frequência Máxima",
                min_value=0.0,
                max_value=100.0,
                value=scenario.frequency.max_value if is_edit else 1.0,
                step=0.1,
                format="%.2f",
                help="Estimativa pessimista de eventos/ano"
            )

        # Validate frequency order
        if not (freq_min <= freq_ml <= freq_max):
            st.error("⚠️ Ordem inválida: mínimo ≤ mais provável ≤ máximo")

        st.markdown("---")
        st.markdown("### Parâmetros de Impacto (R$ por evento)")

        col1, col2, col3 = st.columns(3)

        with col1:
            impact_min = st.number_input(
                "Impacto Mínimo (R$)",
                min_value=0,
                max_value=1_000_000_000,
                value=int(scenario.impact.min_value) if is_edit else 50_000,
                step=10_000,
                help="Estimativa otimista de impacto financeiro"
            )

        with col2:
            impact_ml = st.number_input(
                "Impacto Mais Provável (R$)",
                min_value=0,
                max_value=1_000_000_000,
                value=int(scenario.impact.most_likely) if is_edit else 200_000,
                step=10_000,
                help="Estimativa mais provável de impacto"
            )

        with col3:
            impact_max = st.number_input(
                "Impacto Máximo (R$)",
                min_value=0,
                max_value=1_000_000_000,
                value=int(scenario.impact.max_value) if is_edit else 1_000_000,
                step=10_000,
                help="Estimativa pessimista de impacto"
            )

        # Validate impact order
        if not (impact_min <= impact_ml <= impact_max):
            st.error("⚠️ Ordem inválida: mínimo ≤ mais provável ≤ máximo")

        currency = st.selectbox("Moeda", ["BRL", "USD", "EUR"], index=0)

        st.markdown("---")

        # Preview
        if freq_min <= freq_ml <= freq_max and impact_min <= impact_ml <= impact_max:
            # Calculate expected values
            freq_expected = (freq_min + 4 * freq_ml + freq_max) / 6
            impact_expected = (impact_min + 4 * impact_ml + impact_max) / 6
            eal = freq_expected * impact_expected

            st.markdown("### Preview")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Frequência Esperada", f"{freq_expected:.2f} eventos/ano")
            with col2:
                st.metric("Impacto Esperado", f"R$ {impact_expected:,.0f}")
            with col3:
                st.metric("Exposição Anual Estimada", f"R$ {eal:,.0f}")

        # Submit button
        submitted = st.form_submit_button("💾 Salvar Cenário", type="primary", use_container_width=True)

        if submitted:
            # Validate
            if not name:
                st.error("Nome do cenário é obrigatório.")
            elif not asset:
                st.error("Ativo afetado é obrigatório.")
            elif not threat:
                st.error("Tipo de ameaça é obrigatório.")
            elif not (freq_min <= freq_ml <= freq_max):
                st.error("Parâmetros de frequência inválidos.")
            elif not (impact_min <= impact_ml <= impact_max):
                st.error("Parâmetros de impacto inválidos.")
            else:
                # Create scenario
                new_scenario = RiskScenario(
                    scenario_id=scenario_id,
                    name=name,
                    description=description,
                    metric_id=metric_id,
                    dimension_id=dimension_id,
                    asset=asset,
                    threat=threat,
                    frequency=FrequencyParams(freq_min, freq_ml, freq_max),
                    impact=ImpactParams(float(impact_min), float(impact_ml), float(impact_max), currency),
                )

                # Add to session state
                if "scenarios" not in st.session_state:
                    st.session_state.scenarios = []

                st.session_state.scenarios.append(new_scenario)
                # Clear results since scenarios changed
                st.session_state.results = []

                st.success(f"✅ Cenário '{name}' salvo com sucesso!")
                st.balloons()


def render_import_export():
    """Render import/export functionality."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📤 Importar CSV")
        st.caption("Importe cenários de um arquivo CSV no formato RAP.")

        uploaded_file = st.file_uploader(
            "Selecione o arquivo CSV",
            type=["csv"],
            help="O arquivo deve seguir o formato RAP de cenários"
        )

        if uploaded_file is not None:
            try:
                # Read CSV content
                content = StringIO(uploaded_file.getvalue().decode("utf-8"))
                df = pd.read_csv(content)

                st.markdown("#### Preview do arquivo:")
                st.dataframe(df.head(), use_container_width=True)

                st.markdown(f"**{len(df)} cenário(s) encontrado(s)**")

                if st.button("✅ Importar Cenários", type="primary"):
                    # Reset StringIO
                    content = StringIO(uploaded_file.getvalue().decode("utf-8"))

                    # Parse scenarios
                    imported = []
                    for idx, row in pd.read_csv(content).iterrows():
                        try:
                            scenario = RiskScenario(
                                scenario_id=str(row.get("scenario_id", f"R{idx:03d}")),
                                name=str(row["scenario_name"]),
                                description=str(row.get("description", "")),
                                metric_id=str(row.get("metric_id", "01")),
                                dimension_id=int(row.get("dimension_id", 1)),
                                asset=str(row.get("asset", "Unknown")),
                                threat=str(row.get("threat", "Unknown")),
                                frequency=FrequencyParams(
                                    float(row["freq_min"]),
                                    float(row["freq_most"]),
                                    float(row["freq_max"]),
                                ),
                                impact=ImpactParams(
                                    float(row["impact_min"]),
                                    float(row["impact_most"]),
                                    float(row["impact_max"]),
                                    str(row.get("currency", "BRL")),
                                ),
                            )
                            imported.append(scenario)
                        except Exception as e:
                            st.warning(f"Erro na linha {idx + 1}: {e}")

                    if imported:
                        st.session_state.scenarios = imported
                        st.session_state.results = []
                        st.success(f"✅ {len(imported)} cenário(s) importado(s) com sucesso!")
                        st.rerun()

            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")

        # Template download
        st.markdown("---")
        st.markdown("#### Download Template")

        template_csv = """scenario_id,scenario_name,metric_id,metric_name,dimension_id,asset,threat,description,freq_min,freq_most,freq_max,impact_min,impact_most,impact_max,currency
R001,Ransomware Attack on ERP,01,Tempo de Recuperacao,1,ERP System,Ransomware,Ransomware encrypts critical ERP database,0.1,0.3,0.7,100000,500000,3000000,BRL
R002,Data Breach via Phishing,07,Resiliencia Humana,2,Customer Database,Phishing,Employee compromised via spear phishing,0.2,0.5,1.5,50000,200000,1000000,BRL"""

        st.download_button(
            "📥 Download Template CSV",
            data=template_csv,
            file_name="rap_scenarios_template.csv",
            mime="text/csv",
        )

    with col2:
        st.markdown("### 📥 Exportar CSV")
        st.caption("Exporte os cenários atuais para um arquivo CSV.")

        scenarios = st.session_state.get("scenarios", [])

        if scenarios:
            # Create CSV content
            rows = []
            for s in scenarios:
                rows.append({
                    "scenario_id": s.scenario_id,
                    "scenario_name": s.name,
                    "metric_id": s.metric_id,
                    "dimension_id": s.dimension_id,
                    "asset": s.asset,
                    "threat": s.threat,
                    "description": s.description,
                    "freq_min": s.frequency.min_value,
                    "freq_most": s.frequency.most_likely,
                    "freq_max": s.frequency.max_value,
                    "impact_min": s.impact.min_value,
                    "impact_most": s.impact.most_likely,
                    "impact_max": s.impact.max_value,
                    "currency": s.impact.currency,
                })

            df = pd.DataFrame(rows)

            st.markdown("#### Preview:")
            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False)

            st.download_button(
                "📥 Download Cenários CSV",
                data=csv,
                file_name="rap_scenarios_export.csv",
                mime="text/csv",
                type="primary",
            )
        else:
            st.info("Nenhum cenário para exportar. Crie cenários primeiro.")
