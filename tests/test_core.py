"""
Tests for the core models and taxonomy.
"""

import pytest

from rap.core.model import (
    FrequencyParams,
    ImpactParams,
    ControlEffect,
    LayerAssessment,
    RAPAssessment,
    RiskScenario,
    AssessmentLayer,
)
from rap.core.taxonomy import (
    DIMENSIONS,
    METRICS,
    get_dimension,
    get_metric,
    get_metrics_by_dimension,
    get_all_dimensions,
    get_all_metrics,
    get_dimension_summary,
)
from rap.core.mapping_layers import (
    LayerMapper,
    LayerWeights,
    calculate_gap_factor,
    combine_layer_assessments,
    create_pla_view,
)


class TestFrequencyParams:
    """Tests for FrequencyParams class."""

    def test_valid_params(self):
        """Valid parameters should create object."""
        params = FrequencyParams(0.1, 0.3, 0.7)
        assert params.min_value == 0.1
        assert params.most_likely == 0.3
        assert params.max_value == 0.7

    def test_expected_value(self):
        """Expected value should follow PERT formula."""
        params = FrequencyParams(0.1, 0.3, 0.7)
        expected = (0.1 + 4 * 0.3 + 0.7) / 6
        assert abs(params.expected_value - expected) < 0.001

    def test_invalid_order_raises_error(self):
        """Invalid parameter order should raise ValueError."""
        with pytest.raises(ValueError):
            FrequencyParams(0.5, 0.3, 0.7)  # min > most_likely

        with pytest.raises(ValueError):
            FrequencyParams(0.1, 0.8, 0.7)  # most_likely > max

    def test_invalid_confidence_raises_error(self):
        """Confidence outside [0, 1] should raise ValueError."""
        with pytest.raises(ValueError):
            FrequencyParams(0.1, 0.3, 0.7, confidence=1.5)


class TestImpactParams:
    """Tests for ImpactParams class."""

    def test_valid_params(self):
        """Valid parameters should create object."""
        params = ImpactParams(100_000, 500_000, 3_000_000, "BRL")
        assert params.min_value == 100_000
        assert params.most_likely == 500_000
        assert params.max_value == 3_000_000
        assert params.currency == "BRL"

    def test_expected_value(self):
        """Expected value should follow PERT formula."""
        params = ImpactParams(100_000, 500_000, 3_000_000, "BRL")
        expected = (100_000 + 4 * 500_000 + 3_000_000) / 6
        assert abs(params.expected_value - expected) < 1


class TestControlEffect:
    """Tests for ControlEffect class."""

    def test_apply_to_frequency(self):
        """Should reduce frequency parameters."""
        freq = FrequencyParams(1.0, 2.0, 3.0)
        control = ControlEffect(
            name="Test Control",
            frequency_reduction=0.5,
            effectiveness=1.0,
        )

        reduced = control.apply_to_frequency(freq)

        assert reduced.min_value == 0.5
        assert reduced.most_likely == 1.0
        assert reduced.max_value == 1.5

    def test_apply_to_impact(self):
        """Should reduce impact parameters."""
        impact = ImpactParams(100_000, 200_000, 300_000, "BRL")
        control = ControlEffect(
            name="Test Control",
            impact_reduction=0.5,
            effectiveness=1.0,
        )

        reduced = control.apply_to_impact(impact)

        assert reduced.min_value == 50_000
        assert reduced.most_likely == 100_000
        assert reduced.max_value == 150_000

    def test_effectiveness_factor(self):
        """Effectiveness should scale the reduction."""
        freq = FrequencyParams(1.0, 2.0, 3.0)
        control = ControlEffect(
            name="Test Control",
            frequency_reduction=0.5,
            effectiveness=0.5,  # Only 50% effective
        )

        reduced = control.apply_to_frequency(freq)

        # With 50% effectiveness, reduction is 0.5 * 0.5 = 0.25
        # So factor is 1 - 0.25 = 0.75
        assert reduced.min_value == 0.75
        assert reduced.most_likely == 1.5
        assert reduced.max_value == 2.25


