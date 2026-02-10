import { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import { ko } from 'date-fns/locale';
import { format, subMonths, startOfMonth, endOfMonth, startOfYear } from 'date-fns';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getStats, getMonthlyStats, getStoreStats, getFrequentItems, getStoreCardStats } from '../services/api';
import 'react-datepicker/dist/react-datepicker.css';
import './Dashboard.css';

function Dashboard() {
  const [startDate, setStartDate] = useState(startOfMonth(new Date()));
  const [endDate, setEndDate] = useState(new Date());
  const [summary, setSummary] = useState({ total_amount: 0, receipt_count: 0, avg_amount: 0 });
  const [monthlyData, setMonthlyData] = useState([]);
  const [storeData, setStoreData] = useState([]);
  const [frequentItems, setFrequentItems] = useState([]);
  const [loading, setLoading] = useState(true);

  // 상점 상세 (카드별 지출)
  const [selectedStore, setSelectedStore] = useState(null);
  const [storeCardData, setStoreCardData] = useState([]);
  const [storeCardLoading, setStoreCardLoading] = useState(false);

  const formatDateParam = (date) => format(date, 'yy-MM-dd');

  const fetchData = async () => {
    setLoading(true);
    try {
      const start = formatDateParam(startDate);
      const end = formatDateParam(endDate);

      const [summaryRes, monthlyRes, storeRes, itemsRes] = await Promise.all([
        getStats(start, end),
        getMonthlyStats(start, end),
        getStoreStats(start, end),
        getFrequentItems(start, end, 10)
      ]);

      if (summaryRes.success) setSummary(summaryRes.data);
      if (monthlyRes.success) setMonthlyData(monthlyRes.data);
      if (storeRes.success) setStoreData(storeRes.data);
      if (itemsRes.success) setFrequentItems(itemsRes.data);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    setSelectedStore(null);
  }, [startDate, endDate]);

  const handleStoreClick = async (store) => {
    if (selectedStore === store.store_name) {
      setSelectedStore(null);
      setStoreCardData([]);
      return;
    }

    setSelectedStore(store.store_name);
    setStoreCardLoading(true);

    try {
      const start = formatDateParam(startDate);
      const end = formatDateParam(endDate);
      const res = await getStoreCardStats(store.store_name, start, end);
      if (res.success) {
        setStoreCardData(res.data);
      }
    } catch (err) {
      console.error('Failed to fetch store card stats:', err);
    } finally {
      setStoreCardLoading(false);
    }
  };

  const setQuickRange = (type) => {
    const now = new Date();
    switch (type) {
      case 'thisMonth':
        setStartDate(startOfMonth(now));
        setEndDate(now);
        break;
      case 'lastMonth':
        const lastMonth = subMonths(now, 1);
        setStartDate(startOfMonth(lastMonth));
        setEndDate(endOfMonth(lastMonth));
        break;
      case '3months':
        setStartDate(startOfMonth(subMonths(now, 2)));
        setEndDate(now);
        break;
      case 'thisYear':
        setStartDate(startOfYear(now));
        setEndDate(now);
        break;
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('ko-KR').format(value);
  };

  const getPercent = (amount) => {
    if (!summary.total_amount) return 0;
    return ((amount / summary.total_amount) * 100).toFixed(1);
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{label}</p>
          <p className="tooltip-value">₩{formatCurrency(payload[0].value)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="dashboard">
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
          <button onClick={() => setQuickRange('thisMonth')}>이번 달</button>
          <button onClick={() => setQuickRange('lastMonth')}>지난 달</button>
          <button onClick={() => setQuickRange('3months')}>3개월</button>
          <button onClick={() => setQuickRange('thisYear')}>올해</button>
        </div>
      </div>

      {loading ? (
        <div className="loading">데이터 로딩 중...</div>
      ) : (
        <>
          <div className="summary-cards">
            <div className="summary-card">
              <span className="card-label">총 지출</span>
              <span className="card-value">₩{formatCurrency(summary.total_amount)}</span>
            </div>
            <div className="summary-card">
              <span className="card-label">영수증 수</span>
              <span className="card-value">{summary.receipt_count}건</span>
            </div>
            <div className="summary-card">
              <span className="card-label">평균 금액</span>
              <span className="card-value">₩{formatCurrency(summary.avg_amount)}</span>
            </div>
          </div>

          {monthlyData.length > 0 && (
            <div className="chart-section">
              <h3>월별 지출</h3>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis tickFormatter={(v) => `${(v / 10000).toFixed(0)}만`} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="total_amount" fill="#2196F3" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {storeData.length > 0 && (
            <div className="chart-section">
              <h3>상점별 지출</h3>
              <div className="store-list">
                {storeData.map((store, index) => (
                  <div key={index}>
                    <div
                      className={`store-item ${selectedStore === store.store_name ? 'active' : ''}`}
                      onClick={() => handleStoreClick(store)}
                    >
                      <div className="store-rank">{index + 1}</div>
                      <div className="store-info">
                        <div className="store-name">{store.store_name}</div>
                        <div className="store-visits">{store.visit_count}회 방문</div>
                      </div>
                      <div className="store-stats">
                        <div className="store-amount">₩{formatCurrency(store.total_amount)}</div>
                        <div className="store-percent">{getPercent(store.total_amount)}%</div>
                      </div>
                      <div className="store-arrow">{selectedStore === store.store_name ? '▼' : '▶'}</div>
                    </div>

                    {selectedStore === store.store_name && (
                      <div className="store-card-detail">
                        {storeCardLoading ? (
                          <div className="card-loading">로딩 중...</div>
                        ) : storeCardData.length > 0 ? (
                          <div className="card-list">
                            <div className="card-list-header">카드별 결제 내역</div>
                            {storeCardData.map((card, cardIndex) => (
                              <div key={cardIndex} className="card-item">
                                <span className="card-name">{card.card_name}</span>
                                <span className="card-usage">{card.usage_count}회</span>
                                <span className="card-amount">₩{formatCurrency(card.total_amount)}</span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="card-empty">카드 정보가 없습니다.</div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {frequentItems.length > 0 && (
            <div className="chart-section">
              <h3>자주 구매하는 상품</h3>
              <div className="frequent-items">
                <table>
                  <thead>
                    <tr>
                      <th>순위</th>
                      <th>상품명</th>
                      <th>구매 횟수</th>
                      <th>총 금액</th>
                      <th>평균 주기</th>
                    </tr>
                  </thead>
                  <tbody>
                    {frequentItems.map((item, index) => (
                      <tr key={index}>
                        <td>{index + 1}</td>
                        <td className="item-name">{item.name}</td>
                        <td>{item.purchase_count}회</td>
                        <td>₩{formatCurrency(item.total_amount)}</td>
                        <td>{item.avg_interval_days ? `${item.avg_interval_days}일` : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {monthlyData.length === 0 && storeData.length === 0 && (
            <div className="no-data">
              <p>선택한 기간에 데이터가 없습니다.</p>
              <p>영수증을 스캔하고 저장해보세요!</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Dashboard;
