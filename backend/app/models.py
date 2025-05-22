from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Table, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)  # OAuthの場合はnull許容
    mem0_api_key = Column(String, nullable=True)
    llm_api_key = Column(String, nullable=True)
    llm_provider = Column(String, default="openai")
    oauth_provider = Column(String, nullable=True)  # "google", "github", "apple"など
    oauth_id = Column(String, nullable=True)  # OAuthプロバイダーからのID
    created_at = Column(DateTime, default=datetime.utcnow)
    
    memories = relationship("Memory", back_populates="user")
    topics = relationship("Topic", back_populates="user")
    user_settings = relationship("UserSettings", uselist=False, back_populates="user")

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    memory_retention_days = Column(Integer, default=90)  # メモリ保持期間（日数）
    max_memories_per_topic = Column(Integer, default=1000)  # トピックごとの最大メモリ数
    default_search_type = Column(String, default="vector")  # デフォルト検索タイプ
    default_scope = Column(String, default="personal")  # デフォルトスコープ
    embedding_model = Column(String, default="text-embedding-ada-002")  # 埋め込みモデル
    language_preference = Column(String, default="ja")  # 言語設定
    additional_settings = Column(JSON, default={})  # その他の設定（JSON形式）
    
    user = relationship("User", back_populates="user_settings")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scope = Column(String, default="personal")  # personal, project, teamなど
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="topics")
    memories = relationship("Memory", back_populates="topic")

memory_tag = Table(
    "memory_tags",
    Base.metadata,
    Column("memory_id", Integer, ForeignKey("memories.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    embedding = Column(String, nullable=True)  # 埋め込みベクトル（JSON文字列として保存）
    user_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    scope = Column(String, default="personal")  # personal, project, teamなど
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="memories")
    topic = relationship("Topic", back_populates="memories")
    tags = relationship("Tag", secondary=memory_tag, back_populates="memories")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    memories = relationship("Memory", secondary=memory_tag, back_populates="tags")
