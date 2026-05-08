# SSO-with-ADFS

참조 Demo: [https://github.com/SAML-Toolkits/python-saml](https://github.com/SAML-Toolkits/python-saml)


## Flask 앱 구성

```powershell
# Flask SAML Service Provider Structure

root/
└── app.py (Main Application)
    ├── ⚙️ 1. Initialization & Helpers
    │   ├── init_saml_auth(req)          # SAML 인증 객체 생성 (Config 로드)
    │   └── prepare_flask_request(req)   # Flask 요청을 SAML 라이브러리 규격으로 변환
    │
    ├── 🛣️ 2. Endpoint Routes (Controller)
    │   ├── index()                      # 메인 라우터 (파라미터별 분기 처리)
    │   │   ├── ?sso                     # [Login] IdP로 인증 요청 시작
    │   │   ├── ?acs                     # [ACS] IdP 응답 검증 및 세션 생성
    │   │   ├── ?slo                     # [Logout] IdP에 로그아웃 요청 전송
    │   │   └── ?sls                     # [SLS] 로그아웃 완료 처리 및 세션 삭제
    │   │
    │   ├── attrs()                      # 사용자 세션 속성 정보(Claims) 표시
    │   └── metadata()                   # SP 메타데이터(XML) 생성 (IdP 등록용)
    │
    └── 🚀 3. Execution
        └── main                         # 8123번 포트 웹 서버 구동
```