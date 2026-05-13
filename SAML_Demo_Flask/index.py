import os

from flask import Flask, request, render_template, redirect, session, make_response
from werkzeug.middleware.proxy_fix import ProxyFix

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils


app = Flask(__name__)
app.config["SECRET_KEY"] = "onelogindemopytoolkit"
app.config["SAML_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saml")

# ADFS의 인증 응답을 처리하는 auth.process_response 과정에서, SAML 응답에 명시된 수신 주소(HTTPS)와 Flask가 실제로 인식한 프로토콜(HTTP) 간의 불일치가 발생합니다. 
# 이를 해결하기 위해 프록시 헤더를 교정하여 두 프로토콜을 일치시켜야 합니다.
# ADFS 인증 응답 시 HTTPS/HTTP 불일치 문제를 WSGI 계층에서 즉시 해결합니다.
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# 추후 임시 삭제 헤더 출력용
# @app.before_request
# def print_headers():
#     print("--- Incoming Headers ---")
#     for header, value in request.headers.items():
#         print(f"{header}: {value}")
#     print("-------------------------")


# 2. flask 객체 생성
def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=app.config["SAML_PATH"])
    return auth

# 1. 요청 분석 및 dict로 반환
def prepare_flask_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    return {

        # 예시: https://app.flask.com/sso
        "https": "on" if request.scheme == "https" else "off", # https://
        "http_host": request.host, # Host: app.flask.com
        "script_name": request.path, # 요청 URL: /sso
        "get_data": request.args.copy(), # 뒤 파라미터: ?id=admin&debug=true
        # ADFS에서 대소문자 문제 있을 때, 아래 활성화 하기 https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        "post_data": request.form.copy(), # post 값

    }


@app.route("/", methods=["GET", "POST"])
def index():
    
    # 3. 요청마다 OneLogin_Saml2_Auth 인증 개체 생성
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    
    # 요청 확인 용
    print("https:  " + req["https"])
    print("http_host:  " + req["http_host"])
    # print("script_name:  " + req["script_name"])  

    errors = []
    error_reason = None
    not_auth_warn = False
    success_slo = False
    attributes = False
    paint_logout = False

    if "sso" in request.args:
        # return redirect(auth.login())
        # If AuthNRequest ID need to be stored in order to later validate it, do instead
        
        # flask 쪽 세션 ID 생성 및 브라우저에게 쿠키 전달
        # 이렇게 하면 쿠키에서 세션 ID를 갖고 있음
        sso_built_url = auth.login()

        # [중요] 생성된 리다이렉트 주소를 직접 찍어서 확인합시다.
        print(f"DEBUG - Generated SSO URL: {sso_built_url}")

        session['AuthNRequestID'] = auth.get_last_request_id()
        return redirect(sso_built_url)

    elif "sso2" in request.args:
        return_to = "%sattrs/" % request.host_url
        return redirect(auth.login(return_to))
    
    
    elif "slo" in request.args:
        name_id = session_index = name_id_format = name_id_nq = name_id_spnq = None
        if "samlNameId" in session:
            name_id = session["samlNameId"]
        if "samlSessionIndex" in session:
            session_index = session["samlSessionIndex"]
        if "samlNameIdFormat" in session:
            name_id_format = session["samlNameIdFormat"]
        
        return redirect(auth.logout(name_id=name_id, session_index=session_index, name_id_format=name_id_format))
    elif "acs" in request.args:
        request_id = None
        if "AuthNRequestID" in session:
            request_id = session["AuthNRequestID"]

        # claim 정보 가져오기
        auth.process_response(request_id=request_id)
        errors = auth.get_errors()
        not_auth_warn = not auth.is_authenticated()
        if len(errors) == 0:
            if "AuthNRequestID" in session:
                del session["AuthNRequestID"]

            session["samlUserdata"] = auth.get_attributes()
            session["samlNameId"] = auth.get_nameid()
            session["samlNameIdFormat"] = auth.get_nameid_format()
            session["samlSessionIndex"] = auth.get_session_index()

            print("claim 정보들")
            print(auth.get_attributes())
            print("NameID")
            print(auth.get_nameid())
            print("NameID 스키마")
            print(auth.get_nameid_format())
            print("로그인 한 세선ID")
            print(auth.get_session_index())


            self_url = OneLogin_Saml2_Utils.get_self_url(req)
            if "RelayState" in request.form and self_url != request.form["RelayState"]:
                # To avoid 'Open Redirect' attacks, before execute the redirection confirm
                # the value of the request.form['RelayState'] is a trusted URL.
                return redirect(auth.redirect_to(request.form["RelayState"]))
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()
    elif "sls" in request.args:
        request_id = None
        if "LogoutRequestID" in session:
            request_id = session["LogoutRequestID"]
        dscb = lambda: session.clear()
        url = auth.process_slo(request_id=request_id, delete_session_cb=dscb)
        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                # To avoid 'Open Redirect' attacks, before execute the redirection confirm
                # the value of the url is a trusted URL.
                return redirect(url)
            else:
                success_slo = True
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()

    if "samlUserdata" in session:
        paint_logout = True
        if len(session["samlUserdata"]) > 0:
            attributes = session["samlUserdata"].items()

    return render_template("index.html", errors=errors, error_reason=error_reason, not_auth_warn=not_auth_warn, success_slo=success_slo, attributes=attributes, paint_logout=paint_logout)


@app.route("/attrs/")
def attrs():
    paint_logout = False
    attributes = False

    if "samlUserdata" in session:
        paint_logout = True
        if len(session["samlUserdata"]) > 0:
            attributes = session["samlUserdata"].items()

    return render_template("attrs.html", paint_logout=paint_logout, attributes=attributes)


@app.route("/metadata/")
def metadata():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers["Content-Type"] = "text/xml"
    else:
        resp = make_response(", ".join(errors), 500)
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8123, debug=True)
