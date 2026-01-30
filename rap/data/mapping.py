"""
Data mapping utilities for converting between formats.

This module provides functions for:
- Converting CSV rows to RiskScenario objects and parameters
- Converting scenarios to DataFrames for analysis
- Grouping assessments by metric for RAP analysis
"""

from typing import Optional, Union
import pandas as pd

from rap.core.model import (
    RiskScenario,
    FrequencyParams,
    ImpactParams,
    LayerAssessment,
    RAPAssessment,
    AssessmentLayer,
)
from rap.core.taxonomy import get_metric, get_dimension


def csv_row_to_frequency_params(
    row: Union[dict, pd.Series],
    prefix: str = "freq_",
) -> FrequencyParams:
    """
    Convert a CSV row or dict to FrequencyParams.

    Args:
        row: Dictionary or pandas Series with frequency columns.
        prefix: Column name prefix (default "freq_").

    Returns:
        FrequencyParams object.

    Example:
        >>> row = {"freq_min": 0.1, "freq_most": 0.3, "freq_max": 0.7}
        >>> params = csv_row_to_frequency_params(row)
    """
    return FrequencyParams(
        min_value=float(row[f"{prefix}min"]),
        most_likely=float(row[f"{prefix}most"]),
        max_value=float(row[f"{prefix}max"]),
        confidence=float(row.get(f"{prefix}confidence", 0.8)),
        notes=row.get(f"{prefix}notes"),
    )


def csv_row_to_impact_params(
    row: Union[dict, pd.Series],
    prefix: str = "impact_",
    default_currency: str = "BRL",
) -> ImpactParams:
    """
    Convert a CSV row or dict to ImpactParams.

    Args:
        row: Dictionary or pandas Series with impact columns.
        prefix: Column name prefix (default "impact_").
        default_currency: Default currency if not specified.

    Returns:
        ImpactParams object.

    Example:
        >>> row = {"impact_min": 100000, "impact_most": 500000, "impact_max": 3000000}
        >>> params = csv_row_to_impact_params(row)
    """
    return ImpactParams(
        min_value=float(row[f"{prefix}min"]),
        most_likely=float(row[f"{prefix}most"]),
        max_value=float(row[f"{prefix}max"]),
        currency=str(row.get("currency", default_currency)),
        confidence=float(row.get(f"{prefix}confidence", 0.8)),
        notes=row.get(f"{prefix}notes"),
    )


def csv_row_to_scenario(
    row: Union[dict, pd.Series],
    scenario_id: Optional[str] = None,
) -> RiskScenario:
    """
    Convert a CSV row or dict to a complete RiskScenario.

    Args:
        row: Dictionary or pandas Series with scenario data.
        scenario_id: Optional scenario ID override.

    Returns:
        RiskScenario object.

    Example:
        >>> row = {
        ...     "scenario_name": "Ransomware",
        ...     "metric_id": "01",
        ...     "dimension_id": 1,
        ...     "asset": "ERP",
        ...     "threat": "Ransomware",
        ...     "freq_min": 0.1, "freq_most": 0.3, "freq_max": 0.7,
        ...     "impact_min": 100000, "impact_most": 500000, "impact_max": 3000000,
        ... }
        >>> scenario = csv_row_to_scenario(row)
    """
    freq_params = csv_row_to_frequency_params(row)
    impact_params = csv_row_to_impact_params(row)

    return RiskScenario(
        scenario_id=scenario_id or str(row.get("scenario_id", "")),
        name=str(row["scenario_name"]),
        description=str(row.get("description", "")),
        metric_id=str(row.get("metric_id", "00")),
        dimension_id=int(row.get("dimension_id", 1)),
        asset=str(row.get("asset", "Unknown")),
        threat=str(row.get("threat", "Unknown")),
        frequency=freq_params,
        impact=impact_params,
    )


def scenarios_to_dataframe(scenarios: list[RiskScenario]) -> pd.DataFrame:
    """
    Convert a list of RiskScenario objects to a pandas DataFrame.

    Args:
        scenarios: List of RiskScenario objects.

    Returns:
        DataFrame with scenario data.

    Example:
        >>> df = scenarios_to_dataframe(scenarios)
        >>> df.to_csv("scenarios.csv", index=False)
    """
    rows = []
    for s in scenarios:
        rows.append({
            "scenario_id": s.scenario_id,
            "scenario_name": s.name,
            "description": s.description,
            "metric_id": s.metric_id,
            "dimension_id": s.dimension_id,
            "asset": s.asset,
            "threat": s.threat,
            "freq_min": s.frequency.min_value,
            "freq_most": s.frequency.most_likely,
            "freq_max": s.frequency.max_value,
            "freq_expected": s.frequency.expected_value,
            "impact_min": s.impact.min_value,
            "impact_most": s.impact.most_likely,
            "impact_max": s.impact.max_value,
            "impact_expected": s.impact.expected_value,
            "currency": s.impact.currency,
            "expected_annual_loss": s.get_expected_annual_loss(),
            "controls_count": len(s.controls),
        })
    return pd.DataFrame(rows)


