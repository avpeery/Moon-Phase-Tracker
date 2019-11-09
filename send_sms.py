from twilio.rest import Client
import os
import flask
import flask.ext.sqlalchemy
import schedule
import datetime
from model import *


def write_text(user, moon_phase_title):

    return f"""Good morning { user }. There will be a { moon_phase_title } tonight. Enjoy!"""

def send_text():
    now = datetime.datetime.now()
    client = Client(account_sid, auth_token)
    moon_phase_now = MoonPhaseOccurence.query.filter(MoonPhaseOccurence.start_date == now).one()

    alerts = Alert.query.filter(Alert.moon_phase_type.id == moon_phase_now.moon_phase_type.id).all()

    for alert in alerts:
        if alert.is_active == True:
            text = write_text(alert.user.fname, moon_phase_now.moon_phase_type.title)
            phone = alert.user.phone
            message = client.messages
                    .create(
                         body=text,
                         from_=twilio_number,
                         to=phone
                     )

    return schedule.CancelJob

schedule.every().day.at('10:00').do(send_text)

