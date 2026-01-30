"""
Tests for the Monte Carlo simulation engine and analytics.
"""

import numpy as np
import pytest

from rap.core.model import (
    RiskScenario,
    FrequencyParams,
    ImpactParams,
    ControlEffect,
)
from rap.engine.monte_carlo import (
    simulate_scenario,
    simulate_scenario_from_params,
    simulate_scenarios,
    aggregate_results,
    calculate_expected_annual_loss,
    SimulationConfig,
    SimulationResult,
)
from rap.engine.analytics import (
    calculate_risk_metrics,
    calculate_loss_exceedance_curve,
    calculate_loss_at_exceedance,
    rank_scenarios,
    compare_scenarios,
    calculate_risk_reduction,
    RiskMetrics,
)


class TestSimulationConfig:
    """Tests for SimulationConfig."""

    def test_default_values(self):
        """Default config should have sensible values."""
        config = SimulationConfig()

        assert config.n_iterations == 10_000
        assert config.distribution == "pert"
        assert config.use_poisson_events is True

    def test_custom_values(self):
        """Custom config values should be preserved."""
        config = SimulationConfig(
            n_iterations=5000,
            random_seed=42,
            use_poisson_events=False,
        )

        assert config.n_iterations == 5000
        assert config.random_seed == 42
        assert config.use_poisson_events is False


class TestSimulateScenario:
    """Tests for simulate_scenario function."""

    @pytest.fixture
    def sample_scenario(self) -> RiskScenario:
        """Create a sample scenario for testing."""
        return RiskScenario(
            name="Test Ransomware",
            description="Test scenario",
            metric_id="01",
            dimension_id=1,
            asset="ERP",
            threat="Ransomware",
            frequency=FrequencyParams(0.1, 0.3, 0.7),
            impact=ImpactParams(100_000, 500_000, 3_000_000, "BRL"),
        )

    def test_returns_simulation_result(self, sample_scenario):
        """Should return a SimulationResult object."""
        config = SimulationConfig(n_iterations=1000, random_seed=42)
        result = simulate_scenario(sample_scenario, config)

        assert isinstance(result, SimulationResult)
        assert result.scenario_id == sample_scenario.scenario_id
        assert result.scenario_name == sample_scenario.name
        assert len(result.annual_losses) == 1000

    def test_losses_are_non_negative(self, sample_scenario):
        """All simulated losses should be non-negative."""
        config = SimulationConfig(n_iterations=1000, random_seed=42)
        result = simulate_scenario(sample_scenario, config)

        assert np.all(result.annual_losses >= 0)

    def test_mean_loss_reasonable(self, sample_scenario):
        """Mean loss should be in reasonable range."""
        config = SimulationConfig(n_iterations=10000, random_seed=42)
        result = simulate_scenario(sample_scenario, config)

        # Expected: freq_mean * impact_mean
        # freq_mean ~ (0.1 + 4*0.3 + 0.7) / 6 = 0.333
        # impact_mean ~ (100k + 4*500k + 3M) / 6 = 850k
        # Expected annual loss ~ 283k

        assert result.mean_loss > 0
        assert result.mean_loss < 5_000_000  # Should be less than max impact * max freq

    def test_reproducibility_with_seed(self, sample_scenario):
        """Same seed should produce same results."""
        config1 = SimulationConfig(n_iterations=100, random_seed=42)
        config2 = SimulationConfig(n_iterations=100, random_seed=42)

        result1 = simulate_scenario(sample_scenario, config1)
        result2 = simulate_scenario(sample_scenario, config2)

        np.testing.assert_array_equal(result1.annual_losses, result2.annual_losses)

    def test_zero_frequency_zero_loss(self):
        """If frequency is zero, expected loss should be near zero."""
        scenario = RiskScenario(
            name="Zero Frequency",
            description="Test",
            metric_id="01",
            dimension_id=1,
            asset="Test",
            threat="Test",
            frequency=FrequencyParams(0, 0, 0.01),  # Near zero
            impact=ImpactParams(100_000, 500_000, 1_000_000, "BRL"),
        )
        config = SimulationConfig(n_iterations=1000, random_seed=42)
        result = simulate_scenario(scenario, config)

        # With near-zero frequency, most years should have zero loss
        zero_loss_count = np.sum(result.annual_losses == 0)
        assert zero_loss_count > 900  # At least 90% should be zero

    def test_high_frequency_consistent_loss(self):
        """High frequency should result in consistent annual losses."""
        scenario = RiskScenario(
            name="High Frequency",
            description="Test",
            metric_id="01",
            dimension_id=1,
            asset="Test",
            threat="Test",
            frequency=FrequencyParams(5, 10, 15),  # Multiple events per year
            impact=ImpactParams(100_000, 100_000, 100_000, "BRL"),  # Fixed impact
        )
        config = SimulationConfig(n_iterations=1000, random_seed=42)
        result = simulate_scenario(scenario, config)

        # With ~10 events/year at 100k each, expected loss ~ 1M
        assert result.mean_loss > 500_000
        assert result.mean_loss < 2_000_000


