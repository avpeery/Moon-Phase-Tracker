
from jinja2 import StrictUndefined
import os
from flask import (Flask, jsonify, url_for, render_template, redirect, request, flash, session)
import json
from flask_debugtoolbar import DebugToolbarExtension
from apiclient.discovery import build
import googleapiclient.discovery
import google.oauth2.credentials
import google_auth_oauthlib.flow
import httplib2
from model import User, MoonPhaseOccurence, MoonPhaseType, Solstice, Alert, FullMoonNickname, connect_to_db, db
from lookup_phone import *
import itertools
from helpers import *

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

app = Flask(__name__)
app.secret_key = "ABC"
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage"""

    return render_template('homepage.html')


@app.route('/authorize')
def authorize():
    """Get google oauth for google calendar"""

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = 'http://me.mydomain.com:5000/oauth2callback'

    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  flow.redirect_uri = 'http://me.mydomain.com:5000/oauth2callback'

  authorization_response = request.url
  flow.fetch_token(authorization_response=authorization_response)

  credentials = flow.credentials
  session['credentials'] = credentials_to_dict(credentials)

  flash("Succesfully logged in to Google Calendar! Try adding again.")
  return redirect("/calendar")


@app.route('/add-to-calendar', methods=['GET'])
def make_calendar_event():
    if 'credentials' not in session:
        return redirect('/authorize')

    session['moon_phase_title'] = request.args['title']
    session['moon_phase_date'] = request.args['date']

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    drive = googleapiclient.discovery.build(
      "calendar", API_VERSION, credentials=credentials)

    session['event'] = create_google_calendar_event(session['moon_phase_title'], session['moon_phase_date'])

    event_to_add = drive.events().insert(calendarId='primary', sendNotifications=True, body=session['event']).execute()

    del session['moon_phase_title']
    del session['moon_phase_date']

    flash("Event added to calendar!")
    return redirect("/calendar")


@app.route('/get-moon-phases.json')
def get_moon_phases_from_database():
    """Gets moon phase occurences from database and turns into json object"""

    all_moon_phase_occurences = MoonPhaseOccurence.query.all()
    all_seasonal_solstices = Solstice.query.all()
    list_of_dict_items =[]

    for row in all_moon_phase_occurences:
        start_date = row.start.isoformat()
        if row.full_moon_nickname_id != None:
            list_of_dict_items.append({'id': row.moon_phase_occurence_id, 'title': row.moon_phase_type.title, 'start': start_date})
            list_of_dict_items.append({'id': row.moon_phase_occurence_id, 'title': row.full_moon_nickname.title, 'start': start_date})
        else:
            list_of_dict_items.append({'id': row.moon_phase_occurence_id, 'title': row.moon_phase_type.title, 'start': start_date})

    for row in all_seasonal_solstices:
        start_date = row.start.isoformat()
        list_of_dict_items.append({'id': row.solstice_id, 'title': row.title, 'start': start_date})
 
    return jsonify(list_of_dict_items)


@app.route("/register", methods= ["POST"])
def register_user():
    """Gets post request from homepage sign up, and continues with registration html"""

    email, password = form_get_request("email", "password")

    if User.query.filter_by(email = email).first():
        flash("Account with that email already exists!")
        return redirect("/")

    session['email'] = email
    session['password'] = password

    all_moon_phase_types = MoonPhaseType.query.all()
    all_full_moon_nicknames = FullMoonNickname.query.all()

    return render_template("registration.html", moon_phase_types=all_moon_phase_types, full_moon_nicknames=all_full_moon_nicknames)


@app.route("/process-registration", methods = ["POST"])
def register_to_database():
    fname, lname, phone = form_get_request('fname', 'lname', 'phone')

    moon_phase_types, full_moon_nicknames = form_get_list('moon_phases', 'full_moon_nicknames')

    phone = lookup_phone_number(phone)
    if phone == False:
        flash("Not a valid phone number!")
        return redirect("/")

    email = session["email"]
    password = session["password"]

    user = User(fname=fname, lname=lname, phone= phone, email = email, password = password)

    db.session.add(user)

    user_moon_phase_types = set(moon_phase_types)
    user_full_moon_nicknames = set(full_moon_nicknames)

    all_moon_phase_types = MoonPhaseType.query.all()
    all_full_moon_nicknames = FullMoonNickname.query.all()

    for moon_phase_type in all_moon_phase_types:

        if moon_phase_type.title in user_moon_phase_types:
            moon_phase_alert = Alert(user_id = user.user_id, moon_phase_type_id = moon_phase_type.moon_phase_type_id, is_active=True)
            db.session.add(moon_phase_alert)

        else:
            moon_phase_alert = Alert(user_id = user.user_id, moon_phase_type_id = moon_phase_type.moon_phase_type_id, is_active=False)
            db.session.add(moon_phase_alert)

    for full_moon_nickname in all_full_moon_nicknames:

        if full_moon_nickname.title in user_full_moon_nicknames:
            full_moon_alert = Alert(user_id = user.user_id, full_moon_nickname_id = full_moon_nickname.full_moon_nickname_id, is_active=True)
            db.session.add(full_moon_alert)
        
        else:
            full_moon_alert = Alert(user_id = user.user_id, full_moon_nickname_id = full_moon_nickname.full_moon_nickname_id, is_active=False)
            db.session.add(full_moon_alert)

    db.session.commit()

    return redirect("/calendar")


@app.route("/login", methods=['POST'])
def login_process():
    """Gets post request from login, and adds to session"""

    email, password = form_get_request("email", "password")

    user = User.query.filter((User.email == email), (User.password == password)).first()

    if user: 
        session['email'] = user.email

        flash("Succesfully logged in!")
        return redirect("/calendar")

    flash("That is not a valid email and/or password.")

    return redirect('/')


@app.route("/calendar")
def show_calendar():
    """Displays calendar of moon phases"""

    return render_template("calendar.html")


@app.route("/display-settings")
def user_settings():
    """Displays user's settings"""

    email = session['email']
    user = User.query.filter_by(email = email).first()

    moon_phase_type_alerts = set()
    full_moon_nickname_alerts = set()

    all_moon_phase_types = MoonPhaseType.query.all()
    all_full_moon_nicknames = FullMoonNickname.query.all()

    for alert in user.alerts:

        if alert.is_active == True and alert.moon_phase_type_id != None:
            moon_phase_type_alerts.add(alert.moon_phase_type_id)

        elif alert.is_active == True and alert.full_moon_nickname_id != None:
            full_moon_nickname_alerts.add(alert.full_moon_nickname_id)

    return render_template("settings.html", user = user, moon_phases = all_moon_phase_types, full_moon_nicknames = all_full_moon_nicknames, moon_phase_type_alerts = moon_phase_type_alerts, full_moon_nickname_alerts = full_moon_nickname_alerts)


