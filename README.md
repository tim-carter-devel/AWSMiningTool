# AWS Account Miner

 A script to automagically data mine, visualize and threat model an AWS account.  This project will always be incomplete, as we can continually better data from Amazon Web Services (AWS).

 ## Requirements

 - Python 3+ with the following modules:
   - [dnspython](https://github.com/rthalley/dnspython)
   - [diagrams](https://github.com/mingrammer/diagrams)
 - [boto3](https://github.com/boto/boto3)
 - [awscli](https://github.com/aws/aws-cli)

 ## Usage

 First, there are still some manual entries that need to be made:

 1. This script is not multi-regional yet, so you need to enter your default region under the Global Variable Declaration.

 ```
####################################
#   GLOBAL VARIABLE DECLARATION    #
####################################

# AWS Variables
ACCOUNT = {}
DEFAULT_REGION = 'us-east-1'
 ```

2. I currently create access using the 'SecurityAudit' managed policy.  This does not have access to call the Account Alias, so it needs to be manually entered until I create a custom policy with only the permissions needed using Access Advisor.

```
266     global acct_alias
267     acct_alias = 'AccountAlias'
```

3. 

