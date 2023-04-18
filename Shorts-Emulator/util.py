import names
from random import choice, randint
from uuid import uuid4
import re
from datetime import datetime
from time import sleep

def generate_email():
    domains = ['youtubeaudit.com']
    email = '%s_%s%s@%s' % (names.get_first_name(), names.get_last_name(), randint(1, 999), choice(domains))
    return email.lower()

def generate_password():
    return ('@%s' % uuid4()).split('-')[0]

def swipe_up(device):
    device.swipe((400, 700), (400, 300))

def swipe_down(device):
    device.swipe((200, 300), (200, 1000))

def play_pause(device):
    # pause video
    # device.tap((400, 400))
    device.tap((200, 400))

def tap_on(device, attrs, xml=None):
    elem = device.find_element(attrs=attrs, xml=xml)
    coords = device.get_coordinates(elem)
    #print(coords)
    device.tap(coords)

def tap_on_nth(device, attrs, n, xml=None):
    elem = device.find_elements(attrs=attrs, xml=xml)[n]
    coords = device.get_coordinates(elem)
    device.tap(coords)

def check_disruptions(device):
    pass
    # xml = device.get_xml()
    # if 'Swipe up for next video' in xml:
    #     swipe_up(device)

def like_bookmark_subscribe(device, xml=None):
    xml = device.get_xml() if xml is None else xml
    # like short
    try: tap_on(device, {'resource-id': 'com.google.android.youtube:id/reel_dyn_like'}, xml)
    except: pass

def timestamp():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

def lower_keyboard(device):
    device.type_text(111)

def remove_emojis(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                    "]+", re.UNICODE)
    return re.sub(emoj, '', data)

def preprocess(text):
    text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",text).split())
    text = text.lower()
    return text  
