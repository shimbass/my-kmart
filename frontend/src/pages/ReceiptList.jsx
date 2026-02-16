import { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import { ko } from 'date-fns/locale';
import { format, startOfMonth, endOfMonth, subMonths, startOfYear } from 'date-fns';
import { getReceipts, getReceiptDetail } from '../services/api';
import 'react-datepicker/dist/react-datepicker.css';
import './ReceiptList.css';

function ReceiptList() {
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReceipt, setSelectedReceipt] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Filters (기본: 이번 달, 대시보드와 동일)
  const [startDate, setStartDate] = useState(startOfMonth(new Date()));
  const [endDate, setEndDate] = useState(new Date());
  const [storeFilter, setStoreFilter] = useState('');
  const [cardFilter, setCardFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const [stores, setStores] = useState([]);
  const [cards, setCards] = useState([]);

  const fetchReceipts = async () => {
    setLoading(true);
    try {
      const params = { limit: 100 };
      if (startDate) params.start_date = format(startDate, 'yy-MM-dd');
      if (endDate) params.end_date = format(endDate, 'yy-MM-dd');
      if (storeFilter) params.store_name = storeFilter;
      if (cardFilter) params.card_name = cardFilter;
      if (searchQuery) params.search = searchQuery;

      const response = await getReceipts(params);
      if (response.success) {
        const receiptList = response.receipts || [];
        setReceipts(receiptList);

        // Extract unique stores and cards for filters
        const uniqueStores = [...new Set(receiptList.map(r => r.store_name).filter(Boolean))];
        const uniqueCards = [...new Set(receiptList.map(r => r.card_name).filter(Boolean))];
        setStores(uniqueStores);
        setCards(uniqueCards);
      }
    } catch (err) {
      console.error('Failed to fetch receipts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReceipts();
  }, [startDate, endDate, storeFilter, cardFilter, searchQuery]);

  const handleReceiptClick = async (receipt) => {
    setSelectedReceipt(receipt);
    setDetailLoading(true);
    try {
      const response = await getReceiptDetail(receipt.id);
      if (response.success) {
        setDetailData(response);
      }
    } catch (err) {
      console.error('Failed to fetch receipt detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const closeModal = () => {
    setSelectedReceipt(null);
    setDetailData(null);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('ko-KR').format(value || 0);
  };

  // 날짜 배지용 파싱
  const parseDateBadge = (dateStr) => {
    if (!dateStr) return { day: '-', month: '-' };
    const match = dateStr.match(/(\d{2})-(\d{2})-(\d{2})\s*(\d{2}):(\d{2})/);
    if (match) {
      return {
        day: match[3],
        month: `${match[2]}월`,
        time: `${match[4]}:${match[5]}`
      };
    }
    return { day: '-', month: '-', time: '' };
  };

  const formatDateTime = (dateStr) => {
    if (!dateStr) return '-';
    const match = dateStr.match(/(\d{2})-(\d{2})-(\d{2})\s*(\d{2}):(\d{2})/);
    if (match) {
      return `20${match[1]}년 ${match[2]}월 ${match[3]}일 ${match[4]}:${match[5]}`;
    }
    return dateStr;
  };

  const clearFilters = () => {
    setStartDate(startOfMonth(new Date()));
    setEndDate(new Date());
    setStoreFilter('');
    setCardFilter('');
    setSearchQuery('');
  };

  const setQuickRange = (type) => {
    const now = new Date();
    switch (type) {
      case 'thisMonth':
        setStartDate(startOfMonth(now));
        setEndDate(now);
        break;
      case 'lastMonth': {
        const lastMonth = subMonths(now, 1);
        setStartDate(startOfMonth(lastMonth));
        setEndDate(endOfMonth(lastMonth));
        break;
      }
      case '3months':
        setStartDate(startOfMonth(subMonths(now, 2)));
        setEndDate(now);
        break;
      case 'thisYear':
        setStartDate(startOfYear(now));
        setEndDate(now);
        break;
      default:
        break;
    }
  };

  return (
    <div className="receipt-list-page">
      {/* 1. 맨 위: 시작일-종료일 + 빠른 기간 (대시보드와 동일) */}
      <div className="date-range-section">
        <div className="date-pickers">
          <div className="date-picker-wrapper">
            <label>시작일</label>
            <DatePicker
              selected={startDate}
              onChange={setStartDate}
              selectsStart
              startDate={startDate}
              endDate={endDate}
              dateFormat="yyyy.MM.dd"
              locale={ko}
              className="date-input"
            />
          </div>
          <span className="date-separator">~</span>
          <div className="date-picker-wrapper">
            <label>종료일</label>
            <DatePicker
              selected={endDate}
              onChange={setEndDate}
              selectsEnd
              startDate={startDate}
              endDate={endDate}
              minDate={startDate}
              dateFormat="yyyy.MM.dd"
              locale={ko}
              className="date-input"
            />
          </div>
        </div>
        <div className="quick-buttons">
          <button type="button" onClick={() => setQuickRange('thisMonth')}>이번 달</button>
          <button type="button" onClick={() => setQuickRange('lastMonth')}>지난 달</button>
          <button type="button" onClick={() => setQuickRange('3months')}>3개월</button>
          <button type="button" onClick={() => setQuickRange('thisYear')}>올해</button>
        </div>
      </div>

      {/* 2. 구분: 상품명 검색 */}
      <div className="receipt-search-section">
        <input
          type="text"
          placeholder="상품명 검색..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="receipt-search-input"
        />
      </div>

      {/* 3. 구분: 상점·카드 필터 (도톰한 높이) */}
      <div className="receipt-filters-row">
        <select
          value={storeFilter}
          onChange={(e) => setStoreFilter(e.target.value)}
          className="filter-select"
        >
          <option value="">모든 상점</option>
          {stores.map((store) => (
            <option key={store} value={store}>{store}</option>
          ))}
        </select>
        <select
          value={cardFilter}
          onChange={(e) => setCardFilter(e.target.value)}
          className="filter-select"
        >
          <option value="">모든 카드</option>
          {cards.map((card) => (
            <option key={card} value={card}>{card}</option>
          ))}
        </select>
        <button
          type="button"
          onClick={clearFilters}
          className="clear-filters-btn"
          disabled={!storeFilter && !cardFilter && !searchQuery}
        >
          초기화
        </button>
      </div>

      <div className="receipts-section">
        <h3>영수증 확인</h3>
        {loading ? (
          <div className="loading">로딩 중...</div>
        ) : receipts.length === 0 ? (
          <div className="no-receipts">
            <p>저장된 영수증이 없습니다.</p>
            <p>영수증을 스캔하고 저장해보세요!</p>
          </div>
        ) : (
          <div className="receipts-container">
            {receipts.map((receipt) => {
              const dateBadge = parseDateBadge(receipt.purchase_datetime);
              return (
                <div
                  key={receipt.id}
                  className="receipt-card"
                  onClick={() => handleReceiptClick(receipt)}
                >
                  <div className="receipt-date-badge">
                    <div className="day">{dateBadge.day}</div>
                    <div className="month">{dateBadge.month}</div>
                  </div>
                  <div className="receipt-item-info">
                    <div className="receipt-item-store">{receipt.store_name || '상점명 없음'}</div>
                    <div className="receipt-item-meta">
                      <span className="receipt-item-time">{dateBadge.time}</span>
                      {receipt.card_name && (
                        <span className="receipt-item-card">{receipt.card_name}</span>
                      )}
                    </div>
                  </div>
                  <div className="receipt-item-stats">
                    <div className="receipt-item-amount">₩{formatCurrency(receipt.total_amount)}</div>
                  </div>
                  <div className="receipt-arrow">▶</div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedReceipt && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>×</button>

            {detailLoading ? (
              <div className="modal-loading">로딩 중...</div>
            ) : detailData ? (
              <>
                <div className="modal-header">
                  <h2>{detailData.receipt?.store_name || '영수증 상세'}</h2>
                  <div className="modal-info-row">
                    <span className="modal-info-label">구매일시</span>
                    <span className="modal-info-value">
                      {formatDateTime(detailData.receipt?.purchase_datetime)}
                    </span>
                  </div>
                  <div className="modal-info-row">
                    <span className="modal-info-label">결제수단</span>
                    <span className="modal-info-value">
                      {detailData.receipt?.card_name || '-'}
                    </span>
                  </div>
                </div>

                <div className="modal-items">
                  <table>
                    <thead>
                      <tr>
                        <th>No</th>
                        <th>상품명</th>
                        <th>단가</th>
                        <th>수량</th>
                        <th>금액</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detailData.items?.map((item, index) => (
                        <tr key={index}>
                          <td>{item.no}</td>
                          <td className="item-name">{item.name}</td>
                          <td>₩{formatCurrency(item.unit_price)}</td>
                          <td>{item.quantity}</td>
                          <td>₩{formatCurrency(item.amount)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="modal-total">
                  <span>총 결제금액</span>
                  <span className="total-amount">
                    ₩{formatCurrency(detailData.receipt?.total_amount)}
                  </span>
                </div>
              </>
            ) : (
              <div className="modal-error">상세 정보를 불러올 수 없습니다.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ReceiptList;
