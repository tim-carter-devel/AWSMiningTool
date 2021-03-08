import re
import socket

class SetupWizard:
    # Constructor Method
    def __init__(self):
        self.profile = self.profile_name()
        self.aws = self.build_aws()
        self.local = self.build_local()
        self.logging = self.build_logging()

    def build_aws(self):
        ## Build_AWS Function
        ## Description:     Collects information required to create a session within a specified
        ##                  AWS account and region, and writes those values to a config file.    
        ## Arguments:       None
        ## Return:          conf_dict - dict - key/value pairs of our AWS config parameters.
        print("\nAWS Configuration")
        print('---------------------------------------------------------------------------------------\n')
        conf_dict = {}
        # Validate input for Region: [str]-east/west-[0-9]
        conf_dict['region'] = self.validate_inputs("us-east-1", "AWS Default Region [us-east-1]: ", "[a-zA-Z]+-east-\d|[a-zA-Z]+-west-\d")
        # Validate input for IdP: No special characters
        conf_dict['idp'] = self.validate_inputs("None", "Identity Provider: ", '(?![!@#$%^&*(),.?":{}|<>])')
        # Validate input for SSO: No special characters
        conf_dict['mfa'] = self.validate_inputs("None", "Multifactor Authentication: ", '(?![!@#$%^&*(),.?":{}|<>])')
        return conf_dict



    def build_local(self):
        ## Build_Local Function
        ## Description:     Collects information from the local environment and writes those values to a config file.    
        ## Arguments:       None
        ## Return:          conf_dict - dict - key/value pairs of our local config parameters.
        print("\nLocal Configuration")
        print('---------------------------------------------------------------------------------------\n')
        conf_dict = {}
        # Hostname for IP retrieval
        conf_dict['hostname'] = socket.gethostname()
        print("Hostname: {}".format(conf_dict['hostname']))
        # IP address
        conf_dict['ip_address'] = socket.gethostbyname(conf_dict['hostname'])
        print("IP Address: {}".format(conf_dict['ip_address']))
        return conf_dict

    def build_logging(self):
        ## Build_Logging Function
        ## Description:     Collects information pertinent to logging and writes those values to a config file.    
        ## Arguments:       None
        ## Return:          conf_dict - dict - key/value pairs of our logging config parameters.
        print("\nLogging Configuration")
        print('---------------------------------------------------------------------------------------\n')
        conf_dict = {}
        # Validate input for log format: None
        conf_dict['format'] = self.validate_inputs('datetime', "Log Format (datetime) [%(asctime)-15s %(name)8s: %(message)s]: ", "")
        # Validate input for log level: info, warning, error, critical
        print("""
        ---------------------------------------------------------------------------
        |    INFO    |    WARNING    |    ERROR    |    CRITICAL    |    DEBUG    |
        ---------------------------------------------------------------------------
        """)
        conf_dict['level'] = self.validate_inputs("debug", "Log Level [DEBUG]: ", 'INFO|WARNING|ERROR|CRITICAL|DEBUG')
        return conf_dict
    
    def profile_name(self):
        ## Profile_Name Function
        ## Description:     Prompts user for profile name.
        ## Arguments:       None
        ## Return:          profile - string - the chosen name of the profile.
        print("\nS E T U P   W I Z A R D")
        print('---------------------------------------------------------------------------------------\n')
        # Validate input for Profile Name: No special characters
        profile = self.validate_inputs("default", "Profile Name [default]: ",  '(?![!@#$%^&*(),.?":{}|<>])')
        return profile 
    
    def validate_inputs(self, default, prompt, regex):
        ## Validate_Inputs
        ## Description:     Prompts for input and validates the response based on a regular expression until
        ##                  it receives a valid response.    
        ## Arguments:       prompt - string - the text that prompts the user for a response
        ##                  regex - string - a regular expression detecting the expected response format
        ## Return:          response - string - the validated input.
        valid = None
        while valid is None:
            response = str(input(prompt) or default)
            pattern = re.compile(regex)
            valid = pattern.match(response)
            if valid is None:
                print("The value you've entered is invalid. Please try again.")
            else:
                return response

