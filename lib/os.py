import configparser
import json
import os

def dict_to_json(dict, filename):
    ## Dict_to_JSON Function
    ## Description:     Takes in a dictionary and writes it to a JSON file.
    ## Arguments:       dict - dict - self explanatory
    ##                  filename - string - the desired name of the JSON file.
    ## Return:          None
    json_dict = json.dumps(dict)
    # now write output to a file
    json_file = open('{}'.format(filename), 'w')
    # Pretty-print for easy debug
    json_file.write(simplejson.dumps(simplejson.loads(json_dict), indent=4, sort_keys=True))
    json_file.close()

def files_exist(path,file_list):
    ## Files_Exist Function
    ## Description:     Determines whether all the files in a list of strings exist.
    ## Arguments:       path - string - The path on the local filesystem to the files in the list.
    ##                  file_list - list - A list of strings, which are references to filenames.
    ## Return:          Boolean
    file_counter = 0
    for item in file_list:
        if os.path.isfile("{}{}".format(path, item)):
            file_counter += 1
    if file_counter == len(file_list):
        return True
    else:
        return False

def json_to_dict(account_json):
    ## JSON_to_Dict Function
    ## Description:     Accepts a JSON block and returns it in dict format
    ## Arguments:       account_json - JSON - self explanatory
    ## Return:          account_dict - dict - self explanatory
    with open('./accounts/{}'.format(account_json)) as json_file: 
        account_dict = json.load(json_file)
        return account_dict

def read_config(path, filename, profile):
    ## Read_Config Function
    ## Description:     Reads configuration files.
    ## Arguments:       path - string - The path on the local filesystem to the files in the list.
    ##                  filename - string - Self explanatory.
    ## Return:          dict
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), path, filename))
    print(config._sections)
    profile_dict = config._sections[profile.lower()]
    return profile_dict

def write_config(path, filename, header, config_dict):
    ## Write_Config Function
    ## Description:     Writes configuration files for the tool upon first time use.
    ## Arguments:       path - string - The path on the local filesystem to the files in the list.
    ##                  filename - string - Self explanatory.
    ##                  header - string - the profile name that will be displayed in the configuration file.
    ##                  config_dict - dict - the key/value pairs that make up the content of the file.
    ## Return:          Boolean
    config = configparser.ConfigParser()
    config[header] = config_dict
    try:
        with open("{}{}".format(path, filename), 'w') as config_file:
            config.write(config_file)
            return True
    except (FileExistsError,FileNotFoundError) as e:
        raise Exception(e)
    