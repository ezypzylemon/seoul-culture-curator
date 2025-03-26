import sqlite3
import os
import logging
from typing import List, Dict
from app.api.services.coordinates import AREA_COORDINATES  # 절대 경로로 수정

# DB 절대경로로 설정
DB_PATH = "/home/ubuntu/myproject/backend/app/data/congestion.sqlite"

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_db():
    """DB 초기화: 테이블이 없으면 생성"""
    try:
        db_dir = os.path.dirname(DB_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"디렉토리 {db_dir}가 생성되었습니다.")

        logger.info(f"DB 경로: {DB_PATH}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS congestion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area TEXT NOT NULL,
                congestion_level TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                latitude REAL,
                longitude REAL
            )
        """)
        conn.commit()
        conn.close()

        logger.info("✅ DB 초기화 완료")

    except sqlite3.OperationalError as e:
        logger.error(f"DB 연결 오류: {e}")
    except Exception as e:
        logger.error(f"알 수 없는 오류: {e}")

def save_congestion_data(area: str, congestion_level: str, timestamp: str):
    """혼잡도 데이터를 DB에 저장"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO congestion (area, congestion_level, timestamp)
            VALUES (?, ?, ?)
        """, (area, congestion_level, timestamp))
        conn.commit()
        conn.close()
        logger.info(f"{area} → 혼잡도: {congestion_level}, 시간: {timestamp} 저장 완료")
    except sqlite3.Error as e:
        logger.error(f"데이터 저장 오류: {e}")

def insert_congestion_data(data: List[Dict]):
    """수집한 혼잡도 리스트를 DB에 저장 (좌표 포함)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for item in data:
        area = item["area"]
        congestion_level = item["data"].get("congestion_level", "정보 없음")
        timestamp = item["data"].get("current_time", "정보 없음")
        lat, lng = AREA_COORDINATES.get(area, (None, None))

        cursor.execute(
            """
            INSERT INTO congestion (area, congestion_level, timestamp, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
            """,
            (area, congestion_level, timestamp, lat, lng)
        )

    conn.commit()
    conn.close()

def get_congestion_data():
    """DB에서 전체 혼잡도 데이터 조회"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT area, congestion_level, timestamp, latitude, longitude
            FROM congestion
        """)
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "area": row[0],
                "congestion_level": row[1],
                "timestamp": row[2],
                "latitude": row[3],
                "longitude": row[4]
            })
        return result

    except sqlite3.Error as e:
        logger.error(f"데이터 조회 오류: {e}")
        return []

def get_area_congestion_data(area: str):
    """특정 지역 혼잡도 상세 조회"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT area, congestion_level, timestamp, latitude, longitude
            FROM congestion
            WHERE area = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (area,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "area": row[0],
                "congestion_level": row[1],
                "timestamp": row[2],
                "latitude": row[3],
                "longitude": row[4]
            }
        else:
            return None

    except sqlite3.Error as e:
        logger.error(f"단일 지역 조회 오류: {e}")
        return None

if __name__ == "__main__":
    init_db()
