import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Common/Sidebar';
import Header from './components/Common/Header';
import ChatPanel from './components/Chat/ChatPanel';
import RecommendationPanel from './components/Recommendation/RecommendationPanel';
import CongestionMap from './components/Map/CongestionMap';
import { UserProvider } from './contexts/UserContext';
import './App.css';
import 'leaflet/dist/leaflet.css';



function App() {
  return (
    <UserProvider>
      <Router>
        <div className="app-container">
          <Sidebar />
          <div className="main-content">
            <Header />
            <div className="content-area">
              <Routes>
                <Route path="/chat" element={<ChatPanel />} />
                <Route path="/recommend" element={<RecommendationPanel />} />
                <Route path="/map" element={<CongestionMap />} />
                <Route path="/" element={<Navigate to="/chat" />} />
              </Routes>
            </div>
          </div>
        </div>
      </Router>
    </UserProvider>
  );
}

export default App;