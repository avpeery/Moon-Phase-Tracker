
<p align='center'>
    <img src="static/img/title.jpg">
</p>

## Project Summary

Users interested in tracking moon phases can sign up to receive text alerts for specific moon phase events, or add moon phase events to their personal Google calendars. By using the Python astronomy library, Skyfield, and data from Jet Propulsions Laboratory, moon phase occurrences were calculated from years 2000 – 2050 and stored in the app’s database.

<p align ='center'>
    <img src='static/img/newmoon.png'>
</p>

## About the Developer

Moon Phase Tracker was developed by Anna Peery. Anna's interest in astrology (Taurus sun, Scorpio moon) inspired her to build this app. This is her first fullstack web app project. Learn more about the developer on [LinkedIn](https://www.linkedin.com/in/avpeery/).

## Tech Stack 
**Backend:** Python, Flask, PostgreSQL, SQLAlchemy, OAuth, Skyfield
<br>
**Frontend:** JavaScript, AJAX, jQuery, FullCalendar, HTML5, CSS, Jinja2, Bootstrap
<br>
**APIs:** Twilio, Google Calendar

## User Flow

Sign up for texts 
![Sign Up](static/img/registrationform.gif)
<br>

Change text subscriptions and manage user information
![Settings](static/img/managesettings.gif)
<br>

Access moon phase occurences on the calendar and add calendar event's to personal google calendar
![Calendar](static/img/oauth.gif)
<br>

Checking success of adding the moon phase occurence event to google calendar!
![Oauth](static/img/coldmoon.gif)
