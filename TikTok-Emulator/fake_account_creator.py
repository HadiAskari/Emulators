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



def configure_keyboard(device):
    device.set_keyboard('io.github.visnkmr.nokeyboard/.IMEService')

def restart_app(device):
    device.kill_app('com.ss.android.ugc.trill')
    device.launch_app('com.ss.android.ugc.trill')
    sleep(3)

def generate_credentials(email,password1):
    credentials = namedtuple('Credentials', ['name','email', 'password'])
    return credentials(
        name='%s' % randint(10000, 99999),
        email=email,
        password=password1
    )

def signup_controller(device, credentials):
    while True:
        xml = device.get_xml()
        if "Don’t have an account? Sign up" in xml:
            print("Signup screen. Proceeding.")
            screens.signup_screen(device)
        elif "When’s your birthday?" in xml:
            print("Birthday screen. Waiting.")
            screens.date_of_birth_screen(device, 'Next')
        elif "When’s your birthdate?" in xml:
            print("Birthday screen. Waiting.")
            screens.date_of_birth_screen(device, 'Continue')
        elif "Too many attempts. Try again later." in xml:
            print("Too many attempts. Rebooting.")
            restart_app(device)
        elif 'text="Email"' in xml:
            print("Email screen. Entering email.")
            if "Enter a valid email address" in xml:
                restart_app(device)
            else:
                screens.email_screen(device, credentials.email)
        elif "Verify to continue" in xml:
            print("Captcha screen. Waiting.")
            screens.captcha_screen(device)
        elif "Agree and continue" in xml:
            print("Agree prompt. Agreeing.")
            util.tap_on(device, attrs={'text': 'Agree and continue'})
        elif "Create password" in xml:
            print("Password screen. Entering password.")
            screens.password_screen(device, credentials.password)
        elif "Create nickname" in xml:
            print("Nickname screen. Skipping.")
            screens.skip_screen(device)
        elif "Choose your interests" in xml:
            print("Interests screen. Skipping.")
            screens.skip_screen(device)
        elif "Account Privacy" in xml and "Skip" in xml:
            print("Account privacy screen. Skipping.")
            screens.skip_screen(device)
        elif "Enter phone number" in xml and "Skip" in xml:
            print("Phone number screen. Skipping.")
            screens.skip_screen(device)
        elif "What languages" in xml and "Confirm" in xml:
            print("Language prompt. Confirming.")
            screens.confirm_screen(device)
        elif "access your contacts?" in xml:
            print("Permissions requested. Allowing.")
            screens.permissions_screen(device)
        elif xml == "" or "Swipe up" in xml:
            util.swipe_up(device)
            sleep(5)
            util.play_pause(device)
        elif "Profile" in xml:
            sleep(0.5)
            print("Main app screen. Going to Profile.")
            util.tap_on(device, attrs={'text': "Profile"})
            if "Add bio" in xml or "Add friends" or "Tap to add bio" in xml:
                print("Account signed-in! Quitting.")
                break
            elif "Sign up for an account" in xml:
                print("Signing up for account")
                util.tap_on(device, attrs={'text': 'Sign up'})


# def logout(device):
#     xml = device.get_xml()

#     util.tap_on(device, attrs={'text': '1157'})
#     device.tap((1000, 620))
#     #sleep(0.5)

#     xml = device.get_xml()

#     device.tap((1000, 120))

#     xml = device.get_xml()

#     util.tap_on(device, attrs={'text': 'Settings and privacy'})

#     sleep(0.5)

#     util.swipe_up(device)
#     util.swipe_up(device)

#     util.tap_on(device, attrs={'text': 'Log out'})

#     sleep(0.5)

#     xml = device.get_xml()

#     util.tap_on(device, attrs={'text': 'Log out'})

#     sleep(0.5)
#     xml = device.get_xml()
#     util.tap_on(device, attrs={'text': 'Not Now'})

#     sleep(0.5)
#     xml = device.get_xml()
#     util.tap_on(device, attrs={'text': 'Log out'})










if __name__ == '__main__':
    
    df=pd.read_csv('Fake Account Details - TikTok Accounts.csv')
    email=df['Email'].to_list()
    password='Abcd1234!'

    for i,val in enumerate(email):
        if i <39:
            continue

        print(val,password)    
        credentials=generate_credentials(val,password)
    

        device = get_connected_devices()[0]
        
    



        print("Configuring keyboard...")
        configure_keyboard(device)
        
        print("Starting TikTok...")
        restart_app(device)
        
        try:
            print("Signing up...")
            signup_controller(device, credentials)
            print("Signed-In Please Log-Out")

            print("Logging Out")
            input()
            # logout(device)
        except Exception as e:
            print(e)
            device.screenshot(f'screenshots/{credentials.name}.png')
            device.destroy()
