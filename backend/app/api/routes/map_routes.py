from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from urllib.parse import unquote
from app.api.services.congestion_db import get_congestion_data, get_area_congestion_data

router = APIRouter()

@router.get("/congestion")
async def get_congestion_data_route():
    """전체 혼잡도 데이터 (DB에서 가져옴)"""
    try:
        data = get_congestion_data()
        if data:
            return JSONResponse(content={"data": data}, status_code=200)
        else:
            return JSONResponse(content={"message": "데이터 없음"}, status_code=404)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/congestion/{area}")
async def get_area_congestion(area: str):
    """단일 지역 혼잡도 상세 조회"""
    try:
        decoded_area = unquote(area)
        result = get_area_congestion_data(decoded_area)

        if not result:
            raise HTTPException(status_code=404, detail="해당 지역 데이터 없음")

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