def group_assessments_by_metric(
    assessments: list[LayerAssessment],
) -> dict[str, RAPAssessment]:
    """
    Group layer assessments by metric ID into RAPAssessment objects.

    Args:
        assessments: List of LayerAssessment objects from different layers.

    Returns:
        Dictionary mapping metric_id to RAPAssessment.

    Example:
        >>> assessments = read_assessments_csv("assessments.csv")
        >>> rap_assessments = group_assessments_by_metric(assessments)
        >>> for metric_id, rap in rap_assessments.items():
        ...     print(f"Metric {metric_id}: gap = {rap.calculate_gap():.2f}")
    """
    # Group by metric_id
    by_metric: dict[str, dict[AssessmentLayer, LayerAssessment]] = {}

    for assessment in assessments:
        metric_id = assessment.metric_id
        if metric_id not in by_metric:
            by_metric[metric_id] = {}
        by_metric[metric_id][assessment.layer] = assessment

    # Create RAPAssessment for each metric
    rap_assessments = {}
    for metric_id, layers in by_metric.items():
        rap_assessments[metric_id] = RAPAssessment(
            metric_id=metric_id,
            business_strategy=layers.get(AssessmentLayer.BUSINESS_STRATEGY),
            strategy_risk_governance=layers.get(AssessmentLayer.STRATEGY_RISK_GOVERNANCE),
            offensive_security=layers.get(AssessmentLayer.OFFENSIVE_SECURITY),
        )

    return rap_assessments


def enrich_scenarios_with_taxonomy(scenarios: list[RiskScenario]) -> list[dict]:
    """
    Enrich scenarios with taxonomy information (dimension names, metric details).

    Args:
        scenarios: List of RiskScenario objects.

    Returns:
        List of enriched dictionaries with taxonomy info.
    """
    enriched = []
    for s in scenarios:
        data = s.to_dict()

        # Add metric info
        metric = get_metric(s.metric_id)
        if metric:
            data["metric_name"] = metric.name
            data["metric_description"] = metric.description

        # Add dimension info
        dimension = get_dimension(s.dimension_id)
        if dimension:
            data["dimension_name"] = dimension.name
            data["dimension_name_en"] = dimension.name_en

        enriched.append(data)

    return enriched


def create_scenario_from_assessment(
    rap_assessment: RAPAssessment,
    asset: str,
    threat: str,
    base_impact: tuple[float, float, float] = (100_000, 500_000, 2_000_000),
    currency: str = "BRL",
) -> RiskScenario:
    """
    Create a RiskScenario from a RAP assessment using the layer mapper.

    This is useful when you have layer assessments and want to generate
    scenarios for simulation.

    Args:
        rap_assessment: Combined RAP assessment for a metric.
        asset: Asset at risk.
        threat: Threat actor/event.
        base_impact: Base (min, mode, max) impact values.
        currency: Currency for impact.

    Returns:
        RiskScenario with parameters derived from assessment.
    """
    from rap.core.mapping_layers import LayerMapper

    mapper = LayerMapper()
    freq_params, impact_params = mapper.map_assessment_to_params(
        rap_assessment, currency=currency
    )

    metric = get_metric(rap_assessment.metric_id)
    metric_name = metric.name if metric else f"Metric {rap_assessment.metric_id}"
    dimension_id = metric.dimension_id if metric else 1

    return RiskScenario(
        name=f"{threat} - {metric_name}",
        description=f"Scenario derived from RAP assessment for {metric_name}",
        metric_id=rap_assessment.metric_id,
        dimension_id=dimension_id,
        asset=asset,
        threat=threat,
        frequency=freq_params,
        impact=impact_params,
        rap_assessment=rap_assessment,
    )


def validate_scenario_data(row: Union[dict, pd.Series]) -> list[str]:
    """
    Validate scenario data for required fields and valid values.

    Args:
        row: Dictionary or pandas Series with scenario data.

    Returns:
        List of validation error messages (empty if valid).
    """
    errors = []

    # Required fields
    required = ["scenario_name", "freq_min", "freq_most", "freq_max",
                "impact_min", "impact_most", "impact_max"]

    for field in required:
        if field not in row or pd.isna(row[field]):
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors  # Can't validate values if fields are missing

    # Validate frequency order
    try:
        freq_min = float(row["freq_min"])
        freq_most = float(row["freq_most"])
        freq_max = float(row["freq_max"])

        if not (freq_min <= freq_most <= freq_max):
            errors.append(
                f"Invalid frequency order: min ({freq_min}) <= most ({freq_most}) <= max ({freq_max})"
            )
        if freq_min < 0:
            errors.append(f"Frequency min must be >= 0, got {freq_min}")
    except (ValueError, TypeError) as e:
        errors.append(f"Invalid frequency values: {e}")

    # Validate impact order
    try:
        impact_min = float(row["impact_min"])
        impact_most = float(row["impact_most"])
        impact_max = float(row["impact_max"])

        if not (impact_min <= impact_most <= impact_max):
            errors.append(
                f"Invalid impact order: min ({impact_min}) <= most ({impact_most}) <= max ({impact_max})"
            )
        if impact_min < 0:
            errors.append(f"Impact min must be >= 0, got {impact_min}")
    except (ValueError, TypeError) as e:
        errors.append(f"Invalid impact values: {e}")

    return errors
