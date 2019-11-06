"""Models and database functions for Moon Phase Tracker project"""
from flask_sqlalchemy import SQLAlchemy  
from datetime import datetime

#initialize SQL Alchemy object
db = SQLAlchemy()



class User(db.Model):
    """User of Moon Phase Tracker Web App"""

    __tablename__ = "users"

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

    def __repr__(self):

        return f"<User user_id={self.user_id} email={self.email}>"


class Moon_Phase(db.Model):
    """Moon Phase of Moon Phase Tracker Web App"""

    __tablename__ = "moon_phases"

    moon_phase_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64))
    start_date = db.Column(db.DateTime)

    def __repr__(self):

        return f"<Moon_Phase moon_phase_id={self.moon_phase_id} name={self.name}>"


class Alert(db.Model):

    __tablename__ = "alerts"

    alert_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    moon_phase_id = db.Column(db.Integer, db.ForeignKey('moon_phases.moon_phase_id'))
    alert_type = db.Column(db.String(64))

    user = db.relationship("User", backref=db.backref("alerts"))
    moon_phase = db.relationship("Moon_Phase", backref=db.backref("alerts"))

    def __repr__(self):

        return f"<Alert alert_id={self.alert_id} user_id={self.user_id} moon_phase_id={self.moon_phase_id}>"

def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///moon_phases'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True

    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # to work with interactively

    from server import app
    connect_to_db(app)
    print("Connected to DB.")






