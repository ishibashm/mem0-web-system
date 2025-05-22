from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, UserSettings
from app.schemas import UserOut, UserUpdate
from app.utils.auth import get_current_user

router = APIRouter(tags=["ユーザー"])

@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return current_user

@router.put("/me", response_model=UserOut)
async def update_user_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ユーザー情報を更新"""
    if user_data.mem0_api_key is not None:
        current_user.mem0_api_key = user_data.mem0_api_key
    
    if user_data.llm_api_key is not None:
        current_user.llm_api_key = user_data.llm_api_key
    
    if user_data.llm_provider is not None:
        current_user.llm_provider = user_data.llm_provider
    
    if user_data.settings:
        user_settings = db.query(UserSettings).filter(
            UserSettings.user_id == current_user.id
        ).first()
        
        if not user_settings:
            user_settings = UserSettings(user_id=current_user.id)
            db.add(user_settings)
        
        for key, value in user_data.settings.dict(exclude_unset=True).items():
            setattr(user_settings, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
