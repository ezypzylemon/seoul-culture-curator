from typing import Dict, Any, List
import google.generativeai as genai
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CultureAgent:
    def __init__(self):
        self._model = genai.GenerativeModel('gemini-1.5-flash')
        self._context = {
            "역할": "문화예술 전문 큐레이터",
            "전문분야": [
                "현대미술", "클래식 음악", "공연예술",
                "전통문화", "대중문화", "문화재",
                "도시계획", "교통공학", "관광경영"
            ],
            "성격": "전문적이고 분석적인",
            "특징": [
                "서울시 문화시설 전문가",
                "도시 데이터 분석가",
                "문화예술 기획자",
                "관객 개발 전문가"
            ]
        }

    def analyze_situation(self, area: str, population_data: Dict[str, Any],
                        traffic_data: Dict[str, Any],
                        commercial_data: Dict[str, Any],
                        user_preferences: Dict[str, str]) -> Dict[str, Any]:
        """상황 분석 및 추천"""
        prompt = f"""
        당신은 서울시 문화예술 전문 큐레이터입니다. 다음 정보를 바탕으로 방문객을 위한 상세한 안내를 제공해주세요.

        분석 지역: {area}
        
        실시간 현황:
        - 인구 혼잡도: {population_data.get('congestion_level')}
        - 도보 환경: {population_data.get('congestion_message')}
        - 교통 상황: {traffic_data.get('status')} ({traffic_data.get('speed')} km/h)
        - 상권 활성도: {commercial_data.get('congestion_level')}
        
        방문객 정보:
        - 성별: {user_preferences['gender']}
        - 연령: {user_preferences['age_group']}
        - 자녀동반: {user_preferences['has_children']}
        - 이동수단: {user_preferences['transportation']}

        다음 형식으로 전문적이고 실용적인 안내를 제공해주세요:

        [현재 상황 평가]
        - 전반적인 방문 여건 분석
        - 현재 시점의 장단점
        - 추천 활동 유형

        [최적의 방문 시간대]
        - 현재 추천 활동
        - 피크 타임 정보
        - 권장 체류 시간
        - 시간대별 추천 코스

        [추천 동선]
        - 효율적인 시작점
        - 핵심 관람/체험 포인트
        - 쾌적한 이동 경로
        - 예상 소요 시간
        - 중간 휴식 포인트

        [방문객 안내사항]
        1. 편의시설 정보:
           - 화장실/수유실 위치
           - 식음료 시설
           - 휴식 공간
           - 보관소/물품보관함
           
        2. 안전/편의 정보:
           - 무료 와이파이 존
           - 응급의료 시설
           - 안전요원 상주 구역
           - 장애인 편의시설
           
        3. 기타 유용한 정보:
           - 사진 촬영 가능 구역
           - 음식물 반입 규정
           - 주차/택시 승강장
           - 현장 매표소 위치

        모든 정보는 방문객의 연령대와 이동수단을 고려하여 맞춤형으로 제공해주세요.
        혼잡도가 낮은 경우에도 긍정적인 관점에서 장점과 활용 방안을 제시해주세요.
        """
        
        try:
            response = self._model.generate_content(prompt)
            return self._parse_agent_response(response.text)
        except Exception as e:
            logger.error(f"에이전트 분석 중 오류 발생: {str(e)}")
            return self._get_default_response()

    def _get_default_response(self) -> Dict[str, Any]:
        """기본 응답 생성"""
        return {
            'situation': '현재 상황 분석을 수행할 수 없습니다.',
            'best_time': '시간대별 정보를 불러올 수 없습니다.',
            'route': '추천 동선 정보를 생성할 수 없습니다.',
            'warnings': '안내사항 정보를 불러올 수 없습니다.'
        }

    def get_personalized_recommendation(self,
                                     events: List[Dict[str, Any]], 
                                     user_preferences: Dict[str, str]) -> str:
        """사용자 맞춤 행사 추천"""
        prompt = f"""
        사용자 정보:
        - 성별: {user_preferences['gender']}
        - 나이대: {user_preferences['age_group']}
        - 자녀 여부: {user_preferences['has_children']}
        - 이동수단: {user_preferences['transportation']}

        다음 문화 행사들 중에서 사용자에게 가장 적합한 행사를 추천해주세요:
        {self._format_events(events)}

        다음 기준으로 분석해주세요:
        1. 사용자의 라이프스타일 고려
        2. 이동수단에 따른 접근성
        3. 자녀 동반 가능 여부
        4. 연령대별 선호도
        5. 시간대별 혼잡도
        """
        
        try:
            response = self._model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"행사 추천 중 오류 발생: {str(e)}")
            return "행사 추천을 생성할 수 없습니다. 잠시 후 다시 시도해 주세요."

    @staticmethod
    def _format_events(events: List[Dict[str, Any]]) -> str:
        """이벤트 정보 포맷팅"""
        formatted = []
        for event in events:
            formatted.append(
                f"행사: {event.get('TITLE', '제목 없음')}\n"
                f"장소: {event.get('PLACE', '장소 미정')}\n"
                f"날짜: {event.get('DATE', '날짜 미정')}\n"
                f"분류: {event.get('CODENAME', '분류 없음')}\n"
                f"요금: {event.get('USE_FEE', '요금 정보 없음')}\n"
                f"프로그램: {event.get('PROGRAM', '프로그램 정보 없음')}\n"
            )
        return "\n".join(formatted)

    def _parse_agent_response(self, response: str) -> Dict[str, Any]:
        """에이전트 응답 파싱"""
        try:
            sections = {
                'situation': '현재 상황 평가',
                'best_time': '최적의 방문 시간대',
                'route': '추천 동선',
                'warnings': '방문객 안내사항'
            }
            
            parsed = {}
            text = response.replace('\n\n', '\n').replace('###', '')
            
            # 각 섹션의 시작과 끝 위치 찾기
            section_positions = []
            for section_name, header in sections.items():
                try:
                    start = text.index(header)
                    section_positions.append((start, header, section_name))
                except ValueError:
                    continue
            
            # 시작 위치를 기준으로 정렬
            section_positions.sort()
            
            # 각 섹션의 내용 추출
            for i, (start, header, section_name) in enumerate(section_positions):
                # 다음 섹션의 시작 위치 찾기
                if i < len(section_positions) - 1:
                    end = section_positions[i + 1][0]
                else:
                    end = len(text)
                
                # 해당 섹션의 내용 추출
                content = text[start + len(header):end].strip()
                
                # 내용이 있는 경우에만 저장
                if content:
                    # 불필요한 문자 제거 및 정리
                    content = (content.replace(':', '')
                             .replace('•', '')
                             .replace('*', '')
                             .strip('-')
                             .strip())
                    parsed[section_name] = content
                else:
                    parsed[section_name] = f"{section_name.replace('_', ' ').title()} 정보가 없습니다."
            
            # 누락된 섹션에 대한 기본값 설정
            for section_name in sections.keys():
                if section_name not in parsed:
                    parsed[section_name] = f"{section_name.replace('_', ' ').title()} 정보를 찾을 수 없습니다."
            
            return parsed
            
        except Exception as e:
            logger.error(f"응답 파싱 중 오류 발생: {str(e)}")
            default_response = {
                'situation': '현재 분석을 수행할 수 없습니다.',
                'best_time': '시간대별 정보를 찾을 수 없습니다.',
                'route': '동선 정보를 찾을 수 없습니다.',
                'warnings': '안내사항 정보를 찾을 수 없습니다.'
            }
            return default_response