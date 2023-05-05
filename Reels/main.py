from argparse import ArgumentParser
import argparse
from random import randint
from time import sleep
import util
from emulator import emulate_new_device, get_connected_devices
from collections import namedtuple
import screens
import os
import pandas as pd
import json
import re
from transformers import pipeline
from tqdm.auto import tqdm
from util import classify
import numpy as np


PARAMETERS = dict(
    training_phase_n=10,
    training_phase_sleep=30,
    testing_phase_n=1000,
    intervention_phase_n=10
)


def parse_args():
    args = ArgumentParser()
    args.add_argument('--q', required=True)
    args.add_argument('--i', help='Intervention Type', required=True)
    args.add_argument('--d', help='Device Index', required=True, type=int)
    args.add_argument('--n', help='Account Name Type', required=True)
    return args.parse_args()

def install_apks(device):
    for apk in os.listdir('apks'):
        if not apk.endswith('.apk'):
            continue
        package_name = apk[:-4]
        if not device.is_installed(package_name):
            device.install_apk(os.path.join('apks', apk))

def configure_keyboard(device):
    device.set_keyboard('io.github.visnkmr.nokeyboard/.IMEService')

def restart_app(device):
    device.kill_app('com.instagram.android')
    device.launch_app('com.instagram.android')
    sleep(10)
    util.tap_on(device, {'content-desc': 'Reels'})
    sleep(2)

def training_phase_2(device, query):

    count = 0
    # start training
    training_phase_2_data = []
    for iter in tqdm(range(1000)):

        # restart every 20 videos to refresh app state
        if iter % 20 == 0:
            restart_app(device)

        # break if exit satisfied
        if count > PARAMETERS["training_phase_n"]:
            break

        # grab xml text elements
        xml = device.get_xml()
        text_elems = device.find_elements({'content-desc': re.compile('.+')}, xml)
        text_elems += device.find_elements({'text': re.compile('.+')}, xml)

        row = {}
        for column_id, elem in enumerate(text_elems):
            key = elem['resource-id']
            if key.strip() == '':
                key = 'col_%s' % column_id
            text = elem['content-desc']
            if text.strip() == '':
                text = elem['text']
            row[key] = text


        # grab top comment for description
        util.tap_on(device, {'content-desc': 'Comment'})
        elem = device.find_element({'resource-id': 'com.instagram.android:id/row_comment_textview_comment'})

        # build row
        desc = elem['content-desc']
        delim = desc.index('said')
        author = desc[:delim].strip()
        text = desc[delim + 4:].strip()
        row['author'] = author
        row['text'] = text
        if classify(query, text):
            print(text)
            count += 1
            row['liked'] = True
            # click on like and watch for longer
            util.like_bookmark_subscribe(device)
            util.play_pause(device)
            sleep(PARAMETERS["training_phase_sleep"])
    
        # append to training data
        training_phase_2_data.append(row)

        # hide comments
        util.swipe_down(device)
        sleep(1)

        # swipe to next video
        util.swipe_up(device)
        
    return training_phase_2_data

def testing(device):

    # start testing
    
    testing_phase1_data = []
    for iter in tqdm(range(PARAMETERS["testing_phase_n"])):

        # restart every 50 videos to refresh app state
        if iter % 20 == 0:
            restart_app(device)

        try:
            util.tap_on(device, {'content-desc': 'Comment'})
            elem = device.find_element({'resource-id': 'com.instagram.android:id/row_comment_textview_comment'})
        except:
            util.swipe_up(device)
            continue

        # build row
        try:
            desc = elem['content-desc']
            delim = desc.index('said')
            author = desc[:delim].strip()
            text = desc[delim + 4:].strip()
            row = { 'text': text, 'author': author }
        except:
            util.swipe_up(device)
            continue

        # append to training data
        testing_phase1_data.append(row)

        util.swipe_down(device)
        util.swipe_up(device)
  
    return testing_phase1_data