class TestSimulateFromParams:
    """Tests for simulate_scenario_from_params function."""

    def test_returns_correct_result(self):
        """Should return proper SimulationResult."""
        freq = FrequencyParams(0.1, 0.3, 0.7)
        impact = ImpactParams(100_000, 500_000, 1_000_000, "USD")
        config = SimulationConfig(n_iterations=100, random_seed=42)

        result = simulate_scenario_from_params(
            freq, impact, "test_id", "Test Scenario", config
        )

        assert result.scenario_id == "test_id"
        assert result.scenario_name == "Test Scenario"
        assert result.currency == "USD"
        assert len(result.annual_losses) == 100


class TestSimulateScenarios:
    """Tests for simulate_scenarios function."""

    def test_simulates_multiple_scenarios(self):
        """Should simulate all scenarios in list."""
        scenarios = [
            RiskScenario(
                name=f"Scenario {i}",
                description="Test",
                metric_id="01",
                dimension_id=1,
                asset="Test",
                threat="Test",
                frequency=FrequencyParams(0.1 * i, 0.2 * i, 0.3 * i),
                impact=ImpactParams(100_000, 500_000, 1_000_000, "BRL"),
            )
            for i in range(1, 4)
        ]
        config = SimulationConfig(n_iterations=100, random_seed=42)

        results = simulate_scenarios(scenarios, config)

        assert len(results) == 3
        assert all(isinstance(r, SimulationResult) for r in results)


class TestAggregateResults:
    """Tests for aggregate_results function."""

    def test_aggregates_losses(self):
        """Should sum losses across scenarios."""
        # Create mock results
        result1 = SimulationResult(
            scenario_id="R1",
            scenario_name="Scenario 1",
            annual_losses=np.array([100, 200, 300]),
            n_iterations=3,
            currency="BRL",
        )
        result2 = SimulationResult(
            scenario_id="R2",
            scenario_name="Scenario 2",
            annual_losses=np.array([50, 50, 50]),
            n_iterations=3,
            currency="BRL",
        )

        aggregated = aggregate_results([result1, result2])

        expected = np.array([150, 250, 350])
        np.testing.assert_array_equal(aggregated.annual_losses, expected)

    def test_requires_same_iterations(self):
        """Should raise error if iteration counts differ."""
        result1 = SimulationResult(
            scenario_id="R1",
            scenario_name="Scenario 1",
            annual_losses=np.array([100, 200]),
            n_iterations=2,
            currency="BRL",
        )
        result2 = SimulationResult(
            scenario_id="R2",
            scenario_name="Scenario 2",
            annual_losses=np.array([50, 50, 50]),
            n_iterations=3,
            currency="BRL",
        )

        with pytest.raises(ValueError):
            aggregate_results([result1, result2])


class TestCalculateExpectedAnnualLoss:
    """Tests for calculate_expected_annual_loss function."""

    def test_calculation(self):
        """Should calculate E[freq] * E[impact]."""
        freq = FrequencyParams(0.1, 0.3, 0.7)  # E[freq] = (0.1 + 1.2 + 0.7) / 6 = 0.333
        impact = ImpactParams(100_000, 500_000, 1_000_000, "BRL")  # E[impact] = 566,667

        eal = calculate_expected_annual_loss(freq, impact)
        expected = freq.expected_value * impact.expected_value

        assert abs(eal - expected) < 0.01


class TestCalculateRiskMetrics:
    """Tests for calculate_risk_metrics function."""

    @pytest.fixture
    def sample_result(self) -> SimulationResult:
        """Create a sample simulation result."""
        np.random.seed(42)
        losses = np.random.lognormal(12, 1, 10000)  # Mean ~$200k

        return SimulationResult(
            scenario_id="R1",
            scenario_name="Test Scenario",
            annual_losses=losses,
            n_iterations=10000,
            currency="BRL",
        )

    def test_returns_risk_metrics(self, sample_result):
        """Should return RiskMetrics object."""
        metrics = calculate_risk_metrics(sample_result)

        assert isinstance(metrics, RiskMetrics)
        assert metrics.scenario_id == "R1"
        assert metrics.currency == "BRL"

    def test_mean_calculated_correctly(self, sample_result):
        """Mean should match numpy calculation."""
        metrics = calculate_risk_metrics(sample_result)
        expected_mean = np.mean(sample_result.annual_losses)

        assert abs(metrics.mean_loss - expected_mean) < 0.01

    def test_var_ordering(self, sample_result):
        """VaR values should increase with confidence level."""
        metrics = calculate_risk_metrics(sample_result)

        assert metrics.median_loss < metrics.var_90
        assert metrics.var_90 < metrics.var_95
        assert metrics.var_95 < metrics.var_99

    def test_probability_of_loss(self, sample_result):
        """Probability of loss should be calculated correctly."""
        metrics = calculate_risk_metrics(sample_result)

        expected_prob = np.mean(sample_result.annual_losses > 0)
        assert abs(metrics.probability_of_loss - expected_prob) < 0.01


