from argparse import ArgumentParser
from random import randint
from time import sleep
import util
from emulator import emulate_new_device, get_connected_devices
from collections import namedtuple
import os
import pandas as pd
import re
from tqdm.auto import tqdm
from util import classify


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

def generate_credentials(q):
    credentials = namedtuple('Credentials', ['name', 'email', 'password'])
    return credentials(
        name='%s' % randint(10000, 99999),
        email='barbara_bergren118@youtubeaudit.com',
        password='@7699cef4'
    )

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
    device.kill_app('com.ss.android.ugc.trill')
    device.launch_app('com.ss.android.ugc.trill')
    sleep(10)

def training_phase_2(device, query):
    count = 0
    # start training
    training_phase_2_data = []
    for iter in tqdm(range(1000)):

        # restart every 50 videos to refresh app state
        if iter % 20 == 0:
            restart_app(device)

        # break if success
        if count > PARAMETERS["training_phase_n"]:
            break

        # check for any flow disruptions first
        util.check_disruptions(device)

        # pause video
        util.play_pause(device)

        # click on see more to reveal content
        try: util.tap_on(device, {'text': 'See more'})
        except: pass

        # grab xml
        text_elems = device.find_elements({'text': re.compile('.+')})

        # build row
        row = {}

        for el in text_elems:
            row[el['resource-id']] = el['text']

            # like video if it contains the query needed
            if el['resource-id'] == 'com.ss.android.ugc.trill:id/bc5':
                text = el['text']
                
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

        # press on hide to hide content
        try: util.tap_on(device, {'text': 'Hide'})
        except: pass

        # swipe to next
        util.swipe_up(device)
    return training_phase_2_data

def testing(device):
    testing_phase1_data = []
    for iter in tqdm(range(PARAMETERS["testing_phase_n"])):

        # restart every 50 videos to refresh app state
        if iter % 20 == 0:
            restart_app(device)

        # check for any flow disruptions first
        util.check_disruptions(device)
        
        # watch short for a certain time
        sleep(1)

        # pause video
        util.play_pause(device)

        # click on see more to reveal content
        try: util.tap_on(device, {'text': 'See more'})
        except: pass

        # grab xml
        text_elems = device.find_elements({'text': re.compile('.+')})

        # grab text elements
        row = {}
        for el in text_elems:
            row[el['resource-id']] = el['text']

        # append to training data
        testing_phase1_data.append(row)

        # press on hide to hide content
        try: util.tap_on(device, {'text': 'Hide'})
        except: pass

        util.swipe_up(device)

    return testing_phase1_data

def Not_Interested(device,query, intervention):
    try:
        if intervention == "Not_Interested":
            pass 
        
        intervention_data = []
        count = 0

        # for 1000 videos
        for iter in tqdm(range(1000)):

            # restart every 50 videos to refresh app state
            if iter % 50 == 0:
                restart_app(device)

            # break if success
            if count > PARAMETERS["intervention_phase_n"]:
                break
        
            # check for any flow disruptions first
            util.check_disruptions(device)
            
            # watch short for a certain time
            sleep(1)

            # pause video
            util.play_pause(device)

            # click on see more to reveal content
            try: util.tap_on(device, {'text': 'See more'})
            except: pass

            # grab xml
            text_elems = device.find_elements({'text': re.compile('.+')})

            # build row
            row = {}

            for el in text_elems:

                row[el['resource-id']] = el['text']
                
                # like video if it contains the query needed
                if el['resource-id']=='com.ss.android.ugc.trill:id/bc5':
                    text = el['text']

                    if classify(query, text):
                        count += 1
                        row['Intervened'] = True
                        row['Intervention'] = intervention

                        #longtap
                        device.longtap()

                        # click on Not intereseted
                        util.tap_on(device, {'text': 'Not interested'})
                        sleep(1)
                        
            # append to training data
            intervention_data.append(row)

            # press on hide to hide content
            try: util.tap_on(device, {'text': 'Hide'})
            except: pass

            # swipe to next
            util.swipe_up(device)
    except Exception as e:
        if e == "'NoneType' object is not subscriptable":
            restart_app(device)

    return intervention_data

