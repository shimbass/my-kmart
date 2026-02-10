import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navigation from './components/common/Navigation';
import ScanPage from './pages/ScanPage';
import Dashboard from './pages/Dashboard';
import ReceiptList from './pages/ReceiptList';
import './App.css';

function AppContent() {
  const location = useLocation();
  const [isFullscreen, setIsFullscreen] = useState(false);

  const getIsIOS = () => {
    if (typeof navigator === 'undefined') return false;
    const ua = navigator.userAgent;
    const platform = navigator.platform || '';
    const vendor = navigator.vendor || '';
    return !!(
      /iPhone|iPod|iPad/i.test(ua) ||
      /CriOS|FxiOS|EdgiOS/i.test(ua) ||
      /iPhone|iPod|iPad/i.test(platform) ||
      (platform === 'MacIntel' && navigator.maxTouchPoints > 1) ||
      (/Apple/.test(vendor) && /Mobile|iPad/i.test(ua))
    );
  };

  const hasFullscreenAPI =
    typeof document !== 'undefined' &&
    !!(document.documentElement?.requestFullscreen || document.documentElement?.webkitRequestFullscreen);
  const isSecureContext = typeof window !== 'undefined' && window.isSecureContext;
  const isTopLevel = typeof window !== 'undefined' && window.self === window.top;
  const canFullscreen = hasFullscreenAPI && !getIsIOS() && isSecureContext && isTopLevel;
  const showFullscreenButton = canFullscreen;

  const toggleFullscreen = () => {
    try {
      const doc = document.documentElement;
      const exitFs = document.exitFullscreen || document.webkitExitFullscreen;
      const isFs = document.fullscreenElement || document.webkitFullscreenElement;

      if (isFs) {
        exitFs?.call(document);
        return;
      }
      if (!canFullscreen) return;
      (doc.requestFullscreen || doc.webkitRequestFullscreen)?.call(doc);
    } catch (e) {
      console.warn('Fullscreen not supported', e);
    }
  };

  useEffect(() => {
    const onFullscreenChange = () =>
      setIsFullscreen(!!(document.fullscreenElement || document.webkitFullscreenElement));
    document.addEventListener('fullscreenchange', onFullscreenChange);
    document.addEventListener('webkitfullscreenchange', onFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', onFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', onFullscreenChange);
    };
  }, []);

  const getPageTitle = () => {
    switch (location.pathname) {
      case '/':
        return 'K마트 영수증 스캐너';
      case '/dashboard':
        return '대시보드';
      case '/receipts':
        return '영수증 목록';
      default:
        return 'K마트 영수증 스캐너';
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        {showFullscreenButton && (
          <button
            type="button"
            className={`fullscreen-toggle${isFullscreen ? ' is-fullscreen' : ''}`}
            onClick={toggleFullscreen}
            aria-label={isFullscreen ? '전체 화면 나가기' : '전체 화면'}
            title={isFullscreen ? '전체 화면 나가기' : '전체 화면 (주소창 숨김)'}
          >
            <span className="fullscreen-toggle-icon">{isFullscreen ? '✕' : '⛶'}</span>
          </button>
        )}
        <h1>{getPageTitle()}</h1>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<ScanPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/receipts" element={<ReceiptList />} />
        </Routes>
      </main>

      <Navigation />
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
