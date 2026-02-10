// 개발: 빈 문자열(프록시 사용) / 배포: VITE_API_URL (백엔드 주소)
const API_BASE_URL = import.meta.env.VITE_API_URL ?? '';

export async function analyzeReceipt(imageData) {
  const response = await fetch(`${API_BASE_URL}/api/ocr`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ image: imageData }),
  });

  if (!response.ok) {
    throw new Error(`API 오류: ${response.status}`);
  }

  return response.json();
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.json();
}

export async function saveReceipt(data) {
  console.log('저장 요청 데이터:', JSON.stringify(data, null, 2));

  const response = await fetch(`${API_BASE_URL}/api/receipts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  const result = await response.json();
  console.log('저장 응답:', result);

  if (!response.ok) {
    throw new Error(result.detail || `저장 오류: ${response.status}`);
  }

  return result;
}

export async function getReceipts(params = {}) {
  const searchParams = new URLSearchParams();

  // 기존 방식 호환 (숫자가 오면 limit으로 처리)
  if (typeof params === 'number') {
    searchParams.append('limit', params);
  } else {
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.start_date) searchParams.append('start_date', params.start_date);
    if (params.end_date) searchParams.append('end_date', params.end_date);
    if (params.store_name) searchParams.append('store_name', params.store_name);
    if (params.card_name) searchParams.append('card_name', params.card_name);
    if (params.search) searchParams.append('search', params.search);
  }

  const queryString = searchParams.toString();
  const url = `${API_BASE_URL}/api/receipts${queryString ? '?' + queryString : ''}`;
  const response = await fetch(url);
  return response.json();
}

export async function getReceiptDetail(id) {
  const response = await fetch(`${API_BASE_URL}/api/receipts/${id}`);
  return response.json();
}

export async function deleteReceipt(id) {
  const response = await fetch(`${API_BASE_URL}/api/receipts/${id}`, {
    method: 'DELETE',
  });
  return response.json();
}

// Statistics APIs
export async function getStats(startDate, endDate) {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const response = await fetch(`${API_BASE_URL}/api/stats/summary?${params.toString()}`);
  return response.json();
}

export async function getMonthlyStats(startDate, endDate) {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const response = await fetch(`${API_BASE_URL}/api/stats/monthly?${params.toString()}`);
  return response.json();
}

export async function getStoreStats(startDate, endDate) {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const response = await fetch(`${API_BASE_URL}/api/stats/by-store?${params.toString()}`);
  return response.json();
}

export async function getCardStats(startDate, endDate) {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const response = await fetch(`${API_BASE_URL}/api/stats/by-card?${params.toString()}`);
  return response.json();
}

export async function getFrequentItems(startDate, endDate, limit = 10) {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  params.append('limit', limit);

  const response = await fetch(`${API_BASE_URL}/api/stats/frequent-items?${params.toString()}`);
  return response.json();
}

export async function getStoreCardStats(storeName, startDate, endDate) {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const response = await fetch(`${API_BASE_URL}/api/stats/store/${encodeURIComponent(storeName)}/cards?${params.toString()}`);
  return response.json();
}
