# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

K마트 영수증 인식 웹 애플리케이션. 카메라로 영수증을 촬영하고 Google Gemini API를 통해 상품 정보를 추출하여 구조화된 데이터로 변환한다.

## Commands

### Frontend
```bash
cd frontend && npm install    # 의존성 설치
cd frontend && npm run dev    # 개발 서버 (http://localhost:5173)
cd frontend && npm run build  # 프로덕션 빌드
```

### Backend
```bash
cd backend && pip install -r requirements.txt  # 의존성 설치
cd backend && uvicorn app.main:app --reload    # 개발 서버 (http://localhost:8000)
```

## Architecture

### 모듈 구조
```
Frontend (React + Vite)
├── src/components/Camera.jsx      # 카메라 캡처
├── src/components/ImagePreview.jsx # 이미지 미리보기
├── src/components/ResultTable.jsx  # 결과 테이블 표시
├── src/services/api.js            # API 통신
└── src/App.jsx                    # 메인 앱 (전체화면, 화면전환)

Backend (FastAPI)
├── app/main.py                    # API 엔드포인트
├── app/services/ocr_service.py    # Gemini API OCR 처리
└── app/services/db_service.py     # 데이터베이스 연동
```

### API 엔드포인트
- `POST /api/ocr` - 영수증 이미지 분석
- `POST /api/receipts` - 인식 결과 저장
- `GET /api/receipts` - 저장된 영수증 목록 조회
- `GET /api/receipts/{id}` - 영수증 상세 조회
- `DELETE /api/receipts/{id}` - 영수증 삭제

### 데이터 흐름
카메라 캡처 → base64 이미지 → FastAPI 전송 → Gemini API (이미지 분석 + 텍스트 추출 + 파싱) → JSON 응답 → 테이블 표시

### 출력 데이터 구조
```json
{
  "success": true,
  "storeName": "케이할인마트",
  "cardName": "신한카드",
  "purchaseDateTime": "25-02-02 14:30",
  "items": [
    {
      "no": "001",
      "name": "츄파춥스)피즈캔디 90g",
      "barcode": "6921211117476",
      "unitPrice": 2200,
      "quantity": 1,
      "amount": 2200
    }
  ],
  "rawText": "영수증 전체 텍스트"
}
```

## 환경 변수
- `GEMINI_API_KEY`: Google Gemini API 키 (backend/.env 파일에 설정)
