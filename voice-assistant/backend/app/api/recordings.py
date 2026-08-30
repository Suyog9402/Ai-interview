from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
from app.db.database import get_db
from app.schemas.recording import RecordingResponse, TranscriptResponse, ProcessingRequest, ProcessingResponse
from app.models.recording import Recording, Transcript
from app.models.candidate import Candidate
from app.api.deps import get_current_active_user
from app.services.storage import get_storage
from app.workflows.interview_pipeline import build_interview_pipeline
from app.workflows.state import InterviewPipelineState
import uuid
import os
import re
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recordings", tags=["recordings"])


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be filesystem-safe.
    Removes special characters and replaces spaces with underscores.
    """
    if not name:
        return "unknown"
    # Remove special characters, keep only alphanumeric, spaces, hyphens, underscores
    sanitized = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces and multiple underscores/hyphens with single underscore
    sanitized = re.sub(r'[\s_-]+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    # Limit length to avoid filesystem issues
    return sanitized[:50] if sanitized else "unknown"


@router.post("/{candidate_id}/upload", response_model=RecordingResponse, status_code=status.HTTP_201_CREATED)
async def upload_recording(
    candidate_id: int,
    file: UploadFile = File(...),
    session_id: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Upload interview recording"""
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Get candidate name for folder structure (fallback to email if name not available)
    candidate_name = candidate.full_name if candidate.full_name else candidate.email.split('@')[0]
    sanitized_name = sanitize_filename(candidate_name)
    
    # Store file with candidate name in path
    storage = get_storage()
    file_path = f"recordings/{candidate_id}_{sanitized_name}/{session_id}/{file.filename}"
    
    # Read file content
    file_content = await file.read()
    
    # Upload to storage
    import io
    file_obj = io.BytesIO(file_content)
    stored_path = await storage.upload_file(
        file_content=file_obj,
        file_path=file_path,
        metadata={"filename": file.filename, "content_type": file.content_type}
    )
    
    # Generate HTTP URL (use relative path, not full stored_path)
    video_url = await storage.get_file_url(file_path)
    
    # Create recording record
    # Use relative file_path, not the full stored_path
    db_recording = Recording(
        candidate_id=candidate_id,
        session_id=session_id,
        file_path=file_path,  # Relative path (e.g., "recordings/123/session_abc/video.mp4")
        video_url=video_url,  # HTTP URL
        format="audio" if file.content_type and "audio" in file.content_type else "video",
        file_size_bytes=len(file_content),
        storage_provider="local"
    )
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    
    return db_recording


@router.post("/process", response_model=ProcessingResponse)
async def process_recording(
    request: ProcessingRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Process recording through LangGraph workflow"""
    try:
        # Get recording
        recording = db.query(Recording).filter(
            Recording.candidate_id == request.candidate_id,
            Recording.session_id == request.session_id
        ).first()
        
        if not recording:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recording not found"
            )
        
        # Build workflow state
        initial_state: InterviewPipelineState = {
            "candidate_id": request.candidate_id,
            "session_id": request.session_id,
            "recording_id": recording.id,
            "jd_id": request.jd_id,
            "recording_stored": False,
            "transcription_complete": False,
            "extraction_complete": False,
            "matching_complete": False,
            "rag_complete": False,
            "memory_updated": False,
            "recording_path": recording.file_path,
            "transcript_data": None,
            "extracted_resume_data": None,
            "extracted_transcript_data": None,
            "match_result": None,
            "rag_results": None,
            "next_steps": None,
            "should_continue": True,
            "error_message": None,
            "quality_issues": [],
            "retry_count": 0,
            "processing_metadata": {}
        }
        
        # Run workflow
        workflow = build_interview_pipeline()
        config = {"configurable": {"thread_id": request.session_id}}
        
        # Execute workflow
        final_state = None
        async for state in workflow.astream(initial_state, config):
            final_state = state
        
        if not final_state:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Workflow execution failed"
            )
        
        # Extract results
        match_result_id = None
        if final_state.get("match_result"):
            match_result_id = final_state["match_result"].get("id")
        
        return ProcessingResponse(
            session_id=request.session_id,
            status="completed" if not final_state.get("error_message") else "failed",
            current_stage="completed",
            error_message=final_state.get("error_message"),
            match_result_id=match_result_id,
            next_steps=final_state.get("next_steps")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process recording: {str(e)}"
        )


@router.get("/files/{file_path:path}")
async def serve_recording_file(
    file_path: str,
    db: Session = Depends(get_db)
):
    """
    Serve video/audio files from local storage.
    Works globally if your server is accessible.
    """
    from app.core.config import settings
    
    storage = get_storage()
    
    # Security: Only serve files from storage directory
    storage_path = Path(settings.storage_local_path) / file_path
    storage_base = Path(settings.storage_local_path).resolve()
    
    # Prevent directory traversal attacks
    try:
        storage_path = storage_path.resolve()
        if not str(storage_path).startswith(str(storage_base)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid path"
        )
    
    if not storage_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Determine content type
    content_type = "video/mp4"
    if file_path.endswith(".mp3") or file_path.endswith(".wav"):
        content_type = "audio/mpeg"
    elif file_path.endswith(".webm"):
        content_type = "video/webm"
    elif file_path.endswith(".m4a"):
        content_type = "audio/mp4"
    
    # Return file with proper headers
    return FileResponse(
        path=storage_path,
        media_type=content_type,
        filename=storage_path.name,
        headers={
            "Content-Disposition": f'inline; filename="{storage_path.name}"'
        }
        )


@router.get("/{recording_id}/transcript", response_model=TranscriptResponse)
async def get_transcript(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get transcript for a recording"""
    transcript = db.query(Transcript).filter(Transcript.recording_id == recording_id).first()
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found"
        )
    return transcript


