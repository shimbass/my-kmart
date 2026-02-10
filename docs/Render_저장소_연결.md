# Render에 GitHub 저장소 연결하는 법

저장소: **https://github.com/shimbass/my-kmart**

---

## 1. Render 로그인 및 GitHub 연동

1. [https://dashboard.render.com](https://dashboard.render.com) 접속
2. **Sign in** 또는 **Get started** 클릭
3. **Continue with GitHub** 선택
4. GitHub 로그인 후, Render가 저장소에 접근할 수 있도록 **Authorize** 허용  
   - 처음이면 "Install Render" 또는 "Grant access"로 **shimbass** 계정(또는 해당 조직) 선택 후 저장소 접근 허용

---

## 2. 백엔드(Web Service) 연결

1. Render 대시보드에서 **New +** 버튼 클릭
2. **Web Service** 선택
3. **Connect a repository** 아래에서:
   - **GitHub**가 연결되어 있으면 저장소 목록이 보임
   - **my-kmart** 찾아서 오른쪽 **Connect** 클릭
4. 연결되면 설정 화면으로 넘어감 → 여기서 **Root Directory**: `backend` 등 입력 (이후 단계는 `배포_절차_처음부터.md` 3단계 참고)

**저장소가 안 보일 때**

- **Configure account** 또는 **Configure GitHub** 클릭
- Repository access에서 **All repositories** 또는 **Only select repositories**에서 **my-kmart** 추가
- 저장 후 다시 **New +** → **Web Service** → 저장소 목록에서 **my-kmart** 선택

---

## 3. 프론트엔드(Static Site) 연결

1. Render 대시보드에서 다시 **New +** 버튼 클릭
2. **Static Site** 선택
3. 같은 저장소 **my-kmart** 선택 후 **Connect** 클릭
4. 설정 화면에서 **Root Directory**: `frontend` 등 입력 (이후 단계는 `배포_절차_처음부터.md` 4단계 참고)

---

## 요약

| 할 일 | 위치 |
|--------|------|
| GitHub로 로그인 | Render 로그인 시 **Continue with GitHub** |
| 저장소 권한 허용 | GitHub에서 Render 앱에 **my-kmart** 접근 허용 |
| 백엔드 연결 | New + → **Web Service** → **my-kmart** → Connect |
| 프론트 연결 | New + → **Static Site** → **my-kmart** → Connect |

**같은 저장소(my-kmart)를 백엔드용 Web Service, 프론트용 Static Site 두 번 연결**하면 됩니다. 각 서비스에서 **Root Directory**만 `backend` / `frontend` 로 다르게 설정하면 됩니다.
