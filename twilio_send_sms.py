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


def write_moon_phase_text(user, moon_phase_title, moon_emoji):
    """Returns string for user's text message"""

    #Text for moon phase type alert
    return f"""Good afternoon { user }. There will be a { moon_phase_title } tonight. Enjoy! {moon_emoji}"""


def write_full_moon_nickname_text(user, full_moon_nickname_title):
    """Returns string for user's text message"""

    #Text for moon phase full moon nickname alert
    return f"""Good afternoon { user }. There will be a { full_moon_nickname_title } tonight. Enjoy!"""


def find_tonights_moon():
    """Returns tonight's moon phase or full moon nickname if exists in database"""

    #Moon phase events occur after midnight
    #Alert should be looking for tomorrow's moon phase (to send text for †hat evening)
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    #Query for moon phase occurence that occurs tomorrow
    moon_phase_tonight = MoonPhaseOccurence.query.filter(MoonPhaseOccurence.start == tomorrow).first()
    
    return moon_phase_tonight


def check_alerts(tonights_moon):
    """Returns list of alerts for current moon phase"""

    #check if a moon phase type exists
    if tonights_moon:

        #filter all alerts for both moon phase types or full moon nicknames matching tonight's moon result
        alerts = Alert.query.filter(or_(Alert.moon_phase_type_id == tonights_moon.moon_phase_type_id, Alert.full_moon_nickname_id == tonights_moon.full_moon_nickname_id)).all()
        
        return alerts

    else:

        return None


def send_text():
    """Sends text alerts to user subscribers for current moon phase"""

    #establish twilio client to send text
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    #store tonight's moon object
    tonights_moon_phase = find_tonights_moon()

    #store alerts matching tonight's moon moon phase type or full moon nickname 
    alerts = check_alerts(tonights_moon_phase)

    #alerts exist
    if alerts: 

        for alert in alerts:

            #if alert has a moon phase type and is set to active
            if alert.moon_phase_type_id and alert.is_active == True:  
                
                #create and send moon phase type text
                text = write_moon_phase_text(alert.user.fname, tonights_moon_phase.moon_phase_type.title, tonights_moon_phase.moon_phase_type.emoji)
                phone = alert.user.phone
                message = client.messages.create(body=text, from_=TWILIO_NUMBER, to=phone)

            #if alert has full moon nickname, and is set to active
            if alert.full_moon_nickname_id and alert.is_active == True:

                #create and send full moon nickname text
                text = write_full_moon_nickname_text(alert.user.fname, tonights_moon_phase.full_moon_nickname.title)
                phone = alert.user.phone
                message = client.messages.create(body=text, from_=TWILIO_NUMBER, to=phone)

    else:

        #No texts are sent - no moon phase type
        return None


schedule.every().day.at('18:00').do(send_text)


if __name__ == '__main__':
    connect_to_db(app)
    schedule.run_pending()
    time.sleep(1)





