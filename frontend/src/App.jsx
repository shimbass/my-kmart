import { useState, useEffect, useRef } from 'react';
import Camera from './components/Camera';
import ImagePreview from './components/ImagePreview';
import ResultTable from './components/ResultTable';
import { analyzeReceipt, saveReceipt } from './services/api';
import './App.css';

function App() {
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const mainRef = useRef(null);

  // 전체 화면 전환 가능 여부: API 존재 + 문서 전체 fullscreen 실제 지원 (iOS는 문서 fullscreen 미지원)
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
  // API가 있어도 불가한 경우: 비보안 컨텍스트(HTTP), iframe(상위 정책으로 차단될 수 있음)
  const isSecureContext = typeof window !== 'undefined' && window.isSecureContext;
  const isTopLevel = typeof window !== 'undefined' && window.self === window.top;
  const canFullscreen =
    hasFullscreenAPI && !getIsIOS() && isSecureContext && isTopLevel;
  const showFullscreenButton = canFullscreen;

  // 전체 화면 토글 (브라우저 주소창·UI 숨김)
  const toggleFullscreen = () => {
    try {
      const doc = document.documentElement;
      const exitFs = document.exitFullscreen || document.webkitExitFullscreen;
      const isFs = document.fullscreenElement || document.webkitFullscreenElement;

      if (isFs) {
        exitFs?.call(document);
        return;
      }
      // Fullscreen API 미지원 시 안내
      if (!canFullscreen) {
        return;
      }
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

  // 시작 시 전체 화면 진입 시도 (데스크톱만, 모바일에서는 검정 화면 등 부작용 방지)
  useEffect(() => {
    const isMobile = typeof window !== 'undefined' && (window.innerWidth < 768 || 'ontouchstart' in window);
    if (isMobile) return;
    const doc = document.documentElement;
    const requestFs = doc.requestFullscreen || doc.webkitRequestFullscreen;
    if (!requestFs) return;
    const timer = setTimeout(() => {
      if (document.fullscreenElement || document.webkitFullscreenElement) return;
      requestFs.call(doc).catch(() => {});
    }, 300);
    return () => clearTimeout(timer);
  }, []);

  // 화면 방향 변경 시 스크롤 맨 위로 이동
  useEffect(() => {
    const scrollToTop = () => {
      if (mainRef.current) {
        mainRef.current.scrollTop = 0;
      }
      window.scrollTo(0, 0);
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    };

    const handleOrientationChange = () => {
      // 레이아웃 변경 후 스크롤 적용을 위해 지연
      scrollToTop();
      setTimeout(scrollToTop, 100);
      setTimeout(scrollToTop, 300);
    };

    window.addEventListener('orientationchange', handleOrientationChange);

    // screen.orientation API 지원 시 추가 리스너
    if (screen.orientation) {
      screen.orientation.addEventListener('change', handleOrientationChange);
    }

    return () => {
      window.removeEventListener('orientationchange', handleOrientationChange);
      if (screen.orientation) {
        screen.orientation.removeEventListener('change', handleOrientationChange);
      }
    };
  }, []);

  const handleCapture = (imageData) => {
    setCapturedImage(imageData);
    setError(null);
  };

  const handleRetake = () => {
    setCapturedImage(null);
    setError(null);
  };

  const handleConfirm = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      const response = await analyzeReceipt(capturedImage);

      if (response.success) {
        setResult(response);
      } else {
        setError(response.error || '영수증 분석에 실패했습니다.');
      }
    } catch (err) {
      setError(`API 연결 오류: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setCapturedImage(null);
    setResult(null);
    setError(null);
  };

  const handleSave = async (data) => {
    const response = await saveReceipt(data);
    if (!response.success) {
      throw new Error(response.error || '저장 실패');
    }
    return response;
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
        <h1>{result ? '인식 결과' : 'K마트 영수증 스캐너'}</h1>
      </header>

      <main className="app-main" ref={mainRef}>
        {isProcessing && (
          <div className="processing-overlay">
            <div className="spinner"></div>
            <p>영수증 분석 중...</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError(null)} className="error-close">×</button>
          </div>
        )}

        {result ? (
          <ResultTable data={result} onReset={handleReset} onSave={handleSave} />
        ) : !capturedImage ? (
          <Camera onCapture={handleCapture} />
        ) : (
          <ImagePreview
            imageData={capturedImage}
            onRetake={handleRetake}
            onConfirm={handleConfirm}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>K-Mart Receipt Scanner v1.0</p>
      </footer>
    </div>
  );
}

export default App;