def Unfollow(device,query, intervention):
    try:
        if intervention=="Unfollow":
            pass 
        
        restart_app(device)

        intervention_data = []

        # press on hide to hide content
        try: device.tap((648.0, 1494.5))
        except: pass
        
        try: 
            util.tap_on(device, {'text': 'Following'})
            sleep(0.5)
        except Exception as e:
            print(e)
            pass

        while True:
            try:
                elem = device.find_elements(attrs={'text': 'Following'}, xml=None)
                print(len(elem))
                if not elem:
                    break
                for items in elem:
                    print(items)
                    if items["index"]=="2":
                        print("Here")
                        coords = device.get_coordinates(items)
                        device.tap(coords)
                util.swipe_up(device)
            except Exception as e:
                print(e)

    except Exception as e:
        if e == "'NoneType' object is not subscriptable":
            restart_app(device)

    return intervention_data

def Unfollow_Not_Interested(device,query, intervention):
    try:
        if intervention=="Unfollow_Not_Interested":
            pass 
        
        restart_app(device)

        # press on hide to hide content
        try: device.tap((648.0, 1494.5))
        except: pass
        
        try: 
            util.tap_on(device, {'text': 'Following'})
            sleep(0.5)
        except Exception as e:
            print(e)
            pass

        while True:
            try:
                elem = device.find_elements(attrs={'text': 'Following'}, xml=None)
                print(len(elem))
                if not elem:
                    break
                for items in elem:
                    print(items)
                    if items["index"]=="2":
                        print("Here")
                        coords = device.get_coordinates(items)
                        device.tap(coords)
                util.swipe_up(device)
            except Exception as e:
                print(e)

        restart_app(device)

        intervention_data = []
        count = 0
        


        for iter in tqdm(range(1000)):

            # restart every 50 videos to refresh app state
            if iter % 20 == 0:
                restart_app(device)

            # break if success
            if count > PARAMETERS["intervention_phase_n"]:
                break
            
            # check for any flow disruptions first
            util.check_disruptions(device)
            
            # watch short for a certain time
            sleep(1)

            # pause video
            util.play_pause(device)

            # click on see more to reveal content
            try: util.tap_on(device, {'text': 'See more'})
            except: pass

            # grab xml
            text_elems = device.find_elements({'text': re.compile('.+')})

            # build row
            row = {}

            for el in text_elems:

                row[el['resource-id']] = el['text']
                
                # like video if it contains the query needed
                if el['resource-id']=='com.ss.android.ugc.trill:id/bc5':
                    text = el['text']

                    if classify(query, text):
                        count += 1
                        row['Intervened'] = True
                        row['Intervention'] = intervention

                        #longtap
                        device.longtap()

                        # click on Not intereseted
                        util.tap_on(device, {'text': 'Not interested'})
                        sleep(1)
                        
            # append to training data
            intervention_data.append(row)

            # press on hide to hide content
            try: util.tap_on(device, {'text': 'Hide'})
            except: pass

            # swipe to next
            util.swipe_up(device)

    except Exception as e:
        if e == "'NoneType' object is not subscriptable":
            restart_app(device)

    return intervention_data

