from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.api.routes import chat_routes, recommendation_routes, map_routes
from services.congestion_db import get_congestion_data
import os
from dotenv import load_dotenv

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

# /api/map/congestion 엔드포인트 추가
@app.get("/api/map/congestion")
async def get_congestion():
    # DB에서 혼잡도 데이터 가져오기
    data = get_congestion_data()

    if data:
        return JSONResponse(content={"data": data}, status_code=200)
    else:
        return JSONResponse(content={"message": "데이터 없음"}, status_code=404)

# React 정적 파일 서빙
# 아래 이 줄만 유지
app.mount("/", StaticFiles(directory="static", html=True), name="static")

