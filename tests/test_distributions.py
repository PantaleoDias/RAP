"""
Tests for the distributions module.
"""

import numpy as np
import pytest

from rap.engine.distributions import (
    sample_pert,
    sample_triangular,
    sample_beta_pert,
    pert_mean,
    pert_variance,
    pert_percentile,
    triangular_mean,
)


class TestSamplePERT:
    """Tests for sample_pert function."""

    def test_samples_within_bounds(self):
        """Samples should be within [low, high] range."""
        low, mode, high = 0.1, 0.5, 2.0
        samples = sample_pert(low, mode, high, size=10000, random_state=42)

        assert np.all(samples >= low)
        assert np.all(samples <= high)

    def test_mean_close_to_expected(self):
        """Sample mean should be close to PERT expected value."""
        low, mode, high = 0.1, 0.5, 2.0
        expected_mean = pert_mean(low, mode, high)
        samples = sample_pert(low, mode, high, size=50000, random_state=42)

        # Allow 5% tolerance
        assert abs(samples.mean() - expected_mean) / expected_mean < 0.05

    def test_mode_is_most_common_region(self):
        """Most samples should be around the mode."""
        low, mode, high = 100, 500, 1000
        samples = sample_pert(low, mode, high, size=10000, random_state=42)

        # Count samples near mode (within 20% of range)
        range_20pct = (high - low) * 0.20
        near_mode = np.sum((samples > mode - range_20pct) & (samples < mode + range_20pct))

        # At least 30% should be near mode
        assert near_mode / len(samples) > 0.30

    def test_degenerate_case_low_equals_high(self):
        """When low == high, should return constant value."""
        samples = sample_pert(100, 100, 100, size=100)
        assert np.all(samples == 100)

    def test_invalid_params_raises_error(self):
        """Invalid parameter order should raise ValueError."""
        with pytest.raises(ValueError):
            sample_pert(2.0, 0.5, 0.1)  # low > mode

        with pytest.raises(ValueError):
            sample_pert(0.1, 2.0, 0.5)  # mode > high

    def test_reproducibility_with_seed(self):
        """Same seed should produce same samples."""
        samples1 = sample_pert(0.1, 0.5, 2.0, size=100, random_state=42)
        samples2 = sample_pert(0.1, 0.5, 2.0, size=100, random_state=42)

        np.testing.assert_array_equal(samples1, samples2)

    def test_different_seeds_produce_different_samples(self):
        """Different seeds should produce different samples."""
        samples1 = sample_pert(0.1, 0.5, 2.0, size=100, random_state=42)
        samples2 = sample_pert(0.1, 0.5, 2.0, size=100, random_state=123)

        assert not np.array_equal(samples1, samples2)

    def test_lambda_affects_concentration(self):
        """Higher lambda should concentrate more around mode."""
        low, mode, high = 0.1, 0.5, 2.0

        samples_low_lambda = sample_pert(low, mode, high, size=10000, lambd=2.0, random_state=42)
        samples_high_lambda = sample_pert(low, mode, high, size=10000, lambd=6.0, random_state=42)

        # Higher lambda should have lower variance
        assert np.std(samples_high_lambda) < np.std(samples_low_lambda)


class TestSampleTriangular:
    """Tests for sample_triangular function."""

    def test_samples_within_bounds(self):
        """Samples should be within [low, high] range."""
        low, mode, high = 100_000, 500_000, 3_000_000
        samples = sample_triangular(low, mode, high, size=10000, random_state=42)

        assert np.all(samples >= low)
        assert np.all(samples <= high)

    def test_mean_close_to_expected(self):
        """Sample mean should be close to triangular expected value."""
        low, mode, high = 100_000, 500_000, 3_000_000
        expected_mean = triangular_mean(low, mode, high)
        samples = sample_triangular(low, mode, high, size=50000, random_state=42)

        # Allow 5% tolerance
        assert abs(samples.mean() - expected_mean) / expected_mean < 0.05

    def test_degenerate_case(self):
        """When low == high, should return constant value."""
        samples = sample_triangular(500, 500, 500, size=100)
        assert np.all(samples == 500)

    def test_invalid_params_raises_error(self):
        """Invalid parameter order should raise ValueError."""
        with pytest.raises(ValueError):
            sample_triangular(1000, 500, 100)  # low > mode

    def test_reproducibility(self):
        """Same seed should produce same samples."""
        samples1 = sample_triangular(100, 500, 1000, size=100, random_state=42)
        samples2 = sample_triangular(100, 500, 1000, size=100, random_state=42)

        np.testing.assert_array_equal(samples1, samples2)


class TestBetaPERT:
    """Tests for sample_beta_pert function."""

    def test_equivalent_to_pert_lambda_4(self):
        """sample_beta_pert should be equivalent to sample_pert with lambda=4."""
        low, mode, high = 0.1, 0.5, 2.0

        samples_beta = sample_beta_pert(low, mode, high, size=10000, random_state=42)
        samples_pert = sample_pert(low, mode, high, size=10000, lambd=4.0, random_state=42)

        np.testing.assert_array_equal(samples_beta, samples_pert)


class TestPERTStatistics:
    """Tests for PERT statistical functions."""

    def test_pert_mean_formula(self):
        """PERT mean should follow (low + 4*mode + high) / 6."""
        low, mode, high = 0.1, 0.5, 2.0
        expected = (low + 4 * mode + high) / 6

        assert pert_mean(low, mode, high) == expected

    def test_pert_variance_positive(self):
        """PERT variance should be positive."""
        assert pert_variance(0.1, 0.5, 2.0) > 0

    def test_pert_variance_zero_for_degenerate(self):
        """PERT variance should be zero when low == high."""
        # This is a degenerate case handled in sample_pert
        # For the formula, we test with tiny range
        var = pert_variance(100, 100.001, 100.002)
        assert var < 0.001

    def test_pert_percentile_bounds(self):
        """PERT percentile 0 should be low, 100 should be high."""
        low, mode, high = 0.1, 0.5, 2.0

        p0 = pert_percentile(low, mode, high, 0)
        p100 = pert_percentile(low, mode, high, 100)

        assert abs(p0 - low) < 0.001
        assert abs(p100 - high) < 0.001

    def test_pert_percentile_ordering(self):
        """Higher percentiles should give higher values."""
        low, mode, high = 0.1, 0.5, 2.0

        p25 = pert_percentile(low, mode, high, 25)
        p50 = pert_percentile(low, mode, high, 50)
        p75 = pert_percentile(low, mode, high, 75)

        assert p25 < p50 < p75

    def test_pert_percentile_invalid_raises_error(self):
        """Invalid percentile should raise ValueError."""
        with pytest.raises(ValueError):
            pert_percentile(0.1, 0.5, 2.0, -10)

        with pytest.raises(ValueError):
            pert_percentile(0.1, 0.5, 2.0, 110)


class TestTriangularMean:
    """Tests for triangular_mean function."""

    def test_triangular_mean_formula(self):
        """Triangular mean should follow (low + mode + high) / 3."""
        low, mode, high = 100_000, 500_000, 3_000_000
        expected = (low + mode + high) / 3

        assert triangular_mean(low, mode, high) == expected

    def test_triangular_mean_symmetric(self):
        """For symmetric triangular, mean should equal mode."""
        low, mode, high = 100, 200, 300
        mean = triangular_mean(low, mode, high)

        assert mean == mode