def Not_Interested(device,query, intervention):
    if intervention == "Not_Interested":
        pass 
    
    intervention_data = []
    count = 0

    # for 1000 videos
    for iter in tqdm(range(1000)):

        # restart every 50 videos to refresh app state
        if iter % 20 == 0:
            restart_app(device)

        # break if success
        if count > PARAMETERS["intervention_phase_n"]:
            print('breaking',count)
            break
    
        # check for any flow disruptions first
        #util.check_disruptions(device)
        
        # watch short for a certain time
        sleep(1)

        

        xml = device.get_xml()
        text_elems = device.find_elements({'content-desc': re.compile('.+')}, xml)
        text_elems += device.find_elements({'text': re.compile('.+')}, xml)

        #util.swipe_down(device)

        # build row
        row = {}
        for column_id, elem in enumerate(text_elems):
            key = elem['resource-id']
            if key.strip() == '':
                key = 'col_%s' % column_id
            text = elem['content-desc']
            if text.strip() == '':
                text = elem['text']
            if text == '':
                continue
            row[key] = text

            

        # grab top comment for description
        util.tap_on(device, {'content-desc': 'Comment'})
        elem = device.find_element({'resource-id': 'com.instagram.android:id/row_comment_textview_comment'})

        util.swipe_down(device)

        sleep(1)

        # build row
        desc = elem['content-desc']
        delim = desc.index('said')
        author = desc[:delim].strip()
        text = desc[delim + 4:].strip()
        row['author'] = author
        row['text'] = text


        if classify(query, text):
            print("Here")
            print(text)
            count += 1
            row['Intervened'] = True
            row['Intervention'] = intervention

            device.tap((650,1275))
            sleep(1)

            try: 
                util.tap_on(device, {'text': "Not Interested"})
                device.longtap()
                #util.swipe_down(device)
            except: 
                util.swipe_up(device)
                
        # util.swipe_up(device)

        intervention_data.append(row)

        if not row.get('Intervened', False):
            util.swipe_up(device)
    

    return intervention_data


def Unfollow(device,query, intervention):
    restart_app(device)

    intervention_data=[]


    
    #click profile
    try: util.tap_on(device, attrs={'content-desc': 'Profile'})
    except: pass


    #click following
    try: util.tap_on(device, attrs={'resource-id': 'com.instagram.android:id/row_profile_header_following_container'})
    except: pass

   
    while True:
        try:
            util.tap_on_all(device, 
            {
                'resource-id':"com.instagram.android:id/follow_list_row_large_follow_button",
                'text': 'Following'
            })
            util.swipe_up(device)

        except:
            break
    
    restart_app(device)
    
    return intervention_data

def Unfollow_Not_Interested(device,query, intervention):
    restart_app(device)
    
    #click profile
    try: util.tap_on(device, attrs={'content-desc': 'Profile'})
    except: pass


    #click following
    try: util.tap_on(device, attrs={'resource-id': 'com.instagram.android:id/row_profile_header_following_container'})
    except: pass

   
    while True:
        
        res=util.tap_on_all(device, 
        {
            'resource-id':"com.instagram.android:id/follow_list_row_large_follow_button",
            'text': 'Following'
        })
        util.swipe_up(device)

        if res==-1:
            break



    intervention_data = []
    count = 0

    # for 1000 videos
    for iter in tqdm(range(1000)):

        # restart every 50 videos to refresh app state
        if iter % 20 == 0:
            restart_app(device)

        # break if success
        if count > PARAMETERS["intervention_phase_n"]:
            print('breaking',count)
            break
    
        # check for any flow disruptions first
        #util.check_disruptions(device)
        
        # watch short for a certain time
        sleep(1)

        

        xml = device.get_xml()
        text_elems = device.find_elements({'content-desc': re.compile('.+')}, xml)
        text_elems += device.find_elements({'text': re.compile('.+')}, xml)

        #util.swipe_down(device)

        # build row
        row = {}
        for column_id, elem in enumerate(text_elems):
            key = elem['resource-id']
            if key.strip() == '':
                key = 'col_%s' % column_id
            text = elem['content-desc']
            if text.strip() == '':
                text = elem['text']
            if text == '':
                continue
            row[key] = text

            

        # grab top comment for description
        util.tap_on(device, {'content-desc': 'Comment'})
        elem = device.find_element({'resource-id': 'com.instagram.android:id/row_comment_textview_comment'})

        util.swipe_down(device)

        sleep(1)

        # build row
        desc = elem['content-desc']
        delim = desc.index('said')
        author = desc[:delim].strip()
        text = desc[delim + 4:].strip()
        row['author'] = author
        row['text'] = text


        if classify(query, text):
            print(text)
            count += 1
            row['Intervened'] = True
            row['Intervention'] = intervention

            device.tap((650,1275))
            sleep(1)

            try: 
                util.tap_on(device, {'text': "Not Interested"})
                device.longtap()
                #util.swipe_down(device)
            except: 
                util.swipe_up(device)
                


        intervention_data.append(row)

        
        if not row.get('Intervened', False):
            util.swipe_up(device)
    

    return intervention_data

