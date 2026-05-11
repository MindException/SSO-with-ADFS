# SSO-with-ADFS
간단한 Application을 구현하여 ADFS에서 SAML과 OAuth의 동작 방식에 대해 기록합니다.

## 환경 구조

### 1. SP

IIS와 Flask를 웹서버와 WAS 형태로 구현하였습니다.

* `CN`: app.flask.com
* `Domain`: flask.com
* `SAN`: *.flask.com , flask.com  

### 2. IDP (ADFS)
해당 케이스의 IDP 예시는 ADFS만 해당됩니다. 

* `CN`: sts.LSHCorp.com
* `Domain`: LSHCorp.com
* `SAN`: *.LSHCorp.com , LSHCorp.com , *.sts.LSHCorp.com