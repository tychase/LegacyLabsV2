"""
Project schemas
"""

from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    narrator_voice: str = "documentary_male"
    video_duration: Optional[int] = None


class ProjectCreate(ProjectBase):
    gedcom_file_url: Optional[str] = None


class ProjectUpdate(ProjectBase):
    title: Optional[str] = None
    status: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    transcript: Optional[str] = None
    parsed_data: Optional[dict] = None
    story_themes: Optional[List[str]] = None
    error_message: Optional[str] = None


class ProjectInDBBase(ProjectBase):
    id: int
    owner_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    gedcom_file_url: Optional[str]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    story_themes: Optional[List[str]]

    class Config:
        from_attributes = True


class Project(ProjectInDBBase):
    pass


class ProjectDetail(ProjectInDBBase):
    transcript: Optional[str]
    parsed_data: Optional[dict]
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
