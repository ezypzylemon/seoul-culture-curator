from pydantic import BaseModel
from typing import Dict, List, Optional, Any

# 사용자 선호도 모델
class UserPreferences(BaseModel):
    gender: str = "남성"
    age_group: str = "20대"
    has_children: str = "아니오"
    transportation: str = "도보"

# 채팅 요청/응답 모델
class ChatRequest(BaseModel):
    message: str
    user_preferences: Dict[str, str]

class ChatResponse(BaseModel):
    answer: str

# 추천 요청/응답 모델
class RecommendationRequest(BaseModel):
    location: str
    user_preferences: Dict[str, str]

class RecommendationResponse(BaseModel):
    area: str
    status: Dict[str, Any]
    events: List[Dict[str, Any]]
    analysis: Dict[str, str]

# 지도 데이터 모델
class CongestionData(BaseModel):
    areas: List[Dict[str, Any]]
    statistics: Dict[str, Any]

class AreaCongestionData(BaseModel):
    area: str
    congestion_level: str
    population_range: Dict[str, int]
    coordinates: Dict[str, float]
    traffic_status: Dict[str, Any]
    commercial_status: Dict[str, Any]

# 이벤트 모델
class CulturalEvent(BaseModel):
    title: str
    place: str
    date: str
    code_name: str
    use_fee: str
    program: str

class EventsResponse(BaseModel):
    success: bool
    total_count: int
    data: List[CulturalEvent]
    error: Optional[str] = None