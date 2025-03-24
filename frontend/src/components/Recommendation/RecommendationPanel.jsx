import React, { useState } from 'react';
import { useUser } from '../../contexts/UserContext';
import { getRecommendations } from '../../services/apiService';
import AreaStatus from './AreaStatus';
import EventsList from './EventsList';
import './RecommendationPanel.css';

const RecommendationPanel = () => {
  const { userPreferences } = useUser();
  const [location, setLocation] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [recommendationData, setRecommendationData] = useState(null);
  const [error, setError] = useState('');

  const handleLocationChange = (e) => {
    setLocation(e.target.value);
  };

  const handleSearch = async () => {
    if (!location.trim()) {
      setError('위치를 입력해 주세요');
      return;
    }

    setIsLoading(true);
    setError('');
    setRecommendationData(null);

    try {
      const data = await getRecommendations(location, userPreferences);
      console.log("API 응답 데이터:", data); // 데이터 로깅 추가
      setRecommendationData(data);
    } catch (err) {
      setError(err.message || '추천 정보를 가져오는데 실패했습니다.');
      console.error('추천 정보 요청 오류:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="recommendation-panel">
      <div className="recommendation-header">
        <h2>문화예술 활동 추천</h2>
        <p className="description">
          위치를 입력하면 현재 혼잡도, 교통 상황, 문화 행사 정보를 알려드립니다.
        </p>
      </div>

      <div className="search-container">
        <input
          type="text"
          className="location-input"
          placeholder="위치를 입력하세요 (예: 강남역, 홍대, 명동)"
          value={location}
          onChange={handleLocationChange}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
        />
        <button
          className="search-button"
          onClick={handleSearch}
          disabled={isLoading || !location.trim()}
        >
          {isLoading ? '검색 중...' : '검색'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {isLoading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>추천 정보를 불러오는 중입니다...</p>
        </div>
      )}

      {recommendationData && !isLoading && (
        <div className="recommendation-results">
          <div className="result-header">
            <h3>
              <span className="location-name">{recommendationData.area}</span> 추천 정보
            </h3>
            <p className="location-info">입력하신 위치와 가장 가까운 주요 지역은 '<strong>{recommendationData.area}</strong>'입니다.</p>
            
            {recommendationData.status.coordinates && (
              <p className="coordinates-info">
                좌표 정보: 위도 {recommendationData.status.coordinates.lat}, 경도 {recommendationData.status.coordinates.lng}
              </p>
            )}
          </div>

          <div className="result-content">
            <AreaStatus 
              area={recommendationData.area}
              status={recommendationData.status}
            />

            {/* 맞춤 행사 추천 섹션 추가 */}
            {recommendationData.events && recommendationData.events.data && recommendationData.events.data.length > 0 && (
              <div className="personalized-recommendation">
                <h4>🎯 맞춤 행사 추천</h4>
                <div className="recommendation-content">
                  {recommendationData.personalized_recommendation ? (
                    <div className="formatted-recommendation">
                      {/* 텍스트 포맷 분석 및 구조화 */}
                      {(() => {
                        const text = recommendationData.personalized_recommendation;
                        
                        // 각 섹션 분리 및 가공
                        let sections = {};
                        
                        // 소개 부분 추출
                        const introMatch = text.match(/^(.*?)(?=\*\*비교 분석|\*\*1\.|\*\*결론|$)/s);
                        if (introMatch) sections.intro = introMatch[0].trim();
                        
                        // 비교 분석 또는 분석 섹션 추출
                        const analysisMatch = text.match(/(?:\*\*비교 분석:?\*\*|\*\*1\. 라이프스타일 고려:\*\*)(.*?)(?=\*\*추천 및 근거|\*\*결론|$)/s);
                        if (analysisMatch) sections.analysis = analysisMatch[0].trim();
                        
                        // 추천 및 근거 또는 결론 추출
                        const conclusionMatch = text.match(/(?:\*\*추천 및 근거:?\*\*|\*\*결론:\*\*)(.*?)(?=\*\*추가 정보|$)/s);
                        if (conclusionMatch) sections.conclusion = conclusionMatch[0].trim();
                        
                        // 추가 정보 필요 섹션 추출
                        const additionalInfoMatch = text.match(/\*\*추가 정보(.*?)$/s);
                        if (additionalInfoMatch) sections.additionalInfo = additionalInfoMatch[0].trim();
                        
                        // 렌더링
                        return (
                          <>
                            {sections.intro && <p>{sections.intro}</p>}
                            
                            {sections.analysis && (
                              <>
                                <h5>분석</h5>
                                <div dangerouslySetInnerHTML={{ 
                                  __html: sections.analysis
                                    .replace(/\*\*비교 분석:?\*\*|\*\*1\. 라이프스타일 고려:\*\*/, '')
                                    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
                                    .replace(/\n/g, '<br/>')
                                }} />
                              </>
                            )}
                            
                            {sections.conclusion && (
                              <>
                                <h5>추천 및 근거</h5>
                                <div dangerouslySetInnerHTML={{ 
                                  __html: sections.conclusion
                                    .replace(/\*\*추천 및 근거:?\*\*|\*\*결론:\*\*/, '')
                                    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
                                    .replace(/\n/g, '<br/>')
                                }} />
                              </>
                            )}
                            
                            {sections.additionalInfo && (
                              <>
                                <h5>추가 정보 필요</h5>
                                <div dangerouslySetInnerHTML={{ 
                                  __html: sections.additionalInfo
                                    .replace(/\*\*추가 정보 필요:?\*\*/, '')
                                    .replace(/\* \*\*([^:]+):\*\*/, '• <strong>$1:</strong>')
                                    .replace(/\n\* /g, '<br/>• ')
                                    .replace(/\n/g, '<br/>')
                                }} />
                              </>
                            )}
                          </>
                        );
                      })()}
                    </div>
                  ) : (
                    <p>
                      현재 사용자 정보에 기반한 맞춤 행사 추천을 생성하지 못했습니다.
                      더 정확한 추천을 위해 사용자 설정을 업데이트하거나 다른 지역을 검색해보세요.
                    </p>
                  )}
                </div>
              </div>
            )}

            <div className="analysis-section">
              <h4>🤖 AI 큐레이터의 분석</h4>
              <div className="analysis-content">
                <div className="analysis-item">
                  <h5>현재 상황 평가</h5>
                  <p>{recommendationData.analysis.situation}</p>
                </div>
                <div className="analysis-item">
                  <h5>최적의 방문 시간대</h5>
                  <p>{recommendationData.analysis.best_time}</p>
                </div>
                <div className="analysis-item">
                  <h5>추천 동선</h5>
                  <p>{recommendationData.analysis.route}</p>
                </div>
                <div className="analysis-item">
                  <h5>주의사항</h5>
                  <p>{recommendationData.analysis.warnings}</p>
                </div>
              </div>
            </div>

            <EventsList events={recommendationData.events} />
          </div>
        </div>
      )}

      {!isLoading && !recommendationData && !error && (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <p>위치를 검색하여 맞춤 문화예술 활동을 추천받아보세요.</p>
          <p className="empty-examples">
            추천 검색어: 홍대, 강남, 명동, 북촌, 이태원, 여의도
          </p>
        </div>
      )}
    </div>
  );
};

export default RecommendationPanel;