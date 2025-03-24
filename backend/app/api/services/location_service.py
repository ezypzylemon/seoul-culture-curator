#####################
import requests
import math
import os
import logging
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CityInfo:
    # 서울시 주요 지역 좌표 정보 (위도, 경도)
    AREA_COORDINATES = {
        # 강남구
        "강남 MICE 관광특구": (37.5066614, 127.0628454),
        "강남역": (37.4980854, 127.0276532),
        "고속터미널역": (37.5042724, 127.0046856),
        "교대역": (37.4938933, 127.0142322),
        "선릉역": (37.5045242, 127.0492737),
        "신논현역·논현역": (37.5045551, 127.0252564),
        "역삼역": (37.5006736, 127.0365645),
        "압구정로데오거리": (37.5270616, 127.0389741),
        "청담동 명품거리": (37.5259467, 127.0474042),
        "가로수길": (37.5204173, 127.0229145),

        # 강동구
        "고덕역": (37.5548647, 127.1545159),
        "서울 암사동 유적": (37.5507112, 127.1297664),

        # 강북구
        "미아사거리역": (37.6134436, 127.0303268),
        "북한산우이역": (37.6630642, 127.0118708),
        "수유역": (37.6378355, 127.0251699),        
        "4·19 카페거리": (37.6424396, 127.0145932),
        "수유리 먹자골목": (37.6372165, 127.0255142),

        # 강서구
        "발산역": (37.5581682, 126.8377955),
        "김포공항": (37.5585973, 126.8025488),
        "고척돔": (37.4982125, 126.8429179),
        "강서한강공원": (37.5675813, 126.8225002),

        # 관악구
        "서울대입구역": (37.4812032, 126.9524143),
        "신림역": (37.4840693, 126.9294529),
        "노량진": (37.5133097, 126.9428261),

        # 광진구
        "건대입구역": (37.5404578, 127.0694181),
        "군자역": (37.5571454, 127.0795313),
        "뚝섬역": (37.5474001, 127.0474821),
        "어린이대공원": (37.5480124, 127.0741101),
        "아차산": (37.5552702, 127.0972960),
        "성수카페거리": (37.5426762, 127.0560246),

        # 구로구
        "가산디지털단지역": (37.4819424, 126.8825100),
        "구로디지털단지역": (37.4851566, 126.9014964),
        "구로역": (37.5030528, 126.8818090),
        "남구로역": (37.4856306, 126.8873066),
        "신도림역": (37.5091557, 126.8912390),

        # 노원구
        "창동 신경제 중심지": (37.6537685, 127.0478415),

        # 도봉구
        "쌍문동 맛집거리": (37.6482897, 127.0342835),

        # 동대문구
        "동대문 관광특구": (37.5711652, 127.0075755),
        "동대문역": (37.5712803, 127.0097171),
        "장한평역": (37.5614460, 127.0645451),
        "청량리 제기동 일대 전통시장": (37.5800520, 127.0389451),
        "DDP(동대문디자인플라자)": (37.5674028, 127.0098185),

        # 동작구
        "사당역": (37.4764763, 126.9777464),
        "총신대입구(이수)역": (37.4862592, 126.9822701),

        # 마포구
        "홍대 관광특구": (37.5561090, 126.9225419),
        "합정역": (37.5495737, 126.9139742),
        "홍대입구역(2호선)": (37.5571454, 126.9252262),
        "연남동": (37.5627454, 126.9244356),
        "망원한강공원": (37.5524557, 126.8999944),
        "월드컵공원": (37.5716022, 126.8797896),
        "DMC(디지털미디어시티)": (37.5785683, 126.8915047),

        # 서대문구
        "신촌·이대역": (37.5568707, 126.9368323),
        "충정로역": (37.5595961, 126.9638743),
        "혜화역": (37.5820926, 127.0016370),
        "독립문": (37.5705098, 126.9577767),

        # 서초구
        "양재역": (37.4843030, 127.0341787),
        "방배역 먹자골목": (37.4814106, 126.9974770),
        "서리풀공원·몽마르뜨공원": (37.4866577, 127.0077036),
        "반포한강공원": (37.5102695, 126.9948528),

        # 성동구
        "왕십리역": (37.5612809, 127.0385406),
        "성수카페거리": (37.5426762, 127.0560246),
        "서울숲공원": (37.5443613, 127.0374614),
        "뚝섬한강공원": (37.5297449, 127.0697750),

        # 성북구
        "성신여대입구역": (37.5926880, 127.0162396),
        "외대앞": (37.5964984, 127.0583471),

        # 송파구
        "잠실 관광특구": (37.5130731, 127.1001997),
        "잠실종합운동장": (37.5158076, 127.0731814),
        "잠실한강공원": (37.5207124, 127.0873904),
        "가락시장": (37.4929000, 127.1179767),

        # 양천구
        "오목교역·목동운동장": (37.5245196, 126.8753721),

        # 영등포구
        "영등포 타임스퀘어": (37.5173108, 126.9033793),
        "여의도": (37.5215132, 126.9243001),
        "여의도한강공원": (37.5284309, 126.9337667),

        # 용산구
        "이태원 관광특구": (37.5340087, 126.9941844),
        "삼각지역": (37.5343933, 126.9729813),
        "서울역": (37.5559603, 126.9726557),
        "용산역": (37.5300374, 126.9650008),
        "이태원역": (37.5344381, 126.9941904),
        "국립중앙박물관·용산가족공원": (37.5240796, 126.9803327),
        "남산공원": (37.5507075, 126.9905033),
        "이촌한강공원": (37.5194277, 126.9722253),
        "해방촌·경리단길": (37.5401641, 126.9883095),
        "용리단길": (37.5290107, 126.9650817),
        "이태원 앤틱가구거리": (37.5346098, 126.9910908),

        # 은평구
        "연신내역": (37.6190748, 126.9205244),
        "불광천": (37.6088770, 126.9293697),
        "북서울꿈의숲": (37.6207611, 127.0416319),

        # 종로구
        "종로·청계 관광특구": (37.5704009, 126.9882266),
        "경복궁": (37.5776087, 126.9767453),
        "창덕궁·종묘": (37.5792550, 126.9911624),
        "광화문·덕수궁": (37.5711452, 126.9767365),
        "보신각": (37.5699033, 126.9837760),
        "북촌한옥마을": (37.5824129, 126.9846369),
        "서촌": (37.5791858, 126.9708966),
        "인사동": (37.5743189, 126.9837464),
        "청와대": (37.5866076, 126.9745179),
        "낙산공원·이화마을": (37.5808156, 127.0067010),
        "혜화역": (37.5820926, 127.0016370),
        "익선동": (37.5724551, 126.9896308),

        # 중구
        "명동 관광특구": (37.5636490, 126.9895503),
        "광장(전통)시장": (37.5704438, 127.0092876),
        "덕수궁길·정동": (37.5652771, 126.9745313),
        "남대문시장": (37.5592154, 126.9776091),
        "서울광장": (37.5657000, 126.9769000),
        "북창동 먹자골목": (37.5608374, 126.9753706),

        # 중랑구
        "회기역": (37.5899272, 127.0575051),
        # ... (기존 좌표 정보는 그대로 유지)
    }

    def __init__(self):
        load_dotenv()
        self._api_key = os.getenv("KAKAO_REST_API_KEY")
        self._base_url = os.getenv("KAKAO_API_BASE_URL", "https://dapi.kakao.com/v2/local/search")

    @property
    def api_key(self) -> str:
        return self._api_key

    @classmethod
    def _get_area_coordinates(cls) -> dict:
        """private: 지역 좌표 데이터 접근"""
        return cls.AREA_COORDINATES

    @staticmethod
    def _calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """private: 두 좌표 사이 거리 계산 (km)"""
        R = 6371  # 지구의 반지름 (킬로미터)
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon1 - lon2)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def get_coordinates_from_kakao(self, location_name: str) -> Optional[Tuple[float, float]]:
        """위치 이름으로 좌표 얻기"""
        url = f"{self._base_url}/keyword.json"
        headers = {
            "Authorization": f"KakaoAK {self._api_key}"
        }
        params = {
            "query": location_name
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data['documents']:
                # 첫 번째 결과의 좌표를 반환 (float로 변환)
                return (float(data['documents'][0]['y']), float(data['documents'][0]['x']))
            logger.warning(f"위치 '{location_name}'에 대한 결과가 없습니다.")
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 실패: {str(e)}")
        except Exception as e:
            logger.error(f"좌표 조회 중 오류: {str(e)}")
        
        return None

    # Public interfaces
    @classmethod
    def find_nearest_location(cls, user_location: str) -> str:
        """공개 인터페이스: 가장 가까운 지역 찾기"""
        # 먼저 AREA_COORDINATES에서 직접 조회
        user_coordinates = cls._get_area_coordinates().get(user_location)
        
        # 직접 조회 실패하면 카카오 API 이용
        if not user_coordinates:
            city_info = cls()  # API 호출을 위한 인스턴스 생성
            user_coordinates = city_info.get_coordinates_from_kakao(user_location)
        
        if user_coordinates is None:
            return "위치를 찾을 수 없습니다."

        nearest_location = None
        min_distance = float('inf')

        # 주요 지역과의 거리 계산
        for location, coordinates in cls._get_area_coordinates().items():
            distance = cls._calculate_distance(user_coordinates, coordinates)
            if distance < min_distance:
                min_distance = distance
                nearest_location = location

        return nearest_location

    def get_location_info(self, location: str) -> Dict:
        """공개 인터페이스: 위치 정보 조회"""
        # 먼저 AREA_COORDINATES에서 직접 조회
        coordinates = self.AREA_COORDINATES.get(location)
        
        # 직접 조회 실패하면 카카오 API 이용
        if not coordinates:
            coordinates = self.get_coordinates_from_kakao(location)
            
        if not coordinates:
            return {}
            
        return {
            'coordinates': {
                'lat': coordinates[0],
                'lng': coordinates[1]
            },
            'nearest_location': self.find_nearest_location(location)
        }

def get_coordinates(location: str) -> Optional[Dict[str, float]]:
    """카카오 API를 사용하여 위치의 좌표를 가져옵니다."""
    try:
        # 먼저 AREA_COORDINATES에서 검색
        if location in CityInfo.AREA_COORDINATES:
            lat, lng = CityInfo.AREA_COORDINATES[location]
            return {
                'lat': lat,
                'lng': lng
            }
        
        # 없으면 API 요청
        load_dotenv()
        KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
        params = {"query": location}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        result = response.json()
        if result['documents']:
            return {
                'lat': float(result['documents'][0]['y']),
                'lng': float(result['documents'][0]['x'])
            }
        return None
    except Exception as e:
        logger.error(f"좌표 가져오기 실패: {str(e)}")
        return None