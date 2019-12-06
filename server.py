
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
from urllib.parse import parse_qs
from model import *
from twilio_lookup_phone import *
import itertools
from helpers import *

CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

app = Flask(__name__)
app.secret_key = 'ABC'
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Displays homepage"""

    return render_template('homepage.html')


@app.route('/authorize')
def authorize():
    """Asks user for authorization to google calendar account"""

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = 'http://me.mydomain.com:5000/oauth2callback'

    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    """Processes response for google calendar authorization"""

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = 'http://me.mydomain.com:5000/oauth2callback'

    authorization_response = request.url

    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    session['credentials'] = credentials_to_dict(credentials)

    flash('Succesfully logged in to Google Calendar! Try adding again.')

    return redirect('/calendar')


@app.route('/add-to-calendar', methods=['GET'])
def make_calendar_event():
    """Adds moon phase event to user's google calendar with OAUTH"""

    if 'credentials' not in session:
        return redirect('/authorize')

    session['moon_phase_title'] = request.args['title']
    session['moon_phase_date'] = request.args['date']

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    drive = googleapiclient.discovery.build(
      'calendar', API_VERSION, credentials=credentials)

    session['event'] = create_google_calendar_event(session['moon_phase_title'], session['moon_phase_date'])

    event_to_add = drive.events().insert(calendarId='primary', sendNotifications=True, body=session['event']).execute()

    flash('Event added to calendar!')

    return redirect('/calendar')


@app.route('/get-moon-phases.json')
def get_moon_phases_from_database():
    """Gets moon phase occurences from database and turns into json object"""

    all_moon_phase_occurences = MoonPhaseOccurence.query.all()
    all_seasonal_solstices = Solstice.query.all()

    list_of_moon_phase_dict_items =[]

    list_of_moon_phase_dict_items = append_moon_phase_occurences(list_of_moon_phase_dict_items, all_moon_phase_occurences)

    list_of_all_dict_items = append_seasonal_solstices(list_of_moon_phase_dict_items, all_seasonal_solstices)
 
    return jsonify(list_of_all_dict_items)


@app.route('/register', methods= ['POST'])
def register_user():
    """Gets post request from sign-up form on homepage, and continues with registration.html"""

    email, password = form_get_request('email', 'password')

    if User.query.filter_by(email = email).first():
        flash('Account with that email already exists!')
        return redirect('/')

    session['email'] = email
    session['password'] = password

    all_moon_phase_types = MoonPhaseType.query.all()
    all_full_moon_nicknames = FullMoonNickname.query.all()

    return render_template('registration.html', moon_phase_types=all_moon_phase_types, full_moon_nicknames=all_full_moon_nicknames)


@app.route('/process-registration', methods = ['POST'])
def register_to_database():
    """Receives post request from registration.html, and adds new user/alerts to database"""

    fname, lname, phone = form_get_request('fname', 'lname', 'phone')

    moon_phase_types, full_moon_nicknames = form_get_list('moon_phases', 'full_moon_nicknames')

    phone = lookup_phone_number(phone)

    if phone == False:
        flash('Not a valid phone number!')
        return redirect('/')

    user = User(fname=fname, lname=lname, phone= phone, email = session['email'], password = session['password'])

    db.session.add(user)

    user_moon_phase_types = set(moon_phase_types)
    user_full_moon_nicknames = set(full_moon_nicknames)

    set_new_alerts_for_user(user_moon_phase_types, user_full_moon_nicknames, user)

    db.session.commit()

    session['fname'] = fname

    flash('Signed up successfully!')

    return redirect('/calendar')


@app.route('/login', methods=['POST'])
def login_process():
    """Gets post request from login, and adds to session"""

    email, password = form_get_request('email', 'password')

    user = User.query.filter((User.email == email), (User.password == password)).first()

    if user: 

        session['email'] = user.email
        session['fname'] = user.fname

        flash('Succesfully logged in!')

        return redirect('/calendar')

    flash('That is not a valid email and/or password.')

    return redirect('/')


@app.route('/calendar')
def show_calendar():
    """Displays calendar of moon phases"""

    return render_template('calendar.html')


@app.route('/display-settings')
def user_settings():
    """Displays user's settings"""

    email = session['email']

    user = User.query.filter_by(email = email).first()

    moon_phase_type_alerts = set()
    full_moon_nickname_alets = set()

    all_moon_phase_types = MoonPhaseType.query.all()
    all_full_moon_nicknames = FullMoonNickname.query.all()

    moon_phase_type_alerts, full_moon_nickname_alerts = add_active_alerts_to_sets(user, all_moon_phase_types, all_full_moon_nicknames)

    return render_template('settings.html', user=user, moon_phases=all_moon_phase_types, full_moon_nicknames=all_full_moon_nicknames, moon_phase_type_alerts=moon_phase_type_alerts, full_moon_nickname_alerts=full_moon_nickname_alerts)


@app.route('/change-settings.json', methods=['GET'])
def  change_settings():
    """Receives AJAX request from change-settings.html, and updates database"""

    data = request.args.get("data")

    data_dict = parse_qs(data)

    email = session['email']
    user = User.query.filter_by(email = email).first()

    new_phone = lookup_phone_number(data_dict['phone'][0])

    user.fname, user.lname, user.phone, user.email = data_dict['fname'][0], data_dict['lname'][0], new_phone, data_dict['email'][0]

    session['email'] = email

    new_full_moon_nicknames = []
    new_moon_phases = []

    if 'full_moon_nickname_choices' in data_dict:
        for number in data_dict['full_moon_nickname_choices']:
            new_full_moon_nicknames.append(int(number))

    if 'moon_phase_choices' in data_dict:
        for number in data_dict['moon_phase_choices']:
            new_moon_phases.append(int(number))

    change_alerts_for_user(user, new_moon_phases, new_full_moon_nicknames)

    db.session.commit()

    return jsonify(data_dict)

@app.route('/logout')
def logout_user():
    """Logs user out of session"""

    if 'credentials' in session or 'fname' in session:
        del session['credentials']
        del session['fname']

    del session['email']

    flash('Succesfully logged out!')

    return redirect('/')


if __name__ == '__main__':

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.debug = False

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')