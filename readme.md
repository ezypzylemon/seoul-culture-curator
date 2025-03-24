# 스마트 문화예술 챗봇 및 도시 데이터 서비스

## 개요
이 프로젝트는 서울시의 다양한 도시 데이터를 활용하여 문화예술 관련 추천, 실시간 교통·혼잡도 정보, 경로 안내 및 문화행사 정보를 제공하는 통합 서비스입니다.  
주요 기능은 다음과 같습니다:
- **대화형 챗봇**: 사용자의 질문을 바탕으로 맞춤형 문화예술 및 도시 관련 정보를 제공
- **실시간 교통·혼잡도 정보**: 서울시 교통 상황 및 혼잡 데이터를 이용한 지도 및 히트맵 제공
- **경로 안내 서비스**: 도보, 자동차, 대중교통 별 최적의 경로 추천
- **문화행사 정보 조회**: 서울시 자치구별 문화행사 데이터 수집 및 추천

## 기술 스택

- **Python**: 서비스 전반의 백엔드 로직 구현
- **Streamlit**: 웹 대시보드 및 사용자 인터페이스 구현
- **Folium & streamlit-folium**: 지도 생성 및 시각화 (혼잡도 지도, 경로 지도 등)
- **Requests**: 외부 API 호출 (서울시 공공데이터, 카카오 API, 카카오 길찾기 API 등)
- **Dataclasses & Enum**: 경로 정보 및 이동 수단 관리
- **python-dotenv**: 환경 변수 관리 (API Key 등)
- **Google Generative AI (gemini API)**: LLM 기반 자연어 처리 및 맞춤형 응답 생성

## 모듈 구성

- **main.py**: 서비스 초기화 및 전체 UI 흐름 관리 (채팅, 추천, 혼잡도 지도 기능)
- **traffic_service.py**: 실시간 교통 정보, 대중교통 데이터 및 주차장 정보 조회 기능
- **route_service.py**: 도보, 자동차, 대중교통 기반의 경로 안내 기능
- **display_service.py**: 사용자 인터페이스에 도시 상태, 경로, 이벤트 정보 등을 표시
- **heatmap_service.py**: 서울시 전역의 혼잡도 데이터를 기반으로 한 히트맵 생성 기능
- **city_optimized.py & city_data.py**: 서울시 인구, 상권, 교통 등 도시 데이터 조회 및 파싱 로직
- **카카오_optimized.py & location_service.py**: 카카오 API를 활용한 지도 및 좌표 관련 서비스
- **문화챗봇_optimized.py & chatbot.py**: 사용자의 입력을 분석하고 LLM을 통해 맞춤형 문화 예술 추천 제공
- **agent_service.py**: 문화예술 전문 큐레이터 역할로 상황을 분석 및 추천 제공
- **llm_service.py**: LLM API 호출 및 추천 메시지 생성

## 설치 및 실행

1. **필수 패키지 설치**  
   프로젝트 디렉터리에서 아래 명령어로 필요한 패키지를 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```
   *(requirements.txt 파일에는 Streamlit, Folium, requests, python-dotenv, google-generativeai 등 필요한 패키지가 명시되어 있습니다.)*

2. **환경 변수 설정**  
   프로젝트 루트에 `.env` 파일을 생성하고 다음과 같이 API Key들을 설정합니다.
   ```env
   SEOUL_API_KEY=your_seoul_api_key
   KAKAO_REST_API_KEY=your_kakao_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```
   
3. **실행**  
   터미널에서 아래 명령어를 실행하여 Streamlit 앱을 실행합니다.
   ```bash
   streamlit run main.py
   ```

## 서비스 사용 시나리오

- **채팅**: 사용자 입력에 따라 LLM 기반의 추천 및 응답 제공  
- **추천**: 사용자가 위치를 입력하면, 해당 지역의 인구, 교통, 상권 상태를 분석하여 문화행사와 대체 관광지를 추천  
- **혼잡도 지도**: 서울시 각 지역의 현재 혼잡도를 히트맵과 마커로 시각화하여 실시간 혼잡도 정보를 제공

## 참고

- **API 연동**: 서울시 공공데이터, 카카오 API 및 Google Generative AI API를 활용하여 다양한 도시 데이터와 문화행사 정보를 실시간으로 제공합니다.
- **확장성**: 모듈화된 구조로 새로운 기능(예: 추가 문화행사 카테고리, 새로운 교통 정보 등)을 손쉽게 추가할 수 있습니다.

---

이 서비스는 서울시 도시 데이터를 기반으로 한 문화예술 관련 정보를 통합적으로 제공함으로써, 사용자들이 보다 풍부한 도시 체험 및 문화 활동을 즐길 수 있도록 돕습니다.