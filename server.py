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
from helpers import *

CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

app = Flask(__name__)
#generate secret key
app.secret_key = os.urandom(32)
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    '''Displays homepage'''

    return render_template('homepage.html')


@app.route('/authorize')
def authorize():
    '''Asks user for authorization to google calendar account'''

    #creates flow instance to manage OAuth grant access
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

    #uri configured in API Google console
    flow.redirect_uri = 'http://me.mydomain.com:5000/oauth2callback'

    #finds authorization url
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    session['state'] = state

    #redirect user through authorization url 
    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    '''Processes response for google calendar authorization'''

    #creates flow instance to manage OAuth grant access
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    
    flow.redirect_uri = 'http://me.mydomain.com:5000/oauth2callback'

    authorization_response = request.url

    #fetch tocken for the authorization response
    flow.fetch_token(authorization_response=authorization_response)

    #credentials stored
    credentials = flow.credentials

    session['credentials'] = credentials_to_dict(credentials)

    flash('Succesfully logged in to Google Calendar! Try adding again.')

    return redirect('/calendar')


@app.route('/add-to-calendar', methods=['GET'])
def make_calendar_event():
    '''Adds moon phase event to user's google calendar with OAUTH'''

    #checks if credentials not already in session
    if 'credentials' not in session:
        return redirect('/authorize')

    #gets information about moon phase type to add to calendar
    session['moon_phase_title'] = request.args['title']
    session['moon_phase_date'] = request.args['date']

    #grabs stored OAuth credentials
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    #client a google api client to make google calendar event
    drive = googleapiclient.discovery.build(
      'calendar', API_VERSION, credentials=credentials)

    #creates google calendar event with session stored moon phase info
    session['event'] = create_google_calendar_event(session['moon_phase_title'], session['moon_phase_date'])

    #adds the calendar event to the google calendar
    event_to_add = drive.events().insert(calendarId='primary', sendNotifications=True, body=session['event']).execute()

    flash('Event added to calendar!')

    return redirect('/calendar')


@app.route('/get-moon-phases.json')
def get_moon_phases_from_database():
    '''Gets moon phase occurences from database and turns into json object'''

    #query for all moon phase occcurence and seasonal solstices
    all_moon_phase_occurences = MoonPhaseOccurence.query.all()
    all_seasonal_solstices = Solstice.query.all()

    list_of_moon_phase_dict_items =[]

    #uses helper function to turn items into dictionary to be jsonified
    list_of_moon_phase_dict_items = append_moon_phase_occurences(list_of_moon_phase_dict_items, all_moon_phase_occurences)
    list_of_all_dict_items = append_seasonal_solstices(list_of_moon_phase_dict_items, all_seasonal_solstices)
 
    return jsonify(list_of_all_dict_items)


@app.route('/register', methods= ['POST'])
def register_user():
    '''Gets post request from sign-up form on homepage, and continues with registration.html'''

    #gets form info for email and password
    email, password = form_get_request('email', 'password')

    #checks if user already exists
    if User.query.filter_by(email = email).first():
        flash('Account with that email already exists!')
        return redirect('/')

    #stores email and password in session to access in another route
    session['email'] = email
    session['password'] = password

    #find all moon phases and full moon nicknames to pass onto frontend form
    all_moon_phase_types = MoonPhaseType.query.all()
    all_full_moon_nicknames = FullMoonNickname.query.all()

    return render_template('registration.html', moon_phase_types=all_moon_phase_types, full_moon_nicknames=all_full_moon_nicknames)


