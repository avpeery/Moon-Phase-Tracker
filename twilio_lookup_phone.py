from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os


ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']

def lookup_phone_number(phone):
    """Uses Twilio API to look up phone number, returns number as string"""
    
    #create Twilio client
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    try:

        #check if number is real number using Twilio lookup
        phone_number = client.lookups \
                         .phone_numbers(phone) \
                         .fetch(type=['carrier'])

        #returns formmatted phone number
        return phone_number.phone_number

    #checks Twilio exception responses if number not real
    except TwilioRestException as e:

        #Number not found - return False
        if e.code == 20404:

            return False

        else:

            raise e

