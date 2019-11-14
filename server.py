
from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, MoonPhaseOccurence, MoonPhaseType, Alert, FullMoonNickname, connect_to_db, db

import itertools


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')


@app.route('/register')
def register_user():
    """Dislay registration form"""
    moon_phase_types = MoonPhaseType.query.all()
    full_moon_nicknames = FullMoonNickname.query.all()
    return render_template('registration.html', moon_phase_types=moon_phase_types, full_moon_nicknames=full_moon_nicknames)


@app.route("/register", methods= ["POST"])
def register_process():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    phone = request.form.get('phone')
    email = request.form.get('email')
    password = request.form.get('password')
    moon_phase_types = request.form.getlist('moon_phases')
    full_moon_nicknames = request.form.getlist('full_moon_nicknames')

    if User.query.filter_by(email = email).first():
        flash("Account with that email already exists!")
        return redirect("/register")

    phone = "+1" + phone

    user = User(fname=fname, lname=lname, phone= phone, email = email, password = password)

    db.session.add(user)

    all_moon_phase_types = MoonPhaseType.query.all()
    all_full_moon_nicknames = FullMoonNickname.query.all()

    for moon_phase_type, full_moon_nickname in zip(all_moon_phase_types, all_full_moon_nicknames):
        if moon_phase_type in moon_phase_types:
            
            moon_phase_alert = Alert(user_id = user.user_id, moon_phase_type_id = moon_phase_type.moon_phase_type_id, is_active=True)
            db.session.add(moon_phase_alert)

        elif full_moon_nickname in full_moon_nicknames:

            full_moon_alert = Alert(user_id = user.user_id, full_moon_nickname_id = full_moon_nickname.full_moon_nickname_id, is_active=True)
            db.session.add(full_moon_alert)

        elif moon_phase_type not in moon_phase_types:

            moon_phase_alert = Alert(user_id = user.user_id, moon_phase_type_id = moon_phase_type.moon_phase_type_id, is_active=False)
            db.session.add(moon_phase_alert)
        
        elif full_moon_nickname not in full_moon_nicknames:

            full_moon_alert = Alert(user_id = user.user_id, full_moon_nickname_id = full_moon_nickname.full_moon_nickname_id, is_active=False)
            db.session.add(full_moon_alert)

    db.session.commit()

    return redirect("/")


@app.route('/login')
def login_user():
    return render_template('login.html')


@app.route("/login", methods=['POST'])
def login_process():

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter((User.email == email), (User.password == password)).first()

    if user: 
        session['email'] = user.email

        flash("Succesfully logged in!")
        return redirect("/")

    flash("That is not a valid email and password")
    return redirect('/login')

@app.route("/display-settings")
def user_settings():
    email = session['email']
    user = User.query.filter(User.email == email).first()
    moon_phases = MoonPhaseType.query.all()
    full_moon_nicknames = FullMoonNickname.query.all()

    user_moon_alerts = []
    for alert in user.alerts:
        if alert.is_active == True:
            user_moon_alerts.append(alert.moon_phase_type_id)
            user_moon_alerts.append(alert.full_moon_nickname_id)


    return render_template("settings.html", user = user, moon_phases = moon_phases, full_moon_nicknames = full_moon_nicknames, user_moon_alerts = user_moon_alerts)

@app.route("/change-settings", methods=['POST'])
def  change_settings():
    first_name = request.form.get('fname')
    last_name = request.form.get('lname')
    new_phone = request.form.get('phone')
    new_email = request.form.get('email')
    new_moon_phases = request.form.getlist('moon_phases')
    new_full_moon_nicknames = request.form.getlist("full_moon_nicknames")

    email = session['email']
    user = User.query.filter(User.email == email).first()
    moon_phase_types = MoonPhaseType.query.all()
    full_moon_nicknames = FullMoonNickname.query.all()

    user.fname = first_name
    user.lname = last_name
    user.phone = new_phone
    user.email = new_email
  
    for moon_phase_type, alert in zip(moon_phase_types, user.alerts):
        if moon_phase_type.title in new_moon_phases:
            alert.is_active = True
            db.session.commit()
        else: 
            alert.is_active = False 
            db.session.commit()
  
        elif full_moon_nickname.title in new_full_moon_nicknames:
            alert.is_active = True
            db.session.commit()
    for full_moon_nickname, alert in zip(full_moon_nicknames, user.alerts)


        elif full_moon_nickname.title not in new_full_moon_nicknames:
            alert.is_active = False
            db.session.commit()
        
    db.session.commit()
    return redirect("/display-settings")

@app.route("/logout")
def logout_user():

    del session['email']
    flash('Succesfully logged out!')

    return redirect('/')

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')