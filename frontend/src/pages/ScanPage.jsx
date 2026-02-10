import { useState, useRef } from 'react';
import Camera from '../components/Camera';
import ImagePreview from '../components/ImagePreview';
import ResultTable from '../components/ResultTable';
import { analyzeReceipt, saveReceipt } from '../services/api';

function ScanPage() {
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const mainRef = useRef(null);

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
    <div className="scan-page" ref={mainRef}>
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
    </div>
  );
}

export default ScanPage;
