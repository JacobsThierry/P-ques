# AS simeple as possbile flask google oAuth 2.0

from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
from datetime import date
from datetime import datetime
# decorator for routes that should be accessible only by logged in users
from auth_decorator import login_required, bar_required, admin_required
from flask_admin import Admin
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView
import json
# dotenv setup

from dotenv import load_dotenv

load_dotenv()

# App config
app = Flask(__name__)

url = "paques2022.telecomnancy.net"

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


class BaseModelView(ModelView):
    column_display_pk = True
    page_size = 500
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

@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["2000 per day", "200 per hour"]
)


@app.route('/code/<codeValue>')
@limiter.limit("5 per minute")
@login_required
def code(codeValue):
    c = db_session.query(Code).filter_by(value=codeValue).first()
    if not c:
        return redirect('/')
    
    s_user_id =session["user"]["openid"]
    q1 = db_session.query(has_scanned).filter_by(user_id=s_user_id).filter_by(code_id=c.id)
    if q1.count() == 0:
        hs = has_scanned()
        hs.user_id = s_user_id
        hs.code_id = c.id
        hs.date = datetime.now()
        db_session.add(hs)
        
        u = db_session.query(User).filter_by(openid=s_user_id).first()
        u.points += c.points
        
        print(u.points)
        print(c.value)
        
        db_session.commit()
    return redirect('/')
    

@app.route('/myCommande') 
@login_required
def myCommande():
    s_user_id =session["user"]["openid"]
    l = []
    c = db_session.query(commandeChocolat).filter_by(user_id=s_user_id)
    for cc in c:
        l.append(c)
    return redirect("/") #TODO : faire une liste des commandes
        
    
@app.route('/commande/<int:choo>') 
@login_required
def newCommande(choo):
    s_user_id =session["user"]["openid"]
    c = db_session.query(Chocolat).filter_by(chocolat_id=choo).first()    
    if c is None:
        return redirect("/") #Todo : rediriger vers un écran de confirmation
    u = db_session.query(User).filter_by(openid=s_user_id).first()
    if(u.points < c.chocolat_price):
        return redirect("/")
    cc = commandeChocolat()
    cc.chocolat_id = choo
    cc.user_id = s_user_id
    cc.date_commande = datetime.now()
    cc.servit = False
    cc.date_servit = None
    u.points -= c.chocolat_price
    db_session.add(cc)
    db_session.commit()
    
    return redirect("/")


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


@app.route('/commandes')
@bar_required
def commandes():
    l = []
    coms = db_session.query(commandeChocolat).filter_by(servit=False)
    for cc in coms:
        d = {}
        d["id_commande"] = cc.commande_id
        d["date_commande"] = str(cc.date_commande)
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
    
        
import qrcode
from PIL import Image, ImageDraw, ImageFont
import math
import cv2
from zipfile import ZipFile
import os
from os.path import basename
from flask import send_file

from os import listdir
from os.path import isfile, join

@app.route('/qrCodes')
@admin_required
def getGRCode():
           
    
    codes = db_session.query(Code)
    
    for code in codes:
        make_qr_code(code.value)
        
    
    zipObj = ZipFile('sampleDir.zip', 'w') 
    
    mypath = "out"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    
    for f in onlyfiles:
        zipObj.write("out//" + f)
    
    zipObj.close()
    
    return send_file("sampleDir.zip", as_attachment=True)



compteur_qr = 0

def make_qr_code(data):
    logo_display = Image.open('cul.png')
    
    data = url + "/" + data
    
    bg = Image.open('background.jpg')
    bg = bg.crop((0,0,900,900))
    
    
    logo_display.thumbnail((60, 60))
    
    qr = qrcode.QRCode(
        error_correction=qrcode.ERROR_CORRECT_H,
        border=0 ,
        box_size=16
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    logo_pos = ((img.size[0] - logo_display.size[0]) // 2, (img.size[1] - logo_display.size[1]) // 2)
    
    
    img.paste(logo_display, logo_pos)
    logo_pos = ((bg.size[0] - img.size[0]) // 2, ((bg.size[1] - img.size[1]) // 2) - 50)
    bg.paste(img,logo_pos)
    
    
    
    box_shape = ((112,760), (786,862) )
    
    bgdraw = ImageDraw.Draw(bg)  
    bgdraw.rectangle(box_shape, fill ="#FFFFFF", outline ="#000000")
    
    fnt = ImageFont.truetype("arial.ttf", 26)
    
    w, h = bgdraw.textsize(data, fnt)
    
    W, H = bg.size
    
     
    
    bgdraw.text(((W-w)/2,790), data, font=fnt, fill=(0, 0, 0, 255))
    global compteur_qr
    compteur_qr +=1
    
    bg.save("out/" + str(compteur_qr) + ".png")
    