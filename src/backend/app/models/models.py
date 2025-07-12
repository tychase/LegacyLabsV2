"""
SQLAlchemy models for LegacyLabs
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    B2B_PARTNER = "b2b_partner"


class SubscriptionTier(str, enum.Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    STARTER = "starter"
    FAMILY = "family"
    LEGACY = "legacy"
    ENTERPRISE = "enterprise"


class VideoStatus(str, enum.Enum):
    """Video processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    
    # B2B Partner fields
    company_name = Column(String)
    company_type = Column(String)  # funeral_home, genealogy_service, etc.
    partner_code = Column(String, unique=True, index=True)


class Project(Base):
    """Project model - represents a family history documentary project"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # GEDCOM data
    gedcom_file_url = Column(String)
    parsed_data = Column(JSON)  # Stored parsed GEDCOM data
    
    # Story configuration
    narrator_voice = Column(String, default="documentary_male")
    video_duration = Column(Integer, default=300)  # seconds
    story_themes = Column(JSON)  # List of identified themes
    custom_settings = Column(JSON)  # User preferences
    
    # Status
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.PENDING)
    processing_started_at = Column(DateTime(timezone=True))
    processing_completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    # Output
    video_url = Column(String)
    thumbnail_url = Column(String)
    transcript = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    media_assets = relationship("MediaAsset", back_populates="project", cascade="all, delete-orphan")
    edits = relationship("ProjectEdit", back_populates="project", cascade="all, delete-orphan")


class MediaAsset(Base):
    """Media assets uploaded by users for their projects"""
    __tablename__ = "media_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    asset_type = Column(String)  # image, video, audio
    file_url = Column(String, nullable=False)
    thumbnail_url = Column(String)
    
    # Metadata
    filename = Column(String)
    file_size = Column(Integer)  # bytes
    mime_type = Column(String)
    duration = Column(Integer)  # seconds (for video/audio)
    
    # Usage in timeline
    timeline_position = Column(Integer)  # seconds into video
    display_duration = Column(Integer)  # seconds
    
    # User annotations
    caption = Column(Text)
    person_tags = Column(JSON)  # List of person IDs from GEDCOM
    date_taken = Column(DateTime)
    location = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="media_assets")


class ProjectEdit(Base):
    """Track edits made to projects"""
    __tablename__ = "project_edits"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Edit details
    edit_type = Column(String)  # transcript, media, settings, etc.
    edit_data = Column(JSON)  # Stores the actual edit
    
    # Version tracking
    version = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="edits")


class Subscription(Base):
    """User subscriptions"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Stripe data
    stripe_customer_id = Column(String, unique=True)
    stripe_subscription_id = Column(String, unique=True)
    
    # Subscription details
    tier = Column(SQLEnum(SubscriptionTier), nullable=False)
    status = Column(String)  # active, canceled, past_due, etc.
    
    # Billing
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Usage
    videos_created_this_period = Column(Integer, default=0)
    videos_limit = Column(Integer)  # null for unlimited
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscription")


class Template(Base):
    """Video templates for different story types"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    
    # Template configuration
    story_type = Column(String)  # immigration, military, large_family, etc.
    default_duration = Column(Integer)  # seconds
    scene_templates = Column(JSON)  # List of scene configurations
    music_options = Column(JSON)  # List of suitable music tracks
    
    # Availability
    is_active = Column(Boolean, default=True)
    tier_required = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.STARTER)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StockFootage(Base):
    """Library of stock footage for video generation"""
    __tablename__ = "stock_footage"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    file_url = Column(String, nullable=False)
    thumbnail_url = Column(String)
    
    # Categorization
    era = Column(String)  # 1800s, 1900s, modern, etc.
    region = Column(String)  # north_america, europe, etc.
    theme = Column(String)  # immigration, family, work, etc.
    tags = Column(JSON)  # List of tags
    
    # Technical details
    duration = Column(Integer)  # seconds
    resolution = Column(String)
    file_size = Column(Integer)  # bytes
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexing for search
    __table_args__ = (
        # Add indexes for common queries
    )
