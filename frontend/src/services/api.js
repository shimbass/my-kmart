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

export async function getReceipts(limit = 20) {
  const response = await fetch(`${API_BASE_URL}/api/receipts?limit=${limit}`);
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
