from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.auth import get_current_user
from database.database import get_db
from src import models
from src.schemas import FileCreate, FileOut, FolderCreate, FolderOut

router = APIRouter(prefix="/api/v1", tags=["Folders & Files"])


# --- ПАПКИ ---


@router.post("/folders", response_model=FolderOut, status_code=status.HTTP_201_CREATED)
def create_folder(
    dto: FolderCreate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    existing = (
        db.query(models.Folder)
        .filter(models.Folder.user_id == current_user.id, models.Folder.name == dto.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Папка с таким именем уже есть")

    folder = models.Folder(name=dto.name, user_id=current_user.id)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


@router.get("/folders", response_model=List[FolderOut])
def get_user_folders(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    return db.query(models.Folder).filter(models.Folder.user_id == current_user.id).all()


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(
    folder_id: UUID,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    folder = (
        db.query(models.Folder)
        .filter(models.Folder.id == folder_id, models.Folder.user_id == current_user.id)
        .first()
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Папка не найдена")

    # В Postgres настроен ON DELETE CASCADE — файлы внутри удалятся автоматически
    db.delete(folder)
    db.commit()


# --- ФАЙЛЫ ---


@router.post("/folders/{folder_id}/files", response_model=FileOut, status_code=status.HTTP_201_CREATED)
def add_file_to_folder(
    folder_id: UUID,
    dto: FileCreate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    folder = (
        db.query(models.Folder)
        .filter(models.Folder.id == folder_id, models.Folder.user_id == current_user.id)
        .first()
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Целевая папка не найдена")

    new_file = models.File(
        name=dto.name,
        size_bytes=dto.size_bytes,
        mime_type=dto.mime_type,
        folder_id=folder_id,
        user_id=current_user.id,
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file


@router.get("/folders/{folder_id}/files", response_model=List[FileOut])
def get_folder_files(
    folder_id: UUID,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    folder = (
        db.query(models.Folder)
        .filter(models.Folder.id == folder_id, models.Folder.user_id == current_user.id)
        .first()
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Папка не найдена")

    return (
        db.query(models.File)
        .filter(models.File.folder_id == folder_id, models.File.user_id == current_user.id)
        .all()
    )


@router.get("/files/search", response_model=List[FileOut])
def search_files(
    name: str,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    pattern = f"%{name}%"
    return (
        db.query(models.File)
        .filter(models.File.user_id == current_user.id, models.File.name.ilike(pattern))
        .all()
    )


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: UUID,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    file_record = (
        db.query(models.File)
        .filter(models.File.id == file_id, models.File.user_id == current_user.id)
        .first()
    )
    if not file_record:
        raise HTTPException(status_code=404, detail="Файл не найден")

    db.delete(file_record)
    db.commit()