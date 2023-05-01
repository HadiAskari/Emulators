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
            print("Captcha screen. Waiting for email.")
            screens.captcha_screen(device)
        elif "Enter 6-digit code" in xml:
            print("Code entry screen. Waiting.")
            screens.code_entry_screen(device, credentials.email)
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
            print("Permissions requested. Denying.")
            screens.permissions_screen(device)
        elif xml == "" or "Swipe up" in xml:
            util.swipe_up(device)
            sleep(5)
            util.play_pause(device)
        elif "Profile" in xml and ("Discover" in xml or "Friends" in xml or "Inbox" in xml):
            print("Main app screen. Going to Profile.")
            util.tap_on(device, attrs={'text': "Profile"})
            if "Add bio" in xml or "Add friends" in xml or 'add bio' in xml or "Complete your profile" in xml:
                print("Account signed-in! Quitting.")
                break
            elif "Sign up for an account" in xml:
                print("Signing up for account")
                util.tap_on(device, attrs={'text': 'Sign up'})

def login_controller(device, credentials):
    while True:
        xml = device.get_xml()
        if "Log in to TikTok" in xml and "Use phone / email / username" in xml:
            print("Login screen")
            screens.login_screen(device, credentials)
        elif 'text="Email / Username"' in xml:
            print("Email screen. Entering email.")
            screens.email_username_screen(device, credentials.email, credentials.password)
        elif "Verify to continue" in xml:
            print("Captcha screen. Waiting.")
            screens.captcha_screen(device)
        elif "When’s your birthdate?" in xml:
            print("Birthday screen. Waiting.")
            screens.date_of_birth_screen(device, 'Continue')
        elif "Choose your interests" in xml:
            print("Interests screen. Skipping.")
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
        elif "Swipe up for more" in xml:
            util.swipe_up(device)
        elif "Profile" in xml and ("Discover" in xml or "Friends" in xml or "Inbox" in xml):
            print("Main app screen. Going to Profile.")
            util.tap_on(device, attrs={'text': "Profile"})
            if "add bio" in xml or "Add bio" in xml or "Add friends" in xml or "Set up profile" in xml:
                print("Account signed-in! Quitting.")
                break