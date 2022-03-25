from flask_sqlalchemy import SQLAlchemy


import json
from sqlalchemy_mixins import AllFeaturesMixin
from flask_admin.contrib.sqla import ModelView

from database import Base, db

from flask_admin.model import BaseModelView



class User(Base, AllFeaturesMixin):
    __tablename__ = 'users'
    openid = db.Column(db.String(255), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    picture = db.Column(db.String(255))
    nom = db.Column(db.String(255))
    prenom = db.Column(db.String(255))
    
    points = db.Column(db.Integer)
    
    admin = db.Column(db.Boolean())
    bar = db.Column(db.Boolean())
    
    serialize_only = ('openid', 'email', 'picture', 'nom', 'prenom', 'admin', 'bar')
    
    def dict2obj(dict1):
        u = User()
        
        u.openid = dict1["openid"]
        u.email = dict1["email"]
        u.picture = dict1["picture"]
        u.nom = dict1["nom"]
        u.prenom = dict1["prenom"]
        return u
    
class Code(Base, AllFeaturesMixin):
    __tablename__ = "code"
    
    id = db.Column(db.String(255), primary_key = True)
    value = db.Column(db.String(255), unique=True)
    points = db.Column(db.Integer)


class has_scanned(Base, AllFeaturesMixin):
    __tablename__ = "has_scanned"
    user_id = db.Column(db.String(255), db.ForeignKey('users.openid'), primary_key=True)
    code_id = db.Column(db.String(255), db.ForeignKey('code.id'), primary_key=True)
    date = db.Column(db.DateTime(timezone=True))
    
    
    