@router.post("/webhook/egress")
async def egress_webhook(
    event: dict,
    db: Session = Depends(get_db)
):
    """
    AUTOMATIC: LiveKit calls this when recording finishes
    Downloads video and saves to your local system automatically
    """
    import httpx
    import io
    from app.services.storage import get_storage
    from app.models.recording import Recording
    from datetime import datetime
    
    # LiveKit sends this event when recording completes
    if event.get("event") == "egress_ended":
        egress_info = event.get("egress", {})
        file_outputs = egress_info.get("file_outputs", [])
        
        if not file_outputs:
            logger.error("No file outputs in egress event")
            return {"status": "error", "message": "No file outputs"}
        
        # Extract session info from filepath
        livekit_filepath = file_outputs[0].get("filepath", "")
        # Format: "recordings/{candidate_id}/{session_id}/interview.mp4"
        parts = livekit_filepath.split("/")
        
        if len(parts) >= 3:
            try:
                candidate_id = int(parts[1])
                session_id = parts[2]
            except (ValueError, IndexError):
                # Fallback: try to extract from room name
                room_name = event.get("room", {}).get("name", "")
                session_id = room_name.replace("interview_", "").replace("voice_assistant_room_", "")
                # Try to find candidate by session_id in database
                existing_recording = db.query(Recording).filter(
                    Recording.session_id == session_id
                ).first()
                if existing_recording:
                    candidate_id = existing_recording.candidate_id
                else:
                    logger.error(f"Could not determine candidate_id for session {session_id}")
                    return {"status": "error", "message": "Could not determine candidate_id"}
        else:
            # Fallback: extract from room name or event metadata
            room_name = event.get("room", {}).get("name", "")
            session_id = room_name.replace("interview_", "").replace("voice_assistant_room_", "")
            # Try to find candidate by session_id in database
            existing_recording = db.query(Recording).filter(
                Recording.session_id == session_id
            ).first()
            if existing_recording:
                candidate_id = existing_recording.candidate_id
            else:
                logger.error(f"Could not determine candidate_id for session {session_id}")
                return {"status": "error", "message": "Could not determine candidate_id"}
        
        logger.info(f"📥 Downloading recording for session {session_id}, candidate {candidate_id}")
        
        # Download video from LiveKit
        livekit_url = os.getenv("LIVEKIT_URL", "").replace("wss://", "https://").replace("ws://", "http://")
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        # Get download URL from LiveKit
        egress_id = egress_info.get("egress_id")
        
        try:
            async with httpx.AsyncClient() as client:
                # Try to get file URL from egress info
                file_url = file_outputs[0].get("url")
                
                if not file_url and egress_id:
                    # Alternative: get egress info to find download URL
                    download_url = f"{livekit_url}/twirp/livekit.Egress/GetEgress"
                    headers = {
                        "Authorization": f"Bearer {api_key}:{api_secret}"
                    }
                    response = await client.post(
                        download_url,
                        headers=headers,
                        json={"egress_id": egress_id}
                    )
                    if response.status_code == 200:
                        egress_data = response.json()
                        file_url = egress_data.get("file_outputs", [{}])[0].get("url")
                
                if not file_url:
                    # Last resort: construct download URL
                    file_url = f"{livekit_url}/egress/{livekit_filepath}"
                
                # Download the video file
                logger.info(f"⬇️ Downloading from: {file_url}")
                headers = {}
                if api_key and api_secret:
                    headers["Authorization"] = f"Bearer {api_key}:{api_secret}"
                
                video_response = await client.get(file_url, headers=headers, timeout=300.0)
                video_response.raise_for_status()
                video_data = video_response.content
            
            logger.info(f"✅ Downloaded {len(video_data)} bytes")
            
            # Save to LOCAL storage (your system)
            storage = get_storage()
            storage_path = f"recordings/{candidate_id}/{session_id}/interview.mp4"
            video_stream = io.BytesIO(video_data)
            
            local_file_path = await storage.upload_file(
                file_content=video_stream,
                file_path=storage_path,
                metadata={"content_type": "video/mp4", "source": "livekit_egress"}
            )
            
            logger.info(f"💾 Saved to local storage: {local_file_path}")
            
            # Generate HTTP URL
            video_url = await storage.get_file_url(storage_path)
            
            # Save metadata to database
            recording = Recording(
                candidate_id=candidate_id,
                session_id=session_id,
                file_path=storage_path,
                video_url=video_url,
                format="video",
                duration_seconds=egress_info.get("duration", 0),
                file_size_bytes=len(video_data),
                storage_provider="local"
            )
            
            db.add(recording)
            db.commit()
            db.refresh(recording)
            
            logger.info(f"✅ Recording saved to database with ID: {recording.id}")
            
            return {
                "status": "ok",
                "recording_id": recording.id,
                "video_url": video_url,
                "local_path": local_file_path
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing egress webhook: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    return {"status": "ignored"}

