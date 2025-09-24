from fastapi import APIRouter, HTTPException, Depends
from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.user import User

from database import get_db, PWD_CONTEXT, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models.login import LoginRequest


router = APIRouter()


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)  

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    # Sets expiration time for the token
    # Add remember me functionality later
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    jwt_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token

@router.post("/login/")
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_request.email).first()
    if user and verify_password(login_request.password, user.hashed_password):
        # Generate JWT token
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    # Handle invalid logins better later
    raise HTTPException(status_code=401, detail="Invalid credentials")
    # Add more error handling later

