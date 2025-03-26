import axios from 'axios';

// ✅ API 기본 URL 설정 - "/api" 프리픽스 적용
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

// ✅ API 클라이언트 설정
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60초 타임아웃
});

// 요청 인터셉터 - 모든 요청에 로깅 추가
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API 요청: ${config.method.toUpperCase()} ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    console.error('API 요청 오류:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 오류 처리
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const errorMessage = error.response?.data?.detail || error.message || '알 수 없는 오류가 발생했습니다.';
    console.error('API 응답 오류:', errorMessage);
    return Promise.reject({
      message: errorMessage,
      status: error.response?.status
    });
  }
);

// ✅ 채팅 메시지 전송
export const sendChatMessage = async (message, userPreferences) => {
  try {
    const response = await apiClient.post('/api/chat/message/', {
      message,
      user_preferences: userPreferences
    });
    return response.data;
  } catch (error) {
    console.error('채팅 메시지 전송 오류:', error);
    throw error;
  }
};

// ✅ 추천 정보 요청
export const getRecommendations = async (location, userPreferences) => {
  try {
    const response = await apiClient.post('/api/recommendation/', {
      location,
      user_preferences: userPreferences
    });
    return response.data;
  } catch (error) {
    console.error('추천 정보 요청 오류:', error);
    throw error;
  }
};

// ✅ 혼잡도 지도 데이터 요청
export const getCongestionData = async () => {
  try {
    const response = await apiClient.get('/api/map/congestion');
    return response.data;
  } catch (error) {
    console.error('혼잡도 데이터 요청 오류:', error);
    throw error;
  }
};

// ✅ 특정 지역 혼잡도 정보 요청
export const getAreaCongestion = async (area) => {
  try {
    const response = await apiClient.get(`/api/map/congestion/${encodeURIComponent(area)}`);
    return response.data;
  } catch (error) {
    console.error('지역 혼잡도 정보 요청 오류:', error);
    throw error;
  }
};

// 기본 API 서비스 객체 내보내기
export default {
  sendChatMessage,
  getRecommendations,
  getCongestionData,
  getAreaCongestion
};
