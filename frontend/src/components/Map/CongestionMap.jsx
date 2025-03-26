import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { getCongestionData, getAreaCongestion } from "../../services/apiService";
import "./CongestionMap.css";

const CongestionMap = () => {
  const [congestionData, setCongestionData] = useState(null);
  const [selectedArea, setSelectedArea] = useState(null);
  const [areaDetails, setAreaDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  // 혼잡도 색상 지정 함수
  const getCongestionColor = (level) => {
    switch (level) {
      case "여유":
        return "green";
      case "보통":
        return "blue";
      case "약간 붐빔":
        return "orange";
      case "붐빔":
        return "red";
      default:
        return "gray";
    }
  };

  // 혼잡도 데이터 로드
  useEffect(() => {
    const fetchCongestionData = async () => {
      try {
        setIsLoading(true);
        const data = await getCongestionData(); // ✅ 수정됨
        setCongestionData(data);
      } catch (err) {
        setError("혼잡도 데이터를 불러오는데 실패했습니다.");
        console.error("혼잡도 데이터 요청 오류:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCongestionData();
  }, []);

  // 지역 선택 시 상세 정보 로드
  const handleAreaSelect = async (area) => {
    if (selectedArea === area.properties.name) {
      setSelectedArea(null);
      setAreaDetails(null);
      return;
    }

    try {
      setSelectedArea(area.properties.name);
      const details = await getAreaCongestion(area.properties.name);
      setAreaDetails(details);
    } catch (err) {
      console.error("지역 상세 정보 요청 오류:", err);
      setAreaDetails(null);
    }
  };

  if (isLoading) {
    return (
      <div className="congestion-map-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>혼잡도 데이터를 불러오는 중입니다...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="congestion-map-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="congestion-map-container">
      <div className="map-header">
        <h2>서울시 실시간 혼잡도 지도</h2>
        <p className="description">
          주요 지역의 실시간 혼잡도 정보를 확인하고 지역을 선택하여 상세 정보를 볼 수 있습니다.
        </p>
      </div>

      {/* Leaflet 지도 표시 */}
      <div className="map-view">
        <MapContainer center={[37.5665, 126.9780]} zoom={13} style={{ height: "500px", width: "100%" }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

          {/* 혼잡도 데이터 마커 추가 */}
          {congestionData?.features.map((area, index) => (
            <Marker
              key={index}
              position={[area.geometry.coordinates[1], area.geometry.coordinates[0]]}
              eventHandlers={{
                click: () => handleAreaSelect(area),
              }}
            >
              <Popup>
                <strong>{area.properties.name}</strong> <br />
                혼잡도: {area.properties.congestion}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* 지역 목록 */}
      <div className="map-content">
        <div className="map-areas-list">
          <h3>주요 지역 혼잡도</h3>
          <div className="areas-container">
            {congestionData?.features.map((area, index) => (
              <div
                key={index}
                className={`area-item ${selectedArea === area.properties.name ? "selected" : ""}`}
                onClick={() => handleAreaSelect(area)}
              >
                <div className="area-name">{area.properties.name}</div>
                <div
                  className="area-congestion"
                  style={{
                    backgroundColor: getCongestionColor(area.properties.congestion),
                    color: area.properties.congestion === "여유" ? "#333" : "white",
                  }}
                >
                  {area.properties.congestion}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 선택한 지역 상세 정보 표시 */}
        <div className="map-view">
          {selectedArea ? (
            areaDetails ? (
              <div className="area-details">
                <h3>{areaDetails.area} 상세 정보</h3>

                <div className="detail-section">
                  <h4>혼잡도 정보</h4>
                  <div className="detail-item">
                    <div className="detail-label">혼잡도 레벨</div>
                    <div className="detail-value congestion-badge">
                      {areaDetails.congestion_level}
                    </div>
                  </div>

                  <div className="detail-item">
                    <div className="detail-label">예상 인구</div>
                    <div className="detail-value">
                      {areaDetails.population_range?.min || 0} ~ {areaDetails.population_range?.max || 0}명
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>도로 상태</h4>
                  <div className="detail-item">
                    <div className="detail-label">속도</div>
                    <div className="detail-value">
                      {areaDetails.traffic_status?.speed || "?"} km/h
                    </div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">교통 메시지</div>
                    <div className="detail-value">
                      {areaDetails.traffic_status?.message || "정보 없음"}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="area-details-loading">
                <div className="loading-spinner small"></div>
                <p>지역 정보를 불러오는 중입니다...</p>
              </div>
            )
          ) : (
            <div className="map-placeholder">
              <div className="placeholder-content">
                <p>왼쪽에서 지역을 선택하면 상세 정보가 표시됩니다.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CongestionMap;
