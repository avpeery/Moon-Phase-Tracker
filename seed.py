
from sqlalchemy import func
from model import User, MoonPhaseType, MoonPhaseOccurence, FullMoonNickname, Alert, connect_to_db, db
from server import app

from datetime import datetime
from skyfield import api, almanac
import itertools

MOON_PHASE_TYPES = ["New Moon", "First Quarter", "Full Moon", "Last Quarter"]
FULL_MOON_NICKNAMES = ["Wolf Moon", "Snow Moon", "Worm Moon", "Pink Moon", "Flower Moon", "Strawberry Moon", "Buck Moon", "Sturgeon Moon", "Corn Moon", "Hunter's Moon", "Beaver Moon", "Cold Moon"]

#Add in for blue moons (if two full moons occur in one month, latest is a blue moon)and harvest moon (full moon closest to the autumn solistice - either Sept or Oct)

def load_moon_phase_types():
    """adds moon phase types to moon phase types table"""
    for moon_phase in MOON_PHASE_TYPES:
        moon_phase_type = MoonPhaseType(title=moon_phase)
        db.session.add(moon_phase_type)

    db.session.commit

def load_full_moon_nicknames():
    """adds full moon nicknames to moon phase nicknames table"""
    for (nickname, month) in zip(FULL_MOON_NICKNAMES, range(1, 13)):
        full_moon_nickname = FullMoonNickname(title=nickname, nickname_month=month)
        db.session.add(full_moon_nickname)

    db.session.commit

def load_moon_phase_occurences():
    """adds specific moon phase occurences from file to moon phase occurences table"""
    ts = api.load.timescale(builtin=True)
    e = api.load('de421.bsp')

    t0 = ts.utc(2000, 1, 1)
    t1 = ts.utc(2050, 12, 31)
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(e))

    dates = t.utc_iso()
    moon_phase_names = [almanac.MOON_PHASES[yi] for yi in y]

    for (date, moon_phase_name) in zip(dates, moon_phase_names):

        date = date.replace("Z", "UTC")
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%Z")

        moon_phase_type = MoonPhaseType.query.filter(MoonPhaseType.title == moon_phase_name).first()

        if moon_phase_type.title == "Full Moon":
            full_moon_nickname = FullMoonNickname.query.filter(FullMoonNickname.nickname_month == date.month).first()

            moon_phase_occurence = MoonPhaseOccurence(start_date = date, moon_phase_type_id = moon_phase_type.moon_phase_type_id, full_moon_nickname_id = full_moon_nickname.full_moon_nickname_id)
        else:
            moon_phase_occurence = MoonPhaseOccurence(start_date = date, moon_phase_type_id = moon_phase_type.moon_phase_type_id)         
        
        db.session.add(moon_phase_occurence)

    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()
    load_moon_phase_types()
    load_full_moon_nicknames()
    load_moon_phase_occurences()
    
