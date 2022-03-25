from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


from fichier import app


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbdir/test.db?check_same_thread=False'

db = SQLAlchemy(app)
db_session = db.session()

Base = db.Model



