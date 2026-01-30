"""
Data I/O utilities for reading and writing CSV files.

This module provides functions for:
- Reading scenario definitions from CSV files
- Writing simulation results to CSV files
- Reading layer assessments from CSV files

CSV Format for Scenarios:
    scenario_id,scenario_name,metric_id,metric_name,dimension,asset,threat,
    freq_min,freq_most,freq_max,impact_min,impact_most,impact_max,currency

CSV Format for Results:
    scenario_id,scenario_name,metric_id,mean_loss,median_loss,var_90,var_95,var_99,currency
"""

from pathlib import Path
from typing import Optional, Union
import csv

import pandas as pd

from rap.core.model import (
    RiskScenario,
    FrequencyParams,
    ImpactParams,
    LayerAssessment,
    AssessmentLayer,
)
from rap.engine.monte_carlo import SimulationResult
from rap.engine.analytics import RiskMetrics, calculate_risk_metrics


# Expected columns for scenario CSV
SCENARIO_COLUMNS = [
    "scenario_id",
    "scenario_name",
    "metric_id",
    "metric_name",
    "dimension_id",
    "asset",
    "threat",
    "description",
    "freq_min",
    "freq_most",
    "freq_max",
    "impact_min",
    "impact_most",
    "impact_max",
    "currency",
]

# Expected columns for results CSV
RESULT_COLUMNS = [
    "scenario_id",
    "scenario_name",
    "metric_id",
    "mean_loss",
    "median_loss",
    "var_90",
    "var_95",
    "var_99",
    "min_loss",
    "max_loss",
    "probability_of_loss",
    "currency",
    "n_iterations",
]

# Expected columns for assessment CSV
ASSESSMENT_COLUMNS = [
    "metric_id",
    "layer",
    "score",
    "target_value",
    "actual_value",
    "confidence",
    "evidence",
    "notes",
    "assessor",
    "assessment_date",
]


def read_scenarios_csv(
    filepath: Union[str, Path],
    encoding: str = "utf-8",
) -> list[RiskScenario]:
    """
    Read risk scenarios from a CSV file.

    Args:
        filepath: Path to the CSV file.
        encoding: File encoding (default UTF-8).

    Returns:
        List of RiskScenario objects.

    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If required columns are missing.

    Example:
        >>> scenarios = read_scenarios_csv("examples/ransomware.csv")
        >>> for s in scenarios:
        ...     print(f"{s.scenario_id}: {s.name}")
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Scenario file not found: {filepath}")

    df = pd.read_csv(filepath, encoding=encoding)

    # Check for required columns (minimal set)
    required = ["scenario_name", "freq_min", "freq_most", "freq_max",
                "impact_min", "impact_most", "impact_max"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    scenarios = []
    for idx, row in df.iterrows():
        scenario = _row_to_scenario(row, idx)
        scenarios.append(scenario)

    return scenarios


def _row_to_scenario(row: pd.Series, idx: int) -> RiskScenario:
    """Convert a DataFrame row to a RiskScenario object."""
    # Generate scenario_id if not provided
    scenario_id = str(row.get("scenario_id", f"S{idx:03d}"))

    # Get metric and dimension info
    metric_id = str(row.get("metric_id", "00"))
    dimension_id = int(row.get("dimension_id", 1))

    # Create FrequencyParams
    freq_params = FrequencyParams(
        min_value=float(row["freq_min"]),
        most_likely=float(row["freq_most"]),
        max_value=float(row["freq_max"]),
    )

    # Create ImpactParams
    impact_params = ImpactParams(
        min_value=float(row["impact_min"]),
        most_likely=float(row["impact_most"]),
        max_value=float(row["impact_max"]),
        currency=str(row.get("currency", "BRL")),
    )

    # Create RiskScenario
    return RiskScenario(
        scenario_id=scenario_id,
        name=str(row["scenario_name"]),
        description=str(row.get("description", "")),
        metric_id=metric_id,
        dimension_id=dimension_id,
        asset=str(row.get("asset", "Unknown")),
        threat=str(row.get("threat", "Unknown")),
        frequency=freq_params,
        impact=impact_params,
    )


def write_results_csv(
    results: list[SimulationResult],
    filepath: Union[str, Path],
    encoding: str = "utf-8",
) -> None:
    """
    Write simulation results to a CSV file.

    Args:
        results: List of SimulationResult objects.
        filepath: Path to the output CSV file.
        encoding: File encoding (default UTF-8).

    Example:
        >>> results = simulate_scenarios(scenarios)
        >>> write_results_csv(results, "output/results.csv")
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for result in results:
        metrics = calculate_risk_metrics(result)
        rows.append({
            "scenario_id": result.scenario_id,
            "scenario_name": result.scenario_name,
            "metric_id": result.metadata.get("metric_id", ""),
            "mean_loss": metrics.mean_loss,
            "median_loss": metrics.median_loss,
            "var_90": metrics.var_90,
            "var_95": metrics.var_95,
            "var_99": metrics.var_99,
            "min_loss": metrics.min_loss,
            "max_loss": metrics.max_loss,
            "probability_of_loss": metrics.probability_of_loss,
            "currency": result.currency,
            "n_iterations": result.n_iterations,
        })

    df = pd.DataFrame(rows, columns=RESULT_COLUMNS)
    df.to_csv(filepath, index=False, encoding=encoding)


