from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

import uuid
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

# TODO: Add password hashing and validation later with JWT
class UserCreate(BaseModel):
    email: str
    password: str
    age: Optional[int] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    age: Optional[int] = None
    
class UserResponse(BaseModel):
    user_id: uuid.UUID
    email: EmailStr  # TODO: Add proper error handling for email validation later
    age: Optional[int] = None
