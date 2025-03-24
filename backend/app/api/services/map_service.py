from flask import Flask, jsonify, request
from location_service import get_coordinates

app = Flask(__name__)

# 혼잡도 색상 설정
CONGESTION_COLORS = {
    "여유": "green",
    "보통": "blue",
    "약간 붐빔": "orange",
    "붐빔": "red"
}

@app.route("/api/congestion", methods=["GET"])
def get_congestion_data():
    """혼잡도 데이터를 JSON 형식으로 반환 (React 연동)"""
    area = request.args.get("area", "서울역")  # 기본값: 서울역
    congestion_level = request.args.get("congestion", "보통")  # 기본값: 보통

    # 좌표 가져오기
    coordinates = get_coordinates(area)
    if not coordinates:
        return jsonify({"error": f"{area}의 좌표를 찾을 수 없습니다."}), 404

    # GeoJSON 데이터 생성
    congestion_data = {
        "type": "Feature",
        "properties": {
            "name": area,
            "congestion": congestion_level,
            "color": CONGESTION_COLORS.get(congestion_level, "gray")
        },
        "geometry": {
            "type": "Point",
            "coordinates": [coordinates["lng"], coordinates["lat"]]  # GeoJSON 표준: [경도, 위도]
        }
    }

    return jsonify(congestion_data)

if __name__ == "__main__":
    app.run(debug=True)
