def intro():
    ## Intro Function
    ## Description:     Prints out ASCII logo
    ## Arguments:       None
    ## Return:          None
    print('''      __          _______                                     _     __  __ _                 
     /\ \        / / ____|     /\                            | |   |  \/  (_)                
    /  \ \  /\  / / (___      /  \   ___ ___ ___  _   _ _ __ | |_  | \  / |_ _ __   ___ _ __ 
   / /\ \ \/  \/ / \___ \    / /\ \ / __/ __/ _ \| | | | '_ \| __| | |\/| | | '_ \ / _ \ '__|
  / ____ \  /\  /  ____) |  / ____ \ (_| (_| (_) | |_| | | | | |_  | |  | | | | | |  __/ |   
 /_/    \_\/  \/  |_____/  /_/    \_\___\___\___/ \__,_|_| |_|\__| |_|  |_|_|_| |_|\___|_|   ''')
    print('---------------------------------------------------------------------------------------------\n')

def first_check():
    ## First_Check Function
    ## Description:     Checks if this is the first time the script is being run, and if so starts the Setup Wizard
    ## Arguments:       None
    ## Return:          Boolean
    first_time = False
    while not first_time:
        print("This appears to be your first time using this tool.  Is this true? [Y/n]:")
        response = input()
        if response.upper() == 'Y':
            first_time = True
            return first_time
        elif response.lower() == 'n':
            # If No, raise Exception and exit.
            raise Exception("Configuration files are missing or incorrect. Please check them for syntax errors. If you cannot repair them, delete them and run the AWS Mining tool again.")
        else:
            print("You have provided an invalid response. Please try again.")
    