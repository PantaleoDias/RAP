"""
RAP - Resilience Acceleration Program

A risk quantification framework for cybersecurity resilience,
inspired by FAIR/Open FAIR methodology.

The RAP framework connects three work fronts:
- Business Strategy (Security Advisory)
- Strategy & Risk Governance (GRC)
- Offensive Security (Red Team)

Using 7 digital risk dimensions and 25+ resilience metrics.
"""

from rap.core.model import (
    RiskScenario,
    FrequencyParams,
    ImpactParams,
    ControlEffect,
    LayerAssessment,
    RAPAssessment,
)
from rap.core.taxonomy import (
    RiskDimension,
    RAPMetric,
    DIMENSIONS,
    METRICS,
    get_dimension,
    get_metric,
    get_metrics_by_dimension,
)
from rap.engine.monte_carlo import simulate_scenario, simulate_scenarios
from rap.engine.analytics import calculate_risk_metrics, RiskMetrics

__version__ = "0.1.0"
__all__ = [
    # Core models
    "RiskScenario",
    "FrequencyParams",
    "ImpactParams",
    "ControlEffect",
    "LayerAssessment",
    "RAPAssessment",
    # Taxonomy
    "RiskDimension",
    "RAPMetric",
    "DIMENSIONS",
    "METRICS",
    "get_dimension",
    "get_metric",
    "get_metrics_by_dimension",
    # Engine
    "simulate_scenario",
    "simulate_scenarios",
    "calculate_risk_metrics",
    "RiskMetrics",
]
