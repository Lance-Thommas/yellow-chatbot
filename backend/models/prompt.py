from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text
from database import Base
from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
class PromptCreate(BaseModel):
    project_id: uuid.UUID
    name: str
    description: Optional[str] = None
    content: str
    
class PromptResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: Optional[str] = None
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
class PromptRun(Base):
    __tablename__ = "prompt_runs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, primary_key=True, index=True)
    prompt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prompts.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    input_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # TODO: Implement status enum later (e.g., pending, completed, failed)
    status: Mapped[str] = mapped_column(String, default="pending")  
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    cost: Mapped[Optional[float]] = mapped_column(nullable=True, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
class PromptRunResponse(BaseModel):
    id: uuid.UUID
    prompt_id: uuid.UUID
    user_id: uuid.UUID
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    status: str
    tokens_used: Optional[int] = 0
    cost: Optional[float] = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True