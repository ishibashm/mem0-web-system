from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

from app.database import engine, Base
from app.routers import auth, oauth, users, memories, topics, settings, api

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mem0 Web System API")

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンに制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["認証"])
app.include_router(oauth.router, prefix="/oauth", tags=["OAuth"])
app.include_router(users.router, prefix="/users", tags=["ユーザー"])
app.include_router(memories.router, prefix="/memories", tags=["メモリ"])
app.include_router(topics.router, prefix="/topics", tags=["トピック"])
app.include_router(settings.router, prefix="/settings", tags=["設定"])
app.include_router(api.router, prefix="/api", tags=["API"])

@app.get("/")
async def root():
    return {"message": "Mem0 Web System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
