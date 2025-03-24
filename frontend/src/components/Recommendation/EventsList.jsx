import React from 'react';
import './EventsList.css';

const EventsList = ({ events }) => {
  if (!events || !events.data || events.data.length === 0) {
    return (
      <div className="events-list empty">
        <h4>🎭 문화 행사 정보</h4>
        <div className="empty-message">
          <p>현재 등록된 문화 행사 정보가 없습니다.</p>
        </div>
      </div>
    );
  }

  // 인코딩된 카카오맵 URL 생성
  const getKakaoMapUrl = (place) => {
    const encodedPlace = encodeURIComponent(place);
    return `https://map.kakao.com/link/search/${encodedPlace}`;
  };

  // 행사 날짜 포맷팅
  const formatDate = (dateStr) => {
    if (!dateStr) return '날짜 미정';
    return dateStr;
  };

  return (
    <div className="events-list">
      <h4>🎭 문화 행사 정보</h4>
      <div className="events-count">
        총 {events.total_count}개의 행사 중 {events.data.length}개 표시
      </div>

      <div className="events-container">
        {events.data.map((event, index) => (
          <div className="event-card" key={index}>
            <div className="event-header">
              <h5 className="event-title">{event.TITLE || '제목 없음'}</h5>
              <span className="event-category">{event.CODENAME || '분류 없음'}</span>
            </div>
            
            <div className="event-info">
              <div className="event-detail">
                <span className="info-label">장소:</span>
                <a 
                  href={getKakaoMapUrl(event.PLACE)} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="place-link"
                >
                  {event.PLACE || '장소 미정'} 📍
                </a>
              </div>
              
              <div className="event-detail">
                <span className="info-label">날짜:</span>
                <span>{formatDate(event.DATE)}</span>
              </div>
              
              <div className="event-detail">
                <span className="info-label">요금:</span>
                <span>{event.USE_FEE || '요금 정보 없음'}</span>
              </div>
            </div>
            
            {event.PROGRAM && (
              <div className="event-program">
                <div className="program-label">프로그램</div>
                <p>{event.PROGRAM}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default EventsList;
