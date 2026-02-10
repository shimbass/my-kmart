# Vercel 배포 가이드

이 프로젝트는 **프론트엔드(React)** 와 **백엔드(FastAPI)** 가 분리되어 있습니다.

- **Vercel**: 프론트엔드(React + Vite) 배포에 적합
- **백엔드(FastAPI)**: Vercel은 장기 실행 서버를 지원하지 않으므로 **별도 서비스**에 배포해야 함

---

## 1. 전체 구조

```
[사용자] → Vercel(프론트) → 별도 호스팅(백엔드 API)
```

1. **백엔드**를 먼저 Render / Railway 등에 배포하고 URL을 확보
2. **프론트엔드**를 Vercel에 배포할 때 그 URL을 환경 변수로 설정

---

## 2. 백엔드 배포 (선행 작업)

FastAPI는 Vercel의 서버리스와 방식이 달라서, 아래 중 하나에 배포하는 것을 권장합니다.

### 옵션 A: Render (무료 티어)

1. [render.com](https://render.com) 가입 후 **New → Web Service**
2. GitHub 저장소 연결 후 설정:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` 추가
3. 배포 후 **서비스 URL** 확인 (예: `https://my-kmart-api.onrender.com`)

### 옵션 B: Railway

1. [railway.app](https://railway.app) 가입 후 새 프로젝트
2. GitHub 연동 후 `backend` 폴더 기준 배포, 환경 변수 설정
3. 생성된 URL 확인

백엔드 URL을 **끝에 슬래시 없이** 적어두세요. (예: `https://my-kmart-api.onrender.com`)

---

## 3. 프론트엔드 Vercel 배포

### 3-1. GitHub에 코드 푸시

```bash
cd /Users/shimmac/Documents/vibecoding-master/Study-01/my-kmart
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/본인계정/my-kmart.git
git branch -M main
git push -u origin main
```

### 3-2. Vercel에서 프로젝트 가져오기

1. [vercel.com](https://vercel.com) 로그인 (GitHub 연동 권장)
2. **Add New… → Project**
3. GitHub 저장소 **my-kmart** 선택 후 **Import**

### 3-3. 빌드 설정

| 설정 항목 | 값 |
|-----------|-----|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` (반드시 지정) |
| **Build Command** | `npm run build` (기본값 유지) |
| **Output Directory** | `dist` (기본값 유지) |
| **Install Command** | `npm install` (기본값 유지) |

**Root Directory**를 `frontend`로 두지 않으면 루트에서 `npm run build`가 실행되어 실패합니다.

### 3-4. 환경 변수 (필수)

**Environment Variables**에 다음을 추가합니다.

| Name | Value | 비고 |
|------|--------|------|
| `VITE_API_URL` | `https://여기에-백엔드-URL` | Render 등에서 받은 백엔드 주소, 끝에 `/` 없이 |

예: 백엔드가 `https://my-kmart-api.onrender.com` 이면  
`VITE_API_URL` = `https://my-kmart-api.onrender.com`

### 3-5. 배포

**Deploy** 클릭 후 빌드가 끝나면 프론트엔드 URL이 생성됩니다.

---

## 4. CORS (백엔드 설정)

백엔드가 이미 `allow_origins=["*"]` 로 되어 있으면, Vercel 도메인에서 오는 요청도 허용됩니다.  
나중에 특정 도메인만 허용하려면 배포된 프론트 URL로 제한할 수 있습니다.

```python
# backend/app/main.py 예시 (선택)
allow_origins=[
    "https://my-kmart.vercel.app",
    "http://localhost:5173"
]
```

---

## 5. 체크리스트

- [ ] 백엔드를 Render / Railway 등에 배포하고 URL 확보
- [ ] 백엔드 환경 변수: `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` 설정
- [ ] Vercel 프로젝트 **Root Directory** = `frontend`
- [ ] Vercel 환경 변수 **VITE_API_URL** = 백엔드 URL (끝에 `/` 없이)
- [ ] 배포 후 브라우저에서 API 호출이 되는지 확인 (개발자 도구 Network)

---

## 6. 트러블슈팅

| 현상 | 확인 사항 |
|------|------------|
| 빌드 실패 | Root Directory가 `frontend`인지 확인 |
| API 호출 404 / CORS 에러 | `VITE_API_URL`이 맞는지, 백엔드가 떠 있는지 확인 |
| 이미지 분석 실패 | 백엔드의 `GEMINI_API_KEY`, Render 등 서비스가 슬립 모드에서 깨어났는지 확인 |

무료 플랜에서는 일정 시간 미사용 시 백엔드가 슬립 모드로 들어갈 수 있어, 첫 요청이 느릴 수 있습니다.
