"""
Mapping between RAP's three assessment layers and risk parameters.

This module defines how the three RAP layers are combined to generate
frequency and impact parameters for risk simulation:

1. Business Strategy - Defines objectives (RTO, RPO, risk appetite)
2. Strategy & Risk Governance (GRC) - Assesses controls/processes maturity
3. Offensive Security - Tests real-world performance

The gap between layers directly affects risk parameters:
- Larger gap between objective and reality -> Higher frequency/impact
"""

from dataclasses import dataclass
from typing import Optional
import math

from rap.core.model import (
    AssessmentLayer,
    LayerAssessment,
    RAPAssessment,
    FrequencyParams,
    ImpactParams,
)


@dataclass
class LayerWeights:
    """
    Weights for combining layer assessments.

    Different metrics may weight layers differently based on
    what aspect of risk they represent.

    Attributes:
        business_strategy: Weight for Business Strategy layer (0.0 to 1.0).
        strategy_risk_governance: Weight for GRC layer (0.0 to 1.0).
        offensive_security: Weight for Offensive Security layer (0.0 to 1.0).
    """

    business_strategy: float = 0.25
    strategy_risk_governance: float = 0.35
    offensive_security: float = 0.40

    def __post_init__(self) -> None:
        """Validate weights sum to 1.0."""
        total = (
            self.business_strategy
            + self.strategy_risk_governance
            + self.offensive_security
        )
        if not math.isclose(total, 1.0, rel_tol=0.01):
            raise ValueError(f"Weights must sum to 1.0, got {total}")


# Default weights emphasize Offensive Security (real-world validation)
DEFAULT_WEIGHTS = LayerWeights(
    business_strategy=0.25,
    strategy_risk_governance=0.35,
    offensive_security=0.40,
)

# Weights for compliance-focused metrics
COMPLIANCE_WEIGHTS = LayerWeights(
    business_strategy=0.30,
    strategy_risk_governance=0.50,
    offensive_security=0.20,
)

# Weights for operational resilience metrics
RESILIENCE_WEIGHTS = LayerWeights(
    business_strategy=0.20,
    strategy_risk_governance=0.30,
    offensive_security=0.50,
)


def calculate_gap_factor(rap_assessment: RAPAssessment) -> float:
    """
    Calculate the gap factor between layers.

    The gap factor represents how far reality (Offensive Security results)
    is from the objective (Business Strategy targets) and maturity
    (GRC controls).

    Returns:
        Gap factor from 0.0 (no gap, excellent) to 2.0 (maximum gap, critical).
        Values > 1.0 indicate significant deviations from objectives.
    """
    if not rap_assessment:
        return 1.0  # Neutral if no assessment

    bs_score = (
        rap_assessment.business_strategy.score
        if rap_assessment.business_strategy
        else 5.0
    )
    grc_score = (
        rap_assessment.strategy_risk_governance.score
        if rap_assessment.strategy_risk_governance
        else 5.0
    )
    os_score = (
        rap_assessment.offensive_security.score
        if rap_assessment.offensive_security
        else 5.0
    )

    # Calculate gaps
    # Gap 1: Business Strategy target vs Offensive Security reality
    bs_os_gap = max(0.0, bs_score - os_score)

    # Gap 2: GRC maturity vs Offensive Security reality
    grc_os_gap = max(0.0, grc_score - os_score)

    # Combined gap: weighted average normalized to 0-1 scale
    # Higher gap means higher risk
    combined_gap = (bs_os_gap * 0.6 + grc_os_gap * 0.4) / 10.0

    # Convert to factor: 0.5 (excellent) to 2.0 (critical)
    # Gap of 0 -> factor 0.5 (reduces risk)
    # Gap of 0.5 -> factor 1.0 (neutral)
    # Gap of 1.0 -> factor 2.0 (doubles risk)
    gap_factor = 0.5 + (combined_gap * 1.5)

    return min(2.0, max(0.5, gap_factor))


def calculate_control_effectiveness(rap_assessment: RAPAssessment) -> float:
    """
    Calculate overall control effectiveness from layer assessments.

    Returns:
        Effectiveness factor from 0.0 (no controls) to 1.0 (perfect controls).
    """
    if not rap_assessment:
        return 0.5  # Moderate effectiveness if no assessment

    scores = []
    weights = []

    if rap_assessment.strategy_risk_governance:
        scores.append(rap_assessment.strategy_risk_governance.score / 10.0)
        weights.append(0.6)

    if rap_assessment.offensive_security:
        scores.append(rap_assessment.offensive_security.score / 10.0)
        weights.append(0.4)

    if not scores:
        return 0.5

    # Weighted average
    total_weight = sum(weights)
    effectiveness = sum(s * w for s, w in zip(scores, weights)) / total_weight

    return min(1.0, max(0.0, effectiveness))


