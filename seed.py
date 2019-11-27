
from sqlalchemy import func
from model import User, MoonPhaseType, MoonPhaseOccurence, Solstice, FullMoonNickname, Alert, connect_to_db, db
from server import app

from datetime import datetime
from skyfield import api, almanac
import itertools

MOON_PHASE_TYPES = ["New Moon", "First Quarter", "Full Moon", "Last Quarter"]
FULL_MOON_NICKNAMES = ["Wolf Moon", "Snow Moon", "Worm Moon", "Pink Moon", "Flower Moon", "Strawberry Moon", "Buck Moon", "Sturgeon Moon", "Corn Moon", "Hunter's Moon", "Beaver Moon", "Cold Moon"]
MOON_EMOJIS = ["🌚","🌛", "🌝","🌜"]
TS = api.load.timescale(builtin=True)
E = api.load('seed_files/de421.bsp')


def load_moon_phase_types():
    """adds moon phase types to moon phase types table"""

    for moon_phase, moon_emoji in zip(MOON_PHASE_TYPES, MOON_EMOJIS):
        moon_phase_type = MoonPhaseType(title=moon_phase, emoji=moon_emoji)
        db.session.add(moon_phase_type)

    db.session.commit

def load_full_moon_nicknames():
    """adds full moon nicknames to moon phase nicknames table"""

    for (nickname, month) in zip(FULL_MOON_NICKNAMES, range(1, 13)):
        full_moon_nickname = FullMoonNickname(title=nickname, nickname_month=month)
        db.session.add(full_moon_nickname)

    db.session.commit

def load_solstices():
    """uses skyfield library to calculate season solstices, and add to database"""

    t0 = TS.utc(2000, 1, 1)
    t1 = TS.utc(2050, 12, 31)
    t, y = almanac.find_discrete(t0, t1, almanac.seasons(E))

    dates = t.utc_iso()
    solstice_names = [almanac.SEASON_EVENTS[yi] for yi in y]

    for (date, solstice_name) in zip(dates, solstice_names):
        date = date[:10]
        date = datetime.strptime(date, "%Y-%m-%d")

        solstice_occurence = Solstice(title = solstice_name, start = date)      
        
        db.session.add(solstice_occurence)

    db.session.commit()


def load_moon_phase_occurences():
    """adds specific moon phase occurences from file to moon phase occurences table"""

    t0 = TS.utc(2000, 1, 1)
    t1 = TS.utc(2050, 12, 31)
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(E))

    dates = t.utc_iso()
    moon_phase_names = [almanac.MOON_PHASES[yi] for yi in y]

    for (date, moon_phase_name) in zip(dates, moon_phase_names):
        date = date[:10]
        date = datetime.strptime(date, "%Y-%m-%d")

        moon_phase_type = MoonPhaseType.query.filter(MoonPhaseType.title == moon_phase_name).first()

        if moon_phase_type.title == "Full Moon":
            full_moon_nickname = FullMoonNickname.query.filter(FullMoonNickname.nickname_month == date.month).first()

            moon_phase_occurence = MoonPhaseOccurence(start = date, moon_phase_type_id = moon_phase_type.moon_phase_type_id, full_moon_nickname_id = full_moon_nickname.full_moon_nickname_id)
        else:
            moon_phase_occurence = MoonPhaseOccurence(start = date, moon_phase_type_id = moon_phase_type.moon_phase_type_id)         
        
        db.session.add(moon_phase_occurence)

    db.session.commit()


def load_blue_moon():
    """Adds Blue Moon to FullMoonNickname"""

    blue_moon = FullMoonNickname(title="Blue Moon")
    db.session.add(blue_moon)
    db.session.commit()


def load_harvest_moon():
    """Adds Harvest Moon to FullMoonNickname"""
    harvest_moon = FullMoonNickname(title="Harvest Moon")
    db.session.add(harvest_moon)
    db.session.commit()


def updates_full_moon_nickname_for_full_moon_occurences_to_blue_moon():
    """Checks to see if full phase occurence is a blue moon and updates database"""

    full_moon = MoonPhaseType.query.filter(MoonPhaseType.title == "Full Moon").first()
    blue_moon_nickname = FullMoonNickname.query.filter(FullMoonNickname.title == "Blue Moon").first()

    for idx, full_moon_occurence in enumerate(full_moon.moon_phase_occurences):
        if idx+1 < len(full_moon.moon_phase_occurences):
            if full_moon_occurence.start.month == full_moon.moon_phase_occurences[idx+1].start.month:
                full_moon.moon_phase_occurences[idx+1].full_moon_nickname_id = blue_moon_nickname.full_moon_nickname_id

    db.session.commit()


def updates_full_moon_nickname_for_full_moon_occurences_to_harvest_moon():
    """Checks to see if full phase occurence is a harvest moon and updates database"""

    harvest_moon = FullMoonNickname.query.filter(FullMoonNickname.title == "Harvest Moon").first()
    autumn_equinoxes = Solstice.query.filter(Solstice.title == "Autumnal Equinox").all()
    full_moon = MoonPhaseType.query.filter(MoonPhaseType.title == "Full Moon").first()

    for autumn_equinox in autumn_equinoxes:

        this_years_full_moons = [full_moon_occurence for full_moon_occurence in full_moon.moon_phase_occurences if full_moon_occurence.start.year == autumn_equinox.start.year]
        full_moon_dates = [this_years_full_moon.start for this_years_full_moon in this_years_full_moons] 
        
        closest_full_moon_date = min(full_moon_dates, key=lambda x: abs(x - autumn_equinox.start))
        closest_full_moon = MoonPhaseOccurence.query.filter(MoonPhaseOccurence.start == closest_full_moon_date).first()
        closest_full_moon.full_moon_nickname_id = harvest_moon.full_moon_nickname_id

    db.session.commit()
    

if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()
    load_moon_phase_types()
    load_full_moon_nicknames()
    load_moon_phase_occurences()
    load_solstices()
    load_blue_moon()
    load_harvest_moon()

    updates_full_moon_nickname_for_full_moon_occurences_to_blue_moon() #updating existing full_moon_nicknames_to_blue_moon - find_and_update_for_blue_moons #resource links in the code #testing #s
    updates_full_moon_nickname_for_full_moon_occurences_to_harvest_moon()

    
