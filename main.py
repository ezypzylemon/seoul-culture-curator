import os
import streamlit as st
from 문화챗봇_optimized import ChatBot
from heatmap_service import HeatmapService
from streamlit_folium import st_folium  # 추가

def initialize_session_state():
    """세션 상태 초기화"""
    session_vars = {
        "messages": [],
        "gender": "남성",
        "age_group": "20대",
        "has_children": "아니오",
        "transportation": "도보"
    }
    
    for var, default in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default

def setup_sidebar():
    """사이드바 UI 설정"""
    with st.sidebar:
        st.header("사용자 정보 설정")
        
        # 사용자 정보 입력 필드들
        options = {
            "gender": (["남성", "여성", "기타"], "성별을 선택하세요:"),
            "age_group": (["10대", "20대", "30대", "40대", "50대 이상"], "나이대를 선택하세요:"),
            "has_children": (["예", "아니오"], "자녀가 있으신가요?"),
            "transportation": (["도보", "자가용", "버스", "지하철"], "주로 이용하는 이동수단을 선택하세요:")
        }
        
        for key, (choices, label) in options.items():
            st.session_state[key] = st.selectbox(
                label,
                choices,
                index=choices.index(st.session_state[key])
            )

        tab_selection = st.radio("기능 선택", ["채팅", "추천", "혼잡도 지도"])
        
        if st.button("New Chat", use_container_width=True):
            st.session_state.messages = []
            
        return tab_selection

def handle_chat(chatbot):
    """채팅 기능 처리"""
    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 채팅 입력
    if prompt := st.chat_input("메시지를 입력하세요"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            response = chatbot.handle_user_input(prompt)
            st.markdown(f"AI 응답: {response}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"AI 응답: {response}"
            })

def handle_recommendation(chatbot):
    """추천 기능 처리"""
    # 세션 상태 초기화
    if 'user_location' not in st.session_state:
        st.session_state.user_location = ''
    if 'show_recommendations' not in st.session_state:
        st.session_state.show_recommendations = False

    # 사용자 위치 입력 (폼 사용)
    user_location = st.text_input("위치를 입력하세요:", 
                                value=st.session_state.user_location)
    
    if st.button("추천받기"):
        st.session_state.user_location = user_location
        st.session_state.show_recommendations = True
        
    # 추천 결과 표시
    if st.session_state.show_recommendations and st.session_state.user_location:
        chatbot.display_recommendations(st.session_state.user_location)

def handle_heatmap():
    """혼잡도 히트맵 표시"""
    st.title("서울시 실시간 혼잡도 지도")
    
    heatmap_service = HeatmapService()
    
    # 데이터 새로고침 버튼
    if st.button("🔄 데이터 새로고침", help="실시간 데이터를 다시 불러옵니다"):
        st.cache_data.clear()
        st.rerun()  # experimental_rerun() 대신 rerun() 사용
    
    try:
        # 히트맵 생성
        congestion_map = heatmap_service.create_congestion_heatmap()
        
        # 지도 표시
        st_folium(congestion_map, width=1000, height=600)
        
        # 범례 표시
        st.markdown("""
        ### 혼잡도 범례
        - 🟢 여유 (0-30%)
        - 🔵 보통 (30-60%)
        - 🟡 약간 붐빔 (60-80%)
        - 🔴 붐빔 (80-100%)
        """)
        
    except Exception as e:
        st.error(f"지도 생성 중 오류가 발생했습니다: {str(e)}")
        st.info("데이터 새로고침을 시도해보세요.")

def main():
    """메인 함수"""
    st.set_page_config(
        page_title="스마트문화예술 챗봇",
        page_icon="🎨",
        layout="wide"
    )

    # 세션 상태 초기화
    initialize_session_state()

    # API 키 설정
    api_key = os.getenv("SEOUL_API_KEY")
    if not api_key:
        st.error("SEOUL_API_KEY가 설정되지 않았습니다.")
        return

    # ChatBot 인스턴스 생성
    chatbot = ChatBot(api_key)

    # 사이드바 설정
    tab_selection = setup_sidebar()

    # 메인 UI
    st.title("스마트문화예술 챗봇")

    # 선택된 기능에 따라 처리
    if tab_selection == "추천":
        handle_recommendation(chatbot)
    elif tab_selection == "혼잡도 지도":
        handle_heatmap()
    else:
        handle_chat(chatbot)

if __name__ == "__main__":
    main()