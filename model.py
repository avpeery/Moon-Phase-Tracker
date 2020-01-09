from flask_sqlalchemy import SQLAlchemy  
from datetime import datetime

#Instatiate a SQLAlchemy object
db = SQLAlchemy()


class User(db.Model):
    '''Data model for user'''

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(64), nullable = True)
    lname = db.Column(db.String(64), nullable = True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(64))
    phone = db.Column(db.String(64))

    def __repr__(self):
        '''Returns human readable info about user object'''

        return f'<User user_id={self.user_id} email={self.email}>'

    #hash password functions
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class MoonPhaseType(db.Model):
    '''Data model for moon phase type'''

    __tablename__ = 'moon_phase_types'

    moon_phase_type_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64))
    description = db.Column(db.String(250))
    emoji = db.Column(db.String(20))

    def __repr__(self):
        '''Returns human readable info about moon phase type object'''

        return f'<MoonPhaseType moon_phase_type_id={self.moon_phase_type_id} title={self.title}>'


class FullMoonNickname(db.Model):
    """Data model for  full moon phase nicknames"""

    __tablename__ = 'full_moon_nicknames'

    full_moon_nickname_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64))
    nickname_month = db.Column(db.Integer)
    description = db.Column(db.String(470))

    def __repr__(self):
        '''Returns human readable info about full moon nickname object'''

        return f'<FullMoonNickname full_moon_nickname_id={self.full_moon_nickname_id} title={self.title}>'


class MoonPhaseOccurence(db.Model):
    '''Data model for moon phase occurences'''

    __tablename__ = 'moon_phase_occurences'

    moon_phase_occurence_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    start = db.Column(db.DateTime)
    moon_phase_type_id = db.Column(db.Integer, db.ForeignKey('moon_phase_types.moon_phase_type_id'))
    full_moon_nickname_id = db.Column(db.Integer, db.ForeignKey('full_moon_nicknames.full_moon_nickname_id'))

    moon_phase_type = db.relationship('MoonPhaseType', backref=db.backref('moon_phase_occurences'))
    full_moon_nickname = db.relationship('FullMoonNickname', backref=db.backref('moon_phase_occurences'))

    def __repr__(self):
        '''Returns human readable info about moon phase occurence object'''

        return f'<MoonPhaseOccurence moon_phase_occurence_id={self.moon_phase_occurence_id} moon_phase_type_id ={self.moon_phase_type_id}>'


class Alert(db.Model):
    '''Data model for text alert subscriptions'''

    __tablename__ = 'alerts'

    alert_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    moon_phase_type_id = db.Column(db.Integer, db.ForeignKey('moon_phase_types.moon_phase_type_id'))
    full_moon_nickname_id = db.Column(db.Integer, db.ForeignKey('full_moon_nicknames.full_moon_nickname_id'))
    is_active = db.Column(db.Boolean(False))
    alert_type = db.Column(db.String(64))

    user = db.relationship('User', backref=db.backref('alerts'))
    moon_phase_type = db.relationship('MoonPhaseType', backref=db.backref('alerts'))
    full_moon_nickname = db.relationship('FullMoonNickname', backref=db.backref('alerts'))

    def __repr__(self):
        '''Returns human readable info about alert object'''

        return f'<Alert alert_id={self.alert_id} user_id={self.user_id} moon_phase_type_id={self.moon_phase_type_id}>'


class Solstice(db.Model):
    '''Seasonal solstice and equinox occurences with dates'''

    __tablename__ = 'solstices'

    solstice_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64))
    start = db.Column(db.DateTime)
    
    def __repr__(self):
        '''Returns human readable info about solstice object'''

        return f'<Solstice solstice_id={self.solstice_id} title={self.title}>'


def connect_to_db(app, db_uri = 'postgresql:///moon_phases'):
    '''Connect the database to app'''

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True

    db.app = app
    db.init_app(app)


if __name__ == '__main__':

    from server import app
    connect_to_db(app)
    #for using interactively
    print('Connected to DB.')


