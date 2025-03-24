import React, { useState, useEffect, useRef } from 'react';
import { useUser } from '../../contexts/UserContext';
import { sendChatMessage } from '../../services/apiService';
import ChatMessage from './ChatMessage';
import './ChatPanel.css';

const ChatPanel = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { userPreferences, isFirstVisit, setIsFirstVisit } = useUser();
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // 스크롤을 최신 메시지로 이동
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 컴포넌트 마운트 시 입력 필드에 포커스
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // 초기 환영 메시지
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        { 
          role: 'assistant', 
          content: '안녕하세요! 스마트문화예술 챗봇입니다. 어떤 문화 활동에 관심이 있으신가요?' 
        }
      ]);

      // 첫 방문 시 사용 안내 메시지
      if (isFirstVisit) {
        setTimeout(() => {
          setMessages(prev => [
            ...prev,
            {
              role: 'assistant',
              content: `
### 💡 사용 안내
- 왼쪽 사이드바에서 사용자 정보를 설정하면 더 정확한 추천을 받을 수 있어요.
- 지역명을 언급하면 해당 지역의 실시간 혼잡도와 문화 행사 정보를 알려드립니다.
- 예시: "강남역 주변 문화 행사 추천해줘", "홍대 지역 전시회 알려줘"
              `
            }
          ]);
          setIsFirstVisit(false);
        }, 1000);
      }
    }
  }, [messages, isFirstVisit, setIsFirstVisit]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    
    // 사용자 메시지 추가
    const userMessage = { role: 'user', content: inputValue };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      // API 호출
      const response = await sendChatMessage(inputValue, userPreferences);
      
      // 응답 메시지 추가
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.answer
      }]);
    } catch (error) {
      console.error('메시지 전송 오류:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '죄송합니다, 오류가 발생했습니다. 다시 시도해 주세요.'
      }]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // 자동 높이 조절 textarea
  const handleTextareaChange = (e) => {
    setInputValue(e.target.value);
    
    // 높이 조절
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  };

  return (
    <div className="chat-panel">
      <div className="messages-container">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
        {isLoading && (
          <div className="loading-indicator">
            <div className="loading-dots">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
            <span>AI가 응답 중입니다...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input-container">
        <textarea
          ref={inputRef}
          value={inputValue}
          onChange={handleTextareaChange}
          onKeyPress={handleKeyPress}
          placeholder="메시지를 입력하세요"
          rows={1}
          disabled={isLoading}
        />
        <button 
          className={`send-button ${(!inputValue.trim() || isLoading) ? 'disabled' : ''}`} 
          onClick={handleSendMessage}
          disabled={isLoading || !inputValue.trim()}
        >
          <span className="send-icon">➤</span>
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;
