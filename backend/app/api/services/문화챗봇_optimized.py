import os
import requests
import streamlit as st
import google.generativeai as genai
from typing import Dict, Any
from event_service import get_events
from location_service import CityInfo, get_coordinates
from city_service import SeoulCityData
import folium
from streamlit_folium import st_folium

# 로컬 서비스 import
from map_service import MapService
from llm_service import LLMService
from display_service import DisplayService
from traffic_service import TrafficService
from agent_service import CultureAgent
from route_service import RouteService

# OpenAI API 설정 부분을 Gemini API 설정으로 변경
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class ChatBot:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._city_data = SeoulCityData()
        self._llm_service = LLMService()
        self._display_service = DisplayService()
        self._traffic_service = TrafficService(api_key)
        self._agent = CultureAgent()
        self._route_service = RouteService(os.getenv("KAKAO_API_KEY"))

    def display_recommendations(self, location: str) -> None:
        """공개 인터페이스: 추천 정보 표시"""
        main_area = CityInfo.find_nearest_location(location)
        if main_area == "위치를 찾을 수 없습니다.":
            st.error(main_area)
            return
            
        if main_area:
            st.success(f"입력하신 위치와 가장 가까운 주요 지역은 '{main_area}'입니다.")
            
            population_status = self._city_data.get_population_status(main_area)
            traffic_status = self._city_data.get_traffic_status(main_area)
            commercial_status = self._city_data.get_commercial_status(main_area)

            # 좌표 정보 가져오기
            coordinates = get_coordinates(main_area)
            area_info = {
                'name': main_area,
                'lat': coordinates['lat'] if coordinates else 0,
                'lng': coordinates['lng'] if coordinates else 0,
                'destination_lat': coordinates['lat'] if coordinates else 0,
                'destination_lng': coordinates['lng'] if coordinates else 0
            } if coordinates else None
            
            self._display_service.display_area_status(
                main_area, 
                population_status, 
                traffic_status, 
                commercial_status,
                self._traffic_service if coordinates else None,
                area_info
            )
            
            congestion = population_status.get('congestion_level')
            if congestion in ['붐빔', '약간 붐빔']:
                self._handle_congestion(main_area, congestion, population_status, traffic_status)
            
            # 에이전트 분석 추가
            user_preferences = {
                'gender': st.session_state.gender,
                'age_group': st.session_state.age_group,
                'has_children': st.session_state.has_children,
                'transportation': st.session_state.transportation
            }
            
            agent_analysis = self._agent.analyze_situation(
                main_area,
                population_status,
                traffic_status,
                commercial_status,
                user_preferences
            )
            
            # 에이전트 분석 결과 표시
            with st.expander("🤖 AI 큐레이터의 종합 분석"):
                st.write("### 현재 상황 평가")
                st.write(agent_analysis.get('situation', '정보 없음'))
                
                st.write("### 최적의 방문 시간대")
                st.write(agent_analysis.get('best_time', '정보 없음'))
                
                st.write("### 추천 동선")
                st.write(agent_analysis.get('route', '정보 없음'))
                
                st.write("### 주의사항")
                st.write(agent_analysis.get('warnings', '정보 없음'))
                
                if 'alternatives' in agent_analysis:
                    st.write("### 대체 추천 장소")
                    st.write(agent_analysis['alternatives'])
            
            # 문화 행사 추천
            events_result = get_events(self._api_key, main_area)
            if events_result['success']:
                personalized_recommendation = self._agent.get_personalized_recommendation(
                    events_result['data'],
                    user_preferences
                )
                with st.expander("🎯 맞춤 행사 추천"):
                    st.write(personalized_recommendation)
                    
            self._display_service.display_events(events_result)
            
            # 목적지 좌표만 가져오기
            dest_coords = get_coordinates(main_area)
            
            if dest_coords:
                st.subheader("🗺️ 경로 안내")
                self._display_service.display_route(None, dest_coords, self._route_service)
        else:
            st.error("주요 지역을 찾을 수 없습니다.")

    def _handle_congestion(self, area: str, congestion: str, 
                         population_status: dict, traffic_status: dict):
        """혼잡 상황 처리"""
        forecast = population_status.get("forecast", {})
        
        recommendation = self._llm_service.get_congestion_recommendation(
            area, congestion, forecast, traffic_status
        )
        st.write("\n[AI 추천] 혼잡도 해결 방안:")
        st.write(recommendation)

        alternative_place = self._llm_service.get_alternative_place(
            area, self._city_data.valid_areas
        )
        st.write("\n[주변 추천] 덜 붐비는 대체 장소:")
        st.write(alternative_place)

    def _initialize_session_state(self):
        """private: 세션 상태 초기화"""
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def _get_events_info(self, district: str, limit: int = 3):
        """private: 문화 행사 정보 조회"""
        return get_events(self._api_key, district, limit)

    def _create_congestion_map(self, area: str, congestion_level: str):
        """private: 혼잡도 지도 생성"""
        try:
            coordinates = get_coordinates(area)
            if not coordinates:
                st.error(f"{area}의 좌표를 가져올 수 없습니다.")
                return None
            
            st.write(f"좌표 정보: 위도 {coordinates['lat']}, 경도 {coordinates['lng']}")
            
            m = folium.Map(
                location=[coordinates['lat'], coordinates['lng']], 
                zoom_start=15,
                width=800,
                height=500
            )
            
            colors = {
                '여유': 'green',
                '보통': 'blue',
                '약간 붐빔': 'orange',
                '붐빔': 'red'
            }
            color = colors.get(congestion_level, 'gray')
            
            folium.Marker(
                location=[coordinates['lat'], coordinates['lng']],
                popup=f"{area}\n혼잡도: {congestion_level}",
                icon=folium.Icon(color=color)
            ).add_to(m)
            
            folium.CircleMarker(
                location=[coordinates['lat'], coordinates['lng']],
                radius=30,
                popup=f"{area}\n혼잡도: {congestion_level}",
                color=color,
                fill=True,
                fill_color=color
            ).add_to(m)
            
            return m
        except Exception as e:
            st.error(f"지도 생성 중 오류 발생: {str(e)}")
            return None

    def _ask_llm(self, question: str):
        """private: LLM API 호출"""
        try:
            response = self._model.generate_content(question)
            return response.text
        except Exception as e:
            return f"API 호출 중 오류 발생: {str(e)}"

    def _display_status(self, area: str) -> None:
        """private: 상태 표시"""
        try:
            population_status = self._city_data.get_population_status(area)
            traffic_status = self._city_data.get_traffic_status(area)
            commercial_status = self._city_data.get_commercial_status(area)

            if not population_status or not traffic_status or not commercial_status:
                st.error(f"{area} 지역의 데이터를 불러오는데 실패했습니다.")
                return

            congestion = population_status.get('congestion_level')
            if congestion:
                st.subheader("📍 현재 위치 및 혼잡도")
                congestion_map = self._create_congestion_map(area, congestion)
                if congestion_map:
                    try:
                        st_folium(congestion_map, width=700, height=400, returned_objects=[])
                    except Exception as e:
                        st.error(f"지도 표시 중 오류 발생: {str(e)}")
                else:
                    st.warning("지도를 생성할 수 없습니다.")
                
                st.write("현재 혼잡도: ", congestion)
                
                forecast = population_status.get("forecast", {})
                
                if congestion in ['붐빔', '약간 붐빔']:
                    recommendation_prompt = f"""
                    {area} 지역이 현재 {congestion} 상태입니다.
                    - 현재 시간: {forecast.get('time', '정보 없음')}
                    - 도로 상태: {traffic_status.get('status', '정보 없음')}
                    - 도로 속도: {traffic_status.get('speed', '정보 없음')} km/h
                    
                    이런 상황에서 방문객들이 혼잡을 피하고 더 나은 경험을 할 수 있는 구체적인 방법을 추천해주세요.
                    """
                    ai_recommendation = self._ask_llm(recommendation_prompt)
                    st.write("\n[AI 추천] 혼잡도 해결 방안:")
                    st.write(ai_recommendation)

                    alternative_prompt = f"""
                    다음은 서울시의 주요 관광지/상권 목록입니다:
                    {', '.join(self._city_data.valid_areas)}

                    현재 {area}이(가) 붐비는 상황입니다.
                    이 지역 5km 이내에 있으면서, 비슷한 성격을 가진 덜 붐비는 대체 장소 1곳을 추천해주세요.
                    다음 형식으로 답변해주세요:
                    [대체장소명]: [이유]
                    """
                    alternative_place = self._ask_llm(alternative_prompt)
                    st.write("\n[주변 추천] 덜 붐비는 대체 장소:")
                    st.write(alternative_place)

            else:
                st.warning("혼잡도 정보를 불러올 수 없습니다.")

            if population_status.get("population_range"):
                population_range = population_status["population_range"]
                st.write(f"인구 범위: {population_range.get('min', '정보 없음')}명 ~ {population_range.get('max', '정보 없음')}명")

            if population_status.get("gender_ratio"):
                gender_ratio = population_status["gender_ratio"]
                st.write(f"성비: 남성 {gender_ratio.get('male', '정보 없음')}%, 여성 {gender_ratio.get('female', '정보 없음')}%")

            if population_status.get("age_distribution"):
                st.write("연령 분포:")
                for age_group, percentage in population_status["age_distribution"].items():
                    st.write(f"  {age_group}대: {percentage}%")

            st.write("\n도로 교통 상황:")
            if traffic_status:
                st.write(f"도로 교통 속도: {traffic_status.get('speed', '정보 없음')} km/h")
                st.write(f"도로 교통 상태: {traffic_status.get('status', '정보 없음')}")
                st.write(f"메시지: {traffic_status.get('message', '정보 없음')}")
            else:
                st.warning("교통 정보를 불러올 수 없습니다.")

            st.write("\n상권 현황:")
            if commercial_status and commercial_status.get('food_businesses'):
                for business in commercial_status['food_businesses']:
                    st.write(f"  카테고리: {business.get('category', '정보 없음')}, "
                            f"혼잡도: {business.get('congestion_level', '정보 없음')}, "
                            f"결제 수: {business.get('payment_count', '정보 없음')}, "
                            f"매장 수: {business.get('store_count', '정보 없음')}")
            else:
                st.warning("상권 정보를 불러올 수 없습니다.")

        except Exception as e:
            st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")

    def handle_user_input(self, prompt: str) -> str:
        """공개 인터페이스: 사용자 입력 처리"""
        if "안녕" in prompt:
            return "안녕하세요! 어떤 종류의 문화 활동을 좋아하시나요? 예를 들어, 예술, 음악, 공연, 전시회 등 어떤 것에 관심이 있으신가요?"

        # 사용자 정보 수집
        user_preferences = {
            'gender': st.session_state.gender,
            'age_group': st.session_state.age_group,
            'has_children': st.session_state.has_children,
            'transportation': st.session_state.transportation
        }

        # 현재 위치 기반 정보 가져오기 (사용자가 위치를 언급한 경우)
        location_info = {}
        for area in self._city_data.valid_areas:
            if area in prompt:
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
        return self._llm_service.ask_llm(
            f"""사용자 정보:
            - 성별: {user_preferences['gender']}
            - 나이대: {user_preferences['age_group']}
            - 자녀 여부: {user_preferences['has_children']}
            - 이동수단: {user_preferences['transportation']}
            
            위 정보를 가진 사용자가 다음과 같이 질문했습니다:
            '{prompt}'
            
            사용자의 특성과 선호도를 고려하여 문화 활동을 추천해주세요.
            특히 이동수단과 자녀 동반 여부를 중요하게 고려해주세요."""
        )

    def print_events(self, result: Dict[str, Any]):
        """문화 행사 정보를 Streamlit UI에 표시하는 함수"""
        if result['success']:
            st.write(f"## 참여 가능한 총 {result['total_count']}개의 문화 행사 정보")
            for idx, event in enumerate(result['data'], start=1):
                with st.expander(f"행사 {idx}: {event['TITLE']}"):
                    st.write(f"**장소:** {event['PLACE']}")
                    st.write(f"**날짜:** {event['DATE']}")
                    st.write(f"**분류:** {event['CODENAME']}")
                    st.write(f"**요금:** {event['USE_FEE']}")
                    st.write(f"**프로그램:** {event['PROGRAM']}")
        else:
            st.error(f"문화 행사 정보 조회 실패: {result.get('error', '알 수 없는 오류')}")