from twilio.rest import Client
import os
import flask
from flask_sqlalchemy import SQLAlchemy 
import schedule
from datetime import date, timedelta
import time
from server import app
from model import *

ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']

def write_text(user, moon_phase_title):
    """Returns string for user's text message"""
    return f"""Good afternoon { user }. There will be a { moon_phase_title } tonight. Enjoy! 🌝"""


def find_tonights_moon():
    """Returns tonight's moon phase if exists in database"""
    today = date.today()

    moon_phase_tonight = MoonPhaseOccurence.query.filter(MoonPhaseOccurence.start_date == today).first()

    return moon_phase_tonight


def check_alerts(tonights_moon):
    """Returns list of alerts for current moon phase"""
    if tonights_moon != None:

        alerts = Alert.query.filter(Alert.moon_phase_type_id == tonights_moon.moon_phase_type.moon_phase_type_id).all()

        return alerts
    else:
        return None


def send_text():
    """Sends text alerts to user subscribers for current moon phase"""
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    tonights_moon_phase = find_tonights_moon()
    alerts = check_alerts(tonights_moon_phase)

    if alerts != None: 
        for alert in alerts:

            if alert.is_active == True:
                
                text = write_text(alert.user.fname, tonights_moon_phase.moon_phase_type.title)
                phone = alert.user.phone
                message = client.messages.create(body=text, from_=TWILIO_NUMBER, to=phone)
            else:
                pass
    else:
        return None


schedule.every().day.at("18:00").do(send_text)



if __name__ == "__main__":
    
    connect_to_db(app)
    app.debug=True
    while True: 
        schedule.run_pending() 
        time.sleep(1) 




