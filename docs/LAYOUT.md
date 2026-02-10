# K마트 영수증 스캐너 — 레이아웃 정리

앱의 공통 구조와, 화면별·브레이크포인트별 레이아웃을 정리한 문서입니다.

---

## 1. 공통 구조 (모든 화면)

```
┌─────────────────────────────────────┐
│  .app-header (고정 높이)             │  ← 전체화면 버튼(조건부) + 제목
├─────────────────────────────────────┤
│                                     │
│  .app-main (flex: 1, 스크롤 가능)    │  ← 카메라 / 미리보기 / 결과 중 하나
│                                     │
├─────────────────────────────────────┤
│  .app-footer (고정 높이)             │  ← "K-Mart Receipt Scanner v1.0"
└─────────────────────────────────────┘
```

- **헤더**: `--header-height`(기본 60px), 제목은 결과 화면일 때 "인식 결과", 그 외 "K마트 영수증 스캐너".
- **메인**: `--available-height`까지 사용, `overflow-y: auto`로 스크롤.
- **푸터**: `--footer-height`(기본 40px), 항상 표시.
- **높이 기준**: `100dvh` 사용, 미지원 시 `100vh` + `min-height: 100vh` 폴백.

---

## 2. 화면(뷰) 종류

| 화면 | 컴포넌트 | 메인 내용 |
|------|----------|-----------|
| **촬영** | `Camera.jsx` | 비디오 + 가이드 오버레이("영수증을 가이드 안에 맞춰주세요") + 카메라 컨트롤(시작/후면·전면/촬영/종료) |
| **미리보기** | `ImagePreview.jsx` | 촬영 이미지 + "다시 촬영" / "이미지 분석" 버튼 |
| **인식 결과** | `ResultTable.jsx` | 상품 테이블 + 영수증 정보(상호·카드·구매일시) + 원본 텍스트 + 저장/새 스캔 버튼 |

---

## 3. 브레이크포인트·미디어 쿼리 요약

| 조건 | 대상 | 주요 변경 |
|------|------|------------|
| **기본** | 전체 | `--header-height: 60px`, `--footer-height: 40px`, `--controls-height: 100px` |
| **max-width: 480px** | 소형 모바일 | 헤더 50px, 푸터 36px, 컨트롤 90px, 패딩·폰트 축소, 촬영 버튼 70px, 미리보기 이미지 max-height 40dvh |
| **481px ~ 768px** | 태블릿 세로 | `.app` max-width 600px, 비디오 영역 높이 계산 조정 |
| **min-width: 769px** | 데스크톱 | 헤더 70px, `.app` max-width 800px, 카메라/미리보기/결과 영역 max-width 지정, 촬영 버튼 90px |
| **min-width: 1200px** | 대형 데스크톱 | `.app` max-width 1000px, 카메라/미리보기/결과 max-width 확대 |
| **orientation: landscape & max-height: 600px** | 스마트폰 가로 | 헤더 40px, 푸터 28px, 메인·카메라·미리보기 가로 배치(비디오+컨트롤 나란히), 결과는 세로 스크롤 유지 |
| **orientation: landscape & min-height: 601px & max-width: 1024px** | 태블릿 가로 | 카메라/미리보기 가로 배치(비디오 ~60vw + 컨트롤 패널), 컨트롤 min-width 120px |

---

## 4. 화면별 레이아웃 상세

### 4.1 촬영 화면 (Camera)

- **기본(세로)**  
  - `.camera-container`: 세로 flex, `gap: var(--spacing-md)`.  
  - `.video-wrapper`: flex: 1, `max-height: var(--camera-height)`, 비율 3/4 등은 브레이크포인트에서 조정.  
  - `.camera-controls`: 가로 배치, "카메라 시작" 또는 "후면/전면 · 촬영 · 카메라 종료".  
- **가로(높이 ≤600px)**  
  - `.camera-container`: **가로** flex.  
  - 비디오: `aspect-ratio: 3/4`, 높이 100%.  
  - 컨트롤: **세로**로 오른쪽에, `min-width: 80px`, `max-width: 100px`, 촬영 버튼 50px.  
