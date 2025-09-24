from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.orm import Session
from database import SessionLocal

from models.user import UserCreate, UserResponse, User
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str):
    return pwd_context.hash(password)

@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # save user to database with hashed password
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, age=user.age)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Recheck this later, and remove comment once checked.
    return {
        "user_id": new_user.id,
        "email": new_user.email,
        "age": new_user.age
    }

    # (Trapped) Error reading bcrypt version, missing __about__, check this too
