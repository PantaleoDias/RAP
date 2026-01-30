"""
Core models for the RAP (Resilience Acceleration Program) framework.

This module defines the fundamental data structures for risk quantification,
inspired by FAIR (Factor Analysis of Information Risk) methodology.

Classes:
    FrequencyParams: Parameters for loss event frequency (PERT distribution).
    ImpactParams: Parameters for loss magnitude/impact (PERT distribution).
    ControlEffect: Represents the effect of controls on frequency/impact.
    LayerAssessment: Assessment from one of the three RAP layers.
    RAPAssessment: Combined assessment from all three layers.
    RiskScenario: Complete risk scenario with all parameters.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid


class AssessmentLayer(Enum):
    """The three assessment layers in the RAP framework."""

    BUSINESS_STRATEGY = "business_strategy"
    STRATEGY_RISK_GOVERNANCE = "strategy_risk_governance"  # GRC
    OFFENSIVE_SECURITY = "offensive_security"


@dataclass
class FrequencyParams:
    """
    Parameters for estimating annual loss event frequency.

    Uses a PERT (Program Evaluation and Review Technique) distribution
    defined by minimum, most likely, and maximum values.

    Attributes:
        min_value: Minimum expected annual frequency (optimistic).
        most_likely: Most likely annual frequency (mode).
        max_value: Maximum expected annual frequency (pessimistic).
        confidence: Confidence level in the estimate (0.0 to 1.0).
        notes: Optional notes explaining the estimation rationale.

    Example:
        >>> freq = FrequencyParams(min_value=0.1, most_likely=0.5, max_value=2.0)
        >>> # Represents: at least 0.1 events/year, most likely 0.5, up to 2 events/year
    """

    min_value: float
    most_likely: float
    max_value: float
    confidence: float = 0.8
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate frequency parameters."""
        if not (0 <= self.min_value <= self.most_likely <= self.max_value):
            raise ValueError(
                f"Invalid frequency params: min ({self.min_value}) <= "
                f"most_likely ({self.most_likely}) <= max ({self.max_value}) required"
            )
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")

    @property
    def expected_value(self) -> float:
        """Calculate expected value using PERT formula: (min + 4*ml + max) / 6."""
        return (self.min_value + 4 * self.most_likely + self.max_value) / 6


@dataclass
class ImpactParams:
    """
    Parameters for estimating loss magnitude/impact.

    Uses a PERT distribution for the financial impact of a single loss event.

    Attributes:
        min_value: Minimum expected impact (optimistic).
        most_likely: Most likely impact (mode).
        max_value: Maximum expected impact (pessimistic).
        currency: Currency code (e.g., "BRL", "USD").
        confidence: Confidence level in the estimate (0.0 to 1.0).
        notes: Optional notes explaining the estimation rationale.

    Example:
        >>> impact = ImpactParams(
        ...     min_value=100_000,
        ...     most_likely=500_000,
        ...     max_value=3_000_000,
        ...     currency="BRL"
        ... )
    """

    min_value: float
    most_likely: float
    max_value: float
    currency: str = "BRL"
    confidence: float = 0.8
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate impact parameters."""
        if not (0 <= self.min_value <= self.most_likely <= self.max_value):
            raise ValueError(
                f"Invalid impact params: min ({self.min_value}) <= "
                f"most_likely ({self.most_likely}) <= max ({self.max_value}) required"
            )
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")

    @property
    def expected_value(self) -> float:
        """Calculate expected value using PERT formula: (min + 4*ml + max) / 6."""
        return (self.min_value + 4 * self.most_likely + self.max_value) / 6


@dataclass
class ControlEffect:
    """
    Represents the effect of security controls on risk parameters.

    Controls can reduce frequency (preventive controls) and/or impact
    (detective/corrective controls).

    Attributes:
        name: Name of the control or control set.
        frequency_reduction: Factor to reduce frequency (0.0 to 1.0).
            E.g., 0.3 means frequency is reduced by 30%.
        impact_reduction: Factor to reduce impact (0.0 to 1.0).
            E.g., 0.5 means impact is reduced by 50%.
        effectiveness: Overall effectiveness score (0.0 to 1.0).
        notes: Optional notes about control implementation.

    Example:
        >>> control = ControlEffect(
        ...     name="EDR + SOC 24/7",
        ...     frequency_reduction=0.4,  # 40% fewer successful attacks
        ...     impact_reduction=0.3,     # 30% less impact when attack succeeds
        ...     effectiveness=0.85
        ... )
    """

    name: str
    frequency_reduction: float = 0.0
    impact_reduction: float = 0.0
    effectiveness: float = 1.0
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate control effect parameters."""
        if not (0.0 <= self.frequency_reduction <= 1.0):
            raise ValueError(
                f"frequency_reduction must be between 0 and 1, got {self.frequency_reduction}"
            )
        if not (0.0 <= self.impact_reduction <= 1.0):
            raise ValueError(
                f"impact_reduction must be between 0 and 1, got {self.impact_reduction}"
            )
        if not (0.0 <= self.effectiveness <= 1.0):
            raise ValueError(f"effectiveness must be between 0 and 1, got {self.effectiveness}")

    def apply_to_frequency(self, freq: FrequencyParams) -> FrequencyParams:
        """Apply frequency reduction to frequency parameters."""
        reduction = 1.0 - (self.frequency_reduction * self.effectiveness)
        return FrequencyParams(
            min_value=freq.min_value * reduction,
            most_likely=freq.most_likely * reduction,
            max_value=freq.max_value * reduction,
            confidence=freq.confidence,
            notes=f"{freq.notes or ''} [After control: {self.name}]".strip(),
        )

    def apply_to_impact(self, impact: ImpactParams) -> ImpactParams:
        """Apply impact reduction to impact parameters."""
        reduction = 1.0 - (self.impact_reduction * self.effectiveness)
        return ImpactParams(
            min_value=impact.min_value * reduction,
            most_likely=impact.most_likely * reduction,
            max_value=impact.max_value * reduction,
            currency=impact.currency,
            confidence=impact.confidence,
            notes=f"{impact.notes or ''} [After control: {self.name}]".strip(),
        )


