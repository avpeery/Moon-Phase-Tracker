from model import *
from flask import Flask, request



def form_get_request(*argv):

    form_get_request_list = []

    for arg in argv:
        form_get_request_list.append(request.form.get(arg))

    return form_get_request_list


def form_get_list(*argv):
    form_get_nested_list = []

    for arg in argv:
        form_get_nested_list.append(request.form.getlist(arg))

    return form_get_nested_list

def 
full_moon = MoonPhaseType.query.filter(MoonPhaseType.title == "Full Moon").first()
blue_moon_nickname = FullMoonNickname.query.filter(FullMoonNickname.title == "Blue Moon").first()

if __name__ == "__main__":
    
    connect_to_db(app)
    app.debug=True