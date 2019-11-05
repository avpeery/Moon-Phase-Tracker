"""Models and database functions for Moon Phase Tracker project"""
from flask_sqlalchemy import SQLAlchemy  

#initialize SQL Alchemy object
db = SQLAlhemy()



class User(db.Model):
    """User of Moon Phase Tracker Web App"""
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(64), nullable = True)
    lname = db.Column(db.String(64), nullable = True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(64))
    phone = db.Column(db.String(64))

    new_moon = db.Column(db.Boolean(False))
    first_quarter = db.Column(db.Boolean(False))
    last_quarter = db.Column(db.Boolean(False))
    full_moon = db.Column(db.Boolean(False))

class 