from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


def check_hard_filters(
    jd_requirements: Dict[str, Any],
    resume_data: Dict[str, Any],
    transcript_data: Dict[str, Any],
    settings: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Check hard filters (must-have requirements).
    
    Args:
        jd_requirements: Job description requirements
        resume_data: Extracted resume data
        transcript_data: Extracted transcript data
        settings: Matching settings
    
    Returns:
        Tuple of (passed, failure_reasons)
    """
    failures = []
    
    # Must-have skills
    required_skills = jd_requirements.get("must_have_skills", [])
    if required_skills:
        candidate_skills = extract_skills(resume_data, transcript_data)
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        
        for skill in required_skills:
            if skill.lower() not in candidate_skills_lower:
                failures.append(f"Missing required skill: {skill}")
    
    # Minimum experience
    min_years = jd_requirements.get("min_experience_years", 0)
    if min_years > 0:
        total_years = calculate_experience(resume_data, transcript_data)
        if total_years < min_years:
            failures.append(
                f"Insufficient experience: {total_years} years < required {min_years} years"
            )
    
    # Required qualifications
    required_qualifications = jd_requirements.get("required_qualifications", [])
    if required_qualifications:
        candidate_education = extract_education(resume_data, transcript_data)
        for qual in required_qualifications:
            if not has_qualification(candidate_education, qual):
                failures.append(f"Missing required qualification: {qual}")
    
    # Required tools/technologies
    required_tools = jd_requirements.get("must_have_tools", [])
    if required_tools:
        candidate_tools = extract_tools(resume_data, transcript_data)
        candidate_tools_lower = [t.lower() for t in candidate_tools]
        
        for tool in required_tools:
            if tool.lower() not in candidate_tools_lower:
                failures.append(f"Missing required tool: {tool}")
    
    passed = len(failures) == 0
    if not passed:
        logger.info(f"Hard filters failed: {failures}")
    
    return passed, failures


def extract_skills(resume_data: Dict, transcript_data: Dict) -> List[str]:
    """Extract skills from resume and transcript data"""
    skills = set()
    
    if resume_data:
        skills.update(resume_data.get("skills", []))
        # Also extract from roles and projects
        for role in resume_data.get("roles", []):
            if "description" in role:
                # Could do additional NLP here to extract skills from descriptions
                pass
    
    if transcript_data:
        skills.update(transcript_data.get("skills", []))
    
    return list(skills)


def extract_tools(resume_data: Dict, transcript_data: Dict) -> List[str]:
    """Extract tools/technologies from resume and transcript data"""
    tools = set()
    
    if resume_data:
        tools.update(resume_data.get("tools", []))
        # Extract from projects
        for project in resume_data.get("projects", []):
            tools.update(project.get("technologies", []))
    
    if transcript_data:
        tools.update(transcript_data.get("tools", []))
        for project in transcript_data.get("projects", []):
            tools.update(project.get("technologies", []))
    
    return list(tools)


def calculate_experience(resume_data: Dict, transcript_data: Dict) -> float:
    """Calculate total years of experience"""
    # First try explicit experience_years
    if resume_data and resume_data.get("experience_years"):
        return float(resume_data["experience_years"])
    
    if transcript_data and transcript_data.get("experience_years"):
        return float(transcript_data["experience_years"])
    
    # Calculate from roles
    total_years = 0.0
    all_roles = []
    
    if resume_data:
        all_roles.extend(resume_data.get("roles", []))
    if transcript_data:
        all_roles.extend(transcript_data.get("roles", []))
    
    # Simple calculation: sum up role durations
    # This is a simplified version - in production, you'd handle overlaps
    for role in all_roles:
        start_date = role.get("start_date")
        end_date = role.get("end_date", "present")
        
        if start_date:
            try:
                # Parse dates (simplified - would need proper date parsing)
                if end_date.lower() == "present":
                    # Use current date
                    import datetime
                    end_date = datetime.datetime.now().strftime("%Y-%m")
                
                # Calculate years (simplified)
                start_year = int(start_date.split("-")[0])
                end_year = int(end_date.split("-")[0])
                years = end_year - start_year
                total_years += max(0, years)
            except Exception:
                pass
    
    return total_years


def extract_education(resume_data: Dict, transcript_data: Dict) -> List[Dict]:
    """Extract education information"""
    education = []
    
    if resume_data:
        education.extend(resume_data.get("education", []))
    
    if transcript_data:
        education.extend(transcript_data.get("education", []))
    
    return education


def has_qualification(education: List[Dict], qualification: str) -> bool:
    """Check if candidate has a specific qualification"""
    qualification_lower = qualification.lower()
    
    for edu in education:
        degree = edu.get("degree", "").lower()
        field = edu.get("field", "").lower()
        
        if qualification_lower in degree or qualification_lower in field:
            return True
    
    return False

