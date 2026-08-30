from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.db.database import get_db
from app.schemas.admin import (
    AdminUserCreate,
    AdminUserResponse,
    AdminSettingCreate,
    AdminSettingUpdate,
    AdminSettingResponse,
    MatchingConfig,
    AuditLogResponse
)
from app.models.admin import AdminUser, AdminSetting, AuditLog
from app.api.deps import get_admin_user
from app.core.security import create_access_token
from app.services.admin_service import AdminService
from app.services.interview_service import InterviewService
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["admin"])

# Initialize services
admin_service = AdminService()
interview_service = InterviewService()


@router.post("/auth/login")
async def admin_login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Admin login"""
    try:
        admin_user = db.query(AdminUser).filter(AdminUser.username == username).first()
        
        if not admin_user or not admin_user.verify_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        if not admin_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": admin_user.email, "email": admin_user.email})
        
        # Ensure updated_at is set (use created_at if None)
        admin_data = {
            "id": admin_user.id,
            "username": admin_user.username,
            "email": admin_user.email,
            "is_active": admin_user.is_active,
            "created_at": admin_user.created_at,
            "updated_at": admin_user.updated_at or admin_user.created_at
        }
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "admin_user": AdminUserResponse(**admin_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in admin login: {e}")
        print(error_details)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )


@router.post("/auth/signup", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def admin_signup(
    admin_user: AdminUserCreate,
    db: Session = Depends(get_db)
):
    """
    Public admin signup - only works if no admins exist (for first admin creation).
    After first admin is created, use /admin/users endpoint (requires admin auth).
    """
    try:
        # Check if any admin exists
        existing_admin_count = db.query(AdminUser).count()
        
        if existing_admin_count > 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin signup is only allowed when no admins exist. Please contact an existing admin to create your account, or use the /admin/users endpoint with admin authentication."
            )
        
        # Check if username or email already exists
        existing = db.query(AdminUser).filter(
            (AdminUser.username == admin_user.username) |
            (AdminUser.email == admin_user.email)
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Create first admin
        db_admin = AdminUser(
            username=admin_user.username,
            email=admin_user.email
        )
        db_admin.set_password(admin_user.password)
        
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        
        # Ensure updated_at is set (use created_at if None)
        admin_data = {
            "id": db_admin.id,
            "username": db_admin.username,
            "email": db_admin.email,
            "is_active": db_admin.is_active,
            "created_at": db_admin.created_at,
            "updated_at": db_admin.updated_at or db_admin.created_at
        }
        
        return AdminUserResponse(**admin_data)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in admin signup: {e}")
        print(error_details)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating admin user: {str(e)}"
        )


@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    admin_user: AdminUserCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Create new admin user (admin only)"""
    # Check if username or email already exists
    existing = db.query(AdminUser).filter(
        (AdminUser.username == admin_user.username) |
        (AdminUser.email == admin_user.email)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    db_admin = AdminUser(
        username=admin_user.username,
        email=admin_user.email
    )
    db_admin.set_password(admin_user.password)
    
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    
    # Ensure updated_at is set (use created_at if None)
    admin_data = {
        "id": db_admin.id,
        "username": db_admin.username,
        "email": db_admin.email,
        "is_active": db_admin.is_active,
        "created_at": db_admin.created_at,
        "updated_at": db_admin.updated_at or db_admin.created_at
    }
    
    return AdminUserResponse(**admin_data)


@router.get("/settings/{jd_id}", response_model=AdminSettingResponse)
async def get_jd_settings(
    jd_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get JD-specific settings"""
    setting = db.query(AdminSetting).filter(
        AdminSetting.jd_id == jd_id,
        AdminSetting.setting_name == "matching_config"
    ).order_by(AdminSetting.version.desc()).first()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found"
        )
    
    return setting


@router.post("/settings", response_model=AdminSettingResponse, status_code=status.HTTP_201_CREATED)
async def create_setting(
    setting: AdminSettingCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Create admin setting"""
    # Get latest version
    query = db.query(AdminSetting).filter(
        AdminSetting.setting_name == setting.setting_name
    )
    
    if setting.jd_id:
        query = query.filter(AdminSetting.jd_id == setting.jd_id)
    else:
        query = query.filter(AdminSetting.jd_id == None)
    
    latest = query.order_by(AdminSetting.version.desc()).first()
    next_version = (latest.version + 1) if latest else 1
    
    db_setting = AdminSetting(
        jd_id=setting.jd_id,
        setting_name=setting.setting_name,
        setting_value=setting.setting_value,
        admin_id=current_admin.id,
        version=next_version
    )
    
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    
    # Log audit
    audit_log = AuditLog(
        admin_id=current_admin.id,
        action_type="create",
        resource_type="admin_setting",
        resource_id=db_setting.id,
        changes={"setting_name": setting.setting_name, "jd_id": setting.jd_id}
    )
    db.add(audit_log)
    db.commit()
    
    return db_setting


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get audit logs"""
    logs = db.query(AuditLog).order_by(
        AuditLog.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return logs


# ==================== Statistics & Analytics Endpoints ====================

@router.get("/stats/overview")
async def get_overview_stats(
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get dashboard overview statistics"""
    try:
        stats = admin_service.get_overview_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching overview statistics: {str(e)}"
        )


@router.get("/stats/pipeline")
async def get_pipeline_stats(
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get pipeline funnel metrics (resume uploaded -> parsed -> matched -> interview -> completed -> hired)."""
    try:
        return admin_service.get_pipeline_metrics(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching pipeline statistics: {str(e)}"
        )


@router.get("/stats/health")
async def get_system_health(
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get system health metrics (queue, latency, tokens, cost)."""
    try:
        return admin_service.get_system_health(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching system health: {str(e)}"
        )


@router.get("/stats/score-distribution")
async def get_score_distribution(
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get score distribution analytics"""
    try:
        distribution = admin_service.get_score_distribution(db)
        return distribution
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching score distribution: {str(e)}"
        )


@router.get("/analytics/question-performance")
async def get_question_performance(
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get question-level performance statistics"""
    try:
        performance = admin_service.get_question_performance(db)
        return performance
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching question performance: {str(e)}"
        )


@router.post("/matching/rematch-all")
async def rematch_all_candidates(
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Re-run matching for all candidates with resumes against all active JDs"""
    try:
        from app.models.candidate import Candidate, Resume
        from app.models.jd import JobDescription
        from app.services.matching.engine import MatchingEngine
        from app.models.matching import MatchResult
        
        # Get all candidates with resumes
        candidates = db.query(Candidate).join(Resume).distinct().all()
        
        # Get all active JDs
        jds = db.query(JobDescription).filter(
            JobDescription.current_version_id.isnot(None)
        ).all()
        
        if not jds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active job descriptions found"
            )
        
        matching_engine = MatchingEngine(db)
        matched_count = 0
        error_count = 0
        
        for candidate in candidates:
            # Get latest resume
            resume = db.query(Resume).filter(
                Resume.candidate_id == candidate.id
            ).order_by(Resume.created_at.desc()).first()
            
            if not resume or not resume.extracted_data:
                continue
            
            for jd in jds:
                try:
                    # Re-run matching (will update existing or create new)
                    match_result = await matching_engine.match_candidate_to_jd(
                        candidate_id=candidate.id,
                        jd_id=jd.id,
                        resume_data=resume.extracted_data,
                        transcript_data={},
                        session_id=None
                    )
                    
                    matched_count += 1
                except Exception as e:
                    error_count += 1
                    continue
        
        return {
            "message": "Re-matching completed",
            "candidates_processed": len(candidates),
            "matches_created": matched_count,
            "errors": error_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running re-match: {str(e)}"
        )


@router.get("/activity/recent")
async def get_recent_activity(
    limit: int = Query(3, ge=1, le=20, description="Number of recent activities to return"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get recent activity events from real data"""
    try:
        from app.models.interview import InterviewResult
        from app.models.candidate import Resume
        from app.models.jd import JobDescription
        from datetime import timedelta
        
        activities = []
        now = datetime.now()
        
        # Get recent interviews (last 2 days only, more recent)
        recent_interviews = db.query(InterviewResult).filter(
            InterviewResult.created_at >= now - timedelta(days=2)
        ).order_by(InterviewResult.created_at.desc()).limit(limit).all()
        
        for interview in recent_interviews:
            activities.append({
                "id": f"interview_{interview.id}",
                "type": "interview_completed",
                "timestamp": interview.created_at.isoformat() if interview.created_at else now.isoformat(),
                "description": f"Interview completed ({interview.percentage:.0f}%)" if interview.percentage else "Interview completed",
                "interview_id": interview.session_id,
                "user_id": interview.user_id
            })
        
        # Get recent resume uploads (last 2 days)
        from app.models.candidate import Candidate
        recent_resumes = db.query(Resume).join(Candidate).filter(
            Resume.created_at >= now - timedelta(days=2)
        ).order_by(Resume.created_at.desc()).limit(limit // 2 + 1).all()
        
        for resume in recent_resumes:
            user_id = resume.candidate.user_id if resume.candidate else None
            activities.append({
                "id": f"resume_{resume.id}",
                "type": "resume_parsed",
                "timestamp": resume.created_at.isoformat() if resume.created_at else now.isoformat(),
                "description": "Resume uploaded",
                "user_id": user_id
            })
        
        # Get recent JD creations (last 7 days)
        recent_jds = db.query(JobDescription).filter(
            JobDescription.created_at >= now - timedelta(days=7)
        ).order_by(JobDescription.created_at.desc()).limit(limit // 2 + 1).all()
        
        for jd in recent_jds:
            activities.append({
                "id": f"jd_{jd.id}",
                "type": "jd_created",
                "timestamp": jd.created_at.isoformat() if jd.created_at else now.isoformat(),
                "description": f"JD created: {jd.title}",
                "jd_id": jd.id
            })
        
        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Return only the requested limit
        return activities[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recent activity: {str(e)}"
        )


# ==================== User Rankings & Comparisons ====================

@router.get("/analytics/user-rankings")
async def get_user_rankings(
    sort_by: str = Query(
        "average_score", 
        regex="^(average_score|total_interviews|best_score|improvement|latest_score)$",
        description="Sort by: average_score, total_interviews, best_score, improvement, or latest_score"
    ),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of results to return"),
    min_interviews: int = Query(1, ge=0, description="Minimum number of interviews required"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """
    Get ranked list of users with comprehensive statistics.
    
    Returns users sorted by the specified criteria with ranking, percentile, and detailed metrics.
    """
    try:
        rankings = admin_service.get_user_rankings(
            db, 
            sort_by=sort_by, 
            limit=limit,
            min_interviews=min_interviews
        )
        return {
            "rankings": rankings,
            "total": len(rankings),
            "sort_by": sort_by,
            "min_interviews": min_interviews,
            "metadata": {
                "limit": limit,
                "returned": len(rankings)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user rankings: {str(e)}"
        )


@router.post("/analytics/compare-users")
async def compare_users(
    user_ids: List[int] = Body(
        ..., 
        description="List of user IDs to compare (2-10 users)",
        example=[1, 2, 3]
    ),
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """
    Compare multiple users side-by-side with comprehensive metrics.
    
    Compares users across multiple dimensions:
    - Average scores
    - Total interviews
    - Best scores
    - Latest scores
    - Improvement rates
    
    Returns detailed comparison with summary highlighting best performers.
    """
    try:
        if len(user_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must compare at least 2 users"
            )
        
        if len(user_ids) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot compare more than 10 users at once"
            )
        
        # Validate user IDs are unique
        if len(user_ids) != len(set(user_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate user IDs are not allowed"
            )
        
        comparison = admin_service.compare_users(db, user_ids)
        
        # Check if comparison has error
        if "error" in comparison:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=comparison["error"]
            )
        
        if not comparison.get("users"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid users found for comparison"
            )
        
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing users: {str(e)}"
        )


@router.get("/analytics/top-performers")
async def get_top_performers(
    limit: int = Query(10, ge=1, le=100, description="Number of top performers to return for each category"),
    min_interviews: int = Query(1, ge=1, description="Minimum number of interviews required"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """
    Get top performing users by various metrics.
    
    Returns top performers in multiple categories:
    - Top by average score
    - Top by best single score
    - Top by latest score
    - Most improved users
    - Most active users (most interviews)
    """
    try:
        top_performers = admin_service.get_top_performers(
            db, 
            limit=limit, 
            min_interviews=min_interviews
        )
        return {
            **top_performers,
            "metadata": {
                "limit": limit,
                "min_interviews": min_interviews,
                "categories": {
                    "top_by_average_score": len(top_performers.get("top_by_average_score", [])),
                    "top_by_best_score": len(top_performers.get("top_by_best_score", [])),
                    "top_by_latest_score": len(top_performers.get("top_by_latest_score", [])),
                    "most_improved": len(top_performers.get("most_improved", [])),
                    "most_active": len(top_performers.get("most_active", []))
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching top performers: {str(e)}"
        )


# ==================== User Management Endpoints ====================

@router.get("/users")
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search by email, username, or full name"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get all users with their interview statistics"""
    try:
        users = admin_service.get_all_users_with_stats(db, skip=skip, limit=limit, search=search)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get user details with interview history and statistics"""
    try:
        user_stats = admin_service.get_user_stats(db, user_id)
        if not user_stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get interview history
        interview_history = await interview_service.get_user_history(user_id, db)
        
        # Convert Pydantic models to dicts for JSON serialization
        interview_history_dicts = []
        for interview in interview_history:
            if hasattr(interview, 'dict'):
                interview_history_dicts.append(interview.dict())
            elif hasattr(interview, 'model_dump'):
                interview_history_dicts.append(interview.model_dump())
            else:
                # Fallback: manual conversion
                interview_history_dicts.append({
                    "session_id": interview.session_id,
                    "user_id": interview.user_id,
                    "total_score": interview.total_score,
                    "max_score": interview.max_score,
                    "percentage": interview.percentage,
                    "questions_evaluated": interview.questions_evaluated,
                    "overall_analysis": interview.overall_analysis,
                    "detailed_feedback": interview.detailed_feedback or [],
                    "strengths": interview.strengths or [],
                    "areas_for_improvement": interview.areas_for_improvement or [],
                    "recommendations": interview.recommendations or [],
                    "transcript": interview.transcript or [],
                    "created_at": interview.created_at.isoformat() if interview.created_at else None,
                    "updated_at": interview.updated_at.isoformat() if interview.updated_at else None,
                })
        
        # Get progression data
        progression = admin_service.get_user_progression(db, user_id)
        
        return {
            **user_stats,
            "interview_history": interview_history_dicts,
            "progression": progression
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user details: {str(e)}"
        )


# ==================== Interview Management Endpoints ====================

@router.get("/interviews")
async def get_all_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum score filter"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum score filter"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get all interviews with pagination and filters"""
    try:
        from app.models.interview import InterviewResult
        from sqlalchemy import and_
        
        query = db.query(InterviewResult)
        
        # Apply filters
        filters = []
        if user_id:
            filters.append(InterviewResult.user_id == user_id)
        if min_score is not None:
            filters.append(InterviewResult.percentage >= min_score)
        if max_score is not None:
            filters.append(InterviewResult.percentage <= max_score)
        
        if filters:
            query = query.filter(and_(*filters))
        
        interviews = query.order_by(
            InterviewResult.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        result = []
        for interview in interviews:
            result.append({
                "session_id": interview.session_id,
                "user_id": interview.user_id,
                "total_score": interview.total_score,
                "max_score": interview.max_score,
                "percentage": round(interview.percentage, 2) if interview.percentage else None,
                "questions_evaluated": interview.questions_evaluated,
                "created_at": interview.created_at.isoformat() if interview.created_at else None,
                "updated_at": interview.updated_at.isoformat() if interview.updated_at else None,
                "pass_status": "Pass" if (interview.percentage or 0) >= 70 else "Fail"
            })
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching interviews: {str(e)}"
        )


# IMPORTANT: These specific routes must come BEFORE /interviews/{session_id}
# FastAPI matches routes in order, so /interviews/export must be defined first
@router.get("/interviews/export")
async def export_interviews(
    format: str = Query("csv", regex="^(csv|json)$"),
    user_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Limit number of results"),
    include_transcript: bool = Query(False, description="Include transcript in export"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Export interviews to CSV or JSON"""
    try:
        from app.models.interview import InterviewResult
        from sqlalchemy import and_
        from datetime import datetime as dt
        
        query = db.query(InterviewResult)
        
        # Apply filters
        filters = []
        if user_id:
            filters.append(InterviewResult.user_id == user_id)
        if start_date:
            try:
                start_dt = dt.fromisoformat(start_date)
                filters.append(InterviewResult.created_at >= start_dt)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use YYYY-MM-DD"
                )
        if end_date:
            try:
                end_dt = dt.fromisoformat(end_date)
                filters.append(InterviewResult.created_at <= end_dt)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use YYYY-MM-DD"
                )
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Order first (required before limit/offset in SQLAlchemy)
        query = query.order_by(InterviewResult.created_at.desc())
        
        # Apply limit if provided
        if limit:
            query = query.limit(limit)
        
        interviews = query.all()
        
        if format == "json":
            result = []
            for interview in interviews:
                interview_data = {
                    "session_id": interview.session_id,
                    "user_id": interview.user_id,
                    "total_score": interview.total_score,
                    "max_score": interview.max_score,
                    "percentage": interview.percentage,
                    "questions_evaluated": interview.questions_evaluated,
                    "created_at": interview.created_at.isoformat() if interview.created_at else None,
                    "pass_status": "Pass" if (interview.percentage or 0) >= 70 else "Fail",
                    "has_transcript": interview.transcript is not None and len(interview.transcript) > 0 if interview.transcript else False
                }
                
                # Include transcript if requested
                if include_transcript and interview.transcript:
                    interview_data["transcript"] = interview.transcript
                
                result.append(interview_data)
            return {"interviews": result, "count": len(result)}
        
        elif format == "csv":
            import csv
            import json
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            headers = [
                "Session ID", "User ID", "Total Score", "Max Score", 
                "Percentage", "Questions Evaluated", "Pass Status", "Created At", "Has Transcript"
            ]
            if include_transcript:
                headers.append("Transcript (JSON)")
            writer.writerow(headers)
            
            # Write data
            for interview in interviews:
                row = [
                    interview.session_id,
                    interview.user_id,
                    interview.total_score,
                    interview.max_score,
                    interview.percentage,
                    interview.questions_evaluated,
                    "Pass" if (interview.percentage or 0) >= 70 else "Fail",
                    interview.created_at.isoformat() if interview.created_at else "",
                    "Yes" if (interview.transcript and len(interview.transcript) > 0) else "No"
                ]
                if include_transcript:
                    if interview.transcript:
                        row.append(json.dumps(interview.transcript))
                    else:
                        row.append("")
                writer.writerow(row)
            
            from fastapi.responses import Response
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=interviews_export.csv"}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting interviews: {str(e)}"
        )


@router.get("/interviews/transcript-status")
async def get_transcript_status(
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get statistics about which interviews have transcripts"""
    try:
        from app.models.interview import InterviewResult
        from sqlalchemy import func, case
        
        total = db.query(func.count(InterviewResult.id)).scalar()
        
        with_transcript = db.query(func.count(InterviewResult.id)).filter(
            InterviewResult.transcript.isnot(None)
        ).scalar()
        
        without_transcript = total - with_transcript if total else 0
        
        # Get breakdown by date
        breakdown = db.query(
            func.date(InterviewResult.created_at).label('date'),
            func.count(InterviewResult.id).label('total'),
            func.sum(
                case((InterviewResult.transcript.isnot(None), 1), else_=0)
            ).label('with_transcript')
        ).group_by(
            func.date(InterviewResult.created_at)
        ).order_by(
            func.date(InterviewResult.created_at).desc()
        ).limit(30).all()
        
        return {
            "total_interviews": total or 0,
            "with_transcript": with_transcript or 0,
            "without_transcript": without_transcript,
            "percentage_with_transcript": round((with_transcript / total * 100), 2) if total and total > 0 else 0,
            "daily_breakdown": [
                {
                    "date": str(row.date),
                    "total": row.total,
                    "with_transcript": row.with_transcript or 0,
                    "without_transcript": (row.total - (row.with_transcript or 0))
                }
                for row in breakdown
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching transcript status: {str(e)}"
        )


# This parameterized route must come AFTER all specific routes
@router.get("/interviews/{session_id}")
async def get_interview_details(
    session_id: str,
    db: Session = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    """Get detailed interview information"""
    try:
        # Get interview result - admin can view any interview (user_id=None allows admin access)
        result = await interview_service.get_session_result(
            session_id=session_id,
            user_id=None,  # None = admin can view any user's interview
            db=db
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching interview details: {str(e)}"
        )


