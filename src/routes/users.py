from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.upload_avatar import UploadService
from src.conf.config import settings
from src.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch('/avatar', response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    public_id = UploadService.create_name_avatar(current_user.email, "contacts_base")

    r = UploadService.upload(file.file, public_id)

    src_url = UploadService.get_url_avatar(public_id, r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