@app.route("/change-settings", methods=['POST'])
def  change_settings():
    """Gets post requests from change-settings and updates database"""

    fname, lname, phone, email = form_get_request('fname', 'lname', 'phone', 'email')
    new_moon_phases, new_full_moon_nicknames = form_get_list('moon_phases', 'full_moon_nicknames')

    new_moon_phases = set(new_moon_phases)
    new_full_moon_nicknames = set(new_full_moon_nicknames)

    email = session['email']
    user = User.query.filter_by(email = email).first()

    user.fname = fname
    user.lname = lname
    user.phone = phone
    user.email = email
  
    for user.alert in user.alerts:
        if str(user.alert.moon_phase_type_id) in new_moon_phases:
            user.alert.is_active = True
  
        elif str(user.alert.full_moon_nickname_id) in new_full_moon_nicknames:
            user.alert.is_active = True

        elif str(user.alert.moon_phase_type_id) not in new_moon_phases:
            user.alert.is_active = False 

        elif str(user.alert.full_moon_nickname_id) not in new_full_moon_nicknames:
            user.alert.is_active = False
        
    db.session.commit()
    return redirect("/display-settings")


@app.route("/logout")
def logout_user():
    """Logs user out of session"""

    if 'credentials' in session:
        del session['credentials']

    del session['email']
    flash('Succesfully logged out!')

    return redirect('/')


if __name__ == "__main__":

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.debug = True

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')