@dataclass
class LayerAssessment:
    """
    Assessment from one of the three RAP layers.

    Each layer provides different perspective on the same metric:
    - Business Strategy: Defines objectives (RTO, RPO, risk appetite)
    - Strategy & Risk Governance: Assesses current controls/processes
    - Offensive Security: Tests real-world performance

    Attributes:
        layer: Which assessment layer this comes from.
        metric_id: ID of the RAP metric being assessed.
        score: Assessment score (0.0 to 10.0, where 10 is best).
        target_value: Target value defined for this metric (layer-specific).
        actual_value: Actual measured value (layer-specific).
        confidence: Confidence in this assessment (0.0 to 1.0).
        evidence: Supporting evidence or test results.
        notes: Additional context or observations.
        assessor: Who performed the assessment.
        assessment_date: When the assessment was performed.

    Example:
        >>> # Business Strategy defines RTO target
        >>> bs_assessment = LayerAssessment(
        ...     layer=AssessmentLayer.BUSINESS_STRATEGY,
        ...     metric_id="01",
        ...     score=8.0,
        ...     target_value=2.0,  # RTO target: 2 hours
        ...     notes="Critical ERP system - RTO defined by BIA"
        ... )
        >>>
        >>> # Offensive Security tests actual recovery
        >>> os_assessment = LayerAssessment(
        ...     layer=AssessmentLayer.OFFENSIVE_SECURITY,
        ...     metric_id="01",
        ...     score=5.0,
        ...     actual_value=4.0,  # Actual recovery: 4 hours
        ...     evidence="Ransomware simulation on 2024-01-15"
        ... )
    """

    layer: AssessmentLayer
    metric_id: str
    score: float
    target_value: Optional[float] = None
    actual_value: Optional[float] = None
    confidence: float = 0.8
    evidence: Optional[str] = None
    notes: Optional[str] = None
    assessor: Optional[str] = None
    assessment_date: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate layer assessment."""
        if not (0.0 <= self.score <= 10.0):
            raise ValueError(f"Score must be between 0 and 10, got {self.score}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")


@dataclass
class RAPAssessment:
    """
    Combined assessment from all three RAP layers for a single metric.

    This provides the PLA (3-level) view:
    1. Business Strategy objective
    2. GRC maturity level
    3. Offensive Security test results

    The gap between layers is used to adjust risk parameters.

    Attributes:
        metric_id: ID of the RAP metric.
        business_strategy: Assessment from Business Strategy layer.
        strategy_risk_governance: Assessment from GRC layer.
        offensive_security: Assessment from Offensive Security layer.

    Example:
        >>> rap_assessment = RAPAssessment(
        ...     metric_id="01",
        ...     business_strategy=bs_assessment,
        ...     strategy_risk_governance=grc_assessment,
        ...     offensive_security=os_assessment
        ... )
        >>> gap = rap_assessment.calculate_gap()
    """

    metric_id: str
    business_strategy: Optional[LayerAssessment] = None
    strategy_risk_governance: Optional[LayerAssessment] = None
    offensive_security: Optional[LayerAssessment] = None

    def calculate_gap(self) -> float:
        """
        Calculate the gap between objective and reality.

        Returns a value from 0.0 (no gap) to 1.0 (maximum gap).
        Higher gap indicates higher risk.
        """
        scores = []

        # Get available scores
        if self.business_strategy:
            scores.append(("bs", self.business_strategy.score))
        if self.strategy_risk_governance:
            scores.append(("grc", self.strategy_risk_governance.score))
        if self.offensive_security:
            scores.append(("os", self.offensive_security.score))

        if not scores:
            return 0.5  # Default moderate gap if no assessments

        # Primary gap: between Business Strategy target and Offensive Security reality
        if self.business_strategy and self.offensive_security:
            bs_score = self.business_strategy.score
            os_score = self.offensive_security.score
            # Gap is higher when OS score is lower than BS target
            gap = max(0.0, (bs_score - os_score) / 10.0)
            return min(1.0, gap)

        # Fallback: use average deviation from maximum score
        avg_score = sum(s[1] for s in scores) / len(scores)
        return (10.0 - avg_score) / 10.0

    def get_layer_summary(self) -> dict:
        """Get summary of all layer assessments."""
        return {
            "metric_id": self.metric_id,
            "business_strategy": {
                "score": self.business_strategy.score if self.business_strategy else None,
                "target": self.business_strategy.target_value if self.business_strategy else None,
            },
            "strategy_risk_governance": {
                "score": (
                    self.strategy_risk_governance.score
                    if self.strategy_risk_governance
                    else None
                ),
            },
            "offensive_security": {
                "score": self.offensive_security.score if self.offensive_security else None,
                "actual": (
                    self.offensive_security.actual_value if self.offensive_security else None
                ),
            },
            "gap": self.calculate_gap(),
        }


@dataclass
class RiskScenario:
    """
    Complete risk scenario with all parameters for simulation.

    A risk scenario represents a specific threat against a specific asset,
    with frequency and impact parameters derived from the three RAP layers.

    Attributes:
        scenario_id: Unique identifier for the scenario.
        name: Human-readable scenario name.
        description: Detailed description of the scenario.
        metric_id: Associated RAP metric ID.
        dimension_id: Associated RAP dimension ID.
        asset: The asset or system at risk.
        threat: The threat actor or event type.
        frequency: Frequency parameters (annual).
        impact: Impact parameters (per event).
        controls: List of controls affecting this scenario.
        rap_assessment: Combined assessment from all layers (optional).
        tags: Optional tags for categorization.

    Example:
        >>> scenario = RiskScenario(
        ...     name="Ransomware Attack on ERP",
        ...     description="Ransomware encrypts critical ERP system",
        ...     metric_id="01",
        ...     dimension_id=1,
        ...     asset="ERP System",
        ...     threat="Ransomware",
        ...     frequency=FrequencyParams(0.1, 0.3, 0.7),
        ...     impact=ImpactParams(100_000, 500_000, 3_000_000, "BRL"),
        ... )
    """

    name: str
    description: str
    metric_id: str
    dimension_id: int
    asset: str
    threat: str
    frequency: FrequencyParams
    impact: ImpactParams
    scenario_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    controls: list[ControlEffect] = field(default_factory=list)
    rap_assessment: Optional[RAPAssessment] = None
    tags: list[str] = field(default_factory=list)

    def get_effective_frequency(self) -> FrequencyParams:
        """Get frequency after applying all controls."""
        freq = self.frequency
        for control in self.controls:
            freq = control.apply_to_frequency(freq)
        return freq

    def get_effective_impact(self) -> ImpactParams:
        """Get impact after applying all controls."""
        impact = self.impact
        for control in self.controls:
            impact = control.apply_to_impact(impact)
        return impact

    def get_expected_annual_loss(self) -> float:
        """
        Calculate expected annual loss (simple estimate).

        Uses: E[ALE] = E[Frequency] * E[Impact]
        """
        freq = self.get_effective_frequency()
        impact = self.get_effective_impact()
        return freq.expected_value * impact.expected_value

    def to_dict(self) -> dict:
        """Convert scenario to dictionary representation."""
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "metric_id": self.metric_id,
            "dimension_id": self.dimension_id,
            "asset": self.asset,
            "threat": self.threat,
            "frequency": {
                "min": self.frequency.min_value,
                "most_likely": self.frequency.most_likely,
                "max": self.frequency.max_value,
            },
            "impact": {
                "min": self.impact.min_value,
                "most_likely": self.impact.most_likely,
                "max": self.impact.max_value,
                "currency": self.impact.currency,
            },
            "expected_annual_loss": self.get_expected_annual_loss(),
            "tags": self.tags,
        }
