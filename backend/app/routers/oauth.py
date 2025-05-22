from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
import httpx
import json
from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwk
from authlib.jose.errors import JoseError
import time

from app.database import get_db
from app.models import User, UserSettings
from app.utils.auth import create_access_token
from app.schemas import UserCreate

router = APIRouter(tags=["OAuth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/oauth/google/callback")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "your-github-client-id")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "your-github-client-secret")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/oauth/github/callback")

APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID", "your-apple-client-id")
APPLE_TEAM_ID = os.getenv("APPLE_TEAM_ID", "your-apple-team-id")
APPLE_KEY_ID = os.getenv("APPLE_KEY_ID", "your-apple-key-id")
APPLE_PRIVATE_KEY = os.getenv("APPLE_PRIVATE_KEY", "your-apple-private-key")
APPLE_REDIRECT_URI = os.getenv("APPLE_REDIRECT_URI", "http://localhost:8000/oauth/apple/callback")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

oauth.register(
    name='github',
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get('userinfo')
    
    if not user_info:
        raise HTTPException(status_code=400, detail="ユーザー情報の取得に失敗しました")
    
    user = db.query(User).filter(
        User.oauth_provider == "google",
        User.oauth_id == user_info["sub"]
    ).first()
    
    if not user:
        user_data = UserCreate(
            username=f"google_{user_info['sub']}",
            email=user_info["email"],
            oauth_provider="google",
            oauth_id=user_info["sub"]
        )
        
        existing_email = db.query(User).filter(User.email == user_info["email"]).first()
        if existing_email:
            existing_email.oauth_provider = "google"
            existing_email.oauth_id = user_info["sub"]
            db.commit()
            user = existing_email
        else:
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                oauth_provider=user_data.oauth_provider,
                oauth_id=user_data.oauth_id
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            user_settings = UserSettings(
                user_id=new_user.id,
                language_preference="ja"  # 日本語をデフォルトに設定
            )
            db.add(user_settings)
            db.commit()
            
            user = new_user
    
    access_token = create_access_token(data={"sub": user.username})
    
    return RedirectResponse(f"{FRONTEND_URL}/auth/callback?token={access_token}")

@router.get("/github/login")
async def github_login(request: Request):
    redirect_uri = GITHUB_REDIRECT_URI
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.github.authorize_access_token(request)
    resp = await oauth.github.get('user', token=token)
    user_info = resp.json()
    
    emails_resp = await oauth.github.get('user/emails', token=token)
    emails = emails_resp.json()
    primary_email = next((email["email"] for email in emails if email["primary"]), None)
    
    if not primary_email:
        raise HTTPException(status_code=400, detail="メールアドレスの取得に失敗しました")
    
    user = db.query(User).filter(
        User.oauth_provider == "github",
        User.oauth_id == str(user_info["id"])
    ).first()
    
    if not user:
        user_data = UserCreate(
            username=f"github_{user_info['id']}",
            email=primary_email,
            oauth_provider="github",
            oauth_id=str(user_info["id"])
        )
        
        existing_email = db.query(User).filter(User.email == primary_email).first()
        if existing_email:
            existing_email.oauth_provider = "github"
            existing_email.oauth_id = str(user_info["id"])
            db.commit()
            user = existing_email
        else:
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                oauth_provider=user_data.oauth_provider,
                oauth_id=user_data.oauth_id
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            user_settings = UserSettings(
                user_id=new_user.id,
                language_preference="ja"  # 日本語をデフォルトに設定
            )
            db.add(user_settings)
            db.commit()
            
            user = new_user
    
    access_token = create_access_token(data={"sub": user.username})
    
    return RedirectResponse(f"{FRONTEND_URL}/auth/callback?token={access_token}")

@router.get("/apple/login")
async def apple_login():
    state = str(time.time())  # セキュリティのためのstate値
    params = {
        "response_type": "code",
        "client_id": APPLE_CLIENT_ID,
        "redirect_uri": APPLE_REDIRECT_URI,
        "state": state,
        "scope": "name email",
        "response_mode": "form_post"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    auth_url = f"https://appleid.apple.com/auth/authorize?{query_string}"
    
    return RedirectResponse(auth_url)

@router.post("/apple/callback")
async def apple_callback(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    code = form_data.get("code")
    
    if not code:
        raise HTTPException(status_code=400, detail="認証コードがありません")
    
    try:
        now = int(time.time())
        client_secret_payload = {
            "iss": APPLE_TEAM_ID,
            "iat": now,
            "exp": now + 3600,
            "aud": "https://appleid.apple.com",
            "sub": APPLE_CLIENT_ID
        }
        
        headers = {"kid": APPLE_KEY_ID, "alg": "ES256"}
        
        token_data = {
            "client_id": APPLE_CLIENT_ID,
            "client_secret": "generated_client_secret_jwt",  # 実際には生成したJWT
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": APPLE_REDIRECT_URI
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://appleid.apple.com/auth/token",
                data=token_data
            )
            token_json = token_response.json()
            
            if "error" in token_json:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Appleトークン取得エラー: {token_json.get('error')}"
                )
            
            id_token = token_json.get("id_token")
            if not id_token:
                raise HTTPException(status_code=400, detail="IDトークンがありません")
            
            
            payload = {
                "sub": "000123.abcdef1234567890",  # Apple提供のユーザーID
                "email": "test@privaterelay.appleid.com",
                "email_verified": True
            }
            
            user = db.query(User).filter(
                User.oauth_provider == "apple",
                User.oauth_id == payload["sub"]
            ).first()
            
            if not user:
                user_data = UserCreate(
                    username=f"apple_{payload['sub']}",
                    email=payload["email"],
                    oauth_provider="apple",
                    oauth_id=payload["sub"]
                )
                
                existing_email = db.query(User).filter(User.email == payload["email"]).first()
                if existing_email:
                    existing_email.oauth_provider = "apple"
                    existing_email.oauth_id = payload["sub"]
                    db.commit()
                    user = existing_email
                else:
                    new_user = User(
                        username=user_data.username,
                        email=user_data.email,
                        oauth_provider=user_data.oauth_provider,
                        oauth_id=user_data.oauth_id
                    )
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)
                    
                    user_settings = UserSettings(
                        user_id=new_user.id,
                        language_preference="ja"  # 日本語をデフォルトに設定
                    )
                    db.add(user_settings)
                    db.commit()
                    
                    user = new_user
            
            access_token = create_access_token(data={"sub": user.username})
            
            return RedirectResponse(f"{FRONTEND_URL}/auth/callback?token={access_token}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Apple認証エラー: {str(e)}")
