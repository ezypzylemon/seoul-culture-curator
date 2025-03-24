import requests
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class TransportMode(Enum):
    WALKING = "walk"
    DRIVING = "car"
    TRANSIT = "transit"

@dataclass
class RouteInfo:
    distance: float  # 미터
    duration: int   # 초
    steps: List[str]
    path: List[List[float]]  # [[lat, lng], ...]
    transport_mode: TransportMode

class RouteService:
    def __init__(self, kakao_api_key: str):
        self._api_key = kakao_api_key
        self._headers = {
            "Authorization": f"KakaoAK {self._api_key}"
        }

    def get_routes(self, 
                  start_lat: float, start_lng: float,
                  end_lat: float, end_lng: float,
                  mode: TransportMode) -> List[RouteInfo]:
        """모든 이동 수단에 대한 경로 조회"""
        if mode == TransportMode.DRIVING:
            return self._get_driving_routes(start_lat, start_lng, end_lat, end_lng)
        elif mode == TransportMode.TRANSIT:
            return self._get_transit_routes(start_lat, start_lng, end_lat, end_lng)
        else:
            return self._get_walking_routes(start_lat, start_lng, end_lat, end_lng)

    def _get_driving_routes(self, start_lat: float, start_lng: float,
                          end_lat: float, end_lng: float) -> List[RouteInfo]:
        """자동차 경로 조회"""
        url = "https://apis-navi.kakaomobility.com/v1/directions"
        params = {
            "origin": f"{start_lng},{start_lat}",
            "destination": f"{end_lng},{end_lat}",
            "priority": "RECOMMEND",
            "car_type": "1",
            "alternatives": "true"
        }
        
        try:
            response = requests.get(url, headers=self._headers, params=params)
            data = response.json()
            
            routes = []
            for route in data.get('routes', []):
                steps = []
                path = []
                
                for section in route.get('sections', []):
                    for road in section.get('roads', []):
                        steps.append(road.get('name', ''))
                        path.extend([[p[1], p[0]] for p in road.get('vertexes', [])])
                
                routes.append(RouteInfo(
                    distance=route.get('summary', {}).get('distance', 0),
                    duration=route.get('summary', {}).get('duration', 0),
                    steps=steps,
                    path=path,
                    transport_mode=TransportMode.DRIVING
                ))
            
            return routes
        except Exception as e:
            print(f"자동차 경로 조회 실패: {str(e)}")
            return []

    def _get_transit_routes(self, start_lat: float, start_lng: float,
                          end_lat: float, end_lng: float) -> List[RouteInfo]:
        """대중교통 경로 조회"""
        url = "https://apis-navi.kakaomobility.com/v1/directions"
        params = {
            "origin": f"{start_lng},{start_lat}",
            "destination": f"{end_lng},{end_lat}",
            "priority": "RECOMMEND",
            "mode": "TRANSIT",
            "alternatives": "true"
        }
        
        try:
            response = requests.get(url, headers=self._headers, params=params)
            data = response.json()
            
            routes = []
            for route in data.get('routes', []):
                steps = []
                path = []
                
                for section in route.get('sections', []):
                    if section.get('type') == 'TRANSIT':
                        steps.append(f"{section.get('route_name')} - {section.get('stations', [])[0]}")
                    path.extend([[p[1], p[0]] for p in section.get('guide_points', [])])
                
                routes.append(RouteInfo(
                    distance=route.get('summary', {}).get('distance', 0),
                    duration=route.get('summary', {}).get('duration', 0),
                    steps=steps,
                    path=path,
                    transport_mode=TransportMode.TRANSIT
                ))
            
            return routes
        except Exception as e:
            print(f"대중교통 경로 조회 실패: {str(e)}")
            return []

    def _get_walking_routes(self, start_lat: float, start_lng: float,
                          end_lat: float, end_lng: float) -> List[RouteInfo]:
        """도보 경로 조회"""
        url = "https://apis-navi.kakaomobility.com/v1/directions"
        params = {
            "origin": f"{start_lng},{start_lat}",
            "destination": f"{end_lng},{end_lat}",
            "priority": "RECOMMEND",
            "mode": "WALK"
        }
        
        try:
            response = requests.get(url, headers=self._headers, params=params)
            data = response.json()
            
            routes = []
            path = []
            steps = []
            
            for section in data.get('routes', [])[0].get('sections', []):
                for guide in section.get('guides', []):
                    steps.append(guide.get('name', ''))
                path.extend([[p[1], p[0]] for p in section.get('guide_points', [])])
            
            routes.append(RouteInfo(
                distance=data.get('routes', [])[0].get('summary', {}).get('distance', 0),
                duration=data.get('routes', [])[0].get('summary', {}).get('duration', 0),
                steps=steps,
                path=path,
                transport_mode=TransportMode.WALKING
            ))
            
            return routes
        except Exception as e:
            print(f"도보 경로 조회 실패: {str(e)}")
            return []

    def get_nearby_parking(self, lat: float, lng: float, radius: float = 1.0) -> List[Dict]:
        """주변 주차장 정보 조회"""
        url = f"https://dapi.kakao.com/v2/local/search/category.json"
        params = {
            "category_group_code": "PK6",  # 주차장 카테고리 코드
            "x": str(lng),
            "y": str(lat),
            "radius": str(int(radius * 1000))  # km를 m로 변환
        }
        
        try:
            response = requests.get(url, headers=self._headers, params=params)
            data = response.json()
            
            return [{
                'name': place['place_name'],
                'address': place['road_address_name'] or place['address_name'],
                'phone': place['phone'],
                'distance': float(place['distance']),
                'lat': float(place['y']),
                'lng': float(place['x'])
            } for place in data.get('documents', [])]
        except Exception as e:
            print(f"주차장 정보 조회 실패: {str(e)}")
            return []
