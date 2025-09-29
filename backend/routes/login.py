from fastapi import APIRouter, HTTPException, Depends, Response, status
from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.user import User

from database import get_db, pwd_context
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, MAX_BCRYPT_LEN
from models.login import LoginRequest


router = APIRouter()

# TODO: Transfer to services later and map columns properly
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:MAX_BCRYPT_LEN], hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    # Sets expiration time for the token
    # TODO: Add remember me functionality later
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    jwt_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token

@router.post("/login/")
def login(login_request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_request.email).first()
    if user and verify_password(login_request.password, user.hashed_password):
        print("Received password:", repr(login_request.password)) # Backend debugging
        access_token = create_access_token(data={"sub": user.email})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",  # TODO: Adjust based on requirements
            secure=False    # TODO: Set to True in production with HTTPS  
        )
        return {"message": "Login successful"}
    # TODO: Handle invalid logins better later
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # TODO: Add more error handling later

@router.post("/logout/")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}