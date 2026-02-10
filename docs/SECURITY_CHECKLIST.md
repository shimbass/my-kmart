# GitHub 업로드 전 보안 점검 요약

## ✅ 점검 결과 (안전한 항목)

| 항목 | 상태 | 설명 |
|------|------|------|
| **API 키·비밀값** | ✅ 안전 | `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`는 모두 `os.getenv()`로만 읽음. 코드에 하드코딩 없음. |
| **.env 파일** | ✅ 제외됨 | 루트 `.gitignore`에 `.env`, `backend/.env`, `**/.env` 포함 → 커밋 대상 아님. |
| **.env.example** | ✅ 안전 | `backend/.env.example`은 플레이스홀더만 포함(예: `your_gemini_api_key_here`). 커밋해도 됨. |
| **venv / node_modules** | ✅ 제외됨 | `venv/`, `node_modules/`가 .gitignore에 있어 업로드되지 않음. |
| **빌드 산출물** | ✅ 제외됨 | `dist/`, `dist-ssr/` 제외. |
| **로컬 설정** | ✅ 제외됨 | `.claude/settings.local.json` 제외. (MCP 설정만 있어 비밀 없음.) |
| **프론트 API 호출** | ✅ 안전 | 프론트는 같은 origin(`''`)으로만 요청 → API 키는 백엔드 .env에만 존재. |

---

## ⚠️ 확인 권장

| 항목 | 권장 조치 |
|------|-----------|
| **RECEIPT_ANALYSIS.md** | 실제 구매 내역(상호명, 카드명, 금액, 상품명)이 들어 있음. **개인 데이터로 보이면** (1) `.gitignore`에 `RECEIPT_ANALYSIS.md` 추가하거나, (2) 샘플 데이터로 치환 후 커밋. |
| **backend/.env** | 절대 커밋하지 말 것. 이미 .gitignore에 있으나, `git add .` 전에 `git status`로 `.env`가 목록에 없는지 한 번 확인 권장. |

---

## 📋 첫 푸시 전 체크리스트

```bash
# 1. 커밋될 파일만 확인 ( .env, venv 등이 없어야 함 )
git status

# 2. backend/.env 가 목록에 있으면 안 됨
git status --short | grep -i env
# → backend/.env 가 나오면 안 됨. .env.example 만 나오면 됨.
```

---

## 🔐 요약

- **비밀키·API 키**: 모두 환경 변수로만 사용, `.env`는 Git 제외 → **업로드 시 유출 위험 없음.**
- **개인 데이터**: `RECEIPT_ANALYSIS.md`만 필요 시 제외 또는 샘플로 교체하면 됨.