def Not_Interested_Unfollow(device,query, intervention):
    intervention_data = []
    count = 0

    # for 1000 videos
    for iter in tqdm(range(1000)):

        # restart every 50 videos to refresh app state
        if iter % 20 == 0:
            restart_app(device)

        # break if success
        if count > PARAMETERS["intervention_phase_n"]:
            print('breaking',count)
            break
    
        # check for any flow disruptions first
        #util.check_disruptions(device)
        
        # watch short for a certain time
        sleep(1)

        

        xml = device.get_xml()
        text_elems = device.find_elements({'content-desc': re.compile('.+')}, xml)
        text_elems += device.find_elements({'text': re.compile('.+')}, xml)

        #util.swipe_down(device)

        # build row
        row = {}
        for column_id, elem in enumerate(text_elems):
            key = elem['resource-id']
            if key.strip() == '':
                key = 'col_%s' % column_id
            text = elem['content-desc']
            if text.strip() == '':
                text = elem['text']
            if text == '':
                continue
            row[key] = text

            

        # grab top comment for description
        util.tap_on(device, {'content-desc': 'Comment'})
        elem = device.find_element({'resource-id': 'com.instagram.android:id/row_comment_textview_comment'})

        util.swipe_down(device)

        sleep(1)

        # build row
        desc = elem['content-desc']
        delim = desc.index('said')
        author = desc[:delim].strip()
        text = desc[delim + 4:].strip()
        row['author'] = author
        row['text'] = text

        

        if classify(query, text):
            print(text)
            count += 1
            row['Intervened'] = True
            row['Intervention'] = intervention

            device.tap((650,1275))
            sleep(1)

            try: 
                util.tap_on(device, {'text': "Not Interested"})
                device.longtap()
                #util.swipe_down(device)
            except: 
                util.swipe_up(device)
                


        intervention_data.append(row)

        if not row.get('Intervened'):
            util.swipe_up(device)

    
    restart_app(device)
    
    #click profile
    try: util.tap_on(device, attrs={'content-desc': 'Profile'})
    except: pass


    #click following
    try: util.tap_on(device, attrs={'resource-id': 'com.instagram.android:id/row_profile_header_following_container'})
    except: pass

   

    while True:
        
        res=util.tap_on_all(device, 
        {
            'resource-id':"com.instagram.android:id/follow_list_row_large_follow_button",
            'text': 'Following'
        })
        util.swipe_up(device)

        if res==-1:
            break
    
    restart_app(device)


    return intervention_data


def Control():
    pass


if __name__ == '__main__':
    args = parse_args()
    
    
    device = get_connected_devices()[args.d]
 

    try:
        print("Installing APKs...")
        install_apks(device)

        print("Configuring keyboard...")
        configure_keyboard(device)


        print('Serial', device._Android__device.serial)

        input("Continue?")
        
        print("Training Phase 2...", util.timestamp())
        training_phase_2_data = training_phase_2(device, args.q)
        
        print("Testing Phase 1...", util.timestamp())
        testing_phase_1_data = testing(device)

        print("Saving...", util.timestamp())
        pd.DataFrame(training_phase_2_data).to_csv(f'training_phase_2/{args.q}--{args.i}--{args.n}.csv', index=False)
        pd.DataFrame(testing_phase_1_data).to_csv(f'testing_phase_1/Insta_snatlanshine.csv', index=False)
        
        if args.i == "Not_Interested":
       
            print("Not Interested Only Intervention...", util.timestamp())
            intervention_data = Not_Interested(device,args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}.csv', index=False)
        
        elif args.i == "Unfollow":
            print("Unfollow Only Intervention...", util.timestamp())
            intervention_data = Unfollow(device,args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}.csv', index=False)

        elif args.i == "Unfollow_Not_Interested":
            print("Unfollow then Not Interested Intervention...", util.timestamp())
            intervention_data = Unfollow_Not_Interested(device,args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}.csv', index=False)

        elif args.i == "Not_Interested_Unfollow":
            print("Not Interested then Unfollow Intervention...", util.timestamp())
            intervention_data = Not_Interested_Unfollow(device,args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}.csv', index=False)

        elif args.i == "Control":
            print("Control Intervention")
            intervention_data = Control(device,args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}.csv', index=False)
        
        print("Testing Phase 2... ", util.timestamp())
        testing_phase_2_data = testing(device)

    #     print("Saving...")
    #     pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}_{credentials.name}.csv', index=False)
        pd.DataFrame(testing_phase_2_data).to_csv(f'testing_phase_2/{args.q}--{args.i}--{args.n}.csv', index=False)

    #     device.kill_app('com.ss.android.ugc.trill')
    #     device.type_text(26)

    except Exception as e:
        print(e)
        # device.screenshot(f'screenshots/{credentials.name}.png')
        # device.destroy()

    # finally:
        # pass
        # device.destroy()
    # except Exception as e:
    #     print(e)
    #     device.screenshot(f'screenshots/{credentials.name}.png')
        # device.destroy()
