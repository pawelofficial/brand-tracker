from flask import Flask, render_template,redirect, url_for, request, session
from flask_session import Session
import identity
import identity.web
import app_config
import logging 

logging.basicConfig(level=logging.INFO,filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.log(logging.INFO, 'This is a log message.')

def llog(s = None,**kwargs):
    logging.log(logging.INFO, s)
    for k,v in kwargs.items():
        logging.log(logging.INFO, f'\n{k}={v}')


app = Flask(__name__)
app.config.from_object(app_config)
Session(app)
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


auth = identity.web.Auth(
    session=session,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)


def set_user_in_session():
    user = auth.get_user()
    session['user'] = user
    
def identity_auth_uri():
    return  auth.log_in(scopes=app_config.SCOPE,redirect_uri=url_for("auth_response", _external=True))
        
    

@app.route(app_config.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    set_user_in_session()
    return redirect(url_for("index"))


@app.route("/")
def index():
    llog(session=session)
    user = session.get('user', 'guest')
    if user =='guest':
        user_name = 'guest'
    else:
        user_name = user['preferred_username']
    
    if not (app.config["CLIENT_ID"] and app.config["CLIENT_SECRET"]):
        llog(s='missing client id or secret',client_id=app.config["CLIENT_ID"],client_secret=app.config["CLIENT_SECRET"])
        return render_template('config_error.html')
    return render_template('index.html'
                           ,user=user_name
                           ,auth_uri=identity_auth_uri()['auth_uri']
                           ,version=identity.__version__)


    
@app.route("/login")
def login():
    auth_uri = identity_auth_uri()['auth_uri']
    return redirect(auth_uri)
    
@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
    
    


###password reset is implemented in azure susi already 
###@app.route("/profile")
###def profile():    
###    return render_template('profile.html')
###
###@app.route("/change_password")
###def change_password():    
###    user = session.get('user', {'name': 'guest'})
###    user_name = user['name']
###    if user_name == 'guest':
###        return redirect(url_for("profile"))
###    
###    b2c_reset_password_authority = app.config["B2C_RESET_PASSWORD_AUTHORITY"]
###    client_id = app.config["CLIENT_ID"]
###    password_reset_url = f"{b2c_reset_password_authority}?client_id={client_id}"
###    print(password_reset_url)   
###    # azure: https://pzwebappdev.b2clogin.com/pzwebappdev.onmicrosoft.com/oauth2/v2.0/authorize?p=B2C_1_susi_pwd_reset&client_id=8bd7729a-2ad1-48cf-a3c0-8c4f24e7c21a&nonce=defaultNonce&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2FgetAToken&scope=openid&response_type=code&prompt=login
###    # this: https://pzwebappdev.b2clogin.com/pzwebappdev.onmicrosoft.com/B2C_1_susi_pwd_reset?client_id=8bd7729a-2ad1-48cf-a3c0-8c4f24e7c21a
###    return redirect(password_reset_url) # incorrect url 
