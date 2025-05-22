from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.utils.auth import get_current_user
from app.database import get_db
from app.models import User, UserSettings
from app.schemas import UserSettings as UserSettingsSchema, UserSettingsUpdate

router = APIRouter(tags=["設定"])

@router.get("/", response_model=UserSettingsSchema)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ユーザー設定を取得"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not settings:
        settings = UserSettings(
            user_id=current_user.id,
            language_preference="ja"  # 日本語をデフォルトに設定
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings

@router.put("/", response_model=UserSettingsSchema)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ユーザー設定を更新"""
    db_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not db_settings:
        db_settings = UserSettings(user_id=current_user.id)
        db.add(db_settings)
    
    for key, value in settings_update.dict(exclude_unset=True).items():
        setattr(db_settings, key, value)
    
    db.commit()
    db.refresh(db_settings)
    
    return db_settings
