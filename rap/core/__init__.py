"""Core models and taxonomy for the RAP framework."""

from rap.core.model import (
    RiskScenario,
    FrequencyParams,
    ImpactParams,
    ControlEffect,
    LayerAssessment,
    RAPAssessment,
    AssessmentLayer,
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
from rap.core.mapping_layers import (
    LayerMapper,
    combine_layer_assessments,
    calculate_gap_factor,
)

__all__ = [
    "RiskScenario",
    "FrequencyParams",
    "ImpactParams",
    "ControlEffect",
    "LayerAssessment",
    "RAPAssessment",
    "AssessmentLayer",
    "RiskDimension",
    "RAPMetric",
    "DIMENSIONS",
    "METRICS",
    "get_dimension",
    "get_metric",
    "get_metrics_by_dimension",
    "LayerMapper",
    "combine_layer_assessments",
    "calculate_gap_factor",
]
