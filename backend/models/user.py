from typing import Union # same asOptional (reminder to self)

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String
from database import Base

# SQLAlchemy model for the User table (Database model)
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    age = Column(Integer, nullable=True)

# Add password hashing and validation later with JWT
class UserCreate(BaseModel):
    email: str
    password: str
    age: Union[int, None] = None

class UserUpdate(BaseModel):
    email: Union[str, None] = None
    password: Union[str, None] = None
    age: Union[int, None] = None
    
class UserResponse(BaseModel):
    user_id: int
    email: EmailStr # Add error handling later with a proper message in the frontend
    age: Union[int, None] = None