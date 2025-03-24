import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from 'leaflet';
import "./AreaStatus.css";

// Leaflet 마커 아이콘 관련 이슈 해결
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const AreaStatus = ({ area, status }) => {
  const { population, traffic, commercial, coordinates } = status || {};
  if (!population || !traffic) return null;

  // 혼잡도에 따른 색상
  const getCongestionColor = (level) => {
    switch (level) {
      case "여유":
        return "#4caf50";
      case "보통":
        return "#2196f3";
      case "약간 붐빔":
        return "#ff9800";
      case "붐빔":
        return "#f44336";
      default:
        return "#9e9e9e";
    }
  };

  // 교통 상태에 따른 색상
  const getTrafficColor = (status) => {
    switch (status) {
      case "원활":
        return "#4caf50";
      case "서행":
        return "#ff9800";
      case "정체":
        return "#f44336";
      default:
        return "#9e9e9e";
    }
  };

  // 시간 포맷 변환
  const formatTime = (timeString) => {
    if (!timeString) return "정보 없음";
    try {
      const parts = timeString.split(" ");
      if (parts.length !== 2) return timeString;
      const timePart = parts[1].split(":");
      return `${timePart[0]}:${timePart[1]}`;
    } catch (e) {
      return timeString;
    }
  };

  return (
    <div className="area-status">
      <h4>📍 현재 현황</h4>

      <div className="status-content">
        <div className="status-item congestion">
          <div className="status-label">실시간 혼잡도</div>
          <div
            className="status-value"
            style={{
              backgroundColor: getCongestionColor(population.congestion_level),
              color: population.congestion_level === "여유" ? "#333" : "white",
            }}
          >
            {population.congestion_level || "정보 없음"}
          </div>
          <div className="status-detail">
            {population.congestion_message || "현재 도보 상황 정보가 없습니다."}
          </div>
        </div>

        <div className="status-item">
          <div className="status-label">현재 인구</div>
          <div className="status-value population">
            {population.population_range?.min ?? 0} ~ {population.population_range?.max ?? 0}명
          </div>
          <div className="status-detail">
            <span>데이터 업데이트: {formatTime(population.current_time)}</span>
          </div>
        </div>

        <div className="status-item">
          <div className="status-label">교통 상황</div>
          <div
            className="status-value"
            style={{
              backgroundColor: getTrafficColor(traffic.status),
              color: traffic.status === "원활" ? "#333" : "white",
            }}
          >
            {traffic.status || "정보 없음"} ({traffic.speed || "?"} km/h)
          </div>
          <div className="status-detail">{traffic.message || "현재 도로 교통 정보가 없습니다."}</div>
        </div>

        {commercial && commercial.congestion_level && (
          <div className="status-item">
            <div className="status-label">상권 활성도</div>
            <div
              className="status-value"
              style={{
                backgroundColor: getCongestionColor(commercial.congestion_level),
                color: commercial.congestion_level === "여유" ? "#333" : "white",
              }}
            >
              {commercial.congestion_level}
            </div>
            <div className="status-detail">
              {commercial.food_businesses && commercial.food_businesses.length > 0
                ? `${commercial.food_businesses.length}개 업종 정보 있음`
                : "상세 업종 정보 없음"}
            </div>
          </div>
        )}
      </div>

      {/* 성비 및 연령 분포 정보 추가 */}
      {population.gender_ratio && (
        <div className="demographics-section">
          <h5>인구 통계</h5>
          <div className="demographics-item">
            <div className="demographics-label">성비:</div>
            <div className="demographics-value">
              남성 {population.gender_ratio.male}%, 여성 {population.gender_ratio.female}%
            </div>
          </div>
          
          {population.age_distribution && (
            <div className="demographics-item">
              <div className="demographics-label">연령 분포:</div>
              <div className="demographics-values">
                {Object.entries(population.age_distribution).map(([age, percentage]) => (
                  <div key={age} className="age-item">
                    {age}대: {percentage}%
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 예측 정보 표시 */}
      {population.forecasts && population.forecasts.length > 0 && (
        <div className="forecast-section">
          <h5>📊 향후 {population.forecasts.length}시간 예측 정보</h5>
          <div className="forecast-items">
            {population.forecasts.map((forecast, index) => (
              <div className="forecast-item" key={index}>
                <div className="forecast-time">🕒 {forecast.time} 예측</div>
                <div 
                  className="forecast-level"
                  style={{
                    backgroundColor: getCongestionColor(forecast.congestion_level),
                    color: forecast.congestion_level === "여유" ? "#333" : "white"
                  }}
                >
                  예측 혼잡도: {forecast.congestion_level}
                </div>
                <div className="forecast-pop">
                  예측 인구: {forecast.population_min}~{forecast.population_max}명
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 상권 상세 정보 추가 */}
      {commercial && commercial.food_businesses && commercial.food_businesses.length > 0 && (
        <div className="commercial-section">
          <h5>상권 현황:</h5>
          {commercial.food_businesses.map((business, index) => (
            <div className="business-item" key={index}>
              카테고리: {business.category}, 혼잡도: {business.congestion_level}, 
              결제 수: {business.payment_count}, 매장 수: {business.store_count}
            </div>
          ))}
        </div>
      )}

      {/* Leaflet 지도 표시 */}
      {coordinates && (
        <div className="map-container">
          <MapContainer center={[coordinates.lat, coordinates.lng]} zoom={15} style={{ height: "200px", width: "100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <Marker position={[coordinates.lat, coordinates.lng]}>
              <Popup>{area}</Popup>
            </Marker>
          </MapContainer>
        </div>
      )}
    </div>
  );
};

export default AreaStatus;