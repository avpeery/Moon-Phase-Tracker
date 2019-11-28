from sqlalchemy import func
from model import *
from server import app

from datetime import datetime
from skyfield import api, almanac
import itertools

TS = api.load.timescale(builtin=True)
E = api.load('seed_files/de421.bsp')


def test_data():
    test_moon_phase_type()
    test_full_moon_nickname()
    test_solstices()
    test_moon_phase_occurences()
    test_user()


##################################
### TEST DATA HELPER FUNCTIONS ###
##################################


def test_moon_phase_type():
    """Creates Full Moon moon phase type for testing"""

    moon_phase_type = MoonPhaseType(title="Full Moon", emoji="🌝")
    db.session.add(moon_phase_type)
    db.session.commit()


def test_full_moon_nickname():
    """Creates a full moon nickname for testing"""

    full_moon_nickname = FullMoonNickname(title="Wolf Moon", nickname_month= 1)
    db.session.add(full_moon_nickname)
    db.session.commit()


def test_solstices():
    """Creates seasonal solstices in test database"""

    t0 = TS.utc(2020, 1, 1)
    t1 = TS.utc(2020, 12, 31)
    t, y = almanac.find_discrete(t0, t1, almanac.seasons(E))

    dates = t.utc_iso()
    solstice_names = [almanac.SEASON_EVENTS[yi] for yi in y]

    for (date, solstice_name) in zip(dates, solstice_names):
        date = date[:10]
        date = datetime.strptime(date, "%Y-%m-%d")

        solstice_occurence = Solstice(title = solstice_name, start = date)      
        
        db.session.add(solstice_occurence)

    db.session.commit()


def test_moon_phase_occurences():
    """Creates moon phase occurences in test database"""

    t0 = TS.utc(2020, 1, 1)
    t1 = TS.utc(2020, 12, 31)
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(E))

    dates = t.utc_iso()
    moon_phase_names = [almanac.MOON_PHASES[yi] for yi in y]

    moon_phase_type = MoonPhaseType.query.first()
    full_moon_nickname = FullMoonNickname.query.first()

    for (date, moon_phase_name) in zip(dates, moon_phase_names):
        if moon_phase_name == "Full Moon":
            date = date[:10]
            date = datetime.strptime(date, "%Y-%m-%d")
            if date.month == 1:
                moon_phase_occurence = MoonPhaseOccurence(start = date, moon_phase_type_id = moon_phase_type.moon_phase_type_id, full_moon_nickname_id = full_moon_nickname.full_moon_nickname_id)
            else:
                moon_phase_occurence = MoonPhaseOccurence(start = date, moon_phase_type_id = moon_phase_type.moon_phase_type_id)
            db.session.add(moon_phase_occurence)

    db.session.commit()


def test_user():
    """Creates test user in test database"""

    test_user = User(fname = 'Sally', lname = 'Sample', email = 'sample@sample.com', password = 'password', phone = '+14147913665')
    db.session.add(test_user)
    db.session.commit()




 

