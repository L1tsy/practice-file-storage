from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class UserRegister(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    login: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    login: str
    first_name: str
    last_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class FolderCreate(BaseModel):
    name: str


class FolderOut(BaseModel):
    id: UUID
    name: str
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileCreate(BaseModel):
    name: str
    size_bytes: int
    mime_type: str


class FileOut(BaseModel):
    id: UUID
    folder_id: UUID
    user_id: UUID
    name: str
    size_bytes: int
    mime_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)