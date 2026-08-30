from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from app.models.user import User
from app.models.interview import InterviewResult
from app.models.qa import QAPair
from app.models.candidate import Resume
from app.models.matching import MatchResult


class AdminService:
    """Service for admin dashboard statistics and analytics"""
    
    def __init__(self):
        pass
    
    def get_overview_stats(self, db: Session) -> Dict[str, Any]:
        """Get dashboard overview statistics"""
        try:
            # Total users
            total_users = db.query(User).count()
            active_users = db.query(User).filter(
                User.is_active == True
            ).count()
            
            # Total interviews
            total_interviews = db.query(InterviewResult).count()
            
            # Recent interviews
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            interviews_today = db.query(InterviewResult).filter(
                InterviewResult.created_at >= today_start
            ).count()
            
            interviews_this_week = db.query(InterviewResult).filter(
                InterviewResult.created_at >= week_ago
            ).count()
            
            interviews_this_month = db.query(InterviewResult).filter(
                InterviewResult.created_at >= month_ago
            ).count()
            
            # Score statistics
            score_stats = db.query(
                func.avg(InterviewResult.percentage).label('avg_score'),
                func.min(InterviewResult.percentage).label('min_score'),
                func.max(InterviewResult.percentage).label('max_score'),
                func.count(InterviewResult.id).label('total')
            ).first()
            
            avg_score = float(score_stats.avg_score) if score_stats.avg_score else 0.0
            min_score = float(score_stats.min_score) if score_stats.min_score else 0.0
            max_score = float(score_stats.max_score) if score_stats.max_score else 0.0
            
            # Pass rate (score >= 70)
            pass_count = db.query(InterviewResult).filter(
                InterviewResult.percentage >= 70
            ).count()
            pass_rate = (pass_count / total_interviews * 100) if total_interviews > 0 else 0
            
            # Active users (taken interview in last 30 days)
            active_user_ids = db.query(InterviewResult.user_id).filter(
                InterviewResult.created_at >= month_ago
            ).distinct().count()
            
            # Average interviews per user
            avg_interviews_per_user = (total_interviews / total_users) if total_users > 0 else 0
            
            # Avg interview duration: not stored per-interview; use 0 or placeholder
            avg_interview_duration = 0

            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_interviews": total_interviews,
                "interviews_today": interviews_today,
                "interviews_this_week": interviews_this_week,
                "interviews_this_month": interviews_this_month,
                "average_score": round(avg_score, 2),
                "avg_score": round(avg_score, 2),
                "min_score": round(min_score, 2),
                "max_score": round(max_score, 2),
                "pass_rate": round(pass_rate, 2),
                "pass_count": pass_count,
                "fail_count": total_interviews - pass_count,
                "active_users_30d": active_user_ids,
                "avg_interviews_per_user": round(avg_interviews_per_user, 2),
                "avg_interview_duration": avg_interview_duration,
            }
        except Exception as e:
            print(f"Error getting overview stats: {e}")
            import traceback
            traceback.print_exc()
            # Return default values on error
            return {
                "total_users": 0,
                "active_users": 0,
                "total_interviews": 0,
                "interviews_today": 0,
                "interviews_this_week": 0,
                "interviews_this_month": 0,
                "average_score": 0.0,
                "avg_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0,
                "pass_rate": 0.0,
                "pass_count": 0,
                "fail_count": 0,
                "active_users_30d": 0,
                "avg_interviews_per_user": 0.0,
                "avg_interview_duration": 0,
            }

    def get_pipeline_metrics(self, db: Session) -> Dict[str, Any]:
        """Get pipeline funnel metrics from DB (resume uploaded -> parsed -> matched -> interview -> completed -> hired)."""
        try:
            resume_uploaded = db.query(Resume).count()
            parsed = db.query(Resume).filter(
                (Resume.extracted_data.isnot(None)) | (Resume.raw_text.isnot(None))
            ).count()
            matched = db.query(MatchResult).count()
            total_interviews = db.query(InterviewResult).count()
            completed = total_interviews
            hired_recommended = db.query(InterviewResult).filter(
                InterviewResult.percentage >= 70
            ).count()
            return {
                "resume_uploaded": resume_uploaded,
                "parsed": parsed,
                "matched": matched,
                "interview_started": total_interviews,
                "completed": completed,
                "hired_recommended": hired_recommended,
            }
        except Exception as e:
            print(f"Error getting pipeline metrics: {e}")
            return {
                "resume_uploaded": 0,
                "parsed": 0,
                "matched": 0,
                "interview_started": 0,
                "completed": 0,
                "hired_recommended": 0,
            }

    def get_system_health(self, db: Session) -> Dict[str, Any]:
        """Get system health metrics. Queue/latency/tokens/cost are placeholders if not tracked."""
        try:
            return {
                "queue_size": 0,
                "failure_rate": 0.0,
                "avg_latency_ms": 0,
                "token_usage_today": 0,
                "cost_today": 0.0,
                "uptime_status": "healthy",
            }
        except Exception as e:
            print(f"Error getting system health: {e}")
            return {
                "queue_size": 0,
                "failure_rate": 0.0,
                "avg_latency_ms": 0,
                "token_usage_today": 0,
                "cost_today": 0.0,
                "uptime_status": "healthy",
            }

    def get_user_stats(self, db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Get user's interviews
            interviews = db.query(InterviewResult).filter(
                InterviewResult.user_id == user_id
            ).order_by(InterviewResult.created_at.desc()).all()
            
            total_interviews = len(interviews)
            
            if total_interviews > 0:
                scores = [i.percentage or 0 for i in interviews if i.percentage is not None]
                avg_score = sum(scores) / len(scores) if scores else 0
                best_score = max(scores) if scores else 0
                worst_score = min(scores) if scores else 0
            else:
                avg_score = 0
                best_score = 0
                worst_score = 0
            
            # Get latest interview
            latest_interview = interviews[0] if interviews else None
            
            # Get first interview date
            first_interview = interviews[-1] if interviews else None
            
            # Calculate improvement (if multiple interviews)
            improvement = None
            if len(interviews) >= 2:
                first_score = interviews[-1].percentage or 0
                latest_score = interviews[0].percentage or 0
                improvement = round(latest_score - first_score, 2)
            
            return {
                "user_id": user_id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "total_interviews": total_interviews,
                "average_score": round(avg_score, 2),
                "best_score": round(best_score, 2),
                "worst_score": round(worst_score, 2),
                "latest_interview_date": latest_interview.created_at.isoformat() if latest_interview else None,
                "latest_score": round(latest_interview.percentage, 2) if latest_interview and latest_interview.percentage else None,
                "first_interview_date": first_interview.created_at.isoformat() if first_interview else None,
                "improvement": improvement
            }
        except Exception as e:
            print(f"Error getting user stats: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_all_users_with_stats(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all users with their interview statistics"""
        try:
            query = db.query(User)
            
            # Add search filter if provided
            if search:
                search_filter = or_(
                    User.email.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
            
            users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
            
            result = []
            for user in users:
                # Count interviews for this user
                interview_count = db.query(InterviewResult).filter(
                    InterviewResult.user_id == user.id
                ).count()
                
                # Get average score
                avg_score_result = db.query(
                    func.avg(InterviewResult.percentage)
                ).filter(
                    InterviewResult.user_id == user.id
                ).first()
                
                avg_score = float(avg_score_result[0]) if avg_score_result[0] else 0.0
                
                # Get latest interview date
                latest_interview = db.query(InterviewResult).filter(
                    InterviewResult.user_id == user.id
                ).order_by(InterviewResult.created_at.desc()).first()
                
                # Get best score
                best_interview = db.query(InterviewResult).filter(
                    InterviewResult.user_id == user.id,
                    InterviewResult.percentage.isnot(None)
                ).order_by(InterviewResult.percentage.desc()).first()
                best_score = round(best_interview.percentage, 2) if best_interview and best_interview.percentage else None
                
                # Get latest score
                latest_score = round(latest_interview.percentage, 2) if latest_interview and latest_interview.percentage else None
                
                result.append({
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "total_interviews": interview_count,
                    "average_score": round(avg_score, 2) if avg_score > 0 else None,
                    "best_score": best_score,
                    "latest_score": latest_score,
                    "latest_interview_date": latest_interview.created_at.isoformat() if latest_interview else None
                })
            
            return result
        except Exception as e:
            print(f"Error getting all users with stats: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_score_distribution(self, db: Session) -> Dict[str, Any]:
        """Get score distribution analytics"""
        try:
            # Get all scores
            scores = db.query(InterviewResult.percentage).filter(
                InterviewResult.percentage.isnot(None)
            ).all()
            
            score_values = [float(s[0]) for s in scores if s[0] is not None]
            
            if not score_values:
                return {
                    "total": 0,
                    "ranges": {
                        "0-20": 0,
                        "21-40": 0,
                        "41-60": 0,
                        "61-80": 0,
                        "81-100": 0
                    }
                }
            
            # Count by ranges
            ranges = {
                "0-20": len([s for s in score_values if 0 <= s <= 20]),
                "21-40": len([s for s in score_values if 21 <= s <= 40]),
                "41-60": len([s for s in score_values if 41 <= s <= 60]),
                "61-80": len([s for s in score_values if 61 <= s <= 80]),
                "81-100": len([s for s in score_values if 81 <= s <= 100])
            }
            
            return {
                "total": len(score_values),
                "ranges": ranges,
                "average": round(sum(score_values) / len(score_values), 2),
                "median": round(sorted(score_values)[len(score_values) // 2], 2) if score_values else 0
            }
        except Exception as e:
            print(f"Error getting score distribution: {e}")
            import traceback
            traceback.print_exc()
            return {"total": 0, "ranges": {}}
    
    def get_question_performance(self, db: Session) -> List[Dict[str, Any]]:
        """Get question-level performance statistics"""
        try:
            # Get all Q&A pairs with scores
            qa_pairs = db.query(QAPair).filter(
                QAPair.score.isnot(None)
            ).all()
            
            # Group by question (using first 100 chars as key)
            question_stats = {}
            for qa in qa_pairs:
                question_key = qa.question[:100]  # Use first 100 chars as key
                
                if question_key not in question_stats:
                    question_stats[question_key] = {
                        "question": qa.question,
                        "count": 0,
                        "scores": [],
                        "average_score": 0
                    }
                
                question_stats[question_key]["count"] += 1
                if qa.score is not None:
                    question_stats[question_key]["scores"].append(qa.score)
            
            # Calculate averages
            result = []
            for key, stats in question_stats.items():
                if stats["scores"]:
                    avg_score = sum(stats["scores"]) / len(stats["scores"])
                    stats["average_score"] = round(avg_score, 2)
                    stats["min_score"] = min(stats["scores"])
                    stats["max_score"] = max(stats["scores"])
                else:
                    stats["average_score"] = 0
                    stats["min_score"] = 0
                    stats["max_score"] = 0
                
                result.append(stats)
            
            # Sort by count (most asked first)
            result.sort(key=lambda x: x["count"], reverse=True)
            
            return result[:50]  # Return top 50 questions
        except Exception as e:
            print(f"Error getting question performance: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_user_progression(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Get user's score progression over time"""
        try:
            interviews = db.query(InterviewResult).filter(
                InterviewResult.user_id == user_id,
                InterviewResult.percentage.isnot(None)
            ).order_by(InterviewResult.created_at.asc()).all()
            
            progression = []
            for interview in interviews:
                progression.append({
                    "session_id": interview.session_id,
                    "date": interview.created_at.isoformat() if interview.created_at else None,
                    "score": round(interview.percentage, 2) if interview.percentage else 0,
                    "total_score": interview.total_score,
                    "max_score": interview.max_score
                })
            
            return progression
        except Exception as e:
            print(f"Error getting user progression: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_user_rankings(
        self, 
        db: Session, 
        sort_by: str = "average_score",
        limit: int = 50,
        min_interviews: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get ranked list of users with comprehensive statistics.
        
        Args:
            db: Database session
            sort_by: Sort criteria - 'average_score', 'total_interviews', 'best_score', 
                    'improvement', or 'latest_score'
            limit: Maximum number of results to return
            min_interviews: Minimum number of interviews required to be included
            
        Returns:
            List of user dictionaries with ranking information
        """
        try:
            # Validate sort_by parameter
            valid_sort_options = ["average_score", "total_interviews", "best_score", "improvement", "latest_score"]
            if sort_by not in valid_sort_options:
                sort_by = "average_score"  # Default to average_score
            
            # Get all users with stats (with higher limit to allow filtering)
            users = self.get_all_users_with_stats(db, skip=0, limit=10000)
            
            # Filter users with at least min_interviews
            users_with_interviews = [
                u for u in users 
                if u["total_interviews"] >= min_interviews
            ]
            
            # Calculate additional metrics for each user
            for user in users_with_interviews:
                user_id = user["id"]
                
                try:
                    # Get best score
                    best_interview = db.query(InterviewResult).filter(
                        InterviewResult.user_id == user_id,
                        InterviewResult.percentage.isnot(None)
                    ).order_by(InterviewResult.percentage.desc()).first()
                    user["best_score"] = round(best_interview.percentage, 2) if best_interview and best_interview.percentage else 0.0
                    
                    # Get latest score
                    latest_interview = db.query(InterviewResult).filter(
                        InterviewResult.user_id == user_id,
                        InterviewResult.percentage.isnot(None)
                    ).order_by(InterviewResult.created_at.desc()).first()
                    user["latest_score"] = round(latest_interview.percentage, 2) if latest_interview and latest_interview.percentage else 0.0
                    
                    # Calculate improvement
                    progression = self.get_user_progression(db, user_id)
                    if len(progression) >= 2:
                        first_score = progression[0]["score"]
                        last_score = progression[-1]["score"]
                        user["improvement"] = round(last_score - first_score, 2)
                        user["improvement_percentage"] = round(
                            ((last_score - first_score) / first_score * 100) if first_score > 0 else 0, 
                            2
                        )
                    else:
                        user["improvement"] = 0.0
                        user["improvement_percentage"] = 0.0
                except Exception as e:
                    # If error calculating metrics for one user, set defaults and continue
                    print(f"Error calculating metrics for user {user_id}: {e}")
                    user["best_score"] = 0.0
                    user["latest_score"] = 0.0
                    user["improvement"] = 0.0
                    user["improvement_percentage"] = 0.0
            
            # Sort by specified criteria
            if sort_by == "average_score":
                users_with_interviews.sort(key=lambda x: x.get("average_score", 0), reverse=True)
            elif sort_by == "total_interviews":
                users_with_interviews.sort(key=lambda x: x.get("total_interviews", 0), reverse=True)
            elif sort_by == "best_score":
                users_with_interviews.sort(key=lambda x: x.get("best_score", 0), reverse=True)
            elif sort_by == "improvement":
                users_with_interviews.sort(key=lambda x: x.get("improvement", 0), reverse=True)
            elif sort_by == "latest_score":
                users_with_interviews.sort(key=lambda x: x.get("latest_score", 0), reverse=True)
            
            # Add ranking and percentile
            total_users = len(users_with_interviews)
            for idx, user in enumerate(users_with_interviews[:limit], 1):
                user["rank"] = idx
                # Calculate percentile (higher rank = higher percentile)
                if total_users > 0:
                    user["percentile"] = round((1 - (idx - 1) / total_users) * 100, 2)
                else:
                    user["percentile"] = 0.0
            
            return users_with_interviews[:limit]
        except Exception as e:
            print(f"Error getting user rankings: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def compare_users(
        self, 
        db: Session, 
        user_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Compare multiple users side-by-side with comprehensive metrics.
        
        Args:
            db: Database session
            user_ids: List of user IDs to compare (2-10 users)
            
        Returns:
            Dictionary containing user data, metrics, and comparison summary
        """
        try:
            if not user_ids or len(user_ids) < 2:
                return {
                    "users": [],
                    "metrics": {},
                    "comparison_summary": {},
                    "error": "At least 2 user IDs required"
                }
            
            if len(user_ids) > 10:
                return {
                    "users": [],
                    "metrics": {},
                    "comparison_summary": {},
                    "error": "Cannot compare more than 10 users at once"
                }
            
            comparison = {
                "users": [],
                "metrics": {
                    "average_scores": [],
                    "total_interviews": [],
                    "best_scores": [],
                    "latest_scores": [],
                    "improvements": []
                },
                "comparison_summary": {}
            }
            
            for user_id in user_ids:
                try:
                    user_stats = self.get_user_stats(db, user_id)
                    if not user_stats:
                        continue  # Skip invalid users
                    
                    # Get additional metrics
                    progression = self.get_user_progression(db, user_id)
                    
                    # Get best and latest scores
                    interviews = db.query(InterviewResult).filter(
                        InterviewResult.user_id == user_id,
                        InterviewResult.percentage.isnot(None)
                    ).all()
                    
                    scores = [float(i.percentage) for i in interviews if i.percentage is not None]
                    best_score = max(scores) if scores else 0.0
                    latest_score = scores[0] if scores else 0.0
                    
                    # Calculate improvement
                    improvement = 0.0
                    improvement_percentage = 0.0
                    if len(progression) >= 2:
                        first_score = progression[0]["score"]
                        last_score = progression[-1]["score"]
                        improvement = last_score - first_score
                        if first_score > 0:
                            improvement_percentage = round((improvement / first_score) * 100, 2)
                    
                    user_comparison = {
                        **user_stats,
                        "best_score": round(best_score, 2),
                        "latest_score": round(latest_score, 2),
                        "improvement": round(improvement, 2),
                        "improvement_percentage": improvement_percentage,
                        "progression": progression
                    }
                    
                    comparison["users"].append(user_comparison)
                    comparison["metrics"]["average_scores"].append(user_stats["average_score"])
                    comparison["metrics"]["total_interviews"].append(user_stats["total_interviews"])
                    comparison["metrics"]["best_scores"].append(round(best_score, 2))
                    comparison["metrics"]["latest_scores"].append(round(latest_score, 2))
                    comparison["metrics"]["improvements"].append(round(improvement, 2))
                except Exception as e:
                    print(f"Error processing user {user_id} in comparison: {e}")
                    continue  # Skip this user and continue with others
            
            # Calculate comparison summary
            if comparison["users"] and comparison["metrics"]["average_scores"]:
                metrics = comparison["metrics"]
                
                # Find best performers
                best_avg_idx = metrics["average_scores"].index(max(metrics["average_scores"])) if metrics["average_scores"] else 0
                most_interviews_idx = metrics["total_interviews"].index(max(metrics["total_interviews"])) if metrics["total_interviews"] else 0
                best_single_idx = metrics["best_scores"].index(max(metrics["best_scores"])) if metrics["best_scores"] else 0
                most_improved_idx = metrics["improvements"].index(max(metrics["improvements"])) if metrics["improvements"] else 0
                
                comparison["comparison_summary"] = {
                    "best_average_score": {
                        "value": round(max(metrics["average_scores"]), 2) if metrics["average_scores"] else 0,
                        "user_index": best_avg_idx,
                        "user_email": comparison["users"][best_avg_idx]["email"] if best_avg_idx < len(comparison["users"]) else None
                    },
                    "most_interviews": {
                        "value": max(metrics["total_interviews"]) if metrics["total_interviews"] else 0,
                        "user_index": most_interviews_idx,
                        "user_email": comparison["users"][most_interviews_idx]["email"] if most_interviews_idx < len(comparison["users"]) else None
                    },
                    "best_single_score": {
                        "value": round(max(metrics["best_scores"]), 2) if metrics["best_scores"] else 0,
                        "user_index": best_single_idx,
                        "user_email": comparison["users"][best_single_idx]["email"] if best_single_idx < len(comparison["users"]) else None
                    },
                    "most_improved": {
                        "value": round(max(metrics["improvements"]), 2) if metrics["improvements"] else 0,
                        "user_index": most_improved_idx,
                        "user_email": comparison["users"][most_improved_idx]["email"] if most_improved_idx < len(comparison["users"]) else None
                    },
                    "average_of_all": {
                        "average_score": round(
                            sum(metrics["average_scores"]) / len(metrics["average_scores"]), 
                            2
                        ) if metrics["average_scores"] else 0,
                        "total_interviews": round(
                            sum(metrics["total_interviews"]) / len(metrics["total_interviews"]), 
                            2
                        ) if metrics["total_interviews"] else 0,
                        "best_score": round(
                            sum(metrics["best_scores"]) / len(metrics["best_scores"]), 
                            2
                        ) if metrics["best_scores"] else 0
                    }
                }
            
            return comparison
        except Exception as e:
            print(f"Error comparing users: {e}")
            import traceback
            traceback.print_exc()
            return {
                "users": [],
                "metrics": {},
                "comparison_summary": {},
                "error": str(e)
            }
    
    def get_top_performers(
        self, 
        db: Session, 
        limit: int = 10,
        min_interviews: int = 1
    ) -> Dict[str, Any]:
        """
        Get top performing users by various metrics.
        
        Args:
            db: Database session
            limit: Number of top performers to return for each category
            min_interviews: Minimum interviews required to be included
            
        Returns:
            Dictionary with top performers in different categories
        """
        try:
            # Top by average score
            top_by_score = self.get_user_rankings(
                db, 
                sort_by="average_score", 
                limit=limit * 2,  # Get more to filter
                min_interviews=min_interviews
            )
            top_by_score = [u for u in top_by_score if u["total_interviews"] >= min_interviews][:limit]
            
            # Top by best score
            top_by_best = self.get_user_rankings(
                db, 
                sort_by="best_score", 
                limit=limit * 2,
                min_interviews=min_interviews
            )
            top_by_best = [u for u in top_by_best if u["total_interviews"] >= min_interviews][:limit]
            
            # Top by latest score
            top_by_latest = self.get_user_rankings(
                db, 
                sort_by="latest_score", 
                limit=limit * 2,
                min_interviews=min_interviews
            )
            top_by_latest = [u for u in top_by_latest if u["total_interviews"] >= min_interviews][:limit]
            
            # Most improved (users with multiple interviews showing improvement)
            users = db.query(User).all()
            most_improved = []
            for user in users:
                try:
                    progression = self.get_user_progression(db, user.id)
                    if len(progression) >= 2:
                        first_score = progression[0]["score"]
                        last_score = progression[-1]["score"]
                        improvement = last_score - first_score
                        if improvement > 0:
                            user_stats = self.get_user_stats(db, user.id)
                            if user_stats and user_stats["total_interviews"] >= min_interviews:
                                improvement_percentage = round(
                                    ((last_score - first_score) / first_score * 100) if first_score > 0 else 0, 
                                    2
                                )
                                most_improved.append({
                                    "user_id": user.id,
                                    "email": user.email,
                                    "username": user.username,
                                    "full_name": user.full_name,
                                    "improvement": round(improvement, 2),
                                    "improvement_percentage": improvement_percentage,
                                    "first_score": round(first_score, 2),
                                    "latest_score": round(last_score, 2),
                                    "total_interviews": user_stats["total_interviews"],
                                    "average_score": user_stats["average_score"]
                                })
                except Exception as e:
                    print(f"Error processing user {user.id} for most improved: {e}")
                    continue
            
            most_improved.sort(key=lambda x: x["improvement"], reverse=True)
            
            # Most active (most interviews)
            top_by_activity = self.get_user_rankings(
                db, 
                sort_by="total_interviews", 
                limit=limit,
                min_interviews=min_interviews
            )
            
            return {
                "top_by_average_score": top_by_score,
                "top_by_best_score": top_by_best,
                "top_by_latest_score": top_by_latest,
                "most_improved": most_improved[:limit],
                "most_active": top_by_activity
            }
        except Exception as e:
            print(f"Error getting top performers: {e}")
            import traceback
            traceback.print_exc()
            return {
                "top_by_average_score": [],
                "top_by_best_score": [],
                "top_by_latest_score": [],
                "most_improved": [],
                "most_active": []
            }

