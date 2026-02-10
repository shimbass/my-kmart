export default function ImagePreview({ imageData, onRetake, onConfirm }) {
  return (
    <div className="preview-container">
      <h3>촬영된 이미지</h3>

      <div className="preview-image-wrapper">
        <img src={imageData} alt="촬영된 영수증" className="preview-image" />
      </div>

      <div className="preview-controls">
        <button onClick={onRetake} className="btn btn-secondary">
          다시 촬영
        </button>
        <button onClick={onConfirm} className="btn btn-primary">
          이미지 분석
        </button>
      </div>
    </div>
  );
}