class LayerMapper:
    """
    Maps three-layer assessments to risk parameters.

    This class implements the core logic for converting qualitative
    assessments from Business Strategy, GRC, and Offensive Security
    into quantitative frequency and impact parameters.
    """

    def __init__(
        self,
        weights: LayerWeights = DEFAULT_WEIGHTS,
        base_frequency_range: tuple[float, float, float] = (0.1, 0.5, 2.0),
        base_impact_range: tuple[float, float, float] = (10_000, 100_000, 1_000_000),
    ):
        """
        Initialize the mapper.

        Args:
            weights: Weights for combining layer assessments.
            base_frequency_range: Base (min, mode, max) frequency for average risk.
            base_impact_range: Base (min, mode, max) impact for average risk.
        """
        self.weights = weights
        self.base_freq_min, self.base_freq_mode, self.base_freq_max = base_frequency_range
        self.base_impact_min, self.base_impact_mode, self.base_impact_max = base_impact_range

    def calculate_combined_score(
        self,
        rap_assessment: RAPAssessment,
    ) -> float:
        """
        Calculate weighted combined score from all layers.

        Args:
            rap_assessment: Combined assessment from all layers.

        Returns:
            Combined score from 0.0 to 10.0.
        """
        total_weight = 0.0
        weighted_score = 0.0

        if rap_assessment.business_strategy:
            weighted_score += (
                rap_assessment.business_strategy.score * self.weights.business_strategy
            )
            total_weight += self.weights.business_strategy

        if rap_assessment.strategy_risk_governance:
            weighted_score += (
                rap_assessment.strategy_risk_governance.score
                * self.weights.strategy_risk_governance
            )
            total_weight += self.weights.strategy_risk_governance

        if rap_assessment.offensive_security:
            weighted_score += (
                rap_assessment.offensive_security.score * self.weights.offensive_security
            )
            total_weight += self.weights.offensive_security

        if total_weight == 0:
            return 5.0  # Neutral score if no assessments

        return weighted_score / total_weight

    def score_to_frequency_params(
        self,
        combined_score: float,
        gap_factor: float = 1.0,
    ) -> FrequencyParams:
        """
        Convert combined score to frequency parameters.

        Lower scores indicate higher risk, which means higher frequency.

        Args:
            combined_score: Combined score from 0.0 to 10.0.
            gap_factor: Multiplier based on layer gaps (0.5 to 2.0).

        Returns:
            FrequencyParams for simulation.
        """
        # Invert score: low score (poor security) -> high frequency
        # Score 10 -> factor 0.2, Score 5 -> factor 1.0, Score 0 -> factor 5.0
        score_factor = 5.0 / max(combined_score, 1.0)

        # Apply gap factor
        adjusted_factor = score_factor * gap_factor

        return FrequencyParams(
            min_value=self.base_freq_min * adjusted_factor,
            most_likely=self.base_freq_mode * adjusted_factor,
            max_value=self.base_freq_max * adjusted_factor,
            confidence=0.8,
            notes=f"Derived from RAP score {combined_score:.1f}, gap factor {gap_factor:.2f}",
        )

    def score_to_impact_params(
        self,
        combined_score: float,
        gap_factor: float = 1.0,
        currency: str = "BRL",
    ) -> ImpactParams:
        """
        Convert combined score to impact parameters.

        Lower scores indicate higher risk, which means higher impact.

        Args:
            combined_score: Combined score from 0.0 to 10.0.
            gap_factor: Multiplier based on layer gaps (0.5 to 2.0).
            currency: Currency code for impact values.

        Returns:
            ImpactParams for simulation.
        """
        # Invert score: low score (poor security) -> high impact
        # Score 10 -> factor 0.3, Score 5 -> factor 1.0, Score 0 -> factor 3.0
        score_factor = 3.0 / max(combined_score / 3.0, 1.0)

        # Apply gap factor (less effect on impact than frequency)
        adjusted_factor = score_factor * (0.5 + gap_factor * 0.5)

        return ImpactParams(
            min_value=self.base_impact_min * adjusted_factor,
            most_likely=self.base_impact_mode * adjusted_factor,
            max_value=self.base_impact_max * adjusted_factor,
            currency=currency,
            confidence=0.8,
            notes=f"Derived from RAP score {combined_score:.1f}, gap factor {gap_factor:.2f}",
        )

    def map_assessment_to_params(
        self,
        rap_assessment: RAPAssessment,
        currency: str = "BRL",
    ) -> tuple[FrequencyParams, ImpactParams]:
        """
        Map a RAP assessment to frequency and impact parameters.

        This is the main method for converting three-layer assessments
        into simulation parameters.

        Args:
            rap_assessment: Combined assessment from all layers.
            currency: Currency code for impact values.

        Returns:
            Tuple of (FrequencyParams, ImpactParams).
        """
        combined_score = self.calculate_combined_score(rap_assessment)
        gap_factor = calculate_gap_factor(rap_assessment)

        freq_params = self.score_to_frequency_params(combined_score, gap_factor)
        impact_params = self.score_to_impact_params(combined_score, gap_factor, currency)

        return freq_params, impact_params


