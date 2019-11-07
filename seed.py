
from sqlalchemy import func
from model import User, MoonPhaseType, MoonPhaseOccurence, Alert, connect_to_db, db
from server import app

from datetime import datetime
from skyfield import api, almanac
import itertools

MOON_PHASE_TYPES = ['New Moon', 'First Quarter', 'Full Moon', 'Last Quarter']

def load_moon_phase_types():
    """adds moon phase types to moon phase types table"""
    for moon_phase in MOON_PHASE_TYPES:
        moon_phase_type = MoonPhaseType(title=moon_phase)
        db.session.add(moon_phase_type)

    db.session.commit

def load_moon_phase_occurences():
    """adds specific moon phase occurences from file to moon phase occurences table"""
    ts = api.load.timescale(builtin=True)
    e = api.load('de421.bsp')

    t0 = ts.utc(2000, 1, 1)
    t1 = ts.utc(2000, 12, 31)
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(e))

    dates = t.utc_iso()
    moon_phase_names = [almanac.MOON_PHASES[yi] for yi in y]

    for (date, moon_phase_name) in zip(dates, moon_phase_names):
        date = date[:10]
        date = datetime.strptime(date, "%Y-%m-%d")
        moon_phase_type = MoonPhaseType.query.filter(MoonPhaseType.title == moon_phase_name).first()

        moon_phase_occurence = MoonPhaseOccurence(start_date = date, moon_phase_type_id = moon_phase_type.moon_phase_type_id)         
        db.session.add(moon_phase_occurence)

    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()
    load_moon_phase_types()
    load_moon_phase_occurences()
    
