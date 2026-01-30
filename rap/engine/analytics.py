"""
Risk analytics and metrics calculation.

This module provides functions for calculating risk metrics from
Monte Carlo simulation results, including:

- Mean (expected) annual loss
- Median annual loss
- Value at Risk (VaR) at various confidence levels
- Loss Exceedance Curve (LEC) points
- Comparative risk rankings

These metrics follow FAIR methodology conventions and are commonly
used in risk reporting and decision-making.

References:
- riskquant (Netflix): Loss exceedance curves, scenario ranking
- Open FAIR: VaR and expected loss calculations
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from numpy.typing import NDArray

from rap.engine.monte_carlo import SimulationResult


@dataclass
class RiskMetrics:
    """
    Comprehensive risk metrics from simulation.

    Attributes:
        scenario_id: ID of the scenario.
        scenario_name: Name of the scenario.
        currency: Currency for monetary values.
        mean_loss: Expected (mean) annual loss.
        median_loss: Median annual loss.
        std_loss: Standard deviation of annual loss.
        min_loss: Minimum observed annual loss.
        max_loss: Maximum observed annual loss.
        var_90: Value at Risk at 90% confidence (90th percentile).
        var_95: Value at Risk at 95% confidence (95th percentile).
        var_99: Value at Risk at 99% confidence (99th percentile).
        iqr: Interquartile range (75th - 25th percentile).
        skewness: Skewness of the loss distribution.
        kurtosis: Kurtosis of the loss distribution.
        probability_of_loss: Probability of any loss occurring (loss > 0).
    """

    scenario_id: str
    scenario_name: str
    currency: str
    mean_loss: float
    median_loss: float
    std_loss: float
    min_loss: float
    max_loss: float
    var_90: float
    var_95: float
    var_99: float
    iqr: float
    skewness: float
    kurtosis: float
    probability_of_loss: float
    n_iterations: int

    def to_dict(self) -> dict:
        """Convert metrics to dictionary for serialization."""
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "currency": self.currency,
            "mean_loss": self.mean_loss,
            "median_loss": self.median_loss,
            "std_loss": self.std_loss,
            "min_loss": self.min_loss,
            "max_loss": self.max_loss,
            "var_90": self.var_90,
            "var_95": self.var_95,
            "var_99": self.var_99,
            "iqr": self.iqr,
            "skewness": self.skewness,
            "kurtosis": self.kurtosis,
            "probability_of_loss": self.probability_of_loss,
            "n_iterations": self.n_iterations,
        }

    def summary(self) -> str:
        """Generate human-readable summary of risk metrics."""
        return f"""
Risk Metrics: {self.scenario_name} ({self.scenario_id})
{'=' * 60}
Expected Annual Loss: {self.currency} {self.mean_loss:,.2f}
Median Annual Loss:   {self.currency} {self.median_loss:,.2f}
Standard Deviation:   {self.currency} {self.std_loss:,.2f}

Value at Risk (VaR):
  90th percentile: {self.currency} {self.var_90:,.2f}
  95th percentile: {self.currency} {self.var_95:,.2f}
  99th percentile: {self.currency} {self.var_99:,.2f}

Loss Range: {self.currency} {self.min_loss:,.2f} - {self.currency} {self.max_loss:,.2f}
Probability of Loss: {self.probability_of_loss:.1%}

