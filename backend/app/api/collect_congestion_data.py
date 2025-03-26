from app.api.services.city_service import SeoulCityData
from app.api.services.congestion_db import insert_congestion_data
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def collect_congestion_data():
    city = SeoulCityData()
    area_results = []

    for area in city.valid_areas:
        try:
            # 데이터 수집
            result = city.get_population_status(area)

            if not result:
                logger.warning(f"[{area}] 결과 없음 (None)")
                continue

            if result.get("congestion_level") == "정보 없음":
                logger.warning(f"[{area}] 혼잡도 정보 없음, 스킵")
                continue

            area_results.append({
                "area": area,
                "data": result
            })

            logger.info(f"[{area}] 데이터 수집 성공")

        except Exception as e:
            logger.error(f"[{area}] 처리 중 예외 발생: {e}")
            continue

        # 과도한 요청 방지용 쿨다운
        time.sleep(0.1)

    # ✅ DB 저장 함수 호출
    if area_results:
        insert_congestion_data(area_results)
        logger.info("✅ DB 저장 완료")

    return area_results

if __name__ == "__main__":
    results = collect_congestion_data()
    logger.info(f"✅ 최종 수집된 지역 수: {len(results)}개")