- **태블릿 가로(601px~1024px)**  
  - 비디오 `max-width: 60vw`, 컨트롤 `min-width: 120px`로 패널 형태.

### 4.2 미리보기 화면 (ImagePreview)

- **기본(세로)**  
  - `.preview-container`: 세로 flex.  
  - `.preview-image-wrapper` + `.preview-image`: 이미지, `max-height: 100%` 등.  
  - `.preview-controls`: "다시 촬영" / "이미지 분석" 가로 배치.  
- **가로(높이 ≤600px)**  
  - `.preview-container`: **가로** flex.  
  - `.preview-image-wrapper`: flex: 2.  
  - `.preview-controls`: flex: 0 0 auto, **세로** 배치.  
- **태블릿 가로**  
  - 이미지 영역 `max-width: 60vw`, 컨트롤 `min-width: 120px`.

### 4.3 인식 결과 화면 (ResultTable)

- **공통**  
  - `.result-container`: 세로 flex, `gap: var(--spacing-md)`.  
  - 순서: 제목 "인식 결과" → (편집 안내) → 테이블 래퍼 → `.receipt-info` → `.raw-text-section` → `.result-controls`(저장 / 새 영수증 스캔).  
- **모바일(480px 이하)**  
  - 테이블 폰트·패딩 축소, `word-break: break-word` 등으로 가독성 유지.  
- **데스크톱(769px~)**  
  - `.result-container` max-width 600px(1200px 이상에서 700px).  
  - 테이블 행 호버 스타일.  
- **가로(높이 ≤600px)**  
  - `.result-container`는 계속 **세로** 배치.  
  - `.app-main:has(.result-container)`: `flex-direction: column`, `overflow-y: auto`로 세로 스크롤만 사용.

---

## 5. CSS 변수 (레이아웃 관련)

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `--header-height` | 60px | 헤더 높이 |
| `--footer-height` | 40px | 푸터 높이 |
| `--controls-height` | 100px | 카메라/미리보기 컨트롤 영역 높이 가이드 |
| `--available-height` | calc(100dvh - 헤더 - 푸터 - 패딩) | 메인 콘텐츠 사용 가능 높이 |
| `--camera-height` | calc(available-height - controls - gap) | 비디오 영역 최대 높이 |
| `--spacing-md`, `--spacing-sm`, `--spacing-xs` | 1rem, 0.75rem, 0.5rem | 간격 |
| `--font-size-*` | xs~xl | 제목·본문·버튼 등 폰트 크기 |
| `--btn-size` | 80px | 촬영 버튼 기준 크기(브레이크포인트에서 오버라이드) |

---

## 6. Safe Area·테마

- **Safe Area**  
  `@supports (padding: max(0px))` 안에서 헤더/푸터/메인에 `env(safe-area-inset-*)` 적용.  
  (노치·홈 인디케이터 있는 기기·PWA standalone 대응.)
- **다크/라이트**  
  `prefers-color-scheme: light`에서 `--color-bg`, `--color-text` 등 전환.
- **접근성**  
  `prefers-reduced-motion: reduce`에서 애니메이션·트랜지션 최소화.

---

## 7. 요약 표

| 화면 | 세로(모바일) | 가로(높이≤600px) | 데스크톱(769px~) |
|------|----------------|-------------------|------------------|
| **촬영** | 비디오 위 + 컨트롤 아래 | 비디오 왼쪽 + 컨트롤 오른쪽(세로) | 카메라 영역 max-width, 비율 3/4 |
| **미리보기** | 이미지 위 + 버튼 아래 | 이미지 왼쪽 + 버튼 오른쪽(세로) | 미리보기 영역 max-width |
| **결과** | 테이블 → 정보 → 버튼 (세로 스크롤) | 동일, 메인만 세로 스크롤 | result-container max-width 600~700px |

이 문서는 `frontend/src/App.css`와 각 컴포넌트 구조를 기준으로 작성되었습니다.