def combine_layer_assessments(
    business_strategy: Optional[LayerAssessment] = None,
    strategy_risk_governance: Optional[LayerAssessment] = None,
    offensive_security: Optional[LayerAssessment] = None,
    metric_id: Optional[str] = None,
) -> RAPAssessment:
    """
    Combine individual layer assessments into a RAP assessment.

    Args:
        business_strategy: Assessment from Business Strategy layer.
        strategy_risk_governance: Assessment from GRC layer.
        offensive_security: Assessment from Offensive Security layer.
        metric_id: Optional metric ID (inferred from assessments if not provided).

    Returns:
        Combined RAPAssessment.
    """
    # Infer metric_id from assessments if not provided
    if metric_id is None:
        for assessment in [business_strategy, strategy_risk_governance, offensive_security]:
            if assessment and assessment.metric_id:
                metric_id = assessment.metric_id
                break
        if metric_id is None:
            metric_id = "unknown"

    return RAPAssessment(
        metric_id=metric_id,
        business_strategy=business_strategy,
        strategy_risk_governance=strategy_risk_governance,
        offensive_security=offensive_security,
    )


def create_pla_view(rap_assessment: RAPAssessment) -> dict:
    """
    Create the PLA (3-level) view for a RAP assessment.

    The PLA view shows:
    1. Business Strategy objective
    2. GRC maturity level
    3. Offensive Security test results

    Args:
        rap_assessment: Combined assessment from all layers.

    Returns:
        Dictionary with PLA view data.
    """
    pla_view = {
        "metric_id": rap_assessment.metric_id,
        "levels": {
            "level_1_objective": None,
            "level_2_governance": None,
            "level_3_reality": None,
        },
        "gap_analysis": {
            "objective_vs_reality_gap": None,
            "governance_vs_reality_gap": None,
            "overall_gap_factor": calculate_gap_factor(rap_assessment),
        },
        "risk_implication": None,
    }

    # Level 1: Business Strategy Objective
    if rap_assessment.business_strategy:
        bs = rap_assessment.business_strategy
        pla_view["levels"]["level_1_objective"] = {
            "score": bs.score,
            "target_value": bs.target_value,
            "description": "Compliance/resilience objective defined by business",
            "notes": bs.notes,
        }

    # Level 2: GRC Maturity
    if rap_assessment.strategy_risk_governance:
        grc = rap_assessment.strategy_risk_governance
        pla_view["levels"]["level_2_governance"] = {
            "score": grc.score,
            "description": "Current control and process maturity",
            "evidence": grc.evidence,
            "notes": grc.notes,
        }

    # Level 3: Offensive Security Reality
    if rap_assessment.offensive_security:
        os_sec = rap_assessment.offensive_security
        pla_view["levels"]["level_3_reality"] = {
            "score": os_sec.score,
            "actual_value": os_sec.actual_value,
            "description": "Real-world test results",
            "evidence": os_sec.evidence,
            "notes": os_sec.notes,
        }

    # Gap Analysis
    if rap_assessment.business_strategy and rap_assessment.offensive_security:
        pla_view["gap_analysis"]["objective_vs_reality_gap"] = (
            rap_assessment.business_strategy.score - rap_assessment.offensive_security.score
        )

    if rap_assessment.strategy_risk_governance and rap_assessment.offensive_security:
        pla_view["gap_analysis"]["governance_vs_reality_gap"] = (
            rap_assessment.strategy_risk_governance.score
            - rap_assessment.offensive_security.score
        )

    # Risk Implication
    gap_factor = pla_view["gap_analysis"]["overall_gap_factor"]
    if gap_factor < 0.7:
        pla_view["risk_implication"] = "LOW - Reality exceeds expectations"
    elif gap_factor < 1.0:
        pla_view["risk_implication"] = "MODERATE - Close to objectives"
    elif gap_factor < 1.3:
        pla_view["risk_implication"] = "ELEVATED - Gap between objective and reality"
    elif gap_factor < 1.6:
        pla_view["risk_implication"] = "HIGH - Significant gap requires attention"
    else:
        pla_view["risk_implication"] = "CRITICAL - Major deviation from objectives"

    return pla_view