@app.route('/process-registration', methods = ['POST'])
def register_to_database():
    '''Receives post request from registration.html, and adds new user/alerts to database'''

    #uses helper functions to get form information concisely
    fname, lname, phone = form_get_request('fname', 'lname', 'phone')
    moon_phase_types, full_moon_nicknames = form_get_list('moon_phases', 'full_moon_nicknames')

    #validates if phone number is a real number using Twilio
    phone = lookup_phone_number(phone)

    #if phone number is not valid, redirects back to homepage
    if phone == False:
        flash('Not a valid phone number!')
        return redirect('/')

    #creates new user
    user = User(fname=fname, lname=lname, phone=phone, email=session['email'])

    #sets password hash
    user.set_password(session['password'])

    db.session.add(user)

    #updated lists to sets for better runtime in helper function
    user_moon_phase_types = set(moon_phase_types)
    user_full_moon_nicknames = set(full_moon_nicknames)

    #uses helper function to add alert subscriptions for user to database
    set_new_alerts_for_user(user_moon_phase_types, user_full_moon_nicknames, user)

    db.session.commit()

    #stores user first name in session once registration is completed
    session['fname'] = fname

    flash('Signed up successfully!')

    return redirect('/calendar')


@app.route('/login', methods=['POST'])
def login_process():
    '''Gets post request from login, and adds to session'''

    #uses helper functions to get form information concisely
    email, password = form_get_request('email', 'password')

    #finds user with corresponding email
    user = User.query.filter_by(email=email).first()

    #logs in if user exists and user password hash is true
    if user and user.check_password(password): 

        session['email'] = user.email
        session['fname'] = user.fname

        flash('Succesfully logged in!')

        return redirect('/calendar')

    #if login info not correct, user remains on homepage
    flash('That is not a valid email and/or password.')

    return redirect('/')


@app.route('/calendar')
def show_calendar():
    '''Displays calendar of moon phases'''

    return render_template('calendar.html')


@app.route('/display-settings')
def user_settings():
    '''Displays user's settings'''

    #grab email to find current user
    email = session['email']

    user = User.query.filter_by(email=email).first()

    #create empty sets to be used to store user's alerts 
    moon_phase_type_alerts = set()
    full_moon_nickname_alets = set()

    #grabs all moon phase types and full moon nicknames
    all_moon_phase_types = MoonPhaseType.query.all()
    all_full_moon_nicknames = FullMoonNickname.query.all()

    #checks for user's alerts using helper function
    moon_phase_type_alerts, full_moon_nickname_alerts = add_active_alerts_to_sets(user, all_moon_phase_types, all_full_moon_nicknames)

    #passes user information and user alerts to frontend
    return render_template('settings.html', user=user, moon_phases=all_moon_phase_types, full_moon_nicknames=all_full_moon_nicknames, moon_phase_type_alerts=moon_phase_type_alerts, full_moon_nickname_alerts=full_moon_nickname_alerts)


@app.route('/change-settings.json', methods=['GET'])
def change_settings():
    '''Receives AJAX request from change-settings.html, and updates database'''

    #gets data from updated form
    data = request.args.get('data')

    #parses json data into dictionary
    data_dict = parse_qs(data)

    #grab current user
    email = session['email']
    user = User.query.filter_by(email = email).first()

    #checks phone number is real
    new_phone = lookup_phone_number(data_dict['phone'][0])

    #access information from dictionary to update user
    user.fname, user.lname, user.phone, user.email = data_dict['fname'][0], data_dict['lname'][0], new_phone, data_dict['email'][0]

    #update email in session if it has been changed
    session['email'] = email

    new_full_moon_nicknames = []
    new_moon_phases = []

    #makes separate lists of full moon nickname and moon phase types 
    if 'full_moon_nickname_choices' in data_dict:
        for full_moon_nickname_id in data_dict['full_moon_nickname_choices']:
            new_full_moon_nicknames.append(int(full_moon_nickname_id))

    if 'moon_phase_choices' in data_dict:
        for moon_phase_id in data_dict['moon_phase_choices']:
            new_moon_phases.append(int(moon_phase_id))

    #uses helper function to set new alerts
    change_alerts_for_user(user, new_moon_phases, new_full_moon_nicknames)

    db.session.commit()

    #return back the data to display the updated information
    return jsonify(data_dict)


@app.route('/logout')
def logout_user():
    '''Logs user out of session'''

    session.clear()

    flash('Succesfully logged out!')

    return redirect('/')


if __name__ == '__main__':

    #for Google OAuth
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.debug = False

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')