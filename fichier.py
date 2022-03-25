# AS simeple as possbile flask google oAuth 2.0

from flask import Flask, redirect, url_for, session

from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
from datetime import date
from datetime import datetime

# decorator for routes that should be accessible only by logged in users

from auth_decorator import login_required, bar_required



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

app.secret_key = os.getenv("APP_SECRET_KEY")


app.config['SESSION_COOKIE_NAME'] = 'google-login-session'

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)


# oAuth Setup

oauth = OAuth(app)


#database

from database import db

from database import db_session


from models import *


db.create_all()


def is_accessible_admin():
        

        if("user" in session and session["user"] is not None):

            u = db_session.query(User).filter_by(openid=session["user"]["openid"]).first()
            

            if(u is not None):

                return u.openid == "107461719254711187198" or u.admin == 1

        return False


def is_accessible_bar():
        if("user" in session and session["user"] is not None):

            u = db_session.query(User).filter_by(openid=session["user"]["openid"]).first()
            

            if(u is not None):

                return u.openid == "107461719254711187198" or u.admin == 1

        return False

class myBaseView(AdminIndexView):

    def is_accessible(self):

        return is_accessible_admin()
    

    def inaccessible_callback(self, name, **kwargs):

            return redirect("/")









#admin.add_view(myBaseView())



class BaseModelView(ModelView):

    column_display_pk = True
    

    def is_accessible(self):

        return is_accessible_admin()


    def inaccessible_callback(self, name, **kwargs):

        return redirect("/")



class hasScannedModel(BaseModelView):

    column_list = (has_scanned.user_id, has_scanned.code_id, has_scanned.date )
    


class commandeChocolatModel(BaseModelView):

    column_list = column_list = (commandeChocolat.commande_id, commandeChocolat.chocolat_id, commandeChocolat.user_id, commandeChocolat.date_commande, commandeChocolat.servit, commandeChocolat.date_servit, commandeChocolat.nom, commandeChocolat.prenom)
    
    



class barBaseView(AdminIndexView):
        def is_accessible(self):
            return is_accessible_bar()
    

        def inaccessible_callback(self, name, **kwargs):
            return redirect("/")
        
        
class BarBaseModelView(BaseModelView):
    can_edit = False

class BarCommandeChocolat(BarBaseModelView):
    
    column_list = (commandeChocolat.commande_id, commandeChocolat.chocolat_id, commandeChocolat.user_id, commandeChocolat.date_commande, commandeChocolat.servit, commandeChocolat.date_servit, commandeChocolat.nom, commandeChocolat.prenom)
    can_create = False
    
    


admin = Admin(app, index_view=myBaseView())

admin_bar = Admin(app, index_view = barBaseView(endpoint="bar", url='/bar'))



admin_bar.add_view(BarCommandeChocolat(commandeChocolat, db_session, endpoint="barCommande"))

admin.add_view(BaseModelView(User, db_session))

admin.add_view(BaseModelView(Code, db_session))

admin.add_view(BaseModelView(Chocolat, db_session))

admin.add_view(hasScannedModel(has_scanned, db_session))

admin.add_view(commandeChocolatModel(commandeChocolat, db_session))


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


@app.route('/t')
@bar_required
def t():
    return "aaa"


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
    return redirect('/')
    
        
    
    



@app.route('/authorize')

def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    user_info = resp.json()
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


@app.route('/validerCommande/<int:commandeId>')
@bar_required
def validerCommande(commandeId):
    c = db_session.query(commandeChocolat).filter_by(commande_id=commandeId).first()
    if(c is None):
        return redirect('/')
    else:
        if(c.servit == False):
            c.date_servit = datetime.now()
            c.servit = True
            db_session.commit()
        return redirect('/')
    


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

import json

@app.route('/commandes')
@bar_required
def commandes():
    l = []
    coms = db_session.query(commandeChocolat).filter_by(servit=False)
    for cc in coms:
        d = {}
        d["id_commande"] = cc.commande_id
        d["date_commande"] = cc.date_commande
        choc = {}
        choc["id"] = cc.chocolat_id
        choc["name"] = cc.chocolat
        d["chocolat"] = choc
        ut = {}
        ut["email"] = cc.mail
        ut["nom"] = cc.nom
        ut["prenom"] = cc.prenom
        d["utilisateur"] = ut
        l.append(d)
    return json.dumps(l)
    
        
    