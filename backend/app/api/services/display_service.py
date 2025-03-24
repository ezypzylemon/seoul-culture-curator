import streamlit as st
from typing import Dict, Any
from map_service import MapService
from streamlit_folium import st_folium
import requests
from route_service import RouteService, TransportMode
import folium

class DisplayService:
    @staticmethod
    def display_events(result: Dict[str, Any]):
        """문화 행사 정보 표시"""
        if result['success']:
            st.write(f"## 참여 가능한 총 {result['total_count']}개의 문화 행사 정보")
            for idx, event in enumerate(result['data'], start=1):
                with st.expander(f"행사 {idx}: {event['TITLE']}"):
                    # 카카오맵 링크 생성
                    place_name = event['PLACE']
                    encoded_place = requests.utils.quote(place_name)

                    # 1. 카카오맵 웹 검색 URL
                    kakao_map_url = f"https://map.kakao.com/link/search/{encoded_place}"

                    # 2. 카카오맵 앱 길찾기 URL (모바일용)
                    kakao_navi_url = f"kakaomap://search?q={encoded_place}"

                    # 장소 정보를 클릭 가능한 링크로 표시
                    st.markdown(
                        f"""**장소:** [{place_name}]({kakao_map_url}) 
                        <a href="{kakao_navi_url}" target="_blank" style="text-decoration: none;">
                            <span style="background-color: #FEE500; color: black; padding: 2px 6px; border-radius: 4px; font-size: 0.8em;">
                                📍 길찾기
                            </span>
                        </a>""",
                        unsafe_allow_html=True
                    )

                    # 나머지 정보 표시
                    st.write(f"**날짜:** {event['DATE']}")
                    st.write(f"**분류:** {event['CODENAME']}")
                    st.write(f"**요금:** {event['USE_FEE']}")
                    st.write(f"**프로그램:** {event['PROGRAM']}")

                    # 🔥 iframe 코드 제거됨 🔥
        else:
            st.error(f"문화 행사 정보 조회 실패: {result.get('error', '알 수 없는 오류')}")

    @staticmethod
    def display_area_status(area: str, population_status: dict, 
                          traffic_status: dict, commercial_status: dict,
                          traffic_service=None, area_info=None):
        """지역 상태 정보 표시"""
        congestion = population_status.get('congestion_level')
        if congestion:
            st.subheader("📍 현재 위치 및 혼잡도")
            congestion_map = MapService.create_congestion_map(area, congestion)
            if congestion_map:
                try:
                    st_folium(congestion_map, width=700, height=400, returned_objects=[])
                except Exception as e:
                    st.error(f"지도 표시 중 오류 발생: {str(e)}")

        DisplayService._show_population_info(population_status)
        if traffic_service and area_info:
            DisplayService._show_traffic_info(traffic_status, traffic_service, area_info)
        else:
            DisplayService._show_traffic_info_basic(traffic_status)
        DisplayService._show_commercial_info(commercial_status)

    @staticmethod
    def display_route(start_coords: Dict[str, float], end_coords: Dict[str, float], 
                     route_service: RouteService):
        """경로 정보 표시"""
        if 'start_location' not in st.session_state:
            st.session_state.start_location = ''
        if 'transport_mode' not in st.session_state:
            st.session_state.transport_mode = "도보"
        if 'show_route' not in st.session_state:
            st.session_state.show_route = False
            
        start_location = st.text_input("출발 위치를 입력하세요 (예: 강남역):",
                                       value=st.session_state.start_location,
                                       key='start_location_input')
        
        transport_mode = st.radio(
            "이동 수단 선택",
            ["도보", "자동차", "대중교통"],
            horizontal=True,
            key='transport_mode_input',
            index=["도보", "자동차", "대중교통"].index(st.session_state.transport_mode)
        )
        
        if st.button("경로 검색", key='route_search_button'):
            st.session_state.start_location = start_location
            st.session_state.transport_mode = transport_mode
            st.session_state.show_route = True
            
        if st.session_state.show_route and st.session_state.start_location:
            from 카카오_optimized import get_coordinates
            start_coords = get_coordinates(st.session_state.start_location)
            
            if not start_coords:
                st.error("출발 위치의 좌표를 찾을 수 없습니다.")
                return

            mode_map = {
                "도보": TransportMode.WALKING,
                "자동차": TransportMode.DRIVING,
                "대중교통": TransportMode.TRANSIT
            }

            routes = route_service.get_routes(
                start_coords['lat'], start_coords['lng'],
                end_coords['lat'], end_coords['lng'],
                mode_map[st.session_state.transport_mode]
            )

            if routes:
                m = folium.Map(
                    location=[(start_coords['lat'] + end_coords['lat']) / 2,
                             (start_coords['lng'] + end_coords['lng']) / 2],
                    zoom_start=13
                )

                folium.Marker(
                    [start_coords['lat'], start_coords['lng']],
                    popup='출발지',
                    icon=folium.Icon(color='green')
                ).add_to(m)

                folium.Marker(
                    [end_coords['lat'], end_coords['lng']],
                    popup='도착지',
                    icon=folium.Icon(color='red')
                ).add_to(m)

                for idx, route in enumerate(routes):
                    color = 'blue' if idx == 0 else 'gray'
                    folium.PolyLine(
                        route.path,
                        weight=3,
                        color=color,
                        opacity=0.8
                    ).add_to(m)

                    st.write(f"경로 {idx+1}:")
                    st.write(f"- 거리: {route.distance/1000:.1f}km")
                    st.write(f"- 소요 시간: {route.duration//60}분")
                    if route.steps:
                        st.write("- 주요 경로:")
                        for step in route.steps:
                            st.write(f"  • {step}")

                st_folium(m, width=700, height=400)
        else:
            st.error("경로를 찾을 수 없습니다.")
