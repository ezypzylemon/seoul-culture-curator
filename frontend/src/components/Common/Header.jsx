import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Header.css';

const Header = () => {
  const location = useLocation();
  
  // 현재 활성화된 경로 확인
  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <header className="app-header">
      <div className="header-logo">
        <h1>스마트문화예술 챗봇</h1>
      </div>
      
      <nav className="header-nav">
        <ul>
          <li className={isActive('/chat')}>
            <Link to="/chat">
              <span className="icon">💬</span>
              <span className="text">챗봇</span>
            </Link>
          </li>
          <li className={isActive('/recommend')}>
            <Link to="/recommend">
              <span className="icon">🎯</span>
              <span className="text">추천</span>
            </Link>
          </li>
          <li className={isActive('/map')}>
            <Link to="/map">
              <span className="icon">🗺️</span>
              <span className="text">지도</span>
            </Link>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
