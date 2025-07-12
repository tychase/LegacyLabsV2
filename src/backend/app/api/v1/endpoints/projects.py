"""
Projects endpoints
"""

from typing import Any, List
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.crud import crud_project
from app.models.models import User, Project
from app.schemas import project as project_schema
from app.services.gedcom_processor import process_gedcom_file
from app.services.video_generator import generate_documentary
from app.utils.s3 import upload_file_to_s3

router = APIRouter()


@router.get("/", response_model=List[project_schema.Project])
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve user's projects
    """
    projects = crud_project.project.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return projects


@router.post("/", response_model=project_schema.Project)
async def create_project(
    *,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_active_user),
    title: str = Form(...),
    description: str = Form(None),
    gedcom_file: UploadFile = File(...),
) -> Any:
    """
    Create new project with GEDCOM file upload
    """
    # Validate file extension
    if not gedcom_file.filename.lower().endswith(('.ged', '.gedcom')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a GEDCOM file (.ged or .gedcom)"
        )
    
    # Check file size
    contents = await gedcom_file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(gedcom_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Upload to S3
    try:
        gedcom_url = await upload_file_to_s3(
            file_content=contents,
            file_name=f"gedcom/{current_user.id}/{unique_filename}",
            content_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    # Create project in database
    project_in = project_schema.ProjectCreate(
        title=title,
        description=description,
        gedcom_file_url=gedcom_url
    )
    project = crud_project.project.create_with_owner(
        db=db, obj_in=project_in, owner_id=current_user.id
    )
    
    # Process GEDCOM file in background
    background_tasks.add_task(
        process_project_async,
        project_id=project.id,
        gedcom_content=contents.decode('utf-8')
    )
    
    return project


@router.get("/{project_id}", response_model=project_schema.ProjectDetail)
def read_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get project by ID
    """
    project = crud_project.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return project


@router.delete("/{project_id}")
def delete_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a project
    """
    project = crud_project.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    crud_project.project.remove(db=db, id=project_id)
    return {"message": "Project deleted successfully"}


async def process_project_async(project_id: int, gedcom_content: str):
    """
    Background task to process GEDCOM file and generate video
    """
    from app.db.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Update project status to processing
        project = crud_project.project.get(db=db, id=project_id)
        if not project:
            return
        
        crud_project.project.update(
            db=db,
            db_obj=project,
            obj_in={"status": "processing"}
        )
        
        # Process GEDCOM file
        parsed_data = await process_gedcom_file(gedcom_content)
        
        # Update project with parsed data
        crud_project.project.update(
            db=db,
            db_obj=project,
            obj_in={
                "parsed_data": parsed_data,
                "story_themes": parsed_data.get("narrative_themes", [])
            }
        )
        
        # Generate video documentary
        video_result = await generate_documentary(
            project_id=project_id,
            parsed_data=parsed_data,
            title=project.title
        )
        
        # Update project with video results
        crud_project.project.update(
            db=db,
            db_obj=project,
            obj_in={
                "status": "completed",
                "video_url": video_result["video_url"],
                "thumbnail_url": video_result["thumbnail_url"],
                "transcript": video_result["transcript"],
                "video_duration": video_result["duration"]
            }
        )
        
    except Exception as e:
        # Update project status to failed
        if project:
            crud_project.project.update(
                db=db,
                db_obj=project,
                obj_in={
                    "status": "failed",
                    "error_message": str(e)
                }
            )
    finally:
        db.close()
