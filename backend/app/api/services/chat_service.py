import os
import logging
from typing import Dict, Any, List
import google.generativeai as genai
from app.api.services.city_service import SeoulCityData
from app.api.services.llm_service import LLMService
from app.api.services.agent_service import CultureAgent
from app.api.services.event_service import get_events
from app.api.services.location_service import CityInfo, get_coordinates

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChatBot:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._city_data = SeoulCityData()
        self._llm_service = LLMService()
        self._agent = CultureAgent()
        
        # API 키 설정
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    def handle_user_input(self, message: str, user_preferences: Dict[str, str]) -> str:
        """사용자 입력 처리"""
        # 기본 인사 처리
        if "안녕" in message:
            return "안녕하세요! 어떤 종류의 문화 활동을 좋아하시나요? 예를 들어, 예술, 음악, 공연, 전시회 등 어떤 것에 관심이 있으신가요?"

        # 현재 위치 기반 정보 가져오기 (사용자가 위치를 언급한 경우)
        location_info = {}
        for area in self._city_data.valid_areas:
            if area in message:
                population_status = self._city_data.get_population_status(area)
                traffic_status = self._city_data.get_traffic_status(area)
                commercial_status = self._city_data.get_commercial_status(area)
                location_info = {
                    'area': area,
                    'population': population_status,
                    'traffic': traffic_status,
                    'commercial': commercial_status
                }
                break

        # 에이전트를 통한 분석 수행
        if location_info:
            analysis = self._agent.analyze_situation(
                location_info['area'],
                location_info['population'],
                location_info['traffic'],
                location_info['commercial'],
                user_preferences
            )
            
            # 문화 행사 정보 가져오기
            events = get_events(self._api_key, location_info['area'])
            if events['success']:
                personalized_events = self._agent.get_personalized_recommendation(
                    events['data'],
                    user_preferences
                )
                
                # 종합적인 응답 생성
                response = (
                    f"현재 상황 분석:\n{analysis.get('situation', '')}\n\n"
                    f"추천 방문 시간:\n{analysis.get('best_time', '')}\n\n"
                    f"추천 동선:\n{analysis.get('route', '')}\n\n"
                    f"맞춤 행사 추천:\n{personalized_events}\n\n"
                    f"주의사항:\n{analysis.get('warnings', '')}"
                )
                return response

        # 위치 정보가 없는 경우 일반적인 LLM 응답
        return self._llm_service.get_personalized_recommendation(
            user_preferences,
            message
        )

    def get_recommendations(self, location: str, user_preferences: Dict[str, str]) -> Dict[str, Any]:
        """위치 기반 추천 정보 제공"""
        try:
            # 가장 가까운 주요 지역 찾기
            main_area = CityInfo.find_nearest_location(location)
            if main_area == "위치를 찾을 수 없습니다.":
                return {"error": main_area}
                
            # 지역 데이터 수집
            population_status = self._city_data.get_population_status(main_area)
            traffic_status = self._city_data.get_traffic_status(main_area)
            commercial_status = self._city_data.get_commercial_status(main_area)
            
            # 에이전트 분석
            agent_analysis = self._agent.analyze_situation(
                main_area,
                population_status,
                traffic_status,
                commercial_status,
                user_preferences
            )
            
            # 문화 행사 정보
            events_result = get_events(self._api_key, main_area)
            
            # 맞춤 행사 추천 정보 생성
            personalized_recommendation = None
            if events_result['success'] and events_result['data']:
                personalized_recommendation = self._agent.get_personalized_recommendation(
                    events_result['data'],
                    user_preferences
                )
            
            # 반환 데이터 구성
            return {
                "area": main_area,
                "status": {
                    "population": population_status,
                    "traffic": traffic_status,
                    "commercial": commercial_status,
                    "coordinates": get_coordinates(main_area)
                },
                "analysis": agent_analysis,
                "events": events_result,
                "personalized_recommendation": personalized_recommendation  # 맞춤 추천 정보 추가
            }
        except Exception as e:
            logger.error(f"추천 정보 생성 중 오류: {str(e)}")
            return {"error": f"추천 정보를 가져오는데 실패했습니다: {str(e)}"}

    def _handle_congestion(self, area: str, congestion: str, 
                         population_status: dict, traffic_status: dict) -> Dict[str, str]:
        """혼잡 상황 처리"""
        forecast = population_status.get("forecast", {})
        
        recommendation = self._llm_service.get_congestion_recommendation(
            area, congestion, forecast, traffic_status
        )

        alternative_place = self._llm_service.get_alternative_place(
            area, self._city_data.valid_areas
        )
        
        return {
            "congestion_recommendation": recommendation,
            "alternative_place": alternative_place
        }