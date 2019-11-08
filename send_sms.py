from twilio.rest import Client
import os
import flask
import flask.ext.sqlalchemy
import threading
import time
import schedule

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_NUMBER']



def write_text(user, moon_phase_title):
    return f"""Good morning { user }. There will be a { moon_phase_title } tonight. Enjoy!"""

def send_text(phone):
    client = Client(account_sid, auth_token)
    text = write_text()
    message = client.messages
                    .create(
                         body=text,
                         from_=twilio_number,
                         to=phone
                     )
    return schedule.CancelJob

def schedule_text(moon_phase_occurence.start_date):
    schedule.every().day.at('22:30').do(send_text)