def Not_Interested_Unfollow(device,query, intervention):
    try:
        if intervention=="Not_Interested_Unfollow":
            pass 
        
        restart_app(device)
        intervention_data = []
        count = 0
        
        # upper bound
        for iter in tqdm(range(1000)):

            # restart every 50 videos to refresh app state
            if iter % 20 == 0:
                restart_app(device)

            # break if success
            if count > PARAMETERS["intervention_phase_n"]:
                break
            
            # check for any flow disruptions first
            util.check_disruptions(device)
            
            # watch short for a certain time
            sleep(1)

            # pause video
            util.play_pause(device)

            # click on see more to reveal content
            try: util.tap_on(device, {'text': 'See more'})
            except: pass

            # grab xml
            text_elems = device.find_elements({'text': re.compile('.+')})

            # build row
            row = {}

            for el in text_elems:

                row[el['resource-id']] = el['text']
                
                # like video if it contains the query needed
                if el['resource-id']=='com.ss.android.ugc.trill:id/bc5':
                    text = el['text']

                    if classify(query, text):
                        count += 1
                        row['Intervened'] = True
                        row['Intervention'] = intervention

                        #longtap
                        device.longtap()

                        # click on Not intereseted
                        util.tap_on(device, {'text': 'Not interested'})
                        sleep(1)
                        
            # append to training data
            intervention_data.append(row)

            # press on hide to hide content
            try: util.tap_on(device, {'text': 'Hide'})
            except: pass

            # swipe to next
            util.swipe_up(device)

        restart_app(device)

        intervention_data = []

                        
        

        # press on hide to hide content
        try: util.tap_on(device, {'text': 'Profile'})
        except: pass
        
        try: 
            util.tap_on(device, {'text': 'Following'})
            sleep(0.5)
        except Exception as e:
            print(e)
            pass

        while True:
            try:
                elem = device.find_elements(attrs={'text': 'Following'}, xml=None)[1:]
                print(len(elem))
                if not elem:
                    break
                for items in elem:
                    print(items)
                    if items["index"]=="2":
                        print("Here")
                        coords = device.get_coordinates(items)
                        device.tap(coords)
                util.swipe_up(device)
            except Exception as e:
                print(e)
        
    except Exception as e:
        if e == "'NoneType' object is not subscriptable":
            restart_app(device)

    return intervention_data

def Control():
    pass
        

    


if __name__ == '__main__':
    args = parse_args()
    
    
    print("Launching emulator...")
    # device = emulate_new_device(credentials.name)
    print(args.d)
    device = get_connected_devices()[args.d]
    

    try:
        print("Installing APKs...")
        install_apks(device)

        print("Configuring keyboard...")
        configure_keyboard(device)
        
        input("Continue?")
        
        # try:
        # print("Signing up...")
        # signup_controller(device, credentials)

    #     # with open('accounts.txt', 'a') as f:
    #     #     f.write('\n%s,%s' % (credentials.email, credentials.password))

    #     # print("Logging in")
    #     # login_controller(device, credentials)

    #     # print("Training Phase 1...", util.timestamp())
    #     # training_data_phase1 = training_phase_1(device, args.q)

        print("Training Phase 2...", util.timestamp())
        training_phase_2_data = training_phase_2(device, args.q)
        
        print("Testing Phase 1...", util.timestamp())
        testing_phase_1_data = testing(device)

        print("Saving...", util.timestamp())
        # pd.DataFrame(training_data_phase1).to_csv(f'training_phase_1/{args.q}--{args.i}--{args.n}.csv', index=False)
        pd.DataFrame(training_phase_2_data).to_csv(f'training_phase_2/{args.q}--{args.i}--{args.n}.csv', index=False)
        pd.DataFrame(testing_phase_1_data).to_csv(f'testing_phase_1/{args.q}--{args.i}--{args.n}.csv', index=False)
        
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

        # elif args.i == "Control":
        #     pass


        
        print("Testing Phase 2... ", util.timestamp())
        testing_phase_2_data = testing(device)

        print("Saving...")
    #     
        pd.DataFrame(testing_phase_2_data).to_csv(f'testing_phase_2/{args.q}--{args.i}--{args.n}.csv', index=False)

        device.kill_app('com.ss.android.ugc.trill')
        device.type_text(26)

    except Exception as e:
        # device.screenshot(f'screenshots/{args.n}.png')
        print(e)
        pass

    # finally:
        # pass
        # device.destroy()
    # except Exception as e:
    #     print(e)
    #     device.screenshot(f'screenshots/{args.n}.png')
        # device.destroy()
