# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

K마트 영수증 인식 웹 애플리케이션. 카메라로 영수증을 촬영하고 Google Gemini API를 통해 상품 정보를 추출하여 구조화된 데이터로 변환 및 저장한다. 대시보드에서 지출 통계를 확인하고, 영수증 목록에서 상세 내역을 조회할 수 있다.

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

### 페이지 구조
```
/ (ScanPage)       - 영수증 스캔 및 저장
/dashboard         - 지출 통계 대시보드
/receipts          - 영수증 목록 조회
```

### 프론트엔드 구조 (React + Vite)
```
frontend/src/
├── App.jsx                    # 라우팅, 레이아웃
├── App.css                    # 글로벌 스타일, CSS 변수 (디자인 시스템)
├── pages/
│   ├── ScanPage.jsx           # 스캔 페이지 (카메라 → 미리보기 → 결과)
│   ├── Dashboard.jsx          # 대시보드 (통계, 차트)
│   ├── Dashboard.css
│   ├── ReceiptList.jsx        # 영수증 목록 (필터, 검색, 상세 모달)
│   └── ReceiptList.css
├── components/
│   ├── Camera.jsx             # 카메라 캡처
│   ├── ImagePreview.jsx       # 이미지 미리보기
│   ├── ResultTable.jsx        # OCR 결과 테이블 (인라인 수정)
│   └── common/
│       ├── Navigation.jsx     # 하단 네비게이션 (3탭)
│       └── Navigation.css
└── services/
    └── api.js                 # API 통신 함수
```

### 백엔드 구조 (FastAPI + Supabase)
```
backend/app/
├── main.py                    # API 엔드포인트
├── services/
│   ├── ocr_service.py         # Gemini API OCR 처리
│   ├── db_service.py          # Supabase 데이터베이스 연동
│   └── stats_service.py       # 통계 계산 서비스
└── .env                       # 환경 변수 (API 키)
```

### API 엔드포인트

#### 영수증 CRUD
- `POST /api/ocr` - 영수증 이미지 분석
- `POST /api/receipts` - 인식 결과 저장
- `GET /api/receipts` - 영수증 목록 조회 (필터: start_date, end_date, store_name, card_name, search)
- `GET /api/receipts/{id}` - 영수증 상세 조회
- `DELETE /api/receipts/{id}` - 영수증 삭제

#### 통계 API
- `GET /api/stats/summary` - 요약 통계 (총 지출, 영수증 수, 평균 금액)
- `GET /api/stats/monthly` - 월별 지출 통계
- `GET /api/stats/by-store` - 상점별 지출 통계
- `GET /api/stats/by-card` - 카드별 지출 통계
- `GET /api/stats/frequent-items` - 자주 구매하는 상품 (구매 주기 포함)
- `GET /api/stats/store/{store_name}/cards` - 특정 상점의 카드별 결제 내역

### 데이터 흐름
```
[스캔 페이지]
카메라 캡처 → base64 이미지 → POST /api/ocr → Gemini API → JSON 응답 → 테이블 표시 → 수정 → POST /api/receipts → Supabase 저장

[대시보드]
날짜 선택 → GET /api/stats/* → 차트/리스트 렌더링

[영수증 목록]
필터/검색 → GET /api/receipts → 목록 표시 → 클릭 → GET /api/receipts/{id} → 상세 모달
```

### 데이터베이스 (Supabase PostgreSQL)
```sql
-- receipts 테이블
id, store_name, card_name, purchase_datetime, total_amount, raw_text, created_at

-- items 테이블
id, receipt_id (FK), no, name, barcode, unit_price, quantity, amount
```

### CSS 디자인 시스템 (App.css)
```css
/* 주요 CSS 변수 */
--color-bg            /* 페이지 배경 */
--color-bg-secondary  /* 카드/섹션 배경 */
--color-bg-tertiary   /* 테두리, 구분선 */
--color-text          /* 기본 텍스트 */
--color-text-muted    /* 보조 텍스트 */
--color-primary       /* 강조색 (파란색) */
--color-danger        /* 위험/삭제 (빨간색) */
--spacing-xs/sm/md/lg /* 간격 */
--font-size-xs/sm/md/lg /* 폰트 크기 */
--border-radius       /* 모서리 둥글기 */
--nav-height          /* 하단 네비 높이 */
```

### 주요 의존성
- **Frontend**: react, react-router-dom, react-datepicker, date-fns, recharts
- **Backend**: fastapi, uvicorn, supabase-py, google-generativeai, python-dotenv

## 환경 변수

### backend/.env
```
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### frontend/.env (배포 시)
```
VITE_API_URL=https://your-backend-url.com
```

## 문서
- `docs/페이지_레이아웃.md` - 페이지별 상세 레이아웃 설명
- `docs/PRD.md` - 제품 요구사항 문서
