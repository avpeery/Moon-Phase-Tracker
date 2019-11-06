
from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Moon_Phase, Alert, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')


@app.route('/register')
def register_user():
    return render_template('registration.html')


@app.route("/register", methods= ["POST"])
def register_process():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    phone = request.form.get('phone')
    email = request.form.get('email')
    password = request.form.get('password')
    new_moon = request.form.get('new_moon')
    first_quarter = request.form.get('first_quarter')
    last_quarter = request.form.get('last_quarter')
    full_moon = request.form.get('full_moon')

    if User.query.filter_by(email = email).first():
        flash("Account with that email already exists!")
        return redirect("/register")
    else:
        email = User(fname=fname, lname=lname, phone=phone, email = email, password = password, new_moon=new_moon, first_quarter=first_quarter, last_quarter=last_quarter, full_moon=full_moon)
        db.session.add(email)
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
        session['user_email'] = user.email
        session['user_id'] = user.user_id

        flash("Succesfully logged in!")
        return redirect("/")

    flash("That is not a valid email and password")
    return redirect('/login')


@app.route("/logout")
def logout_user():

    del session['user_email']
    del session['user_id']
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