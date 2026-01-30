"""
RAP Taxonomy: 7 Digital Risk Dimensions and 25+ Resilience Metrics.

This module defines the RAP framework's taxonomy, aligned with industry
standards (Gartner, NIST, ISO 27001) and organized into 7 digital risk dimensions.

The taxonomy provides:
- Risk dimension definitions
- Metric definitions with IDs, names, and descriptions
- Lookup functions for dimensions and metrics
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RiskDimension:
    """
    A digital risk dimension in the RAP framework.

    Attributes:
        id: Unique dimension identifier (1-7).
        name: Dimension name.
        name_en: English name.
        description: Detailed description of the dimension.
        frameworks: Related compliance frameworks.
    """

    id: int
    name: str
    name_en: str
    description: str
    frameworks: tuple[str, ...]


@dataclass(frozen=True)
class RAPMetric:
    """
    A resilience metric in the RAP framework.

    Attributes:
        id: Unique metric identifier (01-25+).
        name: Metric name.
        description: Detailed description of what the metric measures.
        dimension_id: Associated risk dimension ID.
        measurement_type: How the metric is typically measured.
        target_unit: Unit of measurement for targets.
        higher_is_better: Whether higher scores indicate better resilience.
        frameworks: Related compliance framework controls.
    """

    id: str
    name: str
    description: str
    dimension_id: int
    measurement_type: str
    target_unit: str
    higher_is_better: bool = True
    frameworks: tuple[str, ...] = ()


# =============================================================================
# 7 DIGITAL RISK DIMENSIONS
# =============================================================================

DIMENSIONS: dict[int, RiskDimension] = {
    1: RiskDimension(
        id=1,
        name="Resiliência e Recuperação",
        name_en="Resilience and Recovery",
        description=(
            "Capacidade da organização de sobreviver, resistir e recuperar-se de "
            "incidentes cibernéticos, mantendo operações críticas e minimizando "
            "tempo de inatividade."
        ),
        frameworks=("ISO 22301", "NIST CSF Recover", "ISO 27001 A.17"),
    ),
    2: RiskDimension(
        id=2,
        name="Proteção de Identidade e Acesso",
        name_en="Identity and Access Protection",
        description=(
            "Controle rigoroso de identidades, credenciais e acessos privilegiados, "
            "prevenindo movimentação lateral e comprometimento de contas."
        ),
        frameworks=("NIST CSF Protect", "ISO 27001 A.9", "CIS Controls 5-6"),
    ),
    3: RiskDimension(
        id=3,
        name="Segurança de Aplicações e Infraestrutura",
        name_en="Application and Infrastructure Security",
        description=(
            "Hardening de sistemas, segurança em desenvolvimento, gestão de "
            "vulnerabilidades e postura de segurança em nuvem e on-premises."
        ),
        frameworks=("OWASP", "CIS Controls", "NIST SP 800-53", "ISO 27001 A.12-14"),
    ),
    4: RiskDimension(
        id=4,
        name="Proteção de Dados e Compliance",
        name_en="Data Protection and Compliance",
        description=(
            "Privacidade, classificação de dados, conformidade com LGPD/GDPR, "
            "prevenção de vazamentos e evidências de compliance."
        ),
        frameworks=("LGPD", "GDPR", "ISO 27701", "NIST Privacy Framework"),
    ),
    5: RiskDimension(
        id=5,
        name="Segurança OT/IoT/Industrial",
        name_en="OT/IoT/Industrial Security",
        description=(
            "Proteção de ambientes operacionais, sistemas industriais (ICS/SCADA), "
            "dispositivos IoT e convergência IT/OT."
        ),
        frameworks=("IEC 62443", "NIST SP 800-82", "NERC CIP"),
    ),
    6: RiskDimension(
        id=6,
        name="IA e Ameaças Emergentes",
        name_en="AI and Emerging Threats",
        description=(
            "Riscos relacionados à inteligência artificial, deepfakes, modelos de ML "
            "adversariais, e novas tecnologias emergentes."
        ),
        frameworks=("NIST AI RMF", "EU AI Act", "ISO/IEC 42001"),
    ),
    7: RiskDimension(
        id=7,
        name="Gestão de Riscos e Superfície",
        name_en="Risk and Attack Surface Management",
        description=(
            "Visibilidade da superfície de ataque, gestão de terceiros, cadeia de "
            "suprimentos, e alinhamento entre investimento e risco."
        ),
        frameworks=("NIST CSF Identify", "ISO 27001 A.15", "TPRM"),
    ),
}


# =============================================================================
# 25 RAP METRICS
# =============================================================================

METRICS: dict[str, RAPMetric] = {
    # Dimension 1: Resiliência e Recuperação
    "01": RAPMetric(
        id="01",
        name="Tempo de Recuperação de Joias da Coroa",
        description=(
            "Tempo real para recuperar sistemas críticos (joias da coroa) após um "
            "incidente grave. Compara RTO definido vs RTO real em testes."
        ),
        dimension_id=1,
        measurement_type="time_comparison",
        target_unit="hours",
        higher_is_better=False,
        frameworks=("ISO 22301", "NIST CSF RC.RP"),
    ),
    "10": RAPMetric(
        id="10",
        name="Soberania de Dados e Geo-redundância",
        description=(
            "Capacidade de manter dados e operações em múltiplas regiões geográficas, "
            "com controle sobre localização e jurisdição dos dados."
        ),
        dimension_id=1,
        measurement_type="capability_score",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("LGPD Art. 33", "GDPR Chapter V"),
    ),
    "25": RAPMetric(
        id="25",
        name="Gestão de Crises e Comunicação",
        description=(
            "Maturidade dos processos de gestão de crises, comunicação com stakeholders, "
            "e capacidade de resposta coordenada a incidentes."
        ),
        dimension_id=1,
        measurement_type="maturity_level",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("ISO 22301", "NIST CSF RC.CO"),
    ),
    # Dimension 2: Proteção de Identidade e Acesso
    "02": RAPMetric(
        id="02",
        name="Resistência a Movimentação Lateral",
        description=(
            "Capacidade de detectar e bloquear movimentação lateral de atacantes "
            "após compromisso inicial. Mede segmentação e monitoramento."
        ),
        dimension_id=2,
        measurement_type="test_result",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("MITRE ATT&CK TA0008", "CIS Control 13"),
    ),
    "03": RAPMetric(
        id="03",
        name="Proteção de Credenciais Privilegiadas",
        description=(
            "Nível de proteção de contas administrativas e de serviço, incluindo "
            "PAM, rotação de senhas e monitoramento de uso."
        ),
        dimension_id=2,
        measurement_type="control_effectiveness",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("CIS Control 5", "ISO 27001 A.9.2"),
    ),
    "04": RAPMetric(
        id="04",
        name="Maturidade de Zero Trust",
        description=(
            "Nível de implementação de arquitetura Zero Trust: verificação contínua, "
            "microsegmentação, acesso baseado em contexto."
        ),
        dimension_id=2,
        measurement_type="maturity_level",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("NIST SP 800-207", "Forrester ZTX"),
    ),
    "07": RAPMetric(
        id="07",
        name="Resiliência Humana (Phishing)",
        description=(
            "Taxa de sucesso de ataques de phishing simulados. Mede conscientização "
            "e capacidade dos usuários de identificar ameaças."
        ),
        dimension_id=2,
        measurement_type="percentage",
        target_unit="percent_failure",
        higher_is_better=False,
        frameworks=("CIS Control 14", "NIST CSF PR.AT"),
    ),
    # Dimension 3: Segurança de Aplicações e Infraestrutura
    "05": RAPMetric(
        id="05",
        name="Cobertura de Gestão de Vulnerabilidades",
        description=(
            "Percentual de ativos cobertos por scanning de vulnerabilidades e "
            "tempo médio de remediação de vulnerabilidades críticas."
        ),
        dimension_id=3,
        measurement_type="coverage_and_time",
        target_unit="percent_and_days",
        higher_is_better=True,
        frameworks=("CIS Control 7", "ISO 27001 A.12.6"),
    ),
    "06": RAPMetric(
        id="06",
        name="Postura de Segurança em Nuvem",
        description=(
            "Score de configuração segura em ambientes cloud (CSPM), incluindo "
            "IAM, storage, networking e compliance."
        ),
        dimension_id=3,
        measurement_type="cspm_score",
        target_unit="score_0_100",
        higher_is_better=True,
        frameworks=("CIS Benchmarks", "CSA CCM"),
    ),
    "08": RAPMetric(
        id="08",
        name="Segurança no Ciclo de Desenvolvimento",
        description=(
            "Maturidade de práticas DevSecOps: SAST, DAST, SCA, code review, "
            "segurança em pipelines CI/CD."
        ),
        dimension_id=3,
        measurement_type="maturity_level",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("OWASP SAMM", "BSIMM"),
    ),
    "09": RAPMetric(
        id="09",
        name="Efetividade de Detecção e Resposta",
        description=(
            "MTTD (Mean Time to Detect) e MTTR (Mean Time to Respond) para "
            "incidentes de segurança. Cobertura de EDR/XDR/SIEM."
        ),
        dimension_id=3,
        measurement_type="time_metrics",
        target_unit="hours",
        higher_is_better=False,
        frameworks=("NIST CSF DE/RS", "CIS Control 8"),
    ),
    # Dimension 4: Proteção de Dados e Compliance
    "11": RAPMetric(
        id="11",
        name="Classificação e Proteção de Dados",
        description=(
            "Nível de implementação de classificação de dados, DLP, criptografia "
            "e controles de acesso baseados em classificação."
        ),
        dimension_id=4,
        measurement_type="maturity_level",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("ISO 27001 A.8", "NIST SP 800-53 SC"),
    ),
    "12": RAPMetric(
        id="12",
        name="Prevenção de Vazamento de Dados",
        description=(
            "Efetividade de controles DLP em endpoints, rede e cloud. "
            "Histórico de incidentes de vazamento."
        ),
        dimension_id=4,
        measurement_type="control_effectiveness",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("CIS Control 3", "ISO 27001 A.13"),
    ),
    "18": RAPMetric(
        id="18",
        name="Conformidade GDPR/LGPD/Privacidade",
        description=(
            "Nível de conformidade com regulamentações de privacidade, incluindo "
            "gestão de consentimento, direitos dos titulares e RIPD."
        ),
        dimension_id=4,
        measurement_type="compliance_score",
        target_unit="percent",
        higher_is_better=True,
        frameworks=("LGPD", "GDPR", "ISO 27701"),
    ),
    # Dimension 5: Segurança OT/IoT/Industrial
    "13": RAPMetric(
        id="13",
        name="Segmentação IT/OT",
        description=(
            "Nível de segregação entre ambientes de TI e OT/ICS, incluindo "
            "DMZ industrial e controles de acesso."
        ),
        dimension_id=5,
        measurement_type="architecture_score",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("IEC 62443", "NIST SP 800-82"),
    ),
    "14": RAPMetric(
        id="14",
        name="Visibilidade de Ativos OT/IoT",
        description=(
            "Percentual de ativos OT/IoT inventariados, monitorados e com "
            "baseline de comportamento estabelecido."
        ),
        dimension_id=5,
        measurement_type="coverage",
        target_unit="percent",
        higher_is_better=True,
        frameworks=("CIS Control 1", "IEC 62443-2-1"),
    ),
    "15": RAPMetric(
        id="15",
        name="Resiliência de Sistemas Industriais",
        description=(
            "Capacidade de manter operações industriais críticas durante e "
            "após incidentes cibernéticos."
        ),
        dimension_id=5,
        measurement_type="capability_score",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("IEC 62443", "NERC CIP"),
    ),
    # Dimension 6: IA e Ameaças Emergentes
    "16": RAPMetric(
        id="16",
        name="Segurança de Modelos de IA/ML",
        description=(
            "Proteção de modelos de machine learning contra ataques adversariais, "
            "envenenamento de dados e extração de modelo."
        ),
        dimension_id=6,
        measurement_type="maturity_level",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("NIST AI RMF", "MITRE ATLAS"),
    ),
    "17": RAPMetric(
        id="17",
        name="Detecção de Deepfakes e Fraudes por IA",
        description=(
            "Capacidade de detectar e responder a ataques usando deepfakes, "
            "voz sintética e outras técnicas de IA generativa."
        ),
        dimension_id=6,
        measurement_type="capability_score",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("NIST AI RMF", "EU AI Act"),
    ),
    "19": RAPMetric(
        id="19",
        name="Governança de IA Responsável",
        description=(
            "Nível de implementação de governança de IA, incluindo ética, "
            "transparência, explicabilidade e controle humano."
        ),
        dimension_id=6,
        measurement_type="maturity_level",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("ISO/IEC 42001", "EU AI Act"),
    ),
    # Dimension 7: Gestão de Riscos e Superfície
    "20": RAPMetric(
        id="20",
        name="Visibilidade da Superfície de Ataque",
        description=(
            "Conhecimento e monitoramento contínuo da superfície de ataque externa, "
            "incluindo shadow IT, DNS, certificados e exposições."
        ),
        dimension_id=7,
        measurement_type="coverage",
        target_unit="percent",
        higher_is_better=True,
        frameworks=("CIS Control 1", "NIST CSF ID.AM"),
    ),
    "21": RAPMetric(
        id="21",
        name="Gestão de Riscos de Terceiros",
        description=(
            "Maturidade do programa de gestão de riscos de terceiros (TPRM), "
            "incluindo due diligence, monitoramento contínuo e cláusulas contratuais."
        ),
        dimension_id=7,
        measurement_type="maturity_level",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("ISO 27001 A.15", "NIST CSF ID.SC"),
    ),
    "22": RAPMetric(
        id="22",
        name="Segurança da Cadeia de Suprimentos",
        description=(
            "Proteção contra ataques à cadeia de suprimentos de software e "
            "hardware, incluindo SBOM e verificação de integridade."
        ),
        dimension_id=7,
        measurement_type="maturity_level",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("NIST SP 800-161", "SLSA"),
    ),
    "23": RAPMetric(
        id="23",
        name="Inteligência de Ameaças Operacional",
        description=(
            "Capacidade de coletar, analisar e operacionalizar inteligência de "
            "ameaças relevante para o contexto da organização."
        ),
        dimension_id=7,
        measurement_type="maturity_level",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("MITRE ATT&CK", "NIST CSF ID.RA"),
    ),
    "24": RAPMetric(
        id="24",
        name="Alinhamento Investimento x Risco (ROI/FAIR)",
        description=(
            "Capacidade de quantificar riscos e demonstrar ROI de investimentos "
            "em segurança usando metodologias como FAIR."
        ),
        dimension_id=7,
        measurement_type="maturity_level",
        target_unit="score_0_10",
        higher_is_better=True,
        frameworks=("Open FAIR", "NIST CSF ID.RM"),
    ),
}


# =============================================================================
# LOOKUP FUNCTIONS
# =============================================================================


def get_dimension(dimension_id: int) -> Optional[RiskDimension]:
    """
    Get a risk dimension by ID.

    Args:
        dimension_id: Dimension ID (1-7).

    Returns:
        RiskDimension if found, None otherwise.
    """
    return DIMENSIONS.get(dimension_id)


def get_metric(metric_id: str) -> Optional[RAPMetric]:
    """
    Get a RAP metric by ID.

    Args:
        metric_id: Metric ID (e.g., "01", "10", "25").

    Returns:
        RAPMetric if found, None otherwise.
    """
    return METRICS.get(metric_id)


def get_metrics_by_dimension(dimension_id: int) -> list[RAPMetric]:
    """
    Get all metrics for a specific dimension.

    Args:
        dimension_id: Dimension ID (1-7).

    Returns:
        List of RAPMetric objects for the dimension.
    """
    return [m for m in METRICS.values() if m.dimension_id == dimension_id]


def get_all_dimensions() -> list[RiskDimension]:
    """Get all risk dimensions."""
    return list(DIMENSIONS.values())


def get_all_metrics() -> list[RAPMetric]:
    """Get all RAP metrics."""
    return list(METRICS.values())


def get_dimension_summary() -> dict[int, dict]:
    """
    Get summary of all dimensions with their metrics.

    Returns:
        Dictionary mapping dimension ID to dimension info and metric count.
    """
    summary = {}
    for dim_id, dim in DIMENSIONS.items():
        metrics = get_metrics_by_dimension(dim_id)
        summary[dim_id] = {
            "name": dim.name,
            "name_en": dim.name_en,
            "metric_count": len(metrics),
            "metric_ids": [m.id for m in metrics],
        }
    return summary
