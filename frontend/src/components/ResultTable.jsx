import { useState, useEffect, useRef } from 'react';

export default function ResultTable({ data, onReset, onSave }) {
  const { items: originalItems, rawText, purchaseDateTime, storeName, cardName } = data;
  const [items, setItems] = useState(() => JSON.parse(JSON.stringify(originalItems)));
  const [editingCell, setEditingCell] = useState(null); // { index, field }
  const [saveStatus, setSaveStatus] = useState('idle'); // idle, saving, saved, error
  const hasEdited = useRef(false); // 사용자가 수정했는지 추적

  // 원본 데이터 변경 시 items 업데이트 (수정하지 않은 경우에만)
  useEffect(() => {
    if (!hasEdited.current) {
      setItems(JSON.parse(JSON.stringify(originalItems)));
    }
  }, [originalItems]);

  const totalAmount = items.reduce((sum, item) => sum + item.amount, 0);

  const handleCellClick = (index, field) => {
    if (saveStatus === 'saved') return; // 저장 완료 후 수정 불가
    setEditingCell({ index, field });
  };

  const handleCellChange = (index, field, value) => {
    hasEdited.current = true; // 수정 플래그 설정
    const newItems = [...items];
    const item = { ...newItems[index] };

    if (field === 'name') {
      item.name = value;
    } else if (field === 'unitPrice') {
      const numValue = parseInt(value.replace(/[^0-9]/g, '')) || 0;
      item.unitPrice = numValue;
      item.amount = numValue * item.quantity;
    } else if (field === 'quantity') {
      const numValue = parseInt(value.replace(/[^0-9]/g, '')) || 0;
      item.quantity = numValue;
      item.amount = item.unitPrice * numValue;
    } else if (field === 'amount') {
      const numValue = parseInt(value.replace(/[^0-9]/g, '')) || 0;
      item.amount = numValue;
    }

    newItems[index] = item;
    setItems(newItems);
  };

  const handleCellBlur = () => {
    setEditingCell(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      setEditingCell(null);
    }
  };

  const handleSave = async () => {
    if (saveStatus === 'saving' || saveStatus === 'saved') return;

    setSaveStatus('saving');
    try {
      // 데이터 타입 확인 및 변환
      const formattedItems = items.map(item => ({
        no: String(item.no || ''),
        name: String(item.name || ''),
        barcode: item.barcode ? String(item.barcode) : null,
        unitPrice: parseInt(item.unitPrice) || 0,
        quantity: parseInt(item.quantity) || 0,
        amount: parseInt(item.amount) || 0
      }));

      const saveData = {
        items: formattedItems,
        rawText: rawText || '',
        storeName: storeName || null,
        cardName: cardName || null,
        purchaseDateTime: purchaseDateTime || null
      };
      console.log('저장할 데이터:', saveData);
      await onSave(saveData);
      setSaveStatus('saved');
    } catch (error) {
      console.error('저장 실패:', error.message);
      alert(`저장 실패: ${error.message}`);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 2000);
    }
  };

  const getSaveButtonText = () => {
    switch (saveStatus) {
      case 'saving': return '저장 중...';
      case 'saved': return '저장 완료';
      case 'error': return '저장 실패';
      default: return '저장';
    }
  };

  const renderEditableCell = (index, field, value, className = '') => {
    const isEditing = editingCell?.index === index && editingCell?.field === field;
    const displayValue = typeof value === 'number' ? value.toLocaleString() : value;

    if (isEditing) {
      return (
        <input
          type={field === 'name' ? 'text' : 'tel'}
          className="edit-input"
          value={typeof value === 'number' ? value : value}
          onChange={(e) => handleCellChange(index, field, e.target.value)}
          onBlur={handleCellBlur}
          onKeyDown={handleKeyDown}
          autoFocus
        />
      );
    }

    return (
      <span
        className={`editable-cell ${className}`}
        onClick={() => handleCellClick(index, field)}
      >
        {displayValue}
      </span>
    );
  };

  return (
    <div className="result-container">
      <h3>인식 결과</h3>
      {saveStatus !== 'saved' && items.length > 0 && (
        <p className="edit-hint">항목을 터치하면 수정할 수 있습니다</p>
      )}

      {items.length > 0 ? (
        <>
          <div className="result-table-wrapper">
            <table className="result-table">
              <thead>
                <tr>
                  <th>NO</th>
                  <th>상품명</th>
                  <th>단가</th>
                  <th>수량</th>
                  <th>금액</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, index) => (
                  <tr key={index}>
                    <td>{item.no}</td>
                    <td className="product-name">
                      {renderEditableCell(index, 'name', item.name)}
                      {item.barcode && (
                        <span className="barcode">{item.barcode}</span>
                      )}
                    </td>
                    <td className="price">
                      {renderEditableCell(index, 'unitPrice', item.unitPrice)}
                    </td>
                    <td className="quantity">
                      {renderEditableCell(index, 'quantity', item.quantity)}
                    </td>
                    <td className="price">
                      {renderEditableCell(index, 'amount', item.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <td colSpan="4" className="total-label">합계</td>
                  <td className="total-amount">{totalAmount.toLocaleString()}</td>
                </tr>
              </tfoot>
            </table>
          </div>

          <div className="receipt-info">
            {storeName && (
              <div className="info-row">
                <span className="info-label">상호명:</span>
                <span className="info-value">{storeName}</span>
              </div>
            )}
            {cardName && (
              <div className="info-row">
                <span className="info-label">카드명:</span>
                <span className="info-value">{cardName}</span>
              </div>
            )}
            {purchaseDateTime && (
              <div className="info-row">
                <span className="info-label">구매일시:</span>
                <span className="info-value">{purchaseDateTime}</span>
              </div>
            )}
          </div>

          <details className="raw-text-section">
            <summary>원본 텍스트 보기</summary>
            <pre className="raw-text">{rawText}</pre>
          </details>
        </>
      ) : (
        <div className="no-items">
          <p>인식된 상품이 없습니다.</p>
          {rawText && (
            <details className="raw-text-section">
              <summary>원본 텍스트 보기</summary>
              <pre className="raw-text">{rawText}</pre>
            </details>
          )}
        </div>
      )}

      <div className="result-controls">
        {items.length > 0 && (
          <button
            onClick={handleSave}
            className={`btn btn-save ${saveStatus}`}
            disabled={saveStatus === 'saving' || saveStatus === 'saved'}
          >
            {getSaveButtonText()}
          </button>
        )}
        <button onClick={onReset} className="btn btn-primary">
          새 영수증 스캔
        </button>
      </div>
    </div>
  );
}