def write_metrics_csv(
    metrics_list: list[RiskMetrics],
    filepath: Union[str, Path],
    encoding: str = "utf-8",
) -> None:
    """
    Write risk metrics directly to a CSV file.

    Args:
        metrics_list: List of RiskMetrics objects.
        filepath: Path to the output CSV file.
        encoding: File encoding (default UTF-8).
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    rows = [m.to_dict() for m in metrics_list]
    df = pd.DataFrame(rows)
    df.to_csv(filepath, index=False, encoding=encoding)


def read_assessments_csv(
    filepath: Union[str, Path],
    encoding: str = "utf-8",
) -> list[LayerAssessment]:
    """
    Read layer assessments from a CSV file.

    Args:
        filepath: Path to the CSV file.
        encoding: File encoding.

    Returns:
        List of LayerAssessment objects.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Assessment file not found: {filepath}")

    df = pd.read_csv(filepath, encoding=encoding)

    # Check for required columns
    required = ["metric_id", "layer", "score"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    assessments = []
    for _, row in df.iterrows():
        assessment = _row_to_assessment(row)
        assessments.append(assessment)

    return assessments


def _row_to_assessment(row: pd.Series) -> LayerAssessment:
    """Convert a DataFrame row to a LayerAssessment object."""
    # Map layer string to enum
    layer_map = {
        "business_strategy": AssessmentLayer.BUSINESS_STRATEGY,
        "strategy_risk_governance": AssessmentLayer.STRATEGY_RISK_GOVERNANCE,
        "grc": AssessmentLayer.STRATEGY_RISK_GOVERNANCE,
        "offensive_security": AssessmentLayer.OFFENSIVE_SECURITY,
        "red_team": AssessmentLayer.OFFENSIVE_SECURITY,
    }

    layer_str = str(row["layer"]).lower().strip()
    if layer_str not in layer_map:
        raise ValueError(f"Unknown layer: {row['layer']}. Valid: {list(layer_map.keys())}")

    return LayerAssessment(
        layer=layer_map[layer_str],
        metric_id=str(row["metric_id"]),
        score=float(row["score"]),
        target_value=float(row["target_value"]) if pd.notna(row.get("target_value")) else None,
        actual_value=float(row["actual_value"]) if pd.notna(row.get("actual_value")) else None,
        confidence=float(row.get("confidence", 0.8)),
        evidence=str(row.get("evidence", "")) if pd.notna(row.get("evidence")) else None,
        notes=str(row.get("notes", "")) if pd.notna(row.get("notes")) else None,
        assessor=str(row.get("assessor", "")) if pd.notna(row.get("assessor")) else None,
        assessment_date=str(row.get("assessment_date", "")) if pd.notna(row.get("assessment_date")) else None,
    )


def scenarios_to_csv(
    scenarios: list[RiskScenario],
    filepath: Union[str, Path],
    encoding: str = "utf-8",
) -> None:
    """
    Export scenarios to a CSV file (useful for creating templates).

    Args:
        scenarios: List of RiskScenario objects.
        filepath: Path to the output CSV file.
        encoding: File encoding.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for s in scenarios:
        rows.append({
            "scenario_id": s.scenario_id,
            "scenario_name": s.name,
            "metric_id": s.metric_id,
            "metric_name": "",  # Filled in later if needed
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

    df = pd.DataFrame(rows, columns=SCENARIO_COLUMNS)
    df.to_csv(filepath, index=False, encoding=encoding)


def create_scenario_template(
    filepath: Union[str, Path],
    n_examples: int = 3,
) -> None:
    """
    Create a template CSV file with example scenarios.

    Args:
        filepath: Path to the template file.
        n_examples: Number of example rows to include.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    examples = [
        {
            "scenario_id": "R001",
            "scenario_name": "Ransomware Attack on ERP",
            "metric_id": "01",
            "metric_name": "Tempo de Recuperacao Joias da Coroa",
            "dimension_id": 1,
            "asset": "ERP System",
            "threat": "Ransomware",
            "description": "Ransomware encrypts critical ERP database",
            "freq_min": 0.1,
            "freq_most": 0.3,
            "freq_max": 0.7,
            "impact_min": 100000,
            "impact_most": 500000,
            "impact_max": 3000000,
            "currency": "BRL",
        },
        {
            "scenario_id": "R002",
            "scenario_name": "Data Breach via Phishing",
            "metric_id": "07",
            "metric_name": "Resiliencia Humana (Phishing)",
            "dimension_id": 2,
            "asset": "Customer Database",
            "threat": "Phishing/Social Engineering",
            "description": "Employee compromised via spear phishing leads to data exfiltration",
            "freq_min": 0.2,
            "freq_most": 0.5,
            "freq_max": 1.5,
            "impact_min": 50000,
            "impact_most": 200000,
            "impact_max": 1000000,
            "currency": "BRL",
        },
        {
            "scenario_id": "R003",
            "scenario_name": "Supply Chain Compromise",
            "metric_id": "22",
            "metric_name": "Seguranca da Cadeia de Suprimentos",
            "dimension_id": 7,
            "asset": "Software Dependencies",
            "threat": "Supply Chain Attack",
            "description": "Malicious code introduced via compromised dependency",
            "freq_min": 0.05,
            "freq_most": 0.15,
            "freq_max": 0.4,
            "impact_min": 200000,
            "impact_most": 800000,
            "impact_max": 5000000,
            "currency": "BRL",
        },
    ]

    df = pd.DataFrame(examples[:n_examples], columns=SCENARIO_COLUMNS)
    df.to_csv(filepath, index=False)


def create_assessment_template(
    filepath: Union[str, Path],
) -> None:
    """
    Create a template CSV file for layer assessments.

    Args:
        filepath: Path to the template file.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    examples = [
        {
            "metric_id": "01",
            "layer": "business_strategy",
            "score": 8.0,
            "target_value": 2.0,
            "actual_value": "",
            "confidence": 0.9,
            "evidence": "BIA document v2.3",
            "notes": "RTO target for ERP: 2 hours",
            "assessor": "CISO",
            "assessment_date": "2024-01-15",
        },
        {
            "metric_id": "01",
            "layer": "strategy_risk_governance",
            "score": 7.0,
            "target_value": "",
            "actual_value": "",
            "confidence": 0.8,
            "evidence": "DR Plan, Backup Policy",
            "notes": "DR procedures documented and tested quarterly",
            "assessor": "GRC Team",
            "assessment_date": "2024-01-20",
        },
        {
            "metric_id": "01",
            "layer": "offensive_security",
            "score": 5.0,
            "target_value": "",
            "actual_value": 4.0,
            "confidence": 0.95,
            "evidence": "Ransomware simulation report 2024-01",
            "notes": "Actual recovery took 4 hours vs 2 hour target",
            "assessor": "Red Team",
            "assessment_date": "2024-01-25",
        },
    ]

    df = pd.DataFrame(examples, columns=ASSESSMENT_COLUMNS)
    df.to_csv(filepath, index=False)