Based on {self.n_iterations:,} Monte Carlo iterations
"""


@dataclass
class LossExceedancePoint:
    """
    A single point on the Loss Exceedance Curve.

    Attributes:
        loss_value: Loss amount.
        exceedance_probability: Probability that loss exceeds this value.
    """

    loss_value: float
    exceedance_probability: float


def calculate_risk_metrics(result: SimulationResult) -> RiskMetrics:
    """
    Calculate comprehensive risk metrics from simulation result.

    Args:
        result: SimulationResult from Monte Carlo simulation.

    Returns:
        RiskMetrics object with all calculated metrics.

    Example:
        >>> result = simulate_scenario(scenario)
        >>> metrics = calculate_risk_metrics(result)
        >>> print(f"VaR 95%: {metrics.var_95:,.0f} {metrics.currency}")
    """
    losses = result.annual_losses

    # Basic statistics
    mean_loss = float(np.mean(losses))
    median_loss = float(np.median(losses))
    std_loss = float(np.std(losses))
    min_loss = float(np.min(losses))
    max_loss = float(np.max(losses))

    # Value at Risk (percentiles)
    var_90 = float(np.percentile(losses, 90))
    var_95 = float(np.percentile(losses, 95))
    var_99 = float(np.percentile(losses, 99))

    # Interquartile range
    q25 = float(np.percentile(losses, 25))
    q75 = float(np.percentile(losses, 75))
    iqr = q75 - q25

    # Higher moments
    if std_loss > 0:
        skewness = float(_calculate_skewness(losses))
        kurtosis = float(_calculate_kurtosis(losses))
    else:
        skewness = 0.0
        kurtosis = 0.0

    # Probability of any loss
    probability_of_loss = float(np.mean(losses > 0))

    return RiskMetrics(
        scenario_id=result.scenario_id,
        scenario_name=result.scenario_name,
        currency=result.currency,
        mean_loss=mean_loss,
        median_loss=median_loss,
        std_loss=std_loss,
        min_loss=min_loss,
        max_loss=max_loss,
        var_90=var_90,
        var_95=var_95,
        var_99=var_99,
        iqr=iqr,
        skewness=skewness,
        kurtosis=kurtosis,
        probability_of_loss=probability_of_loss,
        n_iterations=result.n_iterations,
    )


def calculate_loss_exceedance_curve(
    result: SimulationResult,
    n_points: int = 100,
) -> list[LossExceedancePoint]:
    """
    Calculate the Loss Exceedance Curve (LEC).

    The LEC shows the probability that the annual loss will exceed
    a given value. It's useful for understanding tail risk.

    Args:
        result: SimulationResult from Monte Carlo simulation.
        n_points: Number of points on the curve.

    Returns:
        List of LossExceedancePoint objects.

    Example:
        >>> lec = calculate_loss_exceedance_curve(result)
        >>> # Find probability of loss > 1 million
        >>> for point in lec:
        ...     if point.loss_value >= 1_000_000:
        ...         print(f"P(Loss > 1M) = {point.exceedance_probability:.1%}")
        ...         break
    """
    losses = result.annual_losses
    sorted_losses = np.sort(losses)

    # Generate n_points evenly spaced through the loss distribution
    indices = np.linspace(0, len(sorted_losses) - 1, n_points, dtype=int)

    points = []
    for idx in indices:
        loss_value = sorted_losses[idx]
        # Exceedance probability: fraction of losses greater than this value
        exceedance_prob = 1.0 - (idx + 1) / len(sorted_losses)
        points.append(
            LossExceedancePoint(
                loss_value=float(loss_value),
                exceedance_probability=float(exceedance_prob),
            )
        )

    return points


def calculate_loss_at_exceedance(
    result: SimulationResult,
    exceedance_probability: float,
) -> float:
    """
    Calculate the loss value at a specific exceedance probability.

    Args:
        result: SimulationResult from Monte Carlo simulation.
        exceedance_probability: Target exceedance probability (0.0 to 1.0).
            E.g., 0.1 means "10% chance of exceeding this loss".

    Returns:
        Loss value at the specified exceedance probability.

    Example:
        >>> # What loss level has a 5% chance of being exceeded?
        >>> loss_at_5pct = calculate_loss_at_exceedance(result, 0.05)
    """
    if not (0.0 <= exceedance_probability <= 1.0):
        raise ValueError(f"Exceedance probability must be 0-1, got {exceedance_probability}")

    # Exceedance of X means percentile of (1 - X)
    percentile = (1.0 - exceedance_probability) * 100
    return float(np.percentile(result.annual_losses, percentile))


def rank_scenarios(
    results: list[SimulationResult],
    ranking_metric: str = "mean_loss",
) -> list[tuple[str, str, float]]:
    """
    Rank scenarios by a specified risk metric.

    Args:
        results: List of SimulationResult objects.
        ranking_metric: Metric to rank by. Options:
            - "mean_loss": Expected annual loss
            - "var_90", "var_95", "var_99": Value at Risk
            - "max_loss": Worst case loss

    Returns:
        List of (scenario_id, scenario_name, metric_value) tuples,
        sorted from highest to lowest risk.

    Example:
        >>> rankings = rank_scenarios(results, "var_95")
        >>> print("Top 3 riskiest scenarios:")
        >>> for id, name, var95 in rankings[:3]:
        ...     print(f"  {name}: VaR 95% = {var95:,.0f}")
    """
    valid_metrics = ["mean_loss", "var_90", "var_95", "var_99", "max_loss", "median_loss"]
    if ranking_metric not in valid_metrics:
        raise ValueError(f"Invalid ranking metric. Choose from: {valid_metrics}")

    rankings = []
    for result in results:
        metrics = calculate_risk_metrics(result)
        value = getattr(metrics, ranking_metric)
        rankings.append((result.scenario_id, result.scenario_name, value))

    # Sort by metric value, descending (highest risk first)
    rankings.sort(key=lambda x: x[2], reverse=True)
    return rankings


def compare_scenarios(
    result_a: SimulationResult,
    result_b: SimulationResult,
) -> dict:
    """
    Compare two scenarios across multiple metrics.

    Args:
        result_a: First simulation result.
        result_b: Second simulation result.

    Returns:
        Dictionary with comparison data.
    """
    metrics_a = calculate_risk_metrics(result_a)
    metrics_b = calculate_risk_metrics(result_b)

    comparison = {
        "scenario_a": {
            "id": result_a.scenario_id,
            "name": result_a.scenario_name,
        },
        "scenario_b": {
            "id": result_b.scenario_id,
            "name": result_b.scenario_name,
        },
        "metrics_comparison": {},
    }

    for metric in ["mean_loss", "median_loss", "var_90", "var_95", "var_99"]:
        val_a = getattr(metrics_a, metric)
        val_b = getattr(metrics_b, metric)
        diff = val_a - val_b
        pct_diff = (diff / val_b * 100) if val_b != 0 else 0

        comparison["metrics_comparison"][metric] = {
            "scenario_a": val_a,
            "scenario_b": val_b,
            "difference": diff,
            "percent_difference": pct_diff,
            "higher_risk": "a" if val_a > val_b else "b",
        }

    return comparison


def calculate_risk_reduction(
    baseline_result: SimulationResult,
    mitigated_result: SimulationResult,
) -> dict:
    """
    Calculate risk reduction achieved by controls/mitigations.

    Args:
        baseline_result: Result without mitigations.
        mitigated_result: Result with mitigations applied.

    Returns:
        Dictionary with risk reduction metrics.
    """
    baseline_metrics = calculate_risk_metrics(baseline_result)
    mitigated_metrics = calculate_risk_metrics(mitigated_result)

    reduction = {}
    for metric in ["mean_loss", "var_90", "var_95", "var_99"]:
        baseline_val = getattr(baseline_metrics, metric)
        mitigated_val = getattr(mitigated_metrics, metric)

        absolute_reduction = baseline_val - mitigated_val
        pct_reduction = (absolute_reduction / baseline_val * 100) if baseline_val > 0 else 0

        reduction[metric] = {
            "baseline": baseline_val,
            "mitigated": mitigated_val,
            "absolute_reduction": absolute_reduction,
            "percent_reduction": pct_reduction,
        }

    return {
        "baseline_scenario": baseline_result.scenario_id,
        "mitigated_scenario": mitigated_result.scenario_id,
        "currency": baseline_result.currency,
        "reductions": reduction,
    }


def _calculate_skewness(data: NDArray[np.float64]) -> float:
    """Calculate skewness of a distribution."""
    n = len(data)
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0.0
    return float(np.sum(((data - mean) / std) ** 3) / n)


def _calculate_kurtosis(data: NDArray[np.float64]) -> float:
    """Calculate excess kurtosis of a distribution."""
    n = len(data)
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0.0
    return float(np.sum(((data - mean) / std) ** 4) / n - 3)


def format_currency(value: float, currency: str = "BRL") -> str:
    """Format a currency value for display."""
    if currency == "BRL":
        return f"R$ {value:,.2f}"
    elif currency == "USD":
        return f"$ {value:,.2f}"
    elif currency == "EUR":
        return f"\u20ac {value:,.2f}"
    else:
        return f"{currency} {value:,.2f}"
