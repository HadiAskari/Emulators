from argparse import ArgumentParser
from random import randint
from time import sleep
import util
from emulator import emulate_new_device, get_connected_devices
from collections import namedtuple
import pandas as pd
import re
from tqdm.auto import tqdm
from util import classify


PARAMETERS = dict(
    training_phase_n=5,
    training_phase_sleep=5,
    testing_phase_n=10,
    intervention_phase_n=5
)

def parse_args():
    args = ArgumentParser()
    args.add_argument('identifier')
    args.add_argument('--q', required=True)
    args.add_argument('--i', help='Intervention Type', required=True)
    return args.parse_args()

def configure_keyboard(device):
    device.set_keyboard('io.github.visnkmr.nokeyboard/.IMEService')

def restart_app(device):
    device.kill_app('com.google.android.youtube')
    device.launch_app('com.google.android.youtube')
    sleep(5)
    util.tap_on(device, attrs={'content-desc': 'Shorts'})


def training_phase_2(device, query):
    count = 0
    # start training
    training_phase_2_data = []

    for iter in tqdm(range(1000)):

        # restart every 50 videos to refresh app state
        if iter % 50 == 0:
            restart_app(device)

        # break if exit satisfied
        if count > PARAMETERS["training_phase_n"]:
            break

        # check for any flow disruptions first
        util.check_disruptions(device)

        # grab xml
        xml = device.get_xml()
        text_elems = device.find_elements({'content-desc': re.compile('.+')}, xml)
        text_elems += device.find_elements({'text': re.compile('.+')}, xml)

        # build row
        row = {}
        for column_id, elem in enumerate(text_elems):
            key = elem['resource-id']
            if key.strip() == '':
                key = 'col_%s' % column_id
            text = elem['content-desc']
            if text.strip() == '':
                text = elem['text']
            row[key] = text
            if classify(query, text):
                count += 1
                if not row.get('liked', False):
                    row['liked'] = True
                    # click on like and watch for longer
                    util.like_bookmark_subscribe(device)
                    sleep(PARAMETERS["training_phase_sleep"])
    
        # append to training data
        training_phase_2_data.append(row)

        # swipe to next video
        util.swipe_up(device)
    
    return training_phase_2_data

def testing(device):
    # start training
    testing_phase1_data = []    
    for iter in tqdm(range(PARAMETERS["testing_phase_n"])):

        # restart every 50 videos to refresh app state
        if iter % 50 == 0:
            restart_app(device)

        # check for any flow disruptions first
        util.check_disruptions(device)

        # grab xml
        xml = device.get_xml()
        text_elems = device.find_elements({'content-desc': re.compile('.+')}, xml)
        text_elems += device.find_elements({'text': re.compile('.+')}, xml)

        # build row
        row = {}
        for column_id, elem in enumerate(text_elems):
            key = elem['resource-id']
            if key.strip() == '':
                key = 'col_%s' % column_id
            text = elem['content-desc']
            if text.strip() == '':
                text = elem['text']
            row[key] = text

        # append to training data
        testing_phase1_data.append(row)
        count += 1
        
        util.swipe_up(device)

    return testing_phase1_data

def Intervention(device,query, intervention):
    try:
        if intervention=="Not_Interested":
            pass 
        
        restart_app(device)
        intervention_data = []
        count = 0
        
        while count <= PARAMETERS["intervention_phase_n"]:
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


if __name__ == '__main__':
    args = parse_args()
    
    print("Launching emulator...")
    # device = emulate_new_device(credentials.name)
    # print("VNC link:", device.get_vnc_link())
    device = get_connected_devices()[0]


    try:
        print("Configuring keyboard...")
        configure_keyboard(device)

        print("Training Phase 2...", util.timestamp())
        training_phase_2_data = training_phase_2(device, args.q)
        
        print("Testing Phase 1...", util.timestamp())
        testing_phase_1_data = testing(device)

        print("Saving...", util.timestamp())
    #     # pd.DataFrame(training_data_phase1).to_csv(f'training_phase_1/{credentials.name}_big.csv', index=False)
        pd.DataFrame(training_phase_2_data).to_csv(f'training_phase_2/{args.identifier}-{args.q}.csv', index=False)
        pd.DataFrame(testing_phase_1_data).to_csv(f'testing_phase_1/{args.identifier}-{args.q}.csv', index=False)
        
    #     print("Intervention...", util.timestamp())
    #     intervention_data = Intervention(device,args.q, args.i)
        
    #     print("Testing Phase 2... ", util.timestamp())
    #     testing_phase_2_data = testing(device)

    #     print("Saving...")
    #     pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}_{credentials.name}.csv', index=False)
    #     pd.DataFrame(testing_phase_2_data).to_csv(f'testing_phase_2/{args.q}_{credentials.name}.csv', index=False)

    #     device.kill_app('com.ss.android.ugc.trill')
    #     device.type_text(26)

    except Exception as e:
        pass
        # device.screenshot(f'screenshots/{credentials.name}.png')
        # device.destroy()

    # finally:
        # pass
        # device.destroy()
    # except Exception as e:
    #     print(e)
    #     device.screenshot(f'screenshots/{credentials.name}.png')
        # device.destroy()
