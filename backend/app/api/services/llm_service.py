import os
import google.generativeai as genai
import logging
from typing import Dict, List, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self._api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self._api_key)
        self._model = genai.GenerativeModel('gemini-1.5-flash')

    def ask_llm(self, question: str) -> str:
        """LLM API 호출"""
        try:
            response = self._model.generate_content(question)
            return response.text
        except Exception as e:
            logger.error(f"API 호출 중 오류 발생: {str(e)}")
            return f"AI 응답을 생성하는 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."

    def get_congestion_recommendation(self, area: str, congestion: str, forecast: dict, traffic_status: dict) -> str:
        """혼잡도 관련 추천사항 생성"""
        walking_condition = forecast.get('congestion_message', '정보 없음')
        traffic_condition = traffic_status.get('status', '정보 없음')
        traffic_speed = traffic_status.get('speed', '정보 없음')

        prompt = f"""
        {area} 지역의 현재 상황:
        1. 전반적 혼잡도: {congestion}
        2. 도보 상황: {walking_condition}
        3. 도로 상태: {traffic_condition}
        4. 도로 속도: {traffic_speed} km/h
        
        다음 기준으로 상황을 분석하고 구체적인 대안을 제시해주세요:
        
        1. 도보 이동이 불편한 경우:
           - 우회 경로 추천
           - 한적한 시간대 추천
           - 주변 대체 장소 추천
        
        2. 차량 이동이 어려운 경우:
           - 가까운 지하철/버스 정류장 활용 방법
           - 주차장이 여유있는 인근 지역 추천
           - 대중교통 환승 포인트 제안
        
        3. 전반적으로 혼잡한 경우:
           - 한적한 인근 장소 추천
           - 방문 시간대 조정 제안
           - 대체 활동 추천
        
        위 상황들을 종합적으로 고려하여 방문객들이 더 나은 경험을 할 수 있도록
        가장 효율적인 3가지 구체적인 대안을 추천해주세요.
        """
        return self.ask_llm(prompt)

    def get_alternative_place(self, area: str, valid_areas: list) -> str:
        """대체 장소 추천"""
        prompt = f"""
        다음은 서울시의 주요 관광지/상권 목록입니다:
        {', '.join(valid_areas)}

        현재 {area}이(가) 붐비는 상황입니다.
        이 지역 5km 이내에 있으면서, 비슷한 성격을 가진 덜 붐비는 대체 장소 1곳을 추천해주세요.
        다음 형식으로 답변해주세요:
        [대체장소명]: [이유]
        """
        return self.ask_llm(prompt)
        
    def get_personalized_recommendation(self, user_preferences: Dict[str, str], prompt: str) -> str:
        """사용자 맞춤형 추천 생성"""
        context = f"""
        사용자 정보:
        - 성별: {user_preferences.get('gender', '남성')}
        - 나이대: {user_preferences.get('age_group', '20대')}
        - 자녀 여부: {user_preferences.get('has_children', '아니오')}
        - 이동수단: {user_preferences.get('transportation', '도보')}
        
        위 정보를 가진 사용자가 다음과 같이 질문했습니다:
        '{prompt}'
        
        사용자의 특성과 선호도를 고려하여 문화 활동을 추천해주세요.
        특히 이동수단과 자녀 동반 여부를 중요하게 고려해주세요."""
        
        return self.ask_llm(context)