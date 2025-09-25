from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, DateTime
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