import boto3

class AWS:
    # Constructor Method
    def __init__(self, account_id, account_name, access_key, secret_key, session_token):
        self.account_id = account_id
        self.account_alias = account_alias
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token
        self.creds = '/home/{}/.aws/credentials'.format(user)
        self.config = '/home/{}/.aws/config'.format(user)
        logging.debug('Creds: {} Config: {}'.format(creds, config))

        ## Check if AWS profile exists
        self.cred_check = self.alter_aws_profiles(self.creds,'check')
        self.config_check = self.alter_aws_profiles(self.config, 'check')
        
        if cred_check is True & config_check is True:
            print('AWS Profiles were located. Creating session...')
            logging.info('AWS Profiles were located.')
            ## Create session and all clients needed
            self.session = boto3.Session(profile_name='default')
            self.cf_client = self.session.client('cloudfront', region_name = 'us-east-1')
            self.ebs_client = self.session.client('elasticbeanstalk', region_name = 'us-east-1')
            self.ec2_client = self.session.client('ec2', region_name = 'us-east-1')
            self.efs_client = self.session.client('efs', region_name = 'us-east-1')
            self.elb_client = self.session.client('elbv2', region_name = 'us-east-1')
            self.ddb_client = self.session.client('dynamodb', region_name = 'us-east-1')
            self.r53_client = self.session.client('route53')
            self.rds_client = self.session.client('rds', region_name = 'us-east-1')
            self.s3_client = self.session.client('s3', region_name = 'us-east-1')
            self.waf_client = self.session.client('wafv2', region_name = 'us-east-1')
            print('Session created. Gathering account information...')
        
            logging.debug('Account ID: {} Account Alias: {}'.format(self.account_id, self.account_alias))
            print('Account ID: {} Account Alias: {}'.format(self.account_id, self.account_alias))

            account_dict = self.make_account_dict(self.account_alias, self.account_id)

            self.save_account_dict()

    # Instance Methods
    def alter_aws_profiles(self, profile, mode):
        ## Return a boolean value based on whether the profiles exist after function completes
        logging.debug('alter_aws_profiles({}, {})'.format(profile, mode))
        
        ## Check file existence
        if os.path.isfile(profile):
            ## If mode is clear, open the file, truncate all contents, close and return False
            if mode == 'clear':
                logging.debug('Deleting {}...'.format(profile))
                cred = open(profile,'r+')
                cred.truncate(0)
                cred.close()
                logging.debug('{} deleted and closed.'.format(profile))
                ## Since the profile data is now erased, return False
                return False
            ## If all we are doing is checking for the file's existence, just return true!
            elif mode == 'check':
                logging.debug('AWS Profiles file [{}] exists.'.format(profile))
                return True
        else:
            return False

    def get_authoritative_nameserver(self, domain, log=lambda msg: None):
        name = dns.name.from_text(domain)
        depth = 2
        default = dns.resolver.get_default_resolver()
        nameserver = default.nameservers[0]
        last = False
        while not last:
            s = name.split(depth)

            last = s[0].to_unicode() == u'@'
            sub = s[1]

            log('Looking up %s on %s' % (sub, nameserver))
            query = dns.message.make_query(sub, dns.rdatatype.NS)
            response = dns.query.udp(query, nameserver)

            rcode = response.rcode()
            if rcode != dns.rcode.NOERROR:
                if rcode == dns.rcode.NXDOMAIN:
                    raise Exception('%s does not exist.' % sub)
                else:
                    raise Exception('Error %s' % dns.rcode.to_text(rcode))

            rrset = None
            if len(response.authority) > 0:
                rrset = response.authority[0]
            else:
                rrset = response.answer[0]

            rr = rrset[0]
            if rr.rdtype == dns.rdatatype.SOA:
                log('Same server is authoritative for %s' % sub)
            else:
                authority = rr.target
                log('%s is authoritative for %s' % (authority, sub))
                nameserver = default.query(authority).rrset[0].to_text()

            depth += 1

        return nameserver

    def make_account_dict(self, account_alias, account_id):
        ## This dictionary should always reflect the structure
        ## of the diagram.  

        ## TIER 1: EXTERNAL TO AWS CLUSTERLESS
        ## Contains: DNS, WAF, CloudFront, Cross Account VPC Peering (happens out of order)
        ## -------------------------------------------------------------------------------

        ## DNS
        self.capture_dns()
        ## WAF
        #capture_waf()
        ## CloudFront
        self.capture_cloudfront()
        ## Cross Account VPC Peering (CAVP)
        ## CAVP actually happens during VPC capture

        ## TIER 2:  ACCOUNT CLUSTER
        ## Contains: Account ID, Account Alias, CAVP Accounts, Global S3 Buckets
        ## -------------------------------------------------------------------------------

        ## Account Alias
        self.alias = account_alias
        ## Account ID
        self.acct_id = account_id
        ## CAVP
        ## CAVP Accounts actually happen during VPC capture
        ## Global S3 Buckets (but we actually populate all of them at the same time)
        capture_s3()

        ## TIER 3:  VPC CLUSTER
        ## Contains: VPC, CAVP, VPC Peering, Int Gateways, Load balancers, WAF, S3 buckets
        ## -------------------------------------------------------------------------------

        ## VPC
        capture_vpcs()
        for vpc in self.vpc:
            ## CAVP & VPC Peering
            capture_vpc_peering(vpc['VpcId'])
        ## Internet Gateways
        capture_internetgw()
        ## Load Balancers
        capture_loadbalancer()

        ## S3
        ## S3 buckets already captured

        ## TIER 4:  REGION CLUSTER
        ## Contains: S3 buckets, WAF Regional, DynamoDB
        ## -------------------------------------------------------------------------------

        ## S3
        ## S3 buckets already captured
        ## WAF Regional
        ## PLACEHOLDER, but presumably, WAF Regional already captured with Global WAF calls
        ## DynamoDB
        capture_dynamodb()

        ## TIER 5:  AVAILABILITY ZONE (AZ) CLUSTER
        ## Contains: Availability Zones, RDS Instances, EFS Mount targets
        ## -------------------------------------------------------------------------------

        ## Availability Zones
        capture_az()
        ## RDS Instances
        capture_rds()
        ## Capture EFS
        capture_efs()

        ## TIER 6:  SUBNET CLUSTER
        ## Contains: Subnets, Security Groups, EC2 Instances 
        ## -------------------------------------------------------------------------------

        ## Subnets
        capture_subnets()                                        
        ## Security Groups
        capture_secgroups()
        ## EC2 Instances
        capture_ec2()

    def save_account_dict(self):
        ## JSON dump account dictionary into file
        with open('./accounts/{}.json'.format(acct_alias), "w") as outfile:  
            json.dump(ACCOUNT, outfile, default=time_converter, indent=2) 

    def time_converter(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        raise TypeError (f"{type(obj)} not datetime")

    ## Capture methods - collects information from AWS Account
    def capture_az(self):
        raw_az = ec2_client.describe_availability_zones()
        self.az = raw_az['AvailabilityZones']

    def capture_cloudfront(self):
        raw_cloudfront = cf_client.list_distributions()
        try:
            self.cloudfront = raw_cloudfront['DistributionList']['Items']
        except KeyError:
            self.cloudfront = []

    def capture_dns(self):
        ## Is it Route53?
        dns = {
            'name': '',
        }
        try:
            ## if there are zones created, Route53 is enabled
            dns_zones = r53_client.list_hosted_zones()
            if dns_zones['HostedZones']:
                dns['name'] = 'Route53'
                dns['zones'] = dns_zones['HostedZones']

                ## Check for Route53 monitoring
                health_checks = r53_client.list_health_checks()
                if health_checks['HealthChecks']:
                    dns['monitoring'] = True
                    dns['checks'] = health_checks['HealthChecks']
                else:
                    dns['monitoring'] = False
                
                ## Capture DNS policies
                policies = r53_client.list_traffic_policies()
                if policies['TrafficPolicySummaries']:
                    dns['policies'] = policies['TrafficPolicySummaries']
                else:
                    dns['policies'] = None
                
                ## Capture DNS Records
                for zone in dns['zones']:
                    dns['records'] = []
                    zone_recs = r53_client.list_resource_record_sets(HostedZoneId=zone['Id'])
                    dns['records'].append({
                        'zone': zone['Id'],
                        'records': zone_recs
                    })
            else:
                #### PLACEHOLDER: This is where we would collect network info and determine domain/DNS
                dns['name'] = 'Other'
                ## get_authoritative_nameserver()  
            self.dns = dns
        except Exception as error:
            print('Oops!  Something went wrong:[DNS] {}'.format(error))
            exit(1)

    def capture_dynamodb(self):
        raw_ddb = ddb_client.list_tables()
        table_dict = {}

        for table in raw_ddb['TableNames']:
            table_raw = ddb_client.describe_table(TableName=table)
            table_dict[table] = table_raw['Table']

        self.dynamodb = table_dict

    def capture_ec2(self):
        for az in self.az:
            for subnet in self.az['Subnets']:
                ## Describe all EC2 instances in VPC and assign all instances to 'ec2' key in VPC dict
                filters = [{'Name': 'subnet-id', 'Values': [subnet['SubnetId']]}]
                raw_ec2 = ec2_client.describe_instances(Filters=filters)

                # Capture EC2 regions
                for rezzie in raw_ec2['Reservations']:
                    for instance in rezzie['Instances']:
                        ## The Region value is just the AZ minus the last character
                        region = instance['Placement']['AvailabilityZone'][:-1]
                        if region not in self.regions:
                            self.regions.append(region)

                subnet['ec2'] = raw_ec2['Reservations']

    def capture_efs(self):
        raw_efs = efs_client.describe_file_systems()
        self.efs = raw_efs['FileSystems']
        for filesystem in self.efs:
            raw_mounts = efs_client.describe_mount_targets(FileSystemId = filesystem['FileSystemId'])
            filesystem['MountTargets'] = raw_mounts['MountTargets']

    def capture_elasticbs(self):
        raw_ebs = ebs_client.describe_applications()
        self.ebs = raw_ebs['Applications']

    def capture_internetgw(self):
        ## Get all Internet Gateways
        raw_igw = ec2_client.describe_internet_gateways()
        if raw_igw['InternetGateways']:
            self.igw = raw_igw['InternetGateways']

    def capture_loadbalancer(self):
        # Get all Load Balancers and their type
        raw_elb = elb_client.describe_load_balancers()
        if raw_elb['LoadBalancers']:
            self.elb = raw_elb['LoadBalancers']

    def capture_rds(self):
        raw_rds = rds_client.describe_db_instances()
        self.rds = raw_rds['DBInstances']

    def capture_s3(self):
        raw_s3 = s3_client.list_buckets()
        
        ## Since the list_buckets call returns very little terms of specific details,
        ## we will need to do a series of calls to fill out those details.
        for bucket in raw_s3['Buckets']:
            ## Get the Acceleration Config (Enabled/Suspended)
            acc_config = s3_client.get_bucket_accelerate_configuration(Bucket = bucket['Name'])
            try:
                bucket['acc_config'] = acc_config['Status']
            except KeyError:
                bucket['acc_config'] = []
            
            ## Get bucket Access Control List (ACL)
            acl = s3_client.get_bucket_acl(Bucket = bucket['Name'])
            bucket['acl'] = acl['Grants']

            ## Get the Cross Origin Resource Sharing (CORS) configuration
            try:
                raw_cors = s3_client.get_bucket_cors(Bucket = bucket['Name'])
                bucket['cors'] = raw_cors['CORSRules']
            except Exception as e:
                bucket['cors'] = []

            ## Get bucket encryption
            try:
                raw_enc = s3_client.get_bucket_encryption(Bucket = bucket['Name'])
                bucket['encrypt'] = raw_enc['ServerSideEncryptionConfiguration']['Rules']
            except Exception as e:
                bucket['encrypt'] = []

            ## Get lifecycle configuration
            try:
                raw_lcc = s3_client.get_bucket_lifecycle_configuration(Bucket = bucket['Name'])
                bucket['lifecycle'] = raw_lcc['Rules']
            except Exception as e:
                bucket['lifecycle'] = []

            ## Get bucket logging
            try:
                raw_log = s3_client.get_bucket_logging(Bucket = bucket['Name'])
                bucket['logging'] = raw_log['LoggingEnabled']
            except Exception as e:
                bucket['logging'] = []

            ## Get bucket policy
            try:
                raw_pol = s3_client.get_bucket_policy(Bucket = bucket['Name'])
                bucket['policy'] = raw_pol
            except Exception as e:
                bucket['policy'] = []

            ## Get bucket replication
            try:
                raw_rep = s3_client.get_bucket_replication(Bucket = bucket['Name'])
                bucket['replication'] = raw_rep['ReplicationConfiguration']
            except Exception as e:
                bucket['replication'] = []

            ## Get bucket tags
            try:
                raw_tags = s3_client.get_bucket_tagging(Bucket = bucket['Name'])
                bucket['tags'] = raw_tags['TagSet']
            except Exception as e:
                bucket['tags'] = []
            
            ## Get bucket versioning
            try:
                raw_ver = s3_client.get_bucket_versioning(Bucket = bucket['Name'])
                bucket['versioning'] = raw_ver
            except Exception as e:
                bucket['versioning'] = []

            ## Get bucket website
            try:
                raw_web = s3_client.get_bucket_website(Bucket = bucket['Name'])
                bucket['website'] = raw_web
            except Exception as e:
                bucket['website'] = []

            ## Get bucket region
            try:
                raw_region = s3_client.get_bucket_location(Bucket = bucket['Name'])
                bucket['region'] = raw_region['LocationConstraint']

                ## Capture S3 regions
                if bucket['region'] not in self.regions:
                    if bucket['region'] != None:
                        self.regions.append(bucket['region'])

            except Exception as e:
                bucket['region'] = []

        self.s3 = raw_s3['Buckets']

        def capture_secgroups(self):
            ## In each VPC dictionary, add a k/v pair for the VPC's Security Groups
            for vpc in self.vpc:
                ## Fetch Security Group dict's filtered by VPC and assign to 'SecurityGroups' key
                raw_secgroups = ec2_client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc['VpcId']]}])
                vpc['SecurityGroups'] = raw_secgroups['SecurityGroups']

        def capture_subnets(self):
            ## In each Availability Zone dictionary, add a k/v pair for the AZ's subnets
            for az in self.az:
                ## Fetch subnet dict's filtered by AZ and assign to 'subnets' key
                raw_subnets = ec2_client.describe_subnets(Filters=[{'Name': 'availability-zone-id', 'Values': [az['ZoneId']]}])
                az['Subnets'] = raw_subnets['Subnets']

        def capture_vpc_peering(self, vpc_id):
            raw_accept = ec2_client.describe_vpc_peering_connections(Filters=[{'Name': 'accepter-vpc-info.vpc-id', 'Values': [vpc_id]}])
            raw_request = ec2_client.describe_vpc_peering_connections(Filters=[{'Name': 'requester-vpc-info.vpc-id', 'Values': [vpc_id]}])

            for vpc in self.vpc:
                if vpc['VpcId'] == vpc_id:
                    vpc['PeerAccept'] = raw_accept['VpcPeeringConnections']
                    vpc['PeerRequest'] = raw_request['VpcPeeringConnections']

        def capture_vpcs(self):
            ## Fetch account VPC's from ec2 and store in the 'vpc' key
            vpc_raw = ec2_client.describe_vpcs()

            self.vpc = vpc_raw['Vpcs']

        def capture_waf(self):
            raw_cloudfront = waf_client.list_web_acls(Scope='CLOUDFRONT')
            raw_region = waf_client.list_web_acls(Scope='REGIONAL')

            self.waf = { 'regional': raw_region['WebACLs'], 'cloudfront': raw_cloudfront['WebACLs'] }
