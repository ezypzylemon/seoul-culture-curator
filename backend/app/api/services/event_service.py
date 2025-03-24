import requests
import os
from typing import Dict, Any, List
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CulturalEventManager:
    # 구별 지역 정보 추가
    DISTRICT_AREAS = {
        "강남구": [
            "강남 MICE 관광특구", "강남역", "고속터미널역", "교대역", "선릉역",
            "신논현역·논현역", "역삼역", "압구정로데오거리", "청담동 명품거리", "가로수길"
        ],
        "강동구": ["고덕역", "서울 암사동 유적"],
        "강북구": ["미아사거리역", "북한산우이역", "수유역", "4·19 카페거리", "수유리 먹자골목"],
        "강서구": ["발산역", "김포공항", "고척돔", "강서한강공원"],
        "관악구": ["서울대입구역", "신림역", "노량진"],
        "광진구": ["건대입구역", "군자역", "뚝섬역", "어린이대공원", "아차산", "성수카페거리"],
        "구로구": ["가산디지털단지역", "구로디지털단지역", "구로역", "남구로역", "신도림역"],
        "노원구": ["창동 신경제 중심지"],
        "도봉구": ["쌍문동 맛집거리"],
        "동대문구": [
            "동대문 관광특구", "동대문역", "장한평역", 
            "청량리 제기동 일대 전통시장", "DDP(동대문디자인플라자)"
        ],
        "동작구": ["사당역", "총신대입구(이수)역"],
        "마포구": [
            "홍대 관광특구", "합정역", "홍대입구역(2호선)", "연남동",
            "망원한강공원", "월드컵공원", "DMC(디지털미디어시티)"
        ],
        "서대문구": ["신촌·이대역", "충정로역", "혜화역", "독립문"],
        "서초구": ["양재역", "방배역 먹자골목", "서리풀공원·몽마르뜨공원", "반포한강공원"],
        "성동구": ["왕십리역", "성수카페거리", "서울숲공원", "뚝섬한강공원"],
        "성북구": ["성신여대입구역", "외대앞"],
        "송파구": ["잠실 관광특구", "잠실종합운동장", "잠실한강공원", "가락시장"],
        "양천구": ["오목교역·목동운동장"],
        "영등포구": ["영등포 타임스퀘어", "여의도", "여의도한강공원"],
        "용산구": [
            "이태원 관광특구", "삼각지역", "서울역", "용산역", "이태원역",
            "국립중앙박물관·용산가족공원", "남산공원", "이촌한강공원",
            "해방촌·경리단길", "용리단길", "이태원 앤틱가구거리"
        ],
        "은평구": ["연신내역", "불광천", "북서울꿈의숲"],
        "종로구": [
            "종로·청계 관광특구", "경복궁", "창덕궁·종묘", "광화문·덕수궁", "보신각",
            "북촌한옥마을", "서촌", "인사동", "청와대", "낙산공원·이화마을", "혜화역", "익선동"
        ],
        "중구": [
            "명동 관광특구", "광장(전통)시장", "덕수궁길·정동길", "남대문시장",
            "서울광장", "북창동 먹자골목"
        ],
        "중랑구": ["회기역"]
    }

    def __init__(self, api_key: str):
        self._api_key = api_key  # private
        self._base_url = "http://openapi.seoul.go.kr:8088"  # private

    @property
    def api_key(self) -> str:
        return self._api_key

    @classmethod
    def get_district_areas(cls) -> dict:
        return cls.DISTRICT_AREAS

    def _make_api_request(self, url: str) -> dict:
        """API 요청을 처리하는 private 메서드"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 실패: {str(e)}")
            return {'success': False, 'error': f'API 요청 실패: {str(e)}'}

    def _is_event_active(self, date_str: str, current_date: datetime.date) -> bool:
        """이벤트 활성화 여부를 확인하는 private 메서드"""
        try:
            # 날짜 문자열에서 불필요한 문자 제거
            date_range = date_str.split('~')
            start_date_str = date_range[0].strip()  # 시작 날짜
            end_date_str = date_range[1].strip() if len(date_range) > 1 else start_date_str  # 종료 날짜

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            return start_date <= current_date <= end_date  # 현재 날짜가 시작일과 종료일 사이인지 확인
        except ValueError:
            return False  # 날짜 형식이 잘못된 경우 False 반환

    # public interface
    def get_events_by_district(self, district: str, limit: int = 3) -> Dict[str, Any]:
        """공개 인터페이스: 특정 자치구의 문화 행사 정보 조회"""
        try:
            url = f"{self._base_url}/{self._api_key}/json/culturalEventInfo/1/1000/"
            data = self._make_api_request(url)
            
            if not data or 'culturalEventInfo' not in data:
                return {'success': False, 'error': '응답이 비어 있거나 유효하지 않습니다.', 'total_count': 0, 'data': []}
            
            all_events = data['culturalEventInfo'].get('row', [])  # 모든 행사 정보 가져오기
            
            if not all_events:
                return {'success': True, 'total_count': 0, 'data': [], 'message': '현재 등록된 행사가 없습니다.'}
                
            current_date = datetime.now().date()  # 현재 날짜 가져오기
            
            logger.info(f"조회할 구: {district}")
            logger.info(f"전체 이벤트 수: {len(all_events)}")
            
            # 특정 구의 활성화된 이벤트 필터링
            district_events = [
                self.format_event_data(event)
                for event in all_events
                if (event.get('GUNAME', '') == district or district in event.get('PLACE', '')) and
                   self._is_event_active(event.get('DATE', '1970-01-01'), current_date)
            ]
            
            logger.info(f"필터링된 이벤트 수: {len(district_events)}")
            
            return {
                'success': True,
                'total_count': len(district_events),
                'data': district_events[:limit]  # 제한된 수의 이벤트 반환
            }
            
        except Exception as e:
            logger.error(f"행사 정보 조회 중 오류 발생: {str(e)}")
            return {'success': False, 'error': f'알 수 없는 오류: {str(e)}', 'total_count': 0, 'data': []}

    @staticmethod
    def format_event_data(event: dict) -> dict:
        """이벤트 데이터 포맷팅을 위한 정적 메서드"""
        return {
            'TITLE': event.get('TITLE', '제목 없음'),
            'PLACE': event.get('PLACE', '장소 미정'),
            'DATE': event.get('DATE', '날짜 미정'),
            'CODENAME': event.get('CODENAME', '분류 없음'),
            'USE_FEE': event.get('USE_FEE', '요금 정보 없음'),
            'PROGRAM': event.get('PROGRAM', '프로그램 정보 없음'),
        }

    def get_district_info(self, major_place: str) -> str:
        """주요 장소에 해당하는 구별 지역 정보를 반환하는 함수."""
        for district, places in self.DISTRICT_AREAS.items():
            if major_place in places:
                return district
        return "해당 지역 정보 없음"

# Public interface functions
def get_events(api_key: str, major_place: str, limit: int = 3) -> Dict[str, Any]:
    """Public API function"""
    try:
        manager = CulturalEventManager(api_key)
        district = manager.get_district_info(major_place)
        
        if district == "해당 지역 정보 없음":
            # 장소명을 직접 구 이름으로 사용해 보기
            if any(major_place in district for district in manager.DISTRICT_AREAS.keys()):
                district = major_place
        
        return manager.get_events_by_district(district, limit)
    except Exception as e:
        logger.error(f"이벤트 조회 함수 실행 중 오류: {str(e)}")
        return {'success': False, 'error': str(e), 'total_count': 0, 'data': []}