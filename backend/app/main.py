from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import chat_routes, recommendation_routes, map_routes
import os
from dotenv import load_dotenv
from app.api.services.congestion_db import get_congestion_data


# 환경변수 로드
load_dotenv()

app = FastAPI(
    title="스마트문화예술 챗봇 API", 
    description="문화예술 활동 추천 및 실시간 정보 제공 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 앱 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat_routes.router, prefix="/api/chat", tags=["chat"])
app.include_router(recommendation_routes.router, prefix="/api/recommendation", tags=["recommendation"])
app.include_router(map_routes.router, prefix="/api/map", tags=["map"])

# React 정적 파일 서빙
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def serve_spa():
    return FileResponse("static/index.html")
