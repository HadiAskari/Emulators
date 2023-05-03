import names
from random import choice, randint
from uuid import uuid4
import re
from datetime import datetime
from time import sleep
import classifier
import json


with open('keywords.json') as f:
    query_kw = json.load(f)

def generate_email():
    domains = ['youtubeaudit.com']
    email = '%s_%s%s@%s' % (names.get_first_name(), names.get_last_name(), randint(1, 999), choice(domains))
    return email.lower()

def generate_password():
    return ('@%s' % uuid4()).split('-')[0]

def swipe_up(device):
    device.swipe((200, 1000), (200, 300))

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

def tap_on_all(device, attrs, xml=None):
    elem = device.find_elements(attrs=attrs, xml=xml)
    for items in elem:
        coords = device.get_coordinates(items)
        device.tap(coords)
    if not elem:
        return -1 
    else: return 1

def check_disruptions(device):
    xml = device.get_xml()
    if 'Sponsored' in xml:
        #Instagram
        swipe_up(device)
    elif 'Tap to watch LIVE' in xml:
        swipe_up(device)
    elif 'TikTok is more fun' in xml:
        tap_on(device, {'text': 'Don\'t allow'}, xml)
    elif "TikTok isn't responding" in xml:
        tap_on(device, {'text': 'Close app'}, xml)
    # elif ""

def like_bookmark_subscribe(device, xml=None):
    xml = device.get_xml() if xml is None else xml
    # like short
    try: tap_on(device, {'content-desc': 'Like', 'selected': 'false'}, xml)
    except: pass

    # follow creator
    try: tap_on(device, {'content-desc': re.compile('Follow .*') }, xml)
    except: pass

    # bookmark short
    try: 
        tap_on(device, {'resource-id': 'com.ss.android.ugc.trill:id/c0k', 'selected': 'false', 'class': 'android.widget.ImageView'}, xml)
        tap_on(device, {'text': 'OK'})
        sleep(3)
    except: pass

def timestamp():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

def lower_keyboard(device):
    device.type_text(111)

def classify(query, text):
    keywords = query_kw[query]
    for kw in keywords:
        if classifier.classify(kw, text):
            return True
    return False
