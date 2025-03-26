from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import os
from app.models.pydantic_models import ChatRequest, ChatResponse
from app.api.services.chat_service import ChatBot

router = APIRouter()

def get_chat_bot():
    """ChatBot 인스턴스 생성"""
    api_key = os.getenv("SEOUL_API_KEY")
    return ChatBot(api_key)

@router.post("/message/", response_model=ChatResponse)
async def chat_message(request: ChatRequest, chat_bot: ChatBot = Depends(get_chat_bot)):
    """채팅 메시지 처리 엔드포인트"""
    try:
        # 사용자 메시지 처리
        response = chat_bot.handle_user_input(
            request.message,
            request.user_preferences
        )

        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))