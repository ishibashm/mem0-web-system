from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Topic, User
from app.schemas import TopicBase, TopicInDB
from app.utils.auth import get_current_user

router = APIRouter(tags=["トピック"])

@router.post("/", response_model=TopicInDB)
async def create_topic(
    topic_data: TopicBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """新規トピックを作成"""
    new_topic = Topic(
        name=topic_data.name,
        description=topic_data.description,
        scope=topic_data.scope,
        user_id=current_user.id
    )
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    
    return new_topic

@router.get("/", response_model=List[TopicInDB])
async def get_topics(
    skip: int = 0,
    limit: int = 100,
    scope: str = "personal",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ユーザーのトピックを取得"""
    topics = db.query(Topic).filter(
        Topic.user_id == current_user.id,
        Topic.scope == scope
    ).order_by(Topic.created_at.desc()).offset(skip).limit(limit).all()
    
    return topics

@router.get("/{topic_id}", response_model=TopicInDB)
async def get_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """特定のトピックを取得"""
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.user_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="トピックが見つかりません"
        )
    
    return topic

@router.put("/{topic_id}", response_model=TopicInDB)
async def update_topic(
    topic_id: int,
    topic_data: TopicBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """トピックを更新"""
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.user_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="トピックが見つかりません"
        )
    
    topic.name = topic_data.name
    topic.description = topic_data.description
    topic.scope = topic_data.scope
    
    db.commit()
    db.refresh(topic)
    
    return topic

@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """トピックを削除"""
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.user_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="トピックが見つかりません"
        )
    
    db.delete(topic)
    db.commit()
    
    return None
