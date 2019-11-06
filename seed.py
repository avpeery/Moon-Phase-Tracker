
from sqlalchemy import func
from model import User, Moon_Phase, Alert, connect_to_db, db
from server import app

from datetime import datetime
from skyfield import api, almanac
import itertools

def load_moon_phases():
    ts = api.load.timescale(builtin=True)
    e = api.load('de421.bsp')

    t0 = ts.utc(2000, 1, 1)
    t1 = ts.utc(2000, 12, 31)
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(e))

    dates = t.utc_iso()
    moon_phases = [almanac.MOON_PHASES[yi] for yi in y]

    for (date, moon_phase) in zip(dates, moon_phases):
        date = date[:10]
        date = datetime.strptime(date, "%Y-%m-%d")
        moon_phase = Moon_Phase(name = moon_phase, start_date = date)         
        db.session.add(moon_phase)

    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()

    load_moon_phases()
