from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dnd2024-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 uur

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, db: Session) -> models.User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub", 0))
    except JWTError:
        raise HTTPException(status_code=401, detail="Ongeldige of verlopen token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Gebruiker niet gevonden")
    return user


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(
        (models.User.username == username) | (models.User.email == username)
    ).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    user.last_login = datetime.utcnow()
    db.commit()
    return user
