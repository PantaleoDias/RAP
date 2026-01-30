"""
Monte Carlo simulation engine for risk quantification.

This module implements Monte Carlo simulation for calculating annual loss
distributions, following the FAIR methodology approach:

Annual Loss = Sum of (Event Frequency × Event Impact)

For each simulation iteration:
1. Sample annual frequency from PERT/triangular distribution
2. For each event in that year, sample impact from PERT/triangular
3. Sum all impacts to get annual loss for that iteration

After N iterations, we have a distribution of possible annual losses.

References:
- riskquant (Netflix): Simple frequency × impact Monte Carlo
- pyfair: Tree-based calculation with multiple nodes
- Open FAIR: Standard frequency × magnitude model
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np
from numpy.typing import NDArray

from rap.core.model import RiskScenario, FrequencyParams, ImpactParams
from rap.engine.distributions import sample_pert, sample_poisson


@dataclass
class SimulationConfig:
    """
    Configuration for Monte Carlo simulation.

    Attributes:
        n_iterations: Number of Monte Carlo iterations.
        distribution: Distribution type for sampling ("pert" or "triangular").
        frequency_lambd: Lambda parameter for PERT frequency distribution.
        impact_lambd: Lambda parameter for PERT impact distribution.
        random_seed: Random seed for reproducibility.
        use_poisson_events: Whether to model discrete events using Poisson.
    """

    n_iterations: int = 10_000
    distribution: str = "pert"
    frequency_lambd: float = 4.0
    impact_lambd: float = 4.0
    random_seed: Optional[int] = None
    use_poisson_events: bool = True


@dataclass
class SimulationResult:
    """
    Results from Monte Carlo simulation.

    Attributes:
        scenario_id: ID of the simulated scenario.
        scenario_name: Name of the scenario.
        annual_losses: Array of simulated annual losses.
        n_iterations: Number of iterations performed.
        currency: Currency of loss values.
        frequency_samples: Sampled frequencies (optional, for analysis).
        impact_samples: Sampled single-event impacts (optional).
    """

    scenario_id: str
    scenario_name: str
    annual_losses: NDArray[np.float64]
    n_iterations: int
    currency: str = "BRL"
    frequency_samples: Optional[NDArray[np.float64]] = None
    impact_samples: Optional[NDArray[np.float64]] = None
    metadata: dict = field(default_factory=dict)

    @property
    def mean_loss(self) -> float:
        """Calculate mean annual loss."""
        return float(np.mean(self.annual_losses))

    @property
    def median_loss(self) -> float:
        """Calculate median annual loss."""
        return float(np.median(self.annual_losses))

    @property
    def std_loss(self) -> float:
        """Calculate standard deviation of annual loss."""
        return float(np.std(self.annual_losses))

    @property
    def min_loss(self) -> float:
        """Minimum simulated annual loss."""
        return float(np.min(self.annual_losses))

    @property
    def max_loss(self) -> float:
        """Maximum simulated annual loss."""
        return float(np.max(self.annual_losses))

    def percentile(self, p: float) -> float:
        """Calculate a specific percentile of annual losses."""
        return float(np.percentile(self.annual_losses, p))

    def to_dict(self) -> dict:
        """Convert result to dictionary for serialization."""
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "n_iterations": self.n_iterations,
            "currency": self.currency,
            "mean_loss": self.mean_loss,
            "median_loss": self.median_loss,
            "std_loss": self.std_loss,
            "min_loss": self.min_loss,
            "max_loss": self.max_loss,
            "var_90": self.percentile(90),
            "var_95": self.percentile(95),
            "var_99": self.percentile(99),
            "metadata": self.metadata,
        }


def simulate_scenario(
    scenario: RiskScenario,
    config: Optional[SimulationConfig] = None,
) -> SimulationResult:
    """
    Run Monte Carlo simulation for a single risk scenario.

    This function simulates annual losses by:
    1. Sampling frequency (events per year) from PERT distribution
    2. For each event, sampling impact from PERT distribution
    3. Summing impacts to get annual loss
    4. Repeating for n_iterations

    Args:
        scenario: RiskScenario with frequency and impact parameters.
        config: Simulation configuration (uses defaults if not provided).

    Returns:
        SimulationResult with annual loss distribution.

    Example:
        >>> scenario = RiskScenario(
        ...     name="Ransomware",
        ...     description="Ransomware attack on ERP",
        ...     metric_id="01",
        ...     dimension_id=1,
        ...     asset="ERP",
        ...     threat="Ransomware",
        ...     frequency=FrequencyParams(0.1, 0.3, 0.7),
        ...     impact=ImpactParams(100_000, 500_000, 3_000_000, "BRL"),
        ... )
        >>> result = simulate_scenario(scenario)
        >>> print(f"Mean annual loss: {result.mean_loss:,.0f} BRL")
    """
    if config is None:
        config = SimulationConfig()

    # Get effective parameters (after applying controls)
    freq_params = scenario.get_effective_frequency()
    impact_params = scenario.get_effective_impact()

    # Run simulation
    annual_losses, freq_samples, impact_samples = _run_monte_carlo(
        freq_params=freq_params,
        impact_params=impact_params,
        n_iterations=config.n_iterations,
        distribution=config.distribution,
        frequency_lambd=config.frequency_lambd,
        impact_lambd=config.impact_lambd,
        random_seed=config.random_seed,
        use_poisson_events=config.use_poisson_events,
    )

    return SimulationResult(
        scenario_id=scenario.scenario_id,
        scenario_name=scenario.name,
        annual_losses=annual_losses,
        n_iterations=config.n_iterations,
        currency=impact_params.currency,
        frequency_samples=freq_samples,
        impact_samples=impact_samples,
        metadata={
            "metric_id": scenario.metric_id,
            "dimension_id": scenario.dimension_id,
            "asset": scenario.asset,
            "threat": scenario.threat,
            "controls_applied": len(scenario.controls),
        },
    )


def simulate_scenario_from_params(
    freq_params: FrequencyParams,
    impact_params: ImpactParams,
    scenario_id: str = "custom",
    scenario_name: str = "Custom Scenario",
    config: Optional[SimulationConfig] = None,
) -> SimulationResult:
    """
    Run Monte Carlo simulation from raw frequency and impact parameters.

    This is useful when you want to simulate without creating a full
    RiskScenario object.

    Args:
        freq_params: Frequency parameters.
        impact_params: Impact parameters.
        scenario_id: ID for the result.
        scenario_name: Name for the result.
        config: Simulation configuration.

    Returns:
        SimulationResult with annual loss distribution.
    """
    if config is None:
        config = SimulationConfig()

    annual_losses, freq_samples, impact_samples = _run_monte_carlo(
        freq_params=freq_params,
        impact_params=impact_params,
        n_iterations=config.n_iterations,
        distribution=config.distribution,
        frequency_lambd=config.frequency_lambd,
        impact_lambd=config.impact_lambd,
        random_seed=config.random_seed,
        use_poisson_events=config.use_poisson_events,
    )

    return SimulationResult(
        scenario_id=scenario_id,
        scenario_name=scenario_name,
        annual_losses=annual_losses,
        n_iterations=config.n_iterations,
        currency=impact_params.currency,
        frequency_samples=freq_samples,
        impact_samples=impact_samples,
    )


def simulate_scenarios(
    scenarios: list[RiskScenario],
    config: Optional[SimulationConfig] = None,
) -> list[SimulationResult]:
    """
    Run Monte Carlo simulation for multiple scenarios.

    Args:
        scenarios: List of RiskScenario objects.
        config: Simulation configuration (shared across all scenarios).

    Returns:
        List of SimulationResult objects.
    """
    return [simulate_scenario(scenario, config) for scenario in scenarios]


def _run_monte_carlo(
    freq_params: FrequencyParams,
    impact_params: ImpactParams,
    n_iterations: int,
    distribution: str,
    frequency_lambd: float,
    impact_lambd: float,
    random_seed: Optional[int],
    use_poisson_events: bool,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """
    Internal Monte Carlo simulation engine.

    Returns:
        Tuple of (annual_losses, frequency_samples, impact_samples).
    """
    rng = np.random.default_rng(random_seed)

    # Sample frequencies
    freq_samples = sample_pert(
        low=freq_params.min_value,
        mode=freq_params.most_likely,
        high=freq_params.max_value,
        size=n_iterations,
        lambd=frequency_lambd,
        random_state=rng,
    )

    # Sample single-event impacts (will be used multiple times per iteration)
    impact_samples = sample_pert(
        low=impact_params.min_value,
        mode=impact_params.most_likely,
        high=impact_params.max_value,
        size=n_iterations,
        lambd=impact_lambd,
        random_state=rng,
    )

    # Calculate annual losses
    annual_losses = np.zeros(n_iterations)

    if use_poisson_events:
        # Model discrete events: for each year, sample number of events
        # from Poisson with rate = sampled frequency
        for i in range(n_iterations):
            n_events = rng.poisson(freq_samples[i])
            if n_events > 0:
                # Sample impact for each event
                event_impacts = sample_pert(
                    low=impact_params.min_value,
                    mode=impact_params.most_likely,
                    high=impact_params.max_value,
                    size=n_events,
                    lambd=impact_lambd,
                    random_state=rng,
                )
                annual_losses[i] = np.sum(event_impacts)
    else:
        # Simple model: annual loss = frequency × single impact
        # This is a simplified approximation
        annual_losses = freq_samples * impact_samples

    return annual_losses, freq_samples, impact_samples


def aggregate_results(
    results: list[SimulationResult],
    correlation: float = 0.0,
) -> SimulationResult:
    """
    Aggregate multiple simulation results into a combined portfolio view.

    This sums the annual losses across all scenarios for each iteration,
    giving a distribution of total portfolio loss.

    Note: This assumes independence unless correlation is specified.

    Args:
        results: List of SimulationResult objects.
        correlation: Correlation between scenarios (0.0 = independent).
            Not implemented yet for correlated scenarios.

    Returns:
        Aggregated SimulationResult.
    """
    if not results:
        raise ValueError("At least one result required for aggregation")

    if correlation != 0.0:
        raise NotImplementedError("Correlated aggregation not yet implemented")

    # Ensure all results have the same number of iterations
    n_iterations = results[0].n_iterations
    if not all(r.n_iterations == n_iterations for r in results):
        raise ValueError("All results must have the same number of iterations")

    # Sum annual losses across scenarios
    total_losses = np.zeros(n_iterations)
    for result in results:
        total_losses += result.annual_losses

    # Determine currency (use first result's currency)
    currency = results[0].currency

    return SimulationResult(
        scenario_id="aggregated",
        scenario_name=f"Aggregated ({len(results)} scenarios)",
        annual_losses=total_losses,
        n_iterations=n_iterations,
        currency=currency,
        metadata={
            "aggregated_scenarios": [r.scenario_id for r in results],
            "scenario_count": len(results),
        },
    )


def calculate_expected_annual_loss(
    freq_params: FrequencyParams,
    impact_params: ImpactParams,
) -> float:
    """
    Calculate expected annual loss using analytical PERT means.

    This is a quick approximation without running full simulation.

    Args:
        freq_params: Frequency parameters.
        impact_params: Impact parameters.

    Returns:
        Expected annual loss (E[Frequency] × E[Impact]).
    """
    return freq_params.expected_value * impact_params.expected_value
