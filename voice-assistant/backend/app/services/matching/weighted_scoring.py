from typing import Dict, Tuple, Any
import logging
from app.services.matching.evidence_tracker import EvidenceTracker

logger = logging.getLogger(__name__)


def calculate_weighted_score(
    jd_requirements: Dict[str, Any],
    resume_data: Dict[str, Any],
    transcript_data: Dict[str, Any],
    weights: Dict[str, float],  # From admin settings
    evidence_tracker: EvidenceTracker
) -> Tuple[float, Dict[str, float], Dict[str, Any]]:
    """
    Calculate weighted matching score.
    
    Args:
        jd_requirements: Job description requirements
        resume_data: Extracted resume data
        transcript_data: Extracted transcript data
        weights: Weight configuration for each dimension
        evidence_tracker: Evidence tracker instance
    
    Returns:
        Tuple of (total_score, score_breakdown, evidence_map)
    """
    scores = {}
    
    # Skill matching (weighted)
    skill_score = match_skills(
        jd_requirements.get("skills", []),
        resume_data.get("skills", []),
        transcript_data.get("skills", []),
        weights.get("skills", 0.3),
        evidence_tracker
    )
    scores["skills"] = skill_score
    
    # Experience matching
    exp_score = match_experience(
        jd_requirements.get("experience_years", 0),
        resume_data.get("experience_years"),
        transcript_data.get("experience_years"),
        weights.get("experience", 0.2),
        evidence_tracker
    )
    scores["experience"] = exp_score
    
    # Tools/Technologies matching
    tools_score = match_tools(
        jd_requirements.get("tools", []),
        resume_data.get("tools", []),
        transcript_data.get("tools", []),
        weights.get("tools", 0.15),
        evidence_tracker
    )
    scores["tools"] = tools_score
    
    # Education matching
    education_score = match_education(
        jd_requirements.get("education", []),
        resume_data.get("education", []),
        transcript_data.get("education", []),
        weights.get("education", 0.1),
        evidence_tracker
    )
    scores["education"] = education_score
    
    # Projects matching
    projects_score = match_projects(
        jd_requirements.get("project_requirements", []),
        resume_data.get("projects", []),
        transcript_data.get("projects", []),
        weights.get("projects", 0.15),
        evidence_tracker
    )
    scores["projects"] = projects_score
    
    # Roles/Experience alignment
    roles_score = match_roles(
        jd_requirements.get("role_requirements", []),
        resume_data.get("roles", []),
        transcript_data.get("roles", []),
        weights.get("roles", 0.1),
        evidence_tracker
    )
    scores["roles"] = roles_score
    
    # Calculate weighted sum
    total_score = sum(
        scores[dim] * weights.get(dim, 0.0)
        for dim in scores
    )
    
    # Normalize to 0-1 range
    total_score = min(1.0, max(0.0, total_score))
    
    logger.info(f"Score breakdown: {scores}, Total: {total_score}")
    
    return total_score, scores, evidence_tracker.get_evidence_map()


def match_skills(
    jd_skills: list[str],
    resume_skills: list[str],
    transcript_skills: list[str],
    weight: float,
    evidence_tracker: EvidenceTracker
) -> float:
    """Match skills between JD and candidate"""
    if not jd_skills:
        return 1.0  # No skills required = perfect match
    
    candidate_skills = set()
    candidate_skills.update([s.lower() for s in resume_skills])
    candidate_skills.update([s.lower() for s in transcript_skills])
    
    jd_skills_lower = [s.lower() for s in jd_skills]
    matched_skills = []
    
    for skill in jd_skills_lower:
        if skill in candidate_skills:
            matched_skills.append(skill)
            # Add evidence
            # Find source
            source = "resume" if skill in [s.lower() for s in resume_skills] else "transcript"
            evidence_tracker.add_evidence(
                skill=skill,
                source=source,
                location={"type": "skill_match"},
                confidence=0.9
            )
    
    match_ratio = len(matched_skills) / len(jd_skills) if jd_skills else 0.0
    return match_ratio


def match_experience(
    jd_years: float,
    resume_years: float | None,
    transcript_years: float | None,
    weight: float,
    evidence_tracker: EvidenceTracker
) -> float:
    """Match experience years"""
    if jd_years == 0:
        return 1.0  # No experience required
    
    candidate_years = resume_years or transcript_years or 0.0
    
    if candidate_years >= jd_years:
        # Add evidence
        source = "resume" if resume_years else "transcript"
        evidence_tracker.add_evidence(
            skill="experience",
            source=source,
            location={"type": "experience", "years": candidate_years},
            confidence=1.0
        )
        return 1.0
    
    # Partial credit for close matches
    ratio = candidate_years / jd_years if jd_years > 0 else 0.0
    return min(1.0, ratio * 0.8)  # Cap at 80% for partial matches


