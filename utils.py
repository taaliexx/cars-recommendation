from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status, Request
from globals import SECRET_KEY, ALGORITHM

def create_access_token(data: dict, expires_delta: timedelta):
    """Создаёт JWT-токен с истечением времени."""
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token_from_cookie(request: Request):
    """Извлекает и проверяет JWT токен из куки."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("access_token")  # Получаем токен из куки
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        dealer_id: str = payload.get("sub")
        if dealer_id is None:
            raise credentials_exception
        return dealer_id
    except JWTError:
        raise credentials_exception
