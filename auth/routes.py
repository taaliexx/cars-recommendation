from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from utils import create_access_token
from models import Dealer
from database import get_db
import bcrypt
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from globals import ACCESS_TOKEN_EXPIRE_MINUTES
import logging 

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register_dealer(name: str, email: str, password: str, db: Session = Depends(get_db)):
    """Регистрация нового дилера."""
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    dealer = Dealer(name=name, email=email, password_hash=hashed_password)
    db.add(dealer)
    db.commit()
    return {"message": "Dealer registered successfully!"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), response: Response = None):
    """Аутентификация пользователя и выдача JWT-токена, добавление токена в cookies."""
    dealer = db.query(Dealer).filter(Dealer.email == form_data.username).first()
    if not dealer or not bcrypt.checkpw(form_data.password.encode(), dealer.password_hash.encode()):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Генерация токена
    access_token = create_access_token(
        data={"sub": str(dealer.id)}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Добавляем токен в куки
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, max_age=3600)
    
    # Возвращаем успешный ответ, не включая токен в теле
    return {"message": "Login successful"}

@router.post("/logout")
async def logout(response: Response):
    """
    Выход, удаление cookies.
    """
    response.delete_cookie(key="access_token")  # Удаляем куку с токеном
    return {"message": "Successfully logged out"}