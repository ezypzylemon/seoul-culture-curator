import React, { createContext, useState, useContext, useEffect } from 'react';

// 사용자 컨텍스트 생성
const UserContext = createContext();

// 기본 사용자 설정
const defaultPreferences = {
  gender: '남성',
  age_group: '20대',
  has_children: '아니오',
  transportation: '도보'
};

// 사용자 컨텍스트 제공자 컴포넌트
export const UserProvider = ({ children }) => {
  // 로컬 스토리지에서 사용자 설정 로드
  const loadPreferences = () => {
    try {
      const savedPreferences = localStorage.getItem('userPreferences');
      return savedPreferences 
        ? JSON.parse(savedPreferences) 
        : defaultPreferences;
    } catch (error) {
      console.error('설정 로드 중 오류:', error);
      return defaultPreferences;
    }
  };

  // 사용자 상태 관리
  const [userPreferences, setUserPreferences] = useState(loadPreferences);
  const [isFirstVisit, setIsFirstVisit] = useState(true);

  // 사용자 설정 업데이트 함수
  const updatePreferences = (newPreferences) => {
    const updatedPreferences = { ...userPreferences, ...newPreferences };
    setUserPreferences(updatedPreferences);
    
    // 로컬 스토리지에 저장
    try {
      localStorage.setItem('userPreferences', JSON.stringify(updatedPreferences));
    } catch (error) {
      console.error('설정 저장 중 오류:', error);
    }
  };

  // 첫 방문 확인
  useEffect(() => {
    const visited = localStorage.getItem('visited');
    if (visited) {
      setIsFirstVisit(false);
    } else {
      localStorage.setItem('visited', 'true');
    }
  }, []);

  // 제공할 컨텍스트 값
  const contextValue = {
    userPreferences,
    updatePreferences,
    isFirstVisit,
    setIsFirstVisit
  };

  return (
    <UserContext.Provider value={contextValue}>
      {children}
    </UserContext.Provider>
  );
};

// 사용자 컨텍스트 사용 훅
export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser 훅은 UserProvider 내부에서만 사용할 수 있습니다.');
  }
  return context;
};

export default UserContext;
