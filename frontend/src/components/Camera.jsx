import { useRef, useState, useCallback, useEffect } from 'react';

export default function Camera({ onCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [facingMode, setFacingMode] = useState('environment'); // 후면 카메라 기본

  // 전면 카메라 여부
  const isFrontCamera = facingMode === 'user';

  const startCamera = useCallback(async (mode) => {
    try {
      setError(null);

      // 기존 스트림 정리
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach(track => track.stop());
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: mode || facingMode,
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsStreaming(true);
      }
    } catch (err) {
      console.error('카메라 접근 오류:', err);
      setError('카메라에 접근할 수 없습니다. 권한을 확인해주세요.');
    }
  }, [facingMode]);

  const stopCamera = useCallback(() => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setIsStreaming(false);
    }
  }, []);

  const captureImage = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;

    // 비디오 원본 해상도로 캡처
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');

    // 캡처 이미지는 항상 정상 화면으로 저장 (거울 모드 적용 안함)
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // base64로 변환
    const imageData = canvas.toDataURL('image/jpeg', 0.9);

    onCapture(imageData);
  }, [onCapture]);

  const switchCamera = useCallback(async () => {
    const newMode = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(newMode);

    // 카메라가 실행 중이면 새 모드로 바로 재시작
    if (isStreaming) {
      await startCamera(newMode);
    }
  }, [facingMode, isStreaming, startCamera]);

  // 컴포넌트 언마운트시 카메라 정리
  useEffect(() => {
    return () => stopCamera();
  }, [stopCamera]);

  return (
    <div className="camera-container">
      {error && (
        <div className="error-message">{error}</div>
      )}

      <div className="video-wrapper">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="camera-video"
        />
        <canvas ref={canvasRef} style={{ display: 'none' }} />

        {isStreaming && (
          <div className="camera-overlay">
            <div className="receipt-guide">
              <span>영수증을 가이드 안에 맞춰주세요</span>
            </div>
          </div>
        )}
      </div>

      <div className="camera-controls">
        {!isStreaming ? (
          <button onClick={() => startCamera()} className="btn btn-primary">
            카메라 시작
          </button>
        ) : (
          <>
            <button onClick={switchCamera} className="btn btn-secondary">
              {isFrontCamera ? '후면 카메라' : '전면 카메라'}
            </button>
            <button onClick={captureImage} className="btn btn-capture">
              촬영
            </button>
            <button onClick={stopCamera} className="btn btn-secondary">
              카메라 종료
            </button>
          </>
        )}
      </div>
    </div>
  );
}
