from functools import wraps
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM


def auth_required(route_handler):
    @wraps(route_handler)
    def wrapper(*args, request: Request, **kwargs):
        
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_email = payload.get("sub")
            if not user_email:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        kwargs['user_email'] = user_email
        return route_handler(*args, **kwargs)
    
    return wrapper