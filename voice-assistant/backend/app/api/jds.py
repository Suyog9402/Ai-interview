from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.jd import JDCreate, JDUpdate, JDResponse, JDVersionCreate, JDVersionResponse
from app.models.jd import JobDescription, JDVersion
from app.api.deps import get_admin_user
from app.services.jd_sync import sync_jd_to_disk, remove_jd_from_disk
import re

router = APIRouter(prefix="/jds", tags=["job_descriptions"])


@router.post("", response_model=JDResponse, status_code=status.HTTP_201_CREATED)
async def create_jd(
    jd: JDCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Create new JD (admin only)"""
    try:
        db_jd = JobDescription(
            title=jd.title,
            description=jd.description,
            admin_id=admin_user.id
        )
        db.add(db_jd)
        db.flush()
        
        # Create initial version
        db_version = JDVersion(
            jd_id=db_jd.id,
            version_number=1,
            content=jd.content,
            requirements=jd.requirements,
            admin_id=admin_user.id,
            is_active=True
        )
        db.add(db_version)
        db_jd.current_version_id = db_version.id
        
        db.commit()
        db.refresh(db_jd)
        try:
            sync_jd_to_disk(db, db_jd.id, reload_rag=True)
        except Exception as sync_err:
            print(f"Warning: JD sync after create failed: {sync_err}")
        return db_jd
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create JD: {str(e)}"
        )


@router.get("", response_model=List[JDResponse])
async def list_jds(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all job descriptions"""
    from sqlalchemy.orm import joinedload
    
    jds = db.query(JobDescription).options(
        joinedload(JobDescription.current_version)
    ).offset(skip).limit(limit).all()
    return jds


@router.get("/{jd_id}", response_model=JDResponse)
async def get_jd(
    jd_id: int,
    db: Session = Depends(get_db)
):
    """Get JD by ID with all versions"""
    from sqlalchemy.orm import joinedload
    
    jd = db.query(JobDescription).options(
        joinedload(JobDescription.versions),
        joinedload(JobDescription.current_version)
    ).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    return jd


@router.put("/{jd_id}", response_model=JDResponse)
async def update_jd(
    jd_id: int,
    jd_update: JDUpdate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Update JD (admin only)"""
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    update_data = jd_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(jd, field, value)
    
    db.commit()
    db.refresh(jd)
    return jd


@router.post("/{jd_id}/versions", response_model=JDVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_jd_version(
    jd_id: int,
    version: JDVersionCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Create new JD version (admin only)"""
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    # Deactivate current version
    current_version = db.query(JDVersion).filter(
        JDVersion.jd_id == jd_id,
        JDVersion.is_active == True
    ).first()
    if current_version:
        current_version.is_active = False
    
    # Create new version
    db_version = JDVersion(
        jd_id=jd_id,
        version_number=version.version_number,
        content=version.content,
        requirements=version.requirements,
        admin_id=admin_user.id,
        is_active=version.is_active
    )
    db.add(db_version)
    
    if version.is_active:
        jd.current_version_id = db_version.id
    
    db.commit()
    db.refresh(db_version)
    try:
        sync_jd_to_disk(db, jd_id, reload_rag=True)
    except Exception as sync_err:
        print(f"Warning: JD sync after new version failed: {sync_err}")
    return db_version


@router.post("/upload", response_model=JDResponse, status_code=status.HTTP_201_CREATED)
async def upload_jd_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Upload JD from .txt file (admin only)"""
    if not file.filename or not file.filename.lower().endswith('.txt'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt files are allowed"
        )
    
    try:
        # Read file content
        content_bytes = await file.read()
        content_str = content_bytes.decode('utf-8')
        
        # Create JD using existing create_jd logic
        jd_create = JDCreate(
            title=title,
            description=description,
            content=content_str,
            requirements=None  # Can be auto-extracted later
        )
        
        # Reuse create_jd logic
        db_jd = JobDescription(
            title=jd_create.title,
            description=jd_create.description,
            admin_id=admin_user.id
        )
        db.add(db_jd)
        db.flush()
        
        # Create initial version
        db_version = JDVersion(
            jd_id=db_jd.id,
            version_number=1,
            content=jd_create.content,
            requirements=jd_create.requirements,
            admin_id=admin_user.id,
            is_active=True
        )
        db.add(db_version)
        db_jd.current_version_id = db_version.id
        
        db.commit()
        db.refresh(db_jd)
        try:
            sync_jd_to_disk(db, db_jd.id, reload_rag=True)
        except Exception as sync_err:
            print(f"Warning: JD sync after upload failed: {sync_err}")
        return db_jd
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be UTF-8 encoded text"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload JD: {str(e)}"
        )


@router.delete("/{jd_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_jd(
    jd_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Delete JD (admin only)"""
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    slug = (re.sub(r"[^\w\s-]", "", (jd.title or "").strip()).lower().replace(" ", "_").replace("-", "_") or f"jd_{jd_id}").strip("_")
    slug = re.sub(r"_+", "_", slug) or f"jd_{jd_id}"
    filename = f"{slug}.txt"
    try:
        db.delete(jd)
        db.commit()
        remove_jd_from_disk(jd_id, filename)
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete JD: {str(e)}"
        )


@router.patch("/{jd_id}/reopen", response_model=JDResponse)
async def reopen_jd(
    jd_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Reopen a closed job by activating its current version (admin only)"""
    from sqlalchemy.orm import joinedload

    jd = db.query(JobDescription).options(
        joinedload(JobDescription.current_version)
    ).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    if not jd.current_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job has no version to reopen. Add a version first."
        )

    # Deactivate any other active version
    db.query(JDVersion).filter(
        JDVersion.jd_id == jd_id,
        JDVersion.is_active == True
    ).update({JDVersion.is_active: False})

    # Activate current version
    jd.current_version.is_active = True

    db.commit()
    db.refresh(jd)
    try:
        sync_jd_to_disk(db, jd_id, reload_rag=True)
    except Exception as sync_err:
        print(f"Warning: JD sync after reopen failed: {sync_err}")
    return jd


@router.patch("/{jd_id}/versions/{version_id}/activate", response_model=JDResponse)
async def activate_version(
    jd_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Activate a specific JD version (admin only)"""
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    # Verify version belongs to this JD
    version = db.query(JDVersion).filter(
        JDVersion.id == version_id,
        JDVersion.jd_id == jd_id
    ).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found for this job description"
        )
    
    try:
        # Deactivate current version
        current_version = db.query(JDVersion).filter(
            JDVersion.jd_id == jd_id,
            JDVersion.is_active == True
        ).first()
        if current_version:
            current_version.is_active = False
        
        # Activate requested version
        version.is_active = True
        jd.current_version_id = version_id
        
        db.commit()
        db.refresh(jd)
        try:
            sync_jd_to_disk(db, jd_id, reload_rag=True)
        except Exception as sync_err:
            print(f"Warning: JD sync after activate version failed: {sync_err}")
        return jd
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate version: {str(e)}"
        )

