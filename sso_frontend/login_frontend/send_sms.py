import requests
from django.conf import settings

def send_sms(number, message):

    if(settings.FAKE_TESTING):
        return True

    url = settings.SMS_GATEWAY_URL

    params = {'username' : settings.SMS_USERNAME,
              'password' : settings.SMS_PASSWORD,
              'to' : number,
              'text' : message}

    response = requests.get(url, params=params)
    if(response.status_code == 202):
        return True
    return False