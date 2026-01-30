"""
Statistical distributions for risk quantification.

This module provides sampling functions for PERT and triangular distributions,
commonly used in FAIR-based risk analysis for modeling uncertainty in
frequency and impact estimates.

The PERT distribution is preferred for risk analysis because:
- It uses three intuitive parameters: minimum, most likely, maximum
- It naturally models expert estimates with uncertainty
- It has smoother tails than triangular distribution

References:
- riskquant (Netflix): Uses PERT for frequency and impact
- pyfair: Uses beta-PERT distribution
- Open FAIR: Recommends PERT/triangular for estimates
"""

import numpy as np
from numpy.typing import NDArray
from scipy import stats


def sample_pert(
    low: float,
    mode: float,
    high: float,
    size: int = 1,
    lambd: float = 4.0,
    random_state: int | np.random.Generator | None = None,
) -> NDArray[np.float64]:
    """
    Sample from a PERT (Program Evaluation and Review Technique) distribution.

    The PERT distribution is a beta distribution scaled to [low, high] with
    mode at the specified value. It's commonly used in risk analysis because
    it provides a smooth distribution based on three-point estimates.

    Args:
        low: Minimum value (optimistic estimate).
        mode: Most likely value (mode of the distribution).
        high: Maximum value (pessimistic estimate).
        size: Number of samples to generate.
        lambd: Shape parameter (default 4.0). Higher values concentrate
            distribution more around the mode. Common values:
            - 4.0: Standard PERT (recommended)
            - 2.0: More uniform spread
            - 6.0: More peaked around mode
        random_state: Random state for reproducibility.

    Returns:
        Array of samples from the PERT distribution.

    Raises:
        ValueError: If parameters are invalid (low > mode or mode > high).

    Example:
        >>> samples = sample_pert(0.1, 0.5, 2.0, size=10000)
        >>> print(f"Mean: {samples.mean():.3f}")  # Close to PERT mean
    """
    if not (low <= mode <= high):
        raise ValueError(f"Invalid PERT params: low ({low}) <= mode ({mode}) <= high ({high})")

    if low == high:
        return np.full(size, low)

    # Handle edge cases where mode equals low or high
    if mode == low:
        mode = low + 0.001 * (high - low)
    elif mode == high:
        mode = high - 0.001 * (high - low)

    # Calculate alpha and beta parameters for the beta distribution
    # Using the PERT formula: mu = (low + lambd * mode + high) / (lambd + 2)
    mu = (low + lambd * mode + high) / (lambd + 2)

    # Scale mu to [0, 1]
    range_val = high - low
    mu_scaled = (mu - low) / range_val

    # Calculate alpha and beta
    # For PERT: alpha = 1 + lambd * (mode - low) / (high - low)
    #           beta = 1 + lambd * (high - mode) / (high - low)
    alpha = 1 + lambd * (mode - low) / range_val
    beta = 1 + lambd * (high - mode) / range_val

    # Get random generator
    rng = np.random.default_rng(random_state)

    # Sample from beta distribution and scale to [low, high]
    samples = rng.beta(alpha, beta, size=size)
    scaled_samples = low + samples * range_val

    return scaled_samples


def sample_beta_pert(
    low: float,
    mode: float,
    high: float,
    size: int = 1,
    random_state: int | np.random.Generator | None = None,
) -> NDArray[np.float64]:
    """
    Sample from a modified beta-PERT distribution (as used in pyfair).

    This is an alias for sample_pert with standard lambda=4.

    Args:
        low: Minimum value.
        mode: Most likely value.
        high: Maximum value.
        size: Number of samples.
        random_state: Random state for reproducibility.

    Returns:
        Array of samples.
    """
    return sample_pert(low, mode, high, size, lambd=4.0, random_state=random_state)


def sample_triangular(
    low: float,
    mode: float,
    high: float,
    size: int = 1,
    random_state: int | np.random.Generator | None = None,
) -> NDArray[np.float64]:
    """
    Sample from a triangular distribution.

    The triangular distribution is simpler than PERT but has sharp
    corners at the endpoints. It's useful when PERT's smooth tails
    are not necessary.

    Args:
        low: Minimum value (left endpoint).
        mode: Most likely value (peak of the triangle).
        high: Maximum value (right endpoint).
        size: Number of samples to generate.
        random_state: Random state for reproducibility.

    Returns:
        Array of samples from the triangular distribution.

    Raises:
        ValueError: If parameters are invalid.

    Example:
        >>> samples = sample_triangular(100_000, 500_000, 3_000_000, size=10000)
    """
    if not (low <= mode <= high):
        raise ValueError(
            f"Invalid triangular params: low ({low}) <= mode ({mode}) <= high ({high})"
        )

    if low == high:
        return np.full(size, low)

    rng = np.random.default_rng(random_state)
    return rng.triangular(low, mode, high, size=size)


