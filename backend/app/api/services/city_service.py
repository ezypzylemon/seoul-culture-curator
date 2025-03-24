import requests
import json
from urllib.parse import quote
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SeoulCityData:
    def __init__(self):
        load_dotenv()
        self._api_key = os.getenv('SEOUL_API_KEY')
        self._base_url = "http://openapi.seoul.go.kr:8088"
        self._headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8'
        }
        self.valid_areas = [
            "강남 MICE 관광특구", "강남역", "고속터미널역", "교대역", "선릉역",
            "신논현역·논현역", "역삼역", "압구정로데오거리", "청담동 명품거리", "가로수길",
            "고덕역", "서울 암사동 유적",
            "미아사거리역", "북한산우이역", "수유역", "4·19 카페거리", "수유리 먹자골목",
            "발산역", "김포공항", "고척돔", "강서한강공원",
            "서울대입구역", "신림역", "노량진",
            "건대입구역", "군자역", "뚝섬역", "어린이대공원", "아차산", "성수카페거리",
            "가산디지털단지역", "구로디지털단지역", "구로역", "남구로역", "신도림역",
            "창동 신경제 중심지",
            "쌍문동 맛집거리",
            "동대문 관광특구", "동대문역", "장한평역", "청량리 제기동 일대 전통시장", 
            "DDP(동대문디자인플라자)",
            "사당역", "총신대입구(이수)역",
            "홍대 관광특구", "합정역", "홍대입구역(2호선)", "연남동",
            "망원한강공원", "월드컵공원", "DMC(디지털미디어시티)",
            "신촌·이대역", "충정로역", "혜화역", "독립문",
            "양재역", "방배역 먹자골목", "서리풀공원·몽마르뜨공원", "반포한강공원",
            "왕십리역", "성수카페거리", "서울숲공원", "뚝섬한강공원",
            "성신여대입구역", "외대앞",
            "잠실 관광특구", "잠실종합운동장", "잠실한강공원", "가락시장",
            "오목교역·목동운동장",
            "영등포 타임스퀘어", "여의도", "여의도한강공원",
            "이태원 관광특구", "삼각지역", "서울역", "용산역", "이태원역",
            "국립중앙박물관·용산가족공원", "남산공원", "이촌한강공원",
            "해방촌·경리단길", "용리단길", "이태원 앤틱가구거리",
            "연신내역", "불광천", "북서울꿈의숲",
            "종로·청계 관광특구", "경복궁", "창덕궁·종묘", "광화문·덕수궁",
            "보신각", "북촌한옥마을", "서촌", "인사동", "청와대",
            "낙산공원·이화마을", "혜화역", "익선동",
            "명동 관광특구", "광장(전통)시장", "덕수궁길·정동길",
            "남대문시장", "서울광장", "북창동 먹자골목",
            "회기역"
        ]

    def _get_endpoint(self, area: str) -> str:
        """private: API 엔드포인트 URL 생성"""
        return f"{self._base_url}/{self._api_key}/json/citydata/1/5/{quote(area)}"

    def _fetch_data(self, area: str) -> Optional[Dict]:
        """private: API로부터 데이터 가져오기"""
        try:
            for attempt in range(3):
                response = requests.get(
                    self._get_endpoint(area), 
                    headers=self._headers, 
                    verify=False,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'CITYDATA' in data:
                        return data['CITYDATA']
                    else:
                        logger.warning(f"시도 {attempt + 1}: 유효하지 않은 응답 형식")
                else:
                    logger.warning(f"시도 {attempt + 1}: 상태 코드 {response.status_code}")
                
                if attempt < 2:
                    time.sleep(1)
            
            logger.error(f"'{area}' 데이터 조회 실패: 최대 재시도 횟수 초과")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 실패: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"예상치 못한 오류: {str(e)}")
            return None

    @property
    def api_key(self) -> str:
        """API 키 getter"""
        return self._api_key

    def get_population_status(self, area: str) -> Dict:
        """공개 인터페이스: 인구 현황 데이터"""
        data = self._fetch_data(area)
        if not data:
            return {}
        return self._extract_population_data(data)

    def get_traffic_status(self, area: str) -> Dict:
        """공개 인터페이스: 교통 현황 데이터"""
        data = self._fetch_data(area)
        if not data:
            return {}
        return self._extract_traffic_data(data)

    def get_commercial_status(self, area: str) -> Dict:
        """공개 인터페이스: 상권 현황 데이터"""
        data = self._fetch_data(area)
        if not data:
            return {}
        return self._extract_commercial_data(data)

    def _extract_population_data(self, data: Dict) -> Dict:
        """private: 인구 데이터 추출"""
        try:
            live_status = data.get('LIVE_PPLTN_STTS', [{}])[0]
            if not live_status:
                return self._get_default_population_data()

            # 현재 시간 정보 추출
            current_time = live_status.get('PPLTN_TIME', '정보 없음')
            
            # 예측 데이터 처리
            forecasts = live_status.get('FCST_PPLTN', [])
            forecast_data = []
            
            for forecast in forecasts:
                forecast_data.append({
                    'time': forecast.get('FCST_TIME', '정보 없음'),
                    'congestion_level': forecast.get('FCST_CONGEST_LVL', '정보 없음'),
                    'population_min': forecast.get('FCST_PPLTN_MIN', '정보 없음'),
                    'population_max': forecast.get('FCST_PPLTN_MAX', '정보 없음')
                })

            return {
                'current_time': current_time,  # 현재 시간 추가
                'congestion_level': live_status.get('AREA_CONGEST_LVL', '정보 없음'),
                'congestion_message': live_status.get('AREA_CONGEST_MSG', '정보 없음'),
                'population_range': {
                    'min': int(live_status.get('AREA_PPLTN_MIN', 0)),
                    'max': int(live_status.get('AREA_PPLTN_MAX', 0))
                },
                'gender_ratio': {
                    'male': live_status.get('MALE_PPLTN_RATE', 0),
                    'female': live_status.get('FEMALE_PPLTN_RATE', 0)
                },
                'age_distribution': {
                    '20s': live_status.get('PPLTN_RATE_20', 0),
                    '30s': live_status.get('PPLTN_RATE_30', 0),
                    '40s': live_status.get('PPLTN_RATE_40', 0)
                },
                'forecasts': forecast_data  # 예측 데이터 배열 추가
            }
        except Exception as e:
            logger.error(f"인구 데이터 추출 중 오류 발생: {str(e)}")
            return self._get_default_population_data()

    def _extract_traffic_data(self, data: Dict) -> Dict:
        """private: 교통 데이터 추출"""
        try:
            traffic = data.get('ROAD_TRAFFIC_STTS', {}).get('AVG_ROAD_DATA', {})
            return {
                'speed': traffic.get('ROAD_TRAFFIC_SPD', '정보 없음'),
                'status': traffic.get('ROAD_TRAFFIC_IDX', '정보 없음'),
                'message': traffic.get('ROAD_MSG', '정보 없음')
            }
        except Exception as e:
            logger.error(f"교통 데이터 추출 중 오류 발생: {str(e)}")
            return {
                'speed': '정보 없음',
                'status': '정보 없음',
                'message': '정보 없음'
            }

    def _extract_commercial_data(self, data: Dict) -> Dict:
        """private: 상권 데이터 추출"""
        try:
            commercial = data.get('LIVE_CMRCL_STTS', {})
            if not isinstance(commercial, dict):
                logger.warning(f"상권 데이터 형식 오류: {type(commercial)}")
                return self._get_default_commercial_data()

            food_categories = ['한식', '일식/중식/양식', '제과/커피/패스트푸드', '기타요식']
            
            businesses = commercial.get('CMRCL_RSB', [])
            if not isinstance(businesses, list):
                logger.warning(f"상권 업종 데이터 형식 오류: {type(businesses)}")
                return self._get_default_commercial_data()

            return {
                'congestion_level': commercial.get('AREA_CMRCL_LVL', '정보 없음'),
                'food_businesses': [
                    {
                        'category': biz.get('RSB_MID_CTGR', '정보 없음'),
                        'congestion_level': biz.get('RSB_PAYMENT_LVL', '정보 없음'),
                        'payment_count': biz.get('RSB_SH_PAYMENT_CNT', '0'),
                        'store_count': biz.get('RSB_MCT_CNT', '0')
                    }
                    for biz in businesses
                    if biz.get('RSB_MID_CTGR') in food_categories
                ]
            }
        except Exception as e:
            logger.error(f"상권 데이터 추출 중 오류 발생: {str(e)}")
            return self._get_default_commercial_data()

    def _get_default_population_data(self) -> Dict:
        """기본 인구 데이터 반환"""
        return {
            'current_time': '정보 없음',
            'congestion_level': '정보 없음',
            'congestion_message': '정보를 불러올 수 없습니다.',
            'population_range': {'min': 0, 'max': 0},
            'gender_ratio': {'male': 0, 'female': 0},
            'age_distribution': {'20s': 0, '30s': 0, '40s': 0},
            'forecasts': []
        }

    def _get_default_commercial_data(self) -> Dict:
        """기본 상권 데이터 반환"""
        return {
            'congestion_level': '정보 없음',
            'food_businesses': []
        }