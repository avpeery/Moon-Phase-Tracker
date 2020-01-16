from model import *
from flask import Flask, request


def form_get_request(*argv):
  '''Receives multiple items from post request, processes, and returns list'''

  form_get_request_list = []

  #loop through arguments given
  for arg in argv:

    #process request and add to list to be returned
    form_get_request_list.append(request.form.get(arg))

  return form_get_request_list


def form_get_list(*argv):
  '''Receives list items (ex: checkboxes) from post request, processes, and returns nested list'''

  form_get_nested_list = []

  for arg in argv:

    form_get_nested_list.append(request.form.getlist(arg))

  return form_get_nested_list


def credentials_to_dict(credentials):
  '''Takes in credentials from OAuth and returns in dictionary format'''

  #Returns dictionary for OAuth process
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


def create_google_calendar_event(title, date):
  '''Takes title and date of event from FullCalendar to turn into google calendar event'''

  #convert datetime object to string to use for google event
  date = datetime.strptime(date[4:15], "%b %d %Y")
  date = date.strftime("%Y-%m-%d")

  #dictionary for google event information
  event = {'summary': title,
            'start': {'date': date,},
            'end': {'date': date}
        }

  return event


def set_new_alerts_for_user(user_moon_phase_choices, user_full_moon_nickname_choices, user):
  '''Takes in user from database, and user's requested moon phase/full moon nicnkname text alerts in sets, adds alerts as active or inactive in database accordingly'''

  #grab all moon phases and full moon nicknames
  all_moon_phase_types = MoonPhaseType.query.all()
  all_full_moon_nicknames = FullMoonNickname.query.all()

  for moon_phase_type in all_moon_phase_types:

    #if moon phase type is in the user's choices
    if moon_phase_type.title in user_moon_phase_choices:

      #create and set alert as active
      moon_phase_alert = Alert(user_id = user.user_id, moon_phase_type_id = moon_phase_type.moon_phase_type_id, is_active=True)

      db.session.add(moon_phase_alert)

    else:

      #moon phase type is not in user's choices
      #create alert and set to not active
      moon_phase_alert = Alert(user_id = user.user_id, moon_phase_type_id = moon_phase_type.moon_phase_type_id, is_active=False)

      db.session.add(moon_phase_alert)

  for full_moon_nickname in all_full_moon_nicknames:

    #if full moon nickname is in user's choices
    if full_moon_nickname.title in user_full_moon_nickname_choices:

      #creeate alert and set to active
      full_moon_alert = Alert(user_id = user.user_id, full_moon_nickname_id = full_moon_nickname.full_moon_nickname_id, is_active=True)

      db.session.add(full_moon_alert)
        
    else:

      #alert not in user's choices - create alert, set to not active
      full_moon_alert = Alert(user_id = user.user_id, full_moon_nickname_id = full_moon_nickname.full_moon_nickname_id, is_active=False)

      db.session.add(full_moon_alert)


def change_alerts_for_user(user, new_moon_phases, new_full_moon_nicknames):
  '''Takes in user, updated requests for moon phase/full moon nickname text alerts as sets and updates alerts active or inactive accordingly'''
  
  for user.alert in user.alerts:

    #if user's moon phase type alert is in updated choices, set to active
    if user.alert.moon_phase_type_id in new_moon_phases:
      user.alert.is_active = True
    
    #if user's full moon nickname alert is in updated choices, set to active
    elif user.alert.full_moon_nickname_id in new_full_moon_nicknames:
      user.alert.is_active = True

    #if user's moon phase type alert is NOT in updated choice, set to not active
    elif user.alert.moon_phase_type_id not in new_moon_phases:
      user.alert.is_active = False 

    #if user's full moon nickname alert is NOT in updated choice, set to not active
    elif user.alert.full_moon_nickname_id not in new_full_moon_nicknames:
      user.alert.is_active = False


def append_moon_phase_occurences(given_list, moon_phase_occurences):
  '''Takes in moon occurences and empty list, appends occurences as dictionaries to list, returns updated list'''
  
  for row in moon_phase_occurences:

    start_date = row.start.isoformat()

    if row.full_moon_nickname_id:

      given_list.append({'id': row.moon_phase_occurence_id, 'title': row.moon_phase_type.title, 'start': start_date})
      given_list.append({'id': row.moon_phase_occurence_id, 'title': row.full_moon_nickname.title, 'start': start_date})

    else:

      given_list.append({'id': row.moon_phase_occurence_id, 'title': row.moon_phase_type.title, 'start': start_date})

  return given_list


def append_seasonal_solstices(given_list, seasonal_solstices):
  """Takes in list and seasonal solstices, appends solstices as dictionaries to list, returns updated list"""

  for row in seasonal_solstices:

    start_date = row.start.isoformat()

    given_list.append({'id': row.solstice_id, 'title': row.title, 'start': start_date})

  return given_list


def add_active_alerts_to_sets(user, moon_phases, full_moon_nicknames):
  """Checks user's alerts for if is_active is true, then adds active alerts to corresponding sets, returns sets in list"""
  
  moon_phase_set = set()
  full_moon_nickname_set = set()

  for alert in user.alerts:

    if alert.is_active == True and alert.moon_phase_type_id:

      moon_phase_set.add(alert.moon_phase_type_id)

    elif alert.is_active == True and alert.full_moon_nickname_id:

      full_moon_nickname_set.add(alert.full_moon_nickname_id)

  return [moon_phase_set, full_moon_nickname_set]