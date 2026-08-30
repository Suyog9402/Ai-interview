"""
Sync JobDescription from DB to filesystem so RAG (match-jds) and interview (select-jd) can use them.
Writes jd/{slug}.txt and interview_questions/{slug}.txt; optionally reloads RAG vector store.
"""
import os
import re
from typing import Optional
from sqlalchemy.orm import Session, joinedload

# Default interview questions template when creating a new JD question file
DEFAULT_QUESTIONS_TEMPLATE = """Tell me about yourself and your background.
What interests you about this role?
Describe your relevant experience for this position.
What are your key strengths?
What is your greatest professional achievement?
Where do you see yourself in 5 years?
Do you have any questions for us?
"""


def _slug_from_title(title: str, jd_id: int) -> str:
    """Produce a filesystem-safe slug from JD title. Ensures uniqueness with jd_id if needed."""
    if not (title or "").strip():
        return f"jd_{jd_id}"
    s = re.sub(r"[^\w\s-]", "", (title or "").strip())
    s = s.lower().replace(" ", "_").replace("-", "_")
    s = re.sub(r"_+", "_", s).strip("_")
    return s or f"jd_{jd_id}"


def get_backend_dirs():
    """Return (backend_dir, jd_dir, questions_dir)."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    jd_dir = os.path.join(backend_dir, "jd")
    questions_dir = os.path.join(backend_dir, "interview_questions")
    return backend_dir, jd_dir, questions_dir


def sync_jd_to_disk(db: Session, jd_id: int, reload_rag: bool = True) -> Optional[str]:
    """
    Sync a JobDescription (with its current active version) to:
    - jd/{slug}.txt  (content for RAG and match-jds)
    - interview_questions/{slug}.txt (questions for interview; created from template if missing)

    Returns the jd_filename (e.g. "backend_developer_senior.txt") on success, None on failure.
    """
    from app.models.jd import JobDescription, JDVersion

    jd = (
        db.query(JobDescription)
        .options(joinedload(JobDescription.current_version))
        .filter(JobDescription.id == jd_id)
        .first()
    )
    if not jd or not jd.current_version:
        return None

    # Only sync JDs that are open (is_active) – closed jobs are not available to candidates
    if not jd.current_version.is_active:
        slug = _slug_from_title(jd.title, jd.id)
        jd_filename = f"{slug}.txt"
        remove_jd_from_disk(jd_id, jd_filename)
        if reload_rag:
            try:
                from app.services.rag_service import rag_service
                rag_service.load_job_descriptions()
            except Exception as e:
                print(f"Warning: could not reload RAG after removing closed JD: {e}")
        return None

    _, jd_dir, questions_dir = get_backend_dirs()
    os.makedirs(jd_dir, exist_ok=True)
    os.makedirs(questions_dir, exist_ok=True)

    slug = _slug_from_title(jd.title, jd.id)
    jd_filename = f"{slug}.txt"
    jd_path = os.path.join(jd_dir, jd_filename)
    questions_path = os.path.join(questions_dir, jd_filename)

    # Write JD content to jd/
    content = (jd.current_version.content or "").strip() or "(No content)"
    with open(jd_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Ensure interview_questions file exists (create template if missing)
    if not os.path.exists(questions_path):
        with open(questions_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_QUESTIONS_TEMPLATE.strip())

    if reload_rag:
        try:
            from app.services.rag_service import rag_service
            rag_service.load_job_descriptions()
        except Exception as e:
            print(f"Warning: could not reload RAG after JD sync: {e}")

    return jd_filename


def remove_jd_from_disk(jd_id: int, slug_or_filename: Optional[str] = None) -> None:
    """Remove jd/{slug}.txt and interview_questions/{slug}.txt for a given JD (e.g. on delete)."""
    if not slug_or_filename:
        return
    filename = slug_or_filename if slug_or_filename.endswith(".txt") else f"{slug_or_filename}.txt"
    _, jd_dir, questions_dir = get_backend_dirs()
    for d in (jd_dir, questions_dir):
        path = os.path.join(d, filename)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Warning: could not remove {path}: {e}")
