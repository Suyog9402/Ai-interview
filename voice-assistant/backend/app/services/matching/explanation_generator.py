from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def generate_explanation(
    match_result: Dict[str, Any],
    jd_requirements: Dict[str, Any],
    candidate_data: Dict[str, Any]
) -> str:
    """
    Generate human-readable explanation of match result.
    
    Args:
        match_result: Match result dictionary
        jd_requirements: JD requirements
        candidate_data: Candidate data
    
    Returns:
        Explanation text
    """
    explanation_parts = []
    
    # Overall score
    score = match_result.get("weighted_score", 0.0)
    explanation_parts.append(f"Overall Match Score: {score:.1%}")
    
    # Hard filter status
    hard_filter_passed = match_result.get("hard_filter_passed", False)
    if hard_filter_passed:
        explanation_parts.append("✓ Passed all hard filters (must-have requirements)")
    else:
        reasons = match_result.get("hard_filter_reasons", [])
        explanation_parts.append("✗ Failed hard filters:")
        for reason in reasons:
            explanation_parts.append(f"  - {reason}")
    
    # Score breakdown
    breakdown = match_result.get("score_breakdown", {})
    if breakdown:
        explanation_parts.append("\nScore Breakdown:")
        for dimension, score in breakdown.items():
            explanation_parts.append(f"  - {dimension.title()}: {score:.1%}")
    
    # Evidence summary
    evidence_map = match_result.get("evidence_map", {})
    if evidence_map:
        explanation_parts.append("\nEvidence Found:")
        for skill, evidence_list in list(evidence_map.items())[:10]:  # Top 10
            sources = [e.get("source") for e in evidence_list]
            source_summary = ", ".join(set(sources))
            explanation_parts.append(f"  - {skill}: Found in {source_summary}")
    
    # Strengths
    strengths = match_result.get("strengths", [])
    if strengths:
        explanation_parts.append("\nStrengths:")
        for strength in strengths[:5]:  # Top 5
            explanation_parts.append(f"  - {strength}")
    
    # Gaps
    gaps = match_result.get("gaps", [])
    if gaps:
        explanation_parts.append("\nAreas for Improvement:")
        for gap in gaps[:5]:  # Top 5
            explanation_parts.append(f"  - {gap}")
    
    return "\n".join(explanation_parts)

