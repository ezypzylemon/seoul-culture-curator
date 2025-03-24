from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.api.services.heatmap_service import HeatmapService

router = APIRouter()

@router.get("/congestion")
async def get_congestion_data():
    """전체 혼잡도 데이터 제공 엔드포인트"""
    try:
        heatmap_service = HeatmapService()
        
        # 혼잡도 데이터 가져오기
        data = heatmap_service.get_congestion_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/congestion/{area}")
async def get_area_congestion(area: str):
    """특정 지역 혼잡도 정보 제공 엔드포인트"""
    try:
        heatmap_service = HeatmapService()
        result = heatmap_service.get_area_congestion_data(area)
        
        # 에러 확인
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
            
        return result
    except HTTPException:
        raise  # 이미 생성된 HTTPException은 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))