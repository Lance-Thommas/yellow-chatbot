from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from database import get_db

from models.user import UserCreate, UserResponse, User
from passlib.context import CryptContext
from config import MAX_BCRYPT_LEN

router = APIRouter()
# TODO: Move to database.py later
# TODO: change from bcrypt to keccak and hash salting
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password[:MAX_BCRYPT_LEN])

@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    # save user to database with hashed password
    hashed_password = hash_password(user.password)
    new_user = User(
        email=user.email, 
        hashed_password=hashed_password,
        )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # TODO: Recheck this later, mapped manually for now
    return new_user
