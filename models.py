import imp
import os
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
import json
from dotenv import load_dotenv

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    # db.create_all()


'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to have multiple verisons of a database
'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()
def roll_back():
    db.session.rollback()

# NOTE: remove this after first run


# db_drop_and_create_all()

'''
Greeting
'''


class Greeting(db.Model):
    __tablename__ = 'greetings'

    id = Column(Integer, primary_key=True)
    lang = Column(String)
    greeting = Column(String)

    def __init__(self, lang, greeting):
        self.lang = lang
        self.greeting = greeting
    def update(self):
        db.session.commit()
    def insert(self):
        db.session.add(self)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def format(self):
        return {
            'lang': self.lang,
            'greeting': self.greeting,
        }
