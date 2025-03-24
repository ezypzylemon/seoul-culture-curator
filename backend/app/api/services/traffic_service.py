import requests
from typing import Dict, Any, List
import streamlit as st
from folium import plugins

class TrafficService:
    TRAFFIC_STATUS_COLORS = {
        '정체': 'red',
        '서행': 'yellow',
        '원활': 'green',
        '보통': 'blue'
    }

    PARKING_API_URL = "http://openapi.seoul.go.kr:8088/{api_key}/json/GetParkInfo/1/1000"
    SUBWAY_API_URL = "http://openapi.seoul.go.kr:8088/{api_key}/json/realtimeStationArrival/1/100/{station_name}"
    BUS_API_URL = "http://openapi.seoul.go.kr:8088/{api_key}/json/busRouteInfo/1/100"

    def __init__(self, api_key: str):
        self._api_key = api_key

    def get_traffic_color(self, status: str) -> str:
        """교통 상태에 따른 색상 반환"""
        return self.TRAFFIC_STATUS_COLORS.get(status, 'gray')

    def get_nearby_parking(self, lat: float, lng: float, radius: float = 1.0) -> List[Dict]:
        """주변 주차장 정보 조회"""
        try:
            response = requests.get(
                self.PARKING_API_URL.format(api_key=self._api_key)
            )
            data = response.json()
            
            parking_lots = []
            for lot in data.get('GetParkInfo', {}).get('row', []):
                # 입력된 좌표 근처의 주차장만 필터링
                if self._is_within_radius(
                    float(lot['LAT']), float(lot['LNG']), 
                    lat, lng, radius
                ):
                    parking_lots.append({
                        'name': lot['PARKING_NAME'],
                        'capacity': lot['CAPACITY'],
                        'available': lot['CUR_PARKING'],
                        'fees': lot['RATES'],
                        'address': lot['ADDR'],
                        'tel': lot['TEL'],
                        'lat': float(lot['LAT']),
                        'lng': float(lot['LNG'])
                    })
            return parking_lots
        except Exception as e:
            print(f"주차장 정보 조회 실패: {str(e)}")
            return []

    def get_public_transport(self, station_name: str) -> Dict[str, Any]:
        """대중교통 정보 조회"""
        try:
            # 지하철 정보 조회
            subway_response = requests.get(
                self.SUBWAY_API_URL.format(
                    api_key=self._api_key,
                    station_name=station_name
                )
            )
            subway_data = subway_response.json()

            # 버스 정보 조회 (정류장 근처 노선)
            bus_response = requests.get(
                self.BUS_API_URL.format(api_key=self._api_key)
            )
            bus_data = bus_response.json()

            return {
                'subway': self._parse_subway_data(subway_data),
                'bus': self._parse_bus_data(bus_data)
            }
        except Exception as e:
            print(f"대중교통 정보 조회 실패: {str(e)}")
            return {'subway': [], 'bus': []}

    def get_alternative_routes(self, start_lat: float, start_lng: float,
                             end_lat: float, end_lng: float) -> List[Dict]:
        """우회 경로 추천"""
        # 카카오 길찾기 API 활용
        KAKAO_MOBILITY_API_URL = "https://apis-navi.kakaomobility.com/v1/directions"
        
        headers = {
            "Authorization": f"KakaoAK {self._api_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "origin": f"{start_lng},{start_lat}",
            "destination": f"{end_lng},{end_lat}",
            "alternatives": "true"  # 대체 경로 요청
        }

        try:
            response = requests.get(KAKAO_MOBILITY_API_URL, headers=headers, params=params)
            routes = response.json().get('routes', [])
            
            return [{
                'path': route['sections'][0]['roads'],
                'duration': route['duration'],
                'distance': route['distance'],
                'traffic_color': self.get_traffic_color(route.get('traffic_state', '보통'))
            } for route in routes]
        except Exception as e:
            print(f"우회 경로 조회 실패: {str(e)}")
            return []

    @staticmethod
    def _is_within_radius(lat1: float, lng1: float, 
                         lat2: float, lng2: float, 
                         radius: float) -> bool:
        """두 지점 사이의 거리가 반경 내에 있는지 확인"""
        from math import sin, cos, sqrt, atan2, radians
        
        R = 6371.0  # 지구의 반지름 (km)

        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        
        dlng = lng2 - lng1
        dlat = lat2 - lat1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c

        return distance <= radius

    @staticmethod
    def _parse_subway_data(data: Dict) -> List[Dict]:
        """지하철 데이터 파싱"""
        arrivals = []
        for train in data.get('realtimeStationArrival', {}).get('row', []):
            arrivals.append({
                'line': train['subwayId'],
                'direction': train['trainLineNm'],
                'message': train['arvlMsg2']
            })
        return arrivals

    @staticmethod
    def _parse_bus_data(data: Dict) -> List[Dict]:
        """버스 데이터 파싱"""
        routes = []
        for bus in data.get('busRouteInfo', {}).get('row', []):
            routes.append({
                'route_id': bus['busRouteId'],
                'route_name': bus['routeName'],
                'route_type': bus['routeType']
            })
        return routes
