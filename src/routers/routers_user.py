from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.core.auth import create_access_token, get_current_user, hash_password, verify_password
from database.database import get_db
from src import models
from src.schemas import TokenResponse, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/api/v1", tags=["Auth & Users"])


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(dto: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.login == dto.login).first()
    if existing:
        raise HTTPException(status_code=409, detail="Логин уже занят")

    new_user = models.User(
        login=dto.login,
        password_hash=hash_password(dto.password),
        first_name=dto.first_name,
        last_name=dto.last_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/auth/login", response_model=TokenResponse)
def login(dto: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.login == dto.login).first()
    if not user or not verify_password(dto.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = create_access_token(data={"sub": str(user.id), "login": user.login})
    return {"access_token": token, "token_type": "Bearer"}


@router.get("/users/by-login/{login}", response_model=UserResponse)
def get_user_by_login(
    login: str,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.login == login).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.get("/users/search")
def search_users(
    query: str,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    pattern = f"%{query}%"
    users = (
        db.query(models.User)
        .filter(or_(models.User.first_name.ilike(pattern), models.User.last_name.ilike(pattern)))
        .all()
    )
    matches = [
        {"id": str(u.id), "login": u.login, "first_name": u.first_name, "last_name": u.last_name}
        for u in users
    ]
    return {"items": matches, "total": len(matches)}