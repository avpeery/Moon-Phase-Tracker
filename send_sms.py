from twilio.rest import Client
import os
import flask
from flask_sqlalchemy import SQLAlchemy 
import schedule
import datetime
import time
from model import *


def write_text(user, moon_phase_title):
    """Returns string for user's text message"""
    return f"""Good morning { user }. There will be a { moon_phase_title } tonight. Enjoy!"""


def find_tonights_moon():
    """Returns tonight's moon phase if exists in database"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    moon_phase_tonight = MoonPhaseOccurence.query.filter(MoonPhaseOccurence.start_date == tomorrow).first()

    return moon_phase_tonight


def check_alerts(tonights_moon):
    """Returns list of alerts for current moon phase"""
    if tonights_moon != None:

        alerts = Alert.query.filter(Alert.moon_phase_type.moon_phase_type_id == moon_phase_tonight.moon_phase_type_id).all()

        return alerts


def send_text():
    """Sends text alerts to user subscribers for current moon phase"""
    client = Client(account_sid, auth_token)

    tonights_moon_phase = find_tonights_moon()
    user_alerts = check_alerts(tonights_moon_phase)

    for alert in user_alerts:

        if alert.is_active == True:

            text = write_text(alert.user.fname, tonights_moon_phase.moon_phase_type.title)
            phone = alert.user.phone
            message = client.messages.create(body=text, from_=twilio_number, to=phone)

    return schedule.CancelJob

schedule.every().day.at('10:00').do(send_text)

while True: 
  
    schedule.run_pending() 
    time.sleep(1) 



