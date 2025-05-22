from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Memory, User, Tag, Topic
from app.schemas import Memory as MemorySchema, MemoryCreate, SearchRequest
from app.utils.auth import get_current_user

try:
    from mem0ai import MemoryClient
except ImportError:
    class MemoryClient:
        def __init__(self, api_key=None):
            self.api_key = api_key
        
        def search(self, query, **kwargs):
            return []
        
        def add(self, content, **kwargs):
            return {"id": "mock-id", "content": content}

router = APIRouter(tags=["メモリ"])

@router.post("/", response_model=MemorySchema)
async def create_memory(
    memory_data: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """新規メモリを作成"""
    if memory_data.topic_id:
        topic = db.query(Topic).filter(
            Topic.id == memory_data.topic_id,
            Topic.user_id == current_user.id
        ).first()
        
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指定されたトピックが見つかりません"
            )
    
    if current_user.mem0_api_key:
        try:
            client = MemoryClient(api_key=current_user.mem0_api_key)
            
            mem0_memory = client.add(
                memory_data.content,
                user_id=str(current_user.id),
                scope=memory_data.scope,
                topic_id=str(memory_data.topic_id) if memory_data.topic_id else None
            )
            
            embedding = mem0_memory.get("embedding", None)
            embedding_str = json.dumps(embedding) if embedding else None
            
        except Exception as e:
            embedding_str = None
    else:
        embedding_str = None
    
    new_memory = Memory(
        content=memory_data.content,
        embedding=embedding_str,
        user_id=current_user.id,
        topic_id=memory_data.topic_id,
        scope=memory_data.scope
    )
    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)
    
    if memory_data.tags:
        for tag_name in memory_data.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            
            new_memory.tags.append(tag)
        
        db.commit()
        db.refresh(new_memory)
    
    return new_memory

@router.get("/", response_model=List[MemorySchema])
async def get_memories(
    skip: int = 0,
    limit: int = 100,
    scope: str = "personal",
    topic_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ユーザーのメモリを取得"""
    query = db.query(Memory).filter(
        Memory.user_id == current_user.id,
        Memory.scope == scope
    )
    
    if topic_id:
        query = query.filter(Memory.topic_id == topic_id)
    
    memories = query.order_by(Memory.created_at.desc()).offset(skip).limit(limit).all()
    
    return memories

@router.post("/search", response_model=List[MemorySchema])
async def search_memories(
    search_data: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """メモリを検索"""
    if search_data.search_type == "time":
        query = db.query(Memory).filter(
            Memory.user_id == current_user.id,
            Memory.scope == search_data.scope
        )
        
        memories = query.order_by(Memory.created_at.desc()).offset(search_data.offset).limit(search_data.limit).all()
        
        return memories
        
    elif search_data.search_type == "keyword":
        query = db.query(Memory).filter(
            Memory.user_id == current_user.id,
            Memory.scope == search_data.scope,
            Memory.content.like(f"%{search_data.query}%")
        )
        
        memories = query.order_by(Memory.created_at.desc()).offset(search_data.offset).limit(search_data.limit).all()
        
        return memories
        
    elif search_data.search_type == "vector":
        if not current_user.mem0_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ベクトル検索にはmem0 APIキーが必要です"
            )
        
        try:
            client = MemoryClient(api_key=current_user.mem0_api_key)
            
            search_results = client.search(
                search_data.query,
                user_id=str(current_user.id),
                scope=search_data.scope,
                limit=search_data.limit
            )
            
            memory_ids = [result.get("id") for result in search_results if result.get("id")]
            
            if not memory_ids:
                return []
            
            memories = db.query(Memory).filter(
                Memory.id.in_(memory_ids)
            ).all()
            
            sorted_memories = sorted(
                memories,
                key=lambda m: memory_ids.index(m.id) if m.id in memory_ids else float('inf')
            )
            
            return sorted_memories
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ベクトル検索中にエラーが発生しました: {str(e)}"
            )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効な検索タイプです。'time', 'keyword', 'vector'のいずれかを指定してください"
        )

@router.get("/{memory_id}", response_model=MemorySchema)
async def get_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """特定のメモリを取得"""
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.user_id == current_user.id
    ).first()
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="メモリが見つかりません"
        )
    
    return memory

@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """メモリを削除"""
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.user_id == current_user.id
    ).first()
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="メモリが見つかりません"
        )
    
    if current_user.mem0_api_key:
        try:
            client = MemoryClient(api_key=current_user.mem0_api_key)
        except Exception:
            pass
    
    db.delete(memory)
    db.commit()
    
    return None