def match_tools(
    jd_tools: list[str],
    resume_tools: list[str],
    transcript_tools: list[str],
    weight: float,
    evidence_tracker: EvidenceTracker
) -> float:
    """Match tools/technologies"""
    if not jd_tools:
        return 1.0
    
    candidate_tools = set()
    candidate_tools.update([t.lower() for t in resume_tools])
    candidate_tools.update([t.lower() for t in transcript_tools])
    
    jd_tools_lower = [t.lower() for t in jd_tools]
    matched_tools = []
    
    for tool in jd_tools_lower:
        if tool in candidate_tools:
            matched_tools.append(tool)
            source = "resume" if tool in [t.lower() for t in resume_tools] else "transcript"
            evidence_tracker.add_evidence(
                skill=tool,
                source=source,
                location={"type": "tool_match"},
                confidence=0.9
            )
    
    match_ratio = len(matched_tools) / len(jd_tools) if jd_tools else 0.0
    return match_ratio


def match_education(
    jd_education: list[Dict],
    resume_education: list[Dict],
    transcript_education: list[Dict],
    weight: float,
    evidence_tracker: EvidenceTracker
) -> float:
    """Match education requirements"""
    if not jd_education:
        return 1.0
    
    candidate_education = resume_education + transcript_education
    
    # Simple matching: check if any JD requirement is met
    matches = 0
    for jd_req in jd_education:
        for cand_edu in candidate_education:
            if education_matches(jd_req, cand_edu):
                matches += 1
                evidence_tracker.add_evidence(
                    skill=jd_req.get("degree", "education"),
                    source="resume" if cand_edu in resume_education else "transcript",
                    location={"type": "education_match"},
                    confidence=0.9
                )
                break
    
    return matches / len(jd_education) if jd_education else 0.0


def match_projects(
    jd_project_reqs: list[Dict],
    resume_projects: list[Dict],
    transcript_projects: list[Dict],
    weight: float,
    evidence_tracker: EvidenceTracker
) -> float:
    """Match project requirements"""
    if not jd_project_reqs:
        return 1.0
    
    candidate_projects = resume_projects + transcript_projects
    
    # Match based on project types/technologies
    matches = 0
    for jd_req in jd_project_reqs:
        for cand_project in candidate_projects:
            if project_matches(jd_req, cand_project):
                matches += 1
                evidence_tracker.add_evidence(
                    skill=cand_project.get("name", "project"),
                    source="resume" if cand_project in resume_projects else "transcript",
                    location={"type": "project_match"},
                    confidence=0.8
                )
                break
    
    return matches / len(jd_project_reqs) if jd_project_reqs else 0.0


def match_roles(
    jd_role_reqs: list[Dict],
    resume_roles: list[Dict],
    transcript_roles: list[Dict],
    weight: float,
    evidence_tracker: EvidenceTracker
) -> float:
    """Match role/position requirements"""
    if not jd_role_reqs:
        return 1.0
    
    candidate_roles = resume_roles + transcript_roles
    
    matches = 0
    for jd_req in jd_role_reqs:
        for cand_role in candidate_roles:
            if role_matches(jd_req, cand_role):
                matches += 1
                evidence_tracker.add_evidence(
                    skill=cand_role.get("title", "role"),
                    source="resume" if cand_role in resume_roles else "transcript",
                    location={"type": "role_match"},
                    confidence=0.85
                )
                break
    
    return matches / len(jd_role_reqs) if jd_role_reqs else 0.0


def education_matches(jd_req: Dict, cand_edu: Dict) -> bool:
    """Check if candidate education matches JD requirement"""
    jd_degree = jd_req.get("degree", "").lower()
    cand_degree = cand_edu.get("degree", "").lower()
    
    if jd_degree and jd_degree in cand_degree:
        return True
    
    jd_field = jd_req.get("field", "").lower()
    cand_field = cand_edu.get("field", "").lower()
    
    if jd_field and jd_field in cand_field:
        return True
    
    return False


def project_matches(jd_req: Dict, cand_project: Dict) -> bool:
    """Check if candidate project matches JD requirement"""
    jd_techs = [t.lower() for t in jd_req.get("technologies", [])]
    cand_techs = [t.lower() for t in cand_project.get("technologies", [])]
    
    if jd_techs:
        # Check if any required technology is present
        return any(tech in cand_techs for tech in jd_techs)
    
    return False


def role_matches(jd_req: Dict, cand_role: Dict) -> bool:
    """Check if candidate role matches JD requirement"""
    jd_title = jd_req.get("title", "").lower()
    cand_title = cand_role.get("title", "").lower()
    
    if jd_title and jd_title in cand_title:
        return True
    
    return False

