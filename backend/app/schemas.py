from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserSettingsBase(BaseModel):
    memory_retention_days: Optional[int] = 90
    max_memories_per_topic: Optional[int] = 1000
    default_search_type: Optional[str] = "vector"
    default_scope: Optional[str] = "personal"
    embedding_model: Optional[str] = "text-embedding-ada-002"
    language_preference: Optional[str] = "ja"
    additional_settings: Optional[Dict[str, Any]] = {}

class UserSettingsCreate(UserSettingsBase):
    pass

class UserSettingsUpdate(UserSettingsBase):
    pass

class UserSettings(UserSettingsBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: Optional[str] = None
    mem0_api_key: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_provider: Optional[str] = "openai"
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None

class UserUpdate(BaseModel):
    mem0_api_key: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_provider: Optional[str] = None
    settings: Optional[UserSettingsUpdate] = None

class UserInDB(UserBase):
    id: int
    hashed_password: Optional[str] = None
    mem0_api_key: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_provider: str = "openai"
    oauth_provider: Optional[str] = None
    created_at: datetime
    user_settings: Optional[UserSettings] = None

    class Config:
        orm_mode = True

class UserOut(UserBase):
    id: int
    llm_provider: str
    oauth_provider: Optional[str] = None
    created_at: datetime
    user_settings: Optional[UserSettings] = None

    class Config:
        orm_mode = True

class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None
    scope: str = "personal"

class TopicCreate(TopicBase):
    pass

class TopicInDB(TopicBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Tag(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class MemoryBase(BaseModel):
    content: str
    scope: str = "personal"

class MemoryCreate(MemoryBase):
    topic_id: Optional[int] = None
    tags: List[str] = []

class Memory(MemoryBase):
    id: int
    user_id: int
    topic_id: Optional[int] = None
    created_at: datetime
    tags: List[Tag] = []

    class Config:
        orm_mode = True

class Message(BaseModel):
    role: str
    content: str
    image_url: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    user_id: str
    scope: str = "personal"
    topic_id: Optional[int] = None

class SearchRequest(BaseModel):
    query: str
    search_type: str  # "keyword", "vector", "time"
    user_id: str
    scope: str = "personal"
    limit: int = 10
    offset: int = 0
