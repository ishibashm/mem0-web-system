from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import User
from app.schemas import ChatRequest, Message
from app.utils.auth import get_current_user

try:
    from mem0ai import MemoryClient, AsyncMemoryClient
except ImportError:
    class MemoryClient:
        def __init__(self, api_key=None):
            self.api_key = api_key
        
        def search(self, query, **kwargs):
            return []
        
        def add(self, content, **kwargs):
            return {"id": "mock-id", "content": content}
    
    class AsyncMemoryClient:
        def __init__(self, api_key=None):
            self.api_key = api_key
        
        async def search(self, query, **kwargs):
            return []
        
        async def add(self, content, **kwargs):
            return {"id": "mock-id", "content": content}

try:
    import openai
    from openai import OpenAI
except ImportError:
    class OpenAI:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.chat = self.Chat()
        
        class Chat:
            def __init__(self):
                self.completions = self.Completions()
            
            class Completions:
                def create(self, **kwargs):
                    class Choice:
                        class Message:
                            content = "これはモックレスポンスです。OpenAI APIキーを設定してください。"
                        message = Message()
                    
                    class Response:
                        choices = [Choice()]
                    
                    return Response()

router = APIRouter(tags=["API"])

@router.post("/v1/chat")
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """チャットAPIエンドポイント"""
    if not current_user.llm_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LLM APIキーが設定されていません"
        )
    
    provider = current_user.llm_provider.lower()
    
    messages = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]
    
    memory_context = []
    if current_user.mem0_api_key:
        try:
            client = MemoryClient(api_key=current_user.mem0_api_key)
            
            last_user_message = next(
                (msg for msg in reversed(chat_request.messages) if msg.role == "user"),
                None
            )
            
            if last_user_message:
                search_results = client.search(
                    last_user_message.content,
                    user_id=chat_request.user_id,
                    scope=chat_request.scope,
                    limit=5
                )
                
                if search_results:
                    memory_context = [
                        {"role": "system", "content": f"関連メモリ: {result.get('content')}"} 
                        for result in search_results
                    ]
        except Exception:
            pass
    
    system_message = {
        "role": "system",
        "content": "あなたは役立つAIアシスタントです。ユーザーの質問に日本語で回答してください。"
    }
    
    final_messages = [system_message] + memory_context + messages
    
    try:
        if provider == "openai":
            client = OpenAI(api_key=current_user.llm_api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=final_messages
            )
            assistant_message = response.choices[0].message.content
            
        elif provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=current_user.llm_api_key)
            response = client.messages.create(
                model="claude-3-opus-20240229",
                messages=final_messages,
                max_tokens=1000
            )
            assistant_message = response.content[0].text
            
        elif provider == "cohere":
            import cohere
            client = cohere.Client(api_key=current_user.llm_api_key)
            response = client.chat(
                message=final_messages[-1]["content"],
                chat_history=[{"role": m["role"], "message": m["content"]} for m in final_messages[:-1]]
            )
            assistant_message = response.text
            
        elif provider == "groq":
            from groq import Groq
            client = Groq(api_key=current_user.llm_api_key)
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=final_messages
            )
            assistant_message = response.choices[0].message.content
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"サポートされていないプロバイダー: {provider}"
            )
        
        if current_user.mem0_api_key:
            try:
                client = MemoryClient(api_key=current_user.mem0_api_key)
                
                last_user_message = next(
                    (msg for msg in reversed(chat_request.messages) if msg.role == "user"),
                    None
                )
                if last_user_message:
                    client.add(
                        last_user_message.content,
                        user_id=chat_request.user_id,
                        scope=chat_request.scope,
                        topic_id=str(chat_request.topic_id) if chat_request.topic_id else None,
                        role="user"
                    )
                
                client.add(
                    assistant_message,
                    user_id=chat_request.user_id,
                    scope=chat_request.scope,
                    topic_id=str(chat_request.topic_id) if chat_request.topic_id else None,
                    role="assistant"
                )
            except Exception:
                pass
        
        return {
            "message": {
                "role": "assistant",
                "content": assistant_message
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM APIの呼び出し中にエラーが発生しました: {str(e)}"
        )

@router.get("/v1/user/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """ユーザープロファイルAPIエンドポイント"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "llm_provider": current_user.llm_provider,
        "oauth_provider": current_user.oauth_provider,
        "settings": {
            "language_preference": current_user.user_settings.language_preference if current_user.user_settings else "ja",
            "default_scope": current_user.user_settings.default_scope if current_user.user_settings else "personal",
            "default_search_type": current_user.user_settings.default_search_type if current_user.user_settings else "vector"
        }
    }
