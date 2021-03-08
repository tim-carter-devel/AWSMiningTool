# AWS Account Miner

 A script to automagically data mine, visualize and threat model an AWS account.  This project will always be incomplete, as we can continually better data from Amazon Web Services (AWS).

 ## Requirements

 - Python 3+ with the following modules:
   - [dnspython](https://github.com/rthalley/dnspython)
   - [diagrams](https://github.com/mingrammer/diagrams)
 - [boto3](https://github.com/boto/boto3)
 - [awscli](https://github.com/aws/aws-cli)

 ## How does it work?

 This tool uses boto3, the Python AWS SDK, to make the API calls into a specified AWS account.  Once authenticated, it gathers data from the following services in the account*:

- CloudFront
- Elastic Beanstalk
- EC2
- Elastic File System
- ELastic Load Balancer .v2
- DynamoDB
- Route53
- RDS
- S3
- WAF .v1 & .v2   

* This list is always expanding as I work on this tool over time

This data is organized into a dictionary and used a reference for diagramming.  The dictionary is saved as a JSON file and passed to the visualizer, which builds the diagram objects in tiers.  The diagram is exported as a PNG and saved to a designated target directory.
 
 ## Getting Started

 ### Install your dependencies:
 ```
 pip install awscli boto3 diagrams dnspython
 ```
 ### AWS Permissions
 Create a role to access AWS services with the _SecurityAudit_ and _WAFReadOnlyAccess_ managed policies attached.
 ### Command Line Options
 ```
 usage: main.py [-h] [-p] [-d] [-t]

optional arguments:
  -h, --help     show this help message and exit
  -p, --profile  specify a configuration profile
  -d, --debug    enable expanded logging and dummy data
  -t, --test     debug mode and existing profiles are cleared

  ```
### Authentication
Use the auth_connector, not included, to authenticate against the AWS account.  From a high level, this will:
- Authenticate
- Call AssumeRole to access the role you previously created
- Return a temporary set of credentials good for the session
- Close that session when we're done, wiping out our temporary credentials

### First Time Run
When the tool is run, it detects whether configuration profiles have been created for the script.  If a profile was not passed as an argument and no profile called 'default' exists, the tool sends you through a Setup Wizard to configure your first profile.  You are greeted by the following prompt:

```

      __          _______                                     _     __  __ _
     /\ \        / / ____|     /\                            | |   |  \/  (_)
    /  \ \  /\  / / (___      /  \   ___ ___ ___  _   _ _ __ | |_  | \  / |_ _ __   ___ _ __ 
   / /\ \ \/  \/ / \___ \    / /\ \ / __/ __/ _ \| | | | '_ \| __| | |\/| | | '_ \ / _ \ '__|
  / ____ \  /\  /  ____) |  / ____ \ (_| (_| (_) | |_| | | | | |_  | |  | | | | | |  __/ |   
 /_/    \_\/  \/  |_____/  /_/    \_\___\___\___/ \__,_|_| |_|\__| |_|  |_|_|_| |_|\___|_|   
---------------------------------------------------------------------------------------------

This appears to be your first time using this tool.  Is this true? [Y/n]:
```
If you respond affirmatively, you will be prompted to enter the following information:
- Profile name [DEFAULT]
- AWS Default Region [us-east-1]
- Identity Provider [None]
- Multifactor authentication [None]
- Logging Format [%(asctime)-15s %(name)8s: %(message)s]
- Log Level

This information gets saved into .ini files that will serve as our configuration profiles for future runs.  Once you have set up a profile, refer to it thusly:
```
python main.py -p <profile name>
```

### AWS Data Collection
Once the tool is able to authenticate against an AWS and assume a role with adequate permissions, it builds a dictionary based on that account's architecture.  If you would like a reference model for an account, you can look at [_account_reference.json_](accounts/account_reference.json).




 
