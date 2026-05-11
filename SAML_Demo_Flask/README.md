# SSO-with-ADFS

참조 Demo: [https://github.com/SAML-Toolkits/python3-saml](https://github.com/SAML-Toolkits/python3-saml)


## Flask 앱 구성

```powershell
# Flask SAML Service Provider Structure

root/
└── app.py (Main Application)
    ├── ⚙️ 1. Initialization & Helpers
    │   ├── init_saml_auth(req)          # SAML 인증 객체 생성 (custom_base_path 사용)
    │   └── prepare_flask_request(req)   # Flask 환경 변수를 SAML 규격 dict로 매핑
    │
    ├── 🛣️ 2. Endpoint Routes (Controller)
    │   ├── index()                      # 메인 라우터 (Query Parameter 분기)
    │   │   ├── ?sso                     # [Login] auth.login() 호출 (IdP 이동)
    │   │   ├── ?sso2                    # [Login] 특정 ReturnTo(/attrs/) 포함 로그인
    │   │   ├── ?acs                     # [ACS] IdP 응답(Post) 처리 및 세션 저장
    │   │   ├── ?slo                     # [Logout] 세션 정보 포함 로그아웃 요청
    │   │   └── ?sls                     # [SLS] 로그아웃 완료 후 세션 클리어(dscb)
    │   │
    │   ├── attrs()                      # 세션에 저장된 samlUserdata 표시
    │   └── metadata()                   # SP 메타데이터 생성 및 XML 반환 (IdP 등록용)
    │
    └── 🚀 3. Execution
        └── main                         # 0.0.0.0:8000 포트로 Flask 앱 구동
```