class TestLossExceedanceCurve:
    """Tests for calculate_loss_exceedance_curve function."""

    def test_returns_points(self):
        """Should return list of LossExceedancePoint."""
        result = SimulationResult(
            scenario_id="R1",
            scenario_name="Test",
            annual_losses=np.array([100, 200, 300, 400, 500]),
            n_iterations=5,
            currency="BRL",
        )

        lec = calculate_loss_exceedance_curve(result, n_points=5)

        assert len(lec) == 5
        assert all(hasattr(p, "loss_value") and hasattr(p, "exceedance_probability") for p in lec)

    def test_exceedance_decreases_with_loss(self):
        """Higher loss values should have lower exceedance probability."""
        np.random.seed(42)
        result = SimulationResult(
            scenario_id="R1",
            scenario_name="Test",
            annual_losses=np.random.uniform(100, 1000, 1000),
            n_iterations=1000,
            currency="BRL",
        )

        lec = calculate_loss_exceedance_curve(result, n_points=10)

        for i in range(len(lec) - 1):
            if lec[i].loss_value < lec[i + 1].loss_value:
                assert lec[i].exceedance_probability >= lec[i + 1].exceedance_probability


class TestCalculateLossAtExceedance:
    """Tests for calculate_loss_at_exceedance function."""

    def test_exceedance_probability(self):
        """Should return correct loss at exceedance level."""
        result = SimulationResult(
            scenario_id="R1",
            scenario_name="Test",
            annual_losses=np.arange(1, 101),  # 1 to 100
            n_iterations=100,
            currency="BRL",
        )

        # 10% exceedance = 90th percentile
        loss = calculate_loss_at_exceedance(result, 0.10)
        expected = np.percentile(result.annual_losses, 90)

        assert abs(loss - expected) < 0.01

    def test_invalid_probability_raises_error(self):
        """Invalid probability should raise ValueError."""
        result = SimulationResult(
            scenario_id="R1",
            scenario_name="Test",
            annual_losses=np.array([100]),
            n_iterations=1,
            currency="BRL",
        )

        with pytest.raises(ValueError):
            calculate_loss_at_exceedance(result, -0.1)

        with pytest.raises(ValueError):
            calculate_loss_at_exceedance(result, 1.5)


class TestRankScenarios:
    """Tests for rank_scenarios function."""

    def test_ranks_by_mean_loss(self):
        """Should rank scenarios by specified metric."""
        results = [
            SimulationResult(
                scenario_id="R1",
                scenario_name="Low Risk",
                annual_losses=np.array([100] * 100),
                n_iterations=100,
                currency="BRL",
            ),
            SimulationResult(
                scenario_id="R2",
                scenario_name="High Risk",
                annual_losses=np.array([1000] * 100),
                n_iterations=100,
                currency="BRL",
            ),
            SimulationResult(
                scenario_id="R3",
                scenario_name="Medium Risk",
                annual_losses=np.array([500] * 100),
                n_iterations=100,
                currency="BRL",
            ),
        ]

        rankings = rank_scenarios(results, "mean_loss")

        assert rankings[0][0] == "R2"  # Highest risk first
        assert rankings[1][0] == "R3"
        assert rankings[2][0] == "R1"  # Lowest risk last


class TestControlEffect:
    """Tests for controls applied to scenarios."""

    def test_control_reduces_frequency(self):
        """Control with frequency reduction should lower expected loss."""
        scenario = RiskScenario(
            name="Test",
            description="Test",
            metric_id="01",
            dimension_id=1,
            asset="Test",
            threat="Test",
            frequency=FrequencyParams(1.0, 2.0, 3.0),
            impact=ImpactParams(100_000, 100_000, 100_000, "BRL"),
        )

        # Add control that reduces frequency by 50%
        scenario.controls.append(
            ControlEffect(
                name="Test Control",
                frequency_reduction=0.5,
                effectiveness=1.0,
            )
        )

        config = SimulationConfig(n_iterations=5000, random_seed=42)
        result = simulate_scenario(scenario, config)

        # Without control, expected loss ~ 2 * 100k = 200k
        # With 50% reduction, expected loss ~ 1 * 100k = 100k
        assert result.mean_loss < 150_000