def sample_lognormal(
    mean: float,
    std: float,
    size: int = 1,
    random_state: int | np.random.Generator | None = None,
) -> NDArray[np.float64]:
    """
    Sample from a lognormal distribution.

    Lognormal is useful for modeling impacts that span several orders
    of magnitude and cannot be negative.

    Args:
        mean: Mean of the underlying normal distribution.
        std: Standard deviation of the underlying normal distribution.
        size: Number of samples.
        random_state: Random state for reproducibility.

    Returns:
        Array of samples from lognormal distribution.
    """
    rng = np.random.default_rng(random_state)
    return rng.lognormal(mean, std, size=size)


def sample_poisson(
    rate: float,
    size: int = 1,
    random_state: int | np.random.Generator | None = None,
) -> NDArray[np.int64]:
    """
    Sample from a Poisson distribution.

    Poisson is commonly used to model the number of events (e.g., attacks)
    that occur in a fixed interval (e.g., one year).

    Args:
        rate: Expected number of events (lambda parameter).
        size: Number of samples.
        random_state: Random state for reproducibility.

    Returns:
        Array of integer samples from Poisson distribution.
    """
    rng = np.random.default_rng(random_state)
    return rng.poisson(rate, size=size)


def pert_mean(low: float, mode: float, high: float, lambd: float = 4.0) -> float:
    """
    Calculate the mean of a PERT distribution.

    Args:
        low: Minimum value.
        mode: Most likely value.
        high: Maximum value.
        lambd: Shape parameter (default 4.0).

    Returns:
        Expected value (mean) of the PERT distribution.
    """
    return (low + lambd * mode + high) / (lambd + 2)


def pert_variance(low: float, mode: float, high: float, lambd: float = 4.0) -> float:
    """
    Calculate the variance of a PERT distribution.

    Args:
        low: Minimum value.
        mode: Most likely value.
        high: Maximum value.
        lambd: Shape parameter (default 4.0).

    Returns:
        Variance of the PERT distribution.
    """
    mu = pert_mean(low, mode, high, lambd)
    alpha = 1 + lambd * (mode - low) / (high - low)
    beta = 1 + lambd * (high - mode) / (high - low)

    # Variance of beta distribution scaled to [low, high]
    beta_var = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
    return beta_var * (high - low) ** 2


def pert_percentile(
    low: float,
    mode: float,
    high: float,
    percentile: float,
    lambd: float = 4.0,
) -> float:
    """
    Calculate a percentile of the PERT distribution.

    Args:
        low: Minimum value.
        mode: Most likely value.
        high: Maximum value.
        percentile: Percentile to calculate (0-100).
        lambd: Shape parameter.

    Returns:
        Value at the specified percentile.
    """
    if not (0 <= percentile <= 100):
        raise ValueError(f"Percentile must be between 0 and 100, got {percentile}")

    # Handle edge case
    if low == high:
        return low

    # Calculate alpha and beta
    alpha = 1 + lambd * (mode - low) / (high - low)
    beta_param = 1 + lambd * (high - mode) / (high - low)

    # Get percentile from beta distribution
    q = percentile / 100.0
    beta_percentile = stats.beta.ppf(q, alpha, beta_param)

    # Scale to [low, high]
    return low + beta_percentile * (high - low)


def triangular_mean(low: float, mode: float, high: float) -> float:
    """
    Calculate the mean of a triangular distribution.

    Args:
        low: Minimum value.
        mode: Most likely value.
        high: Maximum value.

    Returns:
        Expected value (mean) of the triangular distribution.
    """
    return (low + mode + high) / 3


def create_pert_distribution(
    low: float,
    mode: float,
    high: float,
    lambd: float = 4.0,
) -> stats.rv_continuous:
    """
    Create a scipy frozen PERT distribution for advanced operations.

    Args:
        low: Minimum value.
        mode: Most likely value.
        high: Maximum value.
        lambd: Shape parameter.

    Returns:
        Frozen scipy.stats distribution object.
    """
    if low == high:
        # Degenerate case: return constant
        return stats.uniform(loc=low, scale=0)

    alpha = 1 + lambd * (mode - low) / (high - low)
    beta_param = 1 + lambd * (high - mode) / (high - low)

    # Create scaled beta distribution
    return stats.beta(alpha, beta_param, loc=low, scale=high - low)
