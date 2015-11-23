import urllib2
import os

__all__ = ["send_sms"]

def send_sms_get(number, message):
    message = urllib2.quote(message.encode('utf-8'))
    try:
        # SMS_GATEWAY_URL "http://url_to_sms_gateway/?number={number}&text={message}"
        url = os.getenv(SMS_GATEWAY_URL, '').format(number=number, message=message)
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        code = f.readline()
    except urllib2.URLError, e:
        raise e
    return True

def send_sms_post(number, message):
    message = urllib2.quote(message.encode('utf-8'))
    try:
        # SMS_GATEWAY_URL_POST "http://url_to_sms_gateway/"
        url = os.getenv(SMS_GATEWAY_URL_POST, '')
        req = urllib2.Request(url, {"number": number, "text": message})
        f = urllib2.urlopen(req)
        code = f.readline()
    except urllib2.URLError, e:
        raise e
    return True

send_sms = send_sms_get
