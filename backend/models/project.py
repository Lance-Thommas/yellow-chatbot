from typing import Optional
from pydantic import BaseModel
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

import uuid
from sqlalchemy.dialects.postgresql import UUID

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_active: Mapped[int] = mapped_column(default=1)  # 1 for active, 0 for inactive

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    owner_id: uuid.UUID
    is_active: int
    
    class Config:
        from_attributes = True
