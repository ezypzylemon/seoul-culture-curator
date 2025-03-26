import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { getCongestionData, getAreaCongestion } from "../../services/apiService";
import "./CongestionMap.css";

const CongestionMap = () => {
  const [congestionData, setCongestionData] = useState([]);
  const [selectedArea, setSelectedArea] = useState(null);
  const [areaDetails, setAreaDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const getCongestionColor = (level) => {
    switch (level) {
      case "여유": return "green";
      case "보통": return "blue";
      case "약간 붐빔": return "orange";
      case "붐빔": return "red";
      default: return "gray";
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const data = await getCongestionData();
        setCongestionData(data.data); // ✅ 응답의 data 속성만 할당
      } catch (err) {
        console.error("혼잡도 데이터 요청 오류:", err);
        setError("혼잡도 데이터를 불러오는데 실패했습니다.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleAreaSelect = async (areaName) => {
    if (selectedArea === areaName) {
      setSelectedArea(null);
      setAreaDetails(null);
      return;
    }
    try {
      setSelectedArea(areaName);
      const details = await getAreaCongestion(areaName);
      setAreaDetails(details);
    } catch (err) {
      console.error("지역 상세 정보 요청 오류:", err);
      setAreaDetails(null);
    }
  };

  if (isLoading) {
    return <div className="congestion-map-container">혼잡도 데이터를 불러오는 중입니다...</div>;
  }

  if (error) {
    return <div className="congestion-map-container">{error}</div>;
  }

  return (
    <div className="congestion-map-container">
      <h2>서울시 실시간 혼잡도 지도</h2>

      <MapContainer center={[37.5665, 126.9780]} zoom={13} style={{ height: "500px", width: "100%" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {congestionData.map((item, index) => (
          <Marker
            key={index}
            position={[37.5665 + index * 0.005, 126.9780 + index * 0.005]}
            eventHandlers={{ click: () => handleAreaSelect(item.area) }}
          >
            <Popup>
              <strong>{item.area}</strong><br />
              혼잡도: {item.congestion_level}
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      <div className="map-content">
        <div className="map-areas-list">
          <h3>주요 지역 혼잡도</h3>
          <div className="areas-container">
            {congestionData.map((item, index) => (
              <div
                key={index}
                className={`area-item ${selectedArea === item.area ? "selected" : ""}`}
                onClick={() => handleAreaSelect(item.area)}
              >
                <div className="area-name">{item.area}</div>
                <div
                  className="area-congestion"
                  style={{
                    backgroundColor: getCongestionColor(item.congestion_level),
                    color: item.congestion_level === "여유" ? "#333" : "white",
                  }}
                >
                  {item.congestion_level}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="map-view">
          {selectedArea ? (
            areaDetails ? (
              <div className="area-details">
                <h3>{areaDetails.area} 상세 정보</h3>
                <div className="detail-section">
                  <h4>혼잡도 정보</h4>
                  <p>혼잡도: {areaDetails.congestion_level}</p>
                  <p>예상 인구: {areaDetails.population_range?.min || 0} ~ {areaDetails.population_range?.max || 0}명</p>
                </div>
                <div className="detail-section">
                  <h4>도로 상태</h4>
                  <p>속도: {areaDetails.traffic_status?.speed || "?"} km/h</p>
                  <p>교통 메시지: {areaDetails.traffic_status?.message || "정보 없음"}</p>
                </div>
              </div>
            ) : (
              <div className="area-details-loading">지역 정보를 불러오는 중입니다...</div>
            )
          ) : (
            <div className="map-placeholder">왼쪽에서 지역을 선택하면 상세 정보가 표시됩니다.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CongestionMap;
