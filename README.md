# Yin Candle Trading Dashboard (음봉타법 대시보드)

이 저장소는 유튜브에서 검증된 주식 매매 기법인 **"음봉타법"** 조건에 맞는 한국 주식을 찾아주는 파이썬 자동 스캔 대시보드입니다.

## 🚀 배포 방법 (Streamlit Community Cloud 무료 배포)

이 대시보드를 인터넷에 영구적인 주소로 무료 배포하려면 아래 순서를 따라주세요. (Vercel 대신 이 방식이 파이썬 데이터 앱에 가장 적합합니다!)

### 1단계: GitHub에 코드 올리기
1. 컴퓨터에 [Git](https://git-scm.com/)을 설치하고 GitHub.com에 가입합니다.
2. 터미널을 열고 터미널(VS Code 등)에서 현재 폴더로 이동한 뒤 아래 명령어를 입력합니다.
   ```bash
   git init
   git add .
   git commit -m "첫 번째 버전 업로드"
   ```
3. GitHub.com에 접속해 "New repository"를 클릭하여 새 저장소를 만듭니다.
4. 만들어진 저장소의 안내에 따라 리모트(remote)를 연결하고 코드를 push 합니다.
   ```bash
   git branch -M main
   git remote add origin https://github.com/자신의아이디/저장소이름.git
   git push -u origin main
   ```

### 2단계: Streamlit Cloud 연결하기
1. [Streamlit Community Cloud](https://share.streamlit.io/)에 접속하여 GitHub 계정으로 로그인합니다.
2. **"New app"** 버튼을 클릭합니다.
3. 방금 만든 GitHub 저장소(Repository)를 선택하고 대시보드 파일인 `app.py`를 메인 파일 경로에 입력합니다.
4. **"Deploy!"** 버튼을 누르면 끝입니다! 이제 전 세계 어디서든 스마트폰이나 다른 컴퓨터로도 나만의 주식 스캐너에 접속할 수 있습니다.

## 💡 실행 시 화면 테마 팁
Streamlit 우측 상단의 [ ⋮ ] 버튼을 눌러 **Settings -> Theme**를 "Use system setting"이나 "Dark"로 두시면 제가 커스텀한 예쁜 다크모드 디자인을 100% 즐기실 수 있습니다.
