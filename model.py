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

    def __repr__(self):

        return f"<User user_id={self.user_id} email={self.email}>"


class MoonPhaseType(db.Model):
    """Types of Moon Phases"""

    __tablename__ = "moon_phase_types"

    moon_phase_type_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64))
    emoji = db.Column(db.String(20))

    def __repr__(self):

        return f"<MoonPhaseType moon_phase_type_id={self.moon_phase_type_id} title={self.title}>"


class FullMoonNickname(db.Model):
    """Nicknames for full moon phases"""

    __tablename__ = "full_moon_nicknames"

    full_moon_nickname_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64))
    nickname_month = db.Column(db.Integer)

    def __repr__(self):

        return f"<FullMoonNickname full_moon_nickname_id={self.full_moon_nickname_id} title={self.title}>"


class MoonPhaseOccurence(db.Model):
    """Moon Phases with date and time occurences"""

    __tablename__ = "moon_phase_occurences"

    moon_phase_occurence_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    start_date = db.Column(db.DateTime)
    moon_phase_type_id = db.Column(db.Integer, db.ForeignKey('moon_phase_types.moon_phase_type_id'))
    full_moon_nickname_id = db.Column(db.Integer, db.ForeignKey('full_moon_nicknames.full_moon_nickname_id'))

    moon_phase_type = db.relationship("MoonPhaseType", backref=db.backref("moon_phase_occurences"))
    full_moon_nickname = db.relationship("FullMoonNickname", backref=db.backref("moon_phase_occurences"))

    def __repr__(self):

        return f"<MoonPhaseOccurence moon_phase_occurence_id={self.moon_phase_occurence_id} moon_phase_type_id ={self.moon_phase_type_id}>"


class Alert(db.Model):
    """User subscriptions for moon phase text alerts"""

    __tablename__ = "alerts"

    alert_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    moon_phase_type_id = db.Column(db.Integer, db.ForeignKey('moon_phase_types.moon_phase_type_id'))
    full_moon_nickname_id = db.Column(db.Integer, db.ForeignKey('full_moon_nicknames.full_moon_nickname_id'))
    is_active = db.Column(db.Boolean(False))
    alert_type = db.Column(db.String(64))

    user = db.relationship("User", backref=db.backref("alerts"))
    moon_phase_type = db.relationship("MoonPhaseType", backref=db.backref("alerts"))
    full_moon_nickname = db.relationship("FullMoonNickname", backref=db.backref("alerts"))

    def __repr__(self):

        return f"<Alert alert_id={self.alert_id} user_id={self.user_id} moon_phase_type_id={self.moon_phase_type_id}>"


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






