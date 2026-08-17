# CGV 용산 IMAX '오디세이' 예매 오픈 알림

8/26 이후 날짜의 예매가 열리는지 10분마다 자동으로 확인하고,
새로 열리면 이메일로 알려주는 봇입니다. (GitHub Actions로 24시간 무료 실행)

## 설정 방법 (5분이면 끝나요)

### 1. GitHub 저장소 만들기
1. github.com 에서 새 저장소(New repository)를 만드세요. (Private 로 설정 추천)
2. 이 폴더 안의 파일들(`cgv_watch.py`, `state.json`, `requirements.txt`,
   `.github/workflows/watch.yml`)을 그 저장소에 그대로 업로드/푸시하세요.

### 2. Gmail 앱 비밀번호 발급받기
일반 Gmail 비밀번호는 사용할 수 없고, "앱 비밀번호"라는 별도의 16자리 코드가 필요합니다.

1. Google 계정 관리(myaccount.google.com) 접속
2. 왼쪽 메뉴 "보안" 클릭
3. "2단계 인증"이 꺼져 있다면 먼저 켜야 합니다 (필수 조건)
4. 2단계 인증 활성화 후, 보안 페이지에서 "앱 비밀번호" 검색 → 새로 생성
5. 이름은 아무거나 (예: "cgv-watch") 입력 후 생성 → 16자리 코드가 나오면 복사해두기

### 3. GitHub 저장소에 Secrets 등록하기
저장소 페이지에서 `Settings` → `Secrets and variables` → `Actions` → `New repository secret`
으로 아래 3개를 등록하세요.

| Secret 이름 | 값 |
|---|---|
| `GMAIL_ADDRESS` | 본인 Gmail 주소 (예: myaddr@gmail.com) |
| `GMAIL_APP_PASSWORD` | 위에서 발급받은 16자리 앱 비밀번호 (띄어쓰기 없이) |
| `TO_EMAIL` | 알림 받을 이메일 주소 (본인과 같아도 됨) |

### 4. 켜기
Secrets 등록이 끝나면 자동으로 10분마다 실행됩니다.
저장소의 `Actions` 탭에서 "CGV 오디세이 IMAX 예매 오픈 감시" 워크플로우가
돌고 있는지 확인할 수 있어요. `Run workflow` 버튼으로 지금 바로 한 번
수동 실행해서 정상 작동하는지 테스트해볼 수도 있습니다.

## 커스터마이징

`cgv_watch.py` 상단의 설정값들을 바꾸면 됩니다.

- `START_DATE`: 확인을 시작할 날짜 (기본값 2026-08-26)
- `WATCH_DAYS`: START_DATE로부터 며칠치를 확인할지 (기본값 14일)
- `MOV_NO`: 다른 영화로 바꾸고 싶으면 CGV 예매 페이지에서 같은 방식으로
  Request URL 안의 `movNo` 값을 찾아서 교체하면 됩니다.
- `SITE_NO`: 다른 극장으로 바꾸고 싶으면 마찬가지로 `siteNo` 값을 교체.

## 참고

- CGV의 비공식(문서화되지 않은) API를 사용하므로, CGV 쪽에서 API 구조를
  바꾸면 스크립트가 멈출 수 있습니다. 그럴 땐 다시 개발자도구로 새 요청을
  캡처해서 알려주시면 코드를 맞춰드릴게요.
- 요청 주기를 10분보다 훨씬 짧게 (예: 초 단위) 바꾸는 건 CGV 서버에서
  IP가 차단될 위험이 있어 권장하지 않습니다.
