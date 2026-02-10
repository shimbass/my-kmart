# Render.com 배포 가이드

프론트엔드, 백엔드, 데이터베이스(Supabase)를 모두 Render에서 쓰기 위한 **배포 순서**와 **단계**입니다.

---

## 배포 순서 (요약)

```
1. 데이터베이스 → 이미 Supabase 준비됨 (별도 배포 없음)
2. 백엔드(API) 배포 → URL 확보
3. 프론트엔드 배포 → 백엔드 URL을 환경 변수로 설정
```

DB는 Supabase를 그대로 쓰므로, **백엔드 → 프론트엔드** 순서만 지키면 됩니다.

---

## 1단계: 백엔드(Web Service) 배포

백엔드를 먼저 올려서 **API URL**을 만듭니다. 이 URL을 나중에 프론트엔드에서 씁니다.

### 1-1. 새 Web Service 만들기

1. [Render Dashboard](https://dashboard.render.com) 로그인
2. **New +** → **Web Service**
3. 저장소 연결: GitHub에서 **my-kmart** (또는 해당 저장소) 선택
4. **Connect** 후 아래처럼 설정

### 1-2. 백엔드 설정값

| 항목 | 값 |
|------|-----|
| **Name** | `my-kmart-api` (원하는 이름) |
| **Region** | Singapore 또는 가까운 지역 |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### 1-3. 환경 변수 (Environment)

**Environment** 탭에서 다음을 추가합니다.

| Key | Value | 비고 |
|-----|--------|------|
| `GEMINI_API_KEY` | (본인 Gemini API 키) | 필수 |
| `SUPABASE_URL` | (Supabase 프로젝트 URL) | Supabase 대시보드 → Settings → API |
| `SUPABASE_KEY` | (Supabase anon key) | Supabase 대시보드 → Settings → API |

값은 **Secret**로 두는 것을 권장합니다.

### 1-4. 배포

- **Create Web Service** 클릭
- 빌드·배포가 끝나면 상단에 **URL**이 나옵니다.  
  예: `https://my-kmart-api.onrender.com`  
  이 URL을 복사해 두세요 (끝에 `/` 없이).

### 1-5. 동작 확인

- 브라우저에서 `https://본인-백엔드-URL/health` 접속
- `{"status":"healthy", ...}` 비슷한 JSON이 보이면 성공

---

## 2단계: 프론트엔드(Static Site) 배포

백엔드 URL을 알고 있는 상태에서 진행합니다.

### 2-1. 새 Static Site 만들기

1. Render Dashboard에서 **New +** → **Static Site**
2. 같은 GitHub 저장소 **my-kmart** 선택 후 **Connect**

### 2-2. 프론트엔드 설정값

| 항목 | 값 |
|------|-----|
| **Name** | `my-kmart-web` (원하는 이름) |
| **Root Directory** | `frontend` |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |

- **Publish Directory**는 Root가 `frontend`일 때 `frontend` 기준이므로 `dist`만 적으면 됩니다.

### 2-3. 환경 변수 (필수)

**Environment**에서 다음 하나만 추가하면 됩니다.

| Key | Value |
|-----|--------|
| `VITE_API_URL` | 1단계에서 복사한 백엔드 URL (예: `https://my-kmart-api.onrender.com`) |

- 반드시 **https**로, 끝에 **슬래시(/) 없이** 입력합니다.

### 2-4. 배포

- **Create Static Site** 클릭
- 빌드가 끝나면 **사이트 URL**이 생성됩니다.  
  예: `https://my-kmart-web.onrender.com`

### 2-5. 동작 확인

- 위 URL로 접속해서 앱이 뜨는지 확인
- 영수증 촬영 → 분석이 되면 API 연동이 정상입니다.

---

## 3단계: (선택) 커스텀 도메인·자동 배포

- **Custom Domain**: Static Site 또는 Web Service 설정에서 **Custom Domains**로 본인 도메인 연결 가능
- **자동 배포**: GitHub에 푸시하면 Render가 자동으로 다시 빌드·배포합니다 (기본 동작).

---

## 트러블슈팅

| 현상 | 확인할 것 |
|------|------------|
| 백엔드 빌드 실패 | Root Directory가 `backend`인지, Start Command에 `$PORT` 사용했는지 |
| 프론트 빌드 실패 | Root Directory가 `frontend`인지, Build Command에 `npm run build` 포함했는지 |
| 프론트에서 API 호출 실패 | `VITE_API_URL`이 백엔드 URL과 일치하는지, CORS(백엔드는 현재 `*` 허용) |
| 502 / 서버 응답 없음 | 백엔드 무료 플랜 슬립 모드 → 첫 요청 시 30초~1분 정도 걸릴 수 있음 |

---

## 요약 체크리스트

- [ ] 백엔드: Root `backend`, Start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] 백엔드 환경 변수: `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`
- [ ] 백엔드 URL 복사 (끝에 `/` 없이)
- [ ] 프론트: Root `frontend`, Publish `dist`, Build `npm install && npm run build`
- [ ] 프론트 환경 변수: `VITE_API_URL` = 백엔드 URL

이 순서대로 하면 Render에서 프론트·백엔드·DB(Supabase) 구성을 그대로 사용할 수 있습니다.