class TestLayerAssessment:
    """Tests for LayerAssessment class."""

    def test_valid_assessment(self):
        """Valid assessment should create object."""
        assessment = LayerAssessment(
            layer=AssessmentLayer.BUSINESS_STRATEGY,
            metric_id="01",
            score=8.0,
            target_value=2.0,
        )
        assert assessment.score == 8.0
        assert assessment.target_value == 2.0

    def test_invalid_score_raises_error(self):
        """Score outside [0, 10] should raise ValueError."""
        with pytest.raises(ValueError):
            LayerAssessment(
                layer=AssessmentLayer.BUSINESS_STRATEGY,
                metric_id="01",
                score=11.0,
            )


class TestRAPAssessment:
    """Tests for RAPAssessment class."""

    def test_calculate_gap_no_assessments(self):
        """Gap with no assessments should be 0.5 (moderate)."""
        rap = RAPAssessment(metric_id="01")
        assert rap.calculate_gap() == 0.5

    def test_calculate_gap_with_bs_and_os(self):
        """Gap should reflect difference between BS and OS."""
        bs = LayerAssessment(
            layer=AssessmentLayer.BUSINESS_STRATEGY,
            metric_id="01",
            score=8.0,  # High target
        )
        os_sec = LayerAssessment(
            layer=AssessmentLayer.OFFENSIVE_SECURITY,
            metric_id="01",
            score=4.0,  # Low reality
        )

        rap = RAPAssessment(
            metric_id="01",
            business_strategy=bs,
            offensive_security=os_sec,
        )

        gap = rap.calculate_gap()
        assert gap > 0  # Should have positive gap
        assert gap <= 1.0


class TestRiskScenario:
    """Tests for RiskScenario class."""

    def test_create_scenario(self):
        """Should create valid scenario."""
        scenario = RiskScenario(
            name="Test Ransomware",
            description="Test scenario",
            metric_id="01",
            dimension_id=1,
            asset="ERP",
            threat="Ransomware",
            frequency=FrequencyParams(0.1, 0.3, 0.7),
            impact=ImpactParams(100_000, 500_000, 3_000_000, "BRL"),
        )

        assert scenario.name == "Test Ransomware"
        assert scenario.metric_id == "01"

    def test_get_expected_annual_loss(self):
        """Should calculate expected annual loss."""
        scenario = RiskScenario(
            name="Test",
            description="Test",
            metric_id="01",
            dimension_id=1,
            asset="Test",
            threat="Test",
            frequency=FrequencyParams(1.0, 1.0, 1.0),  # Exactly 1 event/year
            impact=ImpactParams(100_000, 100_000, 100_000, "BRL"),  # Exactly 100k
        )

        eal = scenario.get_expected_annual_loss()
        assert abs(eal - 100_000) < 1

    def test_controls_affect_effective_params(self):
        """Controls should reduce effective frequency/impact."""
        scenario = RiskScenario(
            name="Test",
            description="Test",
            metric_id="01",
            dimension_id=1,
            asset="Test",
            threat="Test",
            frequency=FrequencyParams(1.0, 2.0, 3.0),
            impact=ImpactParams(100_000, 200_000, 300_000, "BRL"),
        )

        scenario.controls.append(
            ControlEffect(name="Control", frequency_reduction=0.5)
        )

        effective_freq = scenario.get_effective_frequency()
        assert effective_freq.most_likely == 1.0  # Reduced from 2.0


class TestTaxonomy:
    """Tests for taxonomy functions."""

    def test_dimensions_exist(self):
        """Should have 7 dimensions."""
        assert len(DIMENSIONS) == 7

    def test_metrics_exist(self):
        """Should have multiple metrics."""
        assert len(METRICS) >= 20

    def test_get_dimension(self):
        """Should retrieve dimension by ID."""
        dim = get_dimension(1)
        assert dim is not None
        assert dim.id == 1
        assert "Resiliência" in dim.name

    def test_get_metric(self):
        """Should retrieve metric by ID."""
        metric = get_metric("01")
        assert metric is not None
        assert "Recuperação" in metric.name

    def test_get_metrics_by_dimension(self):
        """Should retrieve metrics for a dimension."""
        metrics = get_metrics_by_dimension(1)
        assert len(metrics) > 0
        assert all(m.dimension_id == 1 for m in metrics)

    def test_dimension_summary(self):
        """Should return summary of all dimensions."""
        summary = get_dimension_summary()
        assert len(summary) == 7
        assert all("metric_count" in info for info in summary.values())


