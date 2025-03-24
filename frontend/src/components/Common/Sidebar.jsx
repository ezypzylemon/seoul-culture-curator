import React, { useState } from 'react';
import { useUser } from '../../contexts/UserContext';
import './Sidebar.css';

const Sidebar = () => {
  const { userPreferences, updatePreferences } = useUser();
  const [isExpanded, setIsExpanded] = useState(false);

  // 사용자 설정 변경 처리
  const handlePreferenceChange = (e) => {
    const { name, value } = e.target;
    updatePreferences({ [name]: value });
  };

  // 사이드바 토글
  const toggleSidebar = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className={`sidebar ${isExpanded ? 'expanded' : ''}`}>
      <div className="sidebar-toggle" onClick={toggleSidebar}>
        {isExpanded ? '◀' : '▶'}
      </div>
      
      <div className="sidebar-content">
        <h2>사용자 설정</h2>
        
        <div className="user-preference">
          <label htmlFor="gender">성별</label>
          <select 
            id="gender" 
            name="gender"
            value={userPreferences.gender}
            onChange={handlePreferenceChange}
          >
            <option value="남성">남성</option>
            <option value="여성">여성</option>
          </select>
        </div>
        
        <div className="user-preference">
          <label htmlFor="age_group">연령대</label>
          <select 
            id="age_group" 
            name="age_group"
            value={userPreferences.age_group}
            onChange={handlePreferenceChange}
          >
            <option value="10대">10대</option>
            <option value="20대">20대</option>
            <option value="30대">30대</option>
            <option value="40대">40대</option>
            <option value="50대">50대</option>
            <option value="60대 이상">60대 이상</option>
          </select>
        </div>
        
        <div className="user-preference">
          <label htmlFor="has_children">자녀 동반</label>
          <select 
            id="has_children" 
            name="has_children"
            value={userPreferences.has_children}
            onChange={handlePreferenceChange}
          >
            <option value="예">예</option>
            <option value="아니오">아니오</option>
          </select>
        </div>
        
        <div className="user-preference">
          <label htmlFor="transportation">이동 수단</label>
          <select 
            id="transportation" 
            name="transportation"
            value={userPreferences.transportation}
            onChange={handlePreferenceChange}
          >
            <option value="도보">도보</option>
            <option value="자동차">자동차</option>
            <option value="대중교통">대중교통</option>
            <option value="자전거">자전거</option>
          </select>
        </div>

        <div className="sidebar-footer">
          <p className="sidebar-note">
            위 정보는 맞춤형 문화 활동 추천을 위해 사용됩니다.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
