from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
from app.api.services.city_service import SeoulCityData
from app.api.services.location_service import CityInfo

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HeatmapService:
    def __init__(self):
        self._city_data = SeoulCityData()
        self._coordinates = CityInfo.AREA_COORDINATES
        
    def get_congestion_data(self) -> dict:
        """서울시 전체 혼잡도 데이터 수집"""
        try:
            all_data = {}
            areas_data = []
            
            for area, coords in self._coordinates.items():
                try:
                    population_status = self._city_data.get_population_status(area)
                    if population_status:
                        congestion = population_status.get('congestion_level', '정보 없음')
                        weight = self._convert_congestion_to_weight(congestion)
                        color = self._get_congestion_color(congestion)
                        
                        areas_data.append({
                            'name': area,
                            'coordinates': {
                                'lat': coords[0], 
                                'lng': coords[1]
                            },
                            'congestion': congestion,
                            'weight': weight,
                            'color': color,
                            'population_min': population_status.get('population_range', {}).get('min', 0),
                            'population_max': population_status.get('population_range', {}).get('max', 0)
                        })
                except Exception as e:
                    logger.error(f"{area} 데이터 수집 중 오류: {str(e)}")
            
            # 통계 정보 생성
            congestion_counts = {
                '여유': 0, '보통': 0, '약간 붐빔': 0, '붐빔': 0, '정보 없음': 0
            }
            
            for area in areas_data:
                congestion = area.get('congestion')
                if congestion in congestion_counts:
                    congestion_counts[congestion] += 1
                else:
                    congestion_counts['정보 없음'] += 1
            
            return {
                "areas": areas_data,
                "statistics": {
                    "total": len(areas_data),
                    "counts": congestion_counts
                }
            }
        except Exception as e:
            logger.error(f"혼잡도 데이터 수집 중 오류: {str(e)}")
            return {"areas": [], "statistics": {"total": 0, "counts": {}}}
    
    def get_area_congestion_data(self, area: str) -> dict:
        """특정 지역의 혼잡도 데이터 수집"""
        try:
            # 지역 좌표 확인
            if area not in self._coordinates:
                return {"error": f"{area} 지역을 찾을 수 없습니다."}
                
            coordinates = self._coordinates[area]
            
            # 데이터 수집
            population_status = self._city_data.get_population_status(area)
            traffic_status = self._city_data.get_traffic_status(area)
            commercial_status = self._city_data.get_commercial_status(area)
            
            if not population_status:
                return {"error": f"{area} 지역의 인구 데이터를 불러올 수 없습니다."}
                
            congestion = population_status.get('congestion_level', '정보 없음')
            color = self._get_congestion_color(congestion)
            
            return {
                "area": area,
                "coordinates": {
                    "lat": coordinates[0],
                    "lng": coordinates[1]
                },
                "congestion_level": congestion,
                "congestion_color": color,
                "population_range": population_status.get('population_range', {"min": 0, "max": 0}),
                "traffic_status": traffic_status,
                "commercial_status": commercial_status
            }
        except Exception as e:
            logger.error(f"{area} 지역 혼잡도 데이터 조회 중 오류: {str(e)}")
            return {"error": f"데이터 조회 중 오류 발생: {str(e)}"}

    @staticmethod
    def _convert_congestion_to_weight(congestion_level: str) -> float:
        """혼잡도를 히트맵 가중치로 변환"""
        weights = {
            '여유': 0.2,
            '보통': 0.4,
            '약간 붐빔': 0.7,
            '붐빔': 1.0
        }
        return weights.get(congestion_level, 0.1)

    @staticmethod
    def _get_congestion_color(congestion_level: str) -> str:
        """혼잡도에 따른 색상 반환"""
        colors = {
            '여유': 'green',
            '보통': 'blue',
            '약간 붐빔': 'orange',
            '붐빔': 'red'
        }
        return colors.get(congestion_level, 'gray')