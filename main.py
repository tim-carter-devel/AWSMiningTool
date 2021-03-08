#############################################################################################
#                                                                                           #
#              ,,                                                                           #
#    MMP""MM""YMM db                    .g8"""bgd                   mm                      #
#    P'   MM   `7                     .dP'     `M                   MM                      #
#         MM    `7MM `7MMpMMMb.pMMMb. dM'       ` ,6"Yb. `7Mb,od8 mmMMmm .gP"Ya `7Mb,od8    # 
#         MM      MM   MM    MM    MM MM         8)   MM   MM' "'   MM  ,M'   Yb  MM' "'    #
#         MM      MM   MM    MM    MM MM.         ,pm9MM   MM       MM  8M""""""  MM        #
#         MM      MM   MM    MM    MM `Mb.     ,'8M   MM   MM       MM  YM.    ,  MM        #
#       .JMML.  .JMML.JMML  JMML  JMML. `"bmmmd' `Moo9^Yo.JMML.     `Mbmo`Mbmmd'.JMML.      #
#                                                                                           #
#                                                                                           #
#       WARNING: All code included in this file and all files related to its function       #
#       are the intellectual property of Timothy Carter and should not used in part or      #
#       in whole, reproduced or repurposed without explicit permission.                     #
#                                                                                           #
#                                                                                           #
#       The purpose of this code is to access an AWS Account and collect many various       #
#       pieces of information about its architecture, topology and configuration.           #
#       These pieces are used to generate a multilayered, interactive web based diagram     #
#       that threat assessments can more easily be simulated upon.                          #
#                                                                                           #
#############################################################################################

import classes.ArgParser
import classes.SetupWizard
import classes.Visualizer
import lib.os
import lib.view



## REGION: FUNCTION DEFINITIONS

def main():
    ## Intro
    lib.view.intro()
    
    # Check to see if .conf files exist
    conf_list = ['aws.conf', 'local.conf']
    conf_check = lib.os.files_exist('conf/', conf_list)

    if conf_check:
        ## Parse arguments
        arg_parser = classes.ArgParser.ArgParser()
        ## Select profile
        profile_name = arg_parser.get_profile()
        aws_dict = lib.os.read_config('conf/', 'aws.conf', profile_name)
        local_dict = lib.os.read_config('conf/', 'local.conf', profile_name)
        profile = classes.Profile.Profile(profile_name, local_dict['hostname'], local_dict['ip_address'], aws_dict['region'], aws_dict['idp'], aws_dict['mfa'] )
        
        if profile.name == "test" or profile.name == "debug":
            ## Visualize Dummy Data
            visualizer = classes.Visualizer.Visualizer()
            account_json = "example.json"
            account_refs_json = "account_reference.json"
            account_dict = lib.os.json_to_dict(account_json)
            account_refs_dict = lib.os.json_to_dict(account_refs_json)
            visualizer.build_arch_diag(account_dict, account_refs_dict)
        else:
            ## Create new account dictionary and visualize
            print("Instantiate AWS Class")
    else:
       first_time = lib.view.first_check()
       if first_time:
            # The Setup Wizard collects config information from the end user
            setup_wizard = classes.SetupWizard.SetupWizard()
            # Write configs
            profile = setup_wizard.profile
            aws_check = lib.os.write_config('conf/', 'aws.ini', profile, setup_wizard.aws)
            local_check = lib.os.write_config('conf/', 'local.ini', profile, setup_wizard.local)

            #if aws_check and local_check:
                #logger.info("Profile created: {}".format(profile))


## REGION:  CODE EXECUTION

main()






                                                                        
                                                                                    
                                                                                    





