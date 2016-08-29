import requests
from django.conf import settings

def send_sms(number, message):

    url = settings.SMS_GATEWAY_URL + '?username=' + settings.SMS_USERNAME + \
    '&password=' + settings.SMS_PASSWORD + '&to=' + number + '&text=' + message

    params = {'username' : settings.SMS_USERNAME,
              'password' : settings.SMS_PASSWORD,
              'to' : number,
              'message' : message}
              
    req = requests.get(url, params=params)
    if(req.status_code == 202):
        return True
    return False
