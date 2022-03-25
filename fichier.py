# AS simeple as possbile flask google oAuth 2.0
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
from datetime import date
from datetime import datetime
# decorator for routes that should be accessible only by logged in users
from auth_decorator import login_required


from flask_admin import Admin

from flask_admin import BaseView, expose, AdminIndexView

from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView


# dotenv setup
from dotenv import load_dotenv
load_dotenv()









# App config
app = Flask(__name__)
# Session config
app.secret_key = "a8465zji98rq465trfvygbhjnk56azjiok89r4qg6589qrg465"

app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# oAuth Setup
oauth = OAuth(app)

#database
from database import db
from database import db_session

from models import *

db.create_all()

def is_accessible_glob():
        
        if("user" in session and session["user"] is not None):
            u = db_session.query(User).filter_by(openid=session["user"]["openid"]).first()
            
            if(u is not None):
                return u.openid == "107461719254711187198" or u.admin == 1
        return False


class myBaseView(AdminIndexView):
    def is_accessible(self):
        return is_accessible_glob()
    
    def inaccessible_callback(self, name, **kwargs):
            return redirect("/")


admin = Admin(app, index_view=myBaseView())

#admin.add_view(myBaseView())


class BaseModelView(ModelView):
    column_display_pk = True
    
    def is_accessible(self):
        return is_accessible_glob()

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/")


class hasScannedModel(BaseModelView):
    column_display_pk = True
    column_list = (has_scanned.user_id, has_scanned.code_id, has_scanned.date )
    


admin.add_view(BaseModelView(User, db_session))
admin.add_view(BaseModelView(Code, db_session))
admin.add_view(hasScannedModel(has_scanned, db_session))



google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://oauth2.googleapis.com/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/certs",
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo', 
    client_kwargs={'scope': 'openid email profile'},
     jwks_uri = "https://www.googleapis.com/oauth2/v3/certs",
)


@app.route('/')
@login_required
def hello_world():
    email = dict(session)['user']['email']
    return f'Hello, you are logge in as {email}!'


@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/code/<codeValue>')
@login_required
def code(codeValue):
    c = Code()
    q = db_session.query(Code).filter_by(value=codeValue)
    if(q.count() == 0):
        return redirect('/')

    c = q[0]
    
    s_user_id =session["user"]["openid"]

    
    
    q1 = db_session.query(has_scanned).filter_by(user_id=s_user_id).filter_by(code_id=c.id)
    
    if q1.count() == 0:
        hs = has_scanned()
        hs.user_id = s_user_id
        hs.code_id = c.id
        hs.date = datetime.now()
        db_session.add(hs)
        db_session.commit()
        print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhha")
        
    
    return redirect('/')
    
        
    
    


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    user_info = resp.json()
    #session['email'] = user_info['email']
    
    
    
    # do something with the token and profile
    user = oauth.google.userinfo(token=token) 
    
    q = db_session.query(User).filter_by(openid = user_info['id'])
    if(q.count() > 0):
        u = q[0]
    else:
        u = User()
        u.email = user_info['email']
        u.openid = user_info['id']
        u.picture = user_info['picture']
        u.nom = user_info['family_name']
        u.prenom = user_info['given_name']
        u.admin = 0
        u.bar = 0
        u.points = 0
        if(u.openid == "107461719254711187198"):
            u.admin = 1
            u.bar = 1
        
        db_session.add(u)
        db_session.commit()
    
    
    
    
    session['user'] = u.to_dict()

    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')