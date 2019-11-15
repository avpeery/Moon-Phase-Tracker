from twilio.rest import Client
import os


ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']


def lookup_phone_number(phone):

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    phone_number = client.lookups \
                         .phone_numbers(phone) \
                         .fetch(type=['carrier'])
    return phone_number.phone_number

lookup_phone_number()