class TestLayerMapper:
    """Tests for LayerMapper class."""

    def test_weights_must_sum_to_one(self):
        """Weights that don't sum to 1.0 should raise error."""
        with pytest.raises(ValueError):
            LayerWeights(
                business_strategy=0.5,
                strategy_risk_governance=0.5,
                offensive_security=0.5,  # Sum = 1.5
            )

    def test_score_to_frequency_params(self):
        """Higher score should result in lower frequency."""
        mapper = LayerMapper()

        high_score_freq = mapper.score_to_frequency_params(9.0)
        low_score_freq = mapper.score_to_frequency_params(3.0)

        assert high_score_freq.most_likely < low_score_freq.most_likely

    def test_map_assessment_to_params(self):
        """Should convert RAP assessment to frequency and impact params."""
        bs = LayerAssessment(
            layer=AssessmentLayer.BUSINESS_STRATEGY,
            metric_id="01",
            score=8.0,
        )
        grc = LayerAssessment(
            layer=AssessmentLayer.STRATEGY_RISK_GOVERNANCE,
            metric_id="01",
            score=7.0,
        )
        os_sec = LayerAssessment(
            layer=AssessmentLayer.OFFENSIVE_SECURITY,
            metric_id="01",
            score=6.0,
        )

        rap = RAPAssessment(
            metric_id="01",
            business_strategy=bs,
            strategy_risk_governance=grc,
            offensive_security=os_sec,
        )

        mapper = LayerMapper()
        freq, impact = mapper.map_assessment_to_params(rap)

        assert isinstance(freq, FrequencyParams)
        assert isinstance(impact, ImpactParams)


class TestGapFactor:
    """Tests for calculate_gap_factor function."""

    def test_no_gap_low_factor(self):
        """When OS matches BS, gap factor should be low."""
        bs = LayerAssessment(
            layer=AssessmentLayer.BUSINESS_STRATEGY,
            metric_id="01",
            score=8.0,
        )
        os_sec = LayerAssessment(
            layer=AssessmentLayer.OFFENSIVE_SECURITY,
            metric_id="01",
            score=8.0,
        )

        rap = RAPAssessment(
            metric_id="01",
            business_strategy=bs,
            offensive_security=os_sec,
        )

        factor = calculate_gap_factor(rap)
        assert factor < 1.0

    def test_large_gap_high_factor(self):
        """Large gap should result in high factor."""
        bs = LayerAssessment(
            layer=AssessmentLayer.BUSINESS_STRATEGY,
            metric_id="01",
            score=10.0,  # High expectation
        )
        os_sec = LayerAssessment(
            layer=AssessmentLayer.OFFENSIVE_SECURITY,
            metric_id="01",
            score=2.0,  # Low reality
        )

        rap = RAPAssessment(
            metric_id="01",
            business_strategy=bs,
            offensive_security=os_sec,
        )

        factor = calculate_gap_factor(rap)
        assert factor > 1.0


class TestPLAView:
    """Tests for create_pla_view function."""

    def test_creates_three_levels(self):
        """Should create view with three levels."""
        bs = LayerAssessment(
            layer=AssessmentLayer.BUSINESS_STRATEGY,
            metric_id="01",
            score=8.0,
            target_value=2.0,
        )
        grc = LayerAssessment(
            layer=AssessmentLayer.STRATEGY_RISK_GOVERNANCE,
            metric_id="01",
            score=7.0,
        )
        os_sec = LayerAssessment(
            layer=AssessmentLayer.OFFENSIVE_SECURITY,
            metric_id="01",
            score=5.0,
            actual_value=4.0,
        )

        rap = RAPAssessment(
            metric_id="01",
            business_strategy=bs,
            strategy_risk_governance=grc,
            offensive_security=os_sec,
        )

        pla = create_pla_view(rap)

        assert "levels" in pla
        assert "level_1_objective" in pla["levels"]
        assert "level_2_governance" in pla["levels"]
        assert "level_3_reality" in pla["levels"]
        assert "gap_analysis" in pla
        assert "risk_implication" in pla
