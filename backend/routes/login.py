from fastapi import APIRouter, HTTPException
from models.login import LoginRequest
from jose import JWTError, jwt
from datetime import datetime, timedelta


router = APIRouter()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
def login(login_request: LoginRequest):
    # Placeholder for actual authentication logic
    # fetch user from database
    # Verify credentials against postgres database
    if login_request.email == "user@example.com" and login_request.password == "password":
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate and return JWT token later

