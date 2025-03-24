from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import os
from app.models.pydantic_models import RecommendationRequest
from app.api.services.chat_service import ChatBot

router = APIRouter()

def get_chat_bot():
    """ChatBot 인스턴스 생성"""
    api_key = os.getenv("SEOUL_API_KEY")
    return ChatBot(api_key)

@router.post("/", response_model=Dict[str, Any])
async def get_recommendation(request: RecommendationRequest, chat_bot: ChatBot = Depends(get_chat_bot)):
    """추천 정보 제공 엔드포인트"""
    try:
        # 위치 기반 추천 처리
        result = chat_bot.get_recommendations(
            request.location,
            request.user_preferences
        )
        
        # 에러 확인
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except HTTPException:
        raise  # 이미 생성된 HTTPException은 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))