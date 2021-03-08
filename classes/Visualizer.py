import classes.ArgParser
from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.database import Dynamodb
from diagrams.aws.general import General
from diagrams.onprem.dns import Coredns
from diagrams.aws.general import Users
from diagrams.aws.network import CloudFront
from diagrams.aws.network import ElasticLoadBalancing
from diagrams.aws.network import InternetGateway
from diagrams.aws.network import Route53
from diagrams.aws.network import VPC
from diagrams.aws.network import VPCPeering
from diagrams.aws.security import WAF
from diagrams.aws.storage import ElasticFileSystemEFS
from diagrams.aws.storage import SimpleStorageServiceS3
from itertools import zip_longest
import json

class Visualizer:
    # Constructor Method
    def __init__(self):
        ## Fetch the account dictionary
     
        # Stylesheets
        self.region_sheet = { 'bgcolor': 'white', 'style': 'dashed', 'pencolor': 'blue' }
        self.row_sheet = { 'bgcolor': 'transparent', 'style': 'solid', 'pencolor': 'white' }
        ## Create diagram lists to group VPC elements
        self.vpcs = []
        self.igws = []
        self.ec2_instances = []
        self.elb_subnets = []
        self.peer_conn = []
        # Track all of the components involved with ingress/egress to the VPC
        self.ingress = []
        self.egress = []
        ## Variables to check for components to help flow connection later
        ##  Cloudfront check
        self.cf_check = False
        ## Internet Gateway check
        self.ig_check = False
        ## Elastic Load Balancing check
        self.elb_check = False

    # Instance Methods
    def build_arch_diag(self, account_dict, account_refs_dict):
        with Diagram(account_dict['account_alias'], show=True, direction="TB"):
            ## TIER 1: EXTERNAL TO AWS CLUSTERLESS
            ## Contains: Users, DNS, WAF, CloudFront, Cross Account VPC Peering (happens out of order)
            ## -------------------------------------------------------------------------------
            
            ## Users
            users = Users('Actors')
            self.ingress.append(users) 
            ## DNS
            if account_dict['dns']['name'] == 'Route53':
                dns = Route53('Route53')
            else:
                dns = TradicionalServer('External DNS')
            self.ingress.append(dns)
            ## WAF
            try:
                if account_dict['waf']['cloudfront']:
                    waf = WAF('WAF - CloudFront')
            except KeyError:
                waf = None    
            ## CloudFront
            if self.check_key(account_dict, 'cf'):
                cloudfront = CloudFront('CloudFront')
                self.ingress.append(cloudfront)
                cf_check = True
            ## CAVP
            cross_accounts = self.check_cross_account_refs(account_dict)

            ## TIER 2:  ACCOUNT CLUSTER
            ## Contains: CAVP Accounts, Account ID, Account Alias, Global S3 Buckets
            ## -------------------------------------------------------------------------------
            
            ## CAVP Accounts
            for x_account in cross_accounts:
                ## Since x_account is the key value for the account dict -
                xaccount_dict = cross_accounts['{}'.format(x_account)]
                ## Next with Accepter Accounts/VPC's/Nodes
                try:
                    if xaccount_dict['xacc_account']:
                        alias = self.get_account_refs(xaccount_dict['xacc_account'], account_refs_dict)
                        with Cluster('Account: {}'.format(alias), graph_attr = { 'margin': '50', 'bgcolor': 'white', 'penwidth': '5'}):    
                            ## Make the cross account VPC
                            with Cluster(xaccount_dict['xacc_vpc'], graph_attr = { 'bgcolor': 'white' }):
                                ## Create the accuester node and add it to the dictionary with the
                                ## Connection ID for diagram connection later.
                                xacc_node = VPCPeering('VPC Peering - Accepter')
                                cross_accounts['{}'.format(x_account)]['xacc_node'] = xacc_node
                except KeyError:
                    try:
                        if xaccount_dict['xreq_account']:
                            alias = self.get_account_refs(xaccount_dict['xreq_account'], account_refs_dict)
                            with Cluster('Account: {}'.format(alias), graph_attr = { 'margin': '50', 'bgcolor': 'white', 'penwidth': '5'}):    
                                ## Make the cross account VPC
                                with Cluster(xaccount_dict['xreq_vpc'], graph_attr = { 'bgcolor': 'white' }):
                                    ## Create the Requester node and add it to the dictionary with the
                                    ## Connection ID for diagram connection later.
                                    xreq_node = VPCPeering('VPC Peering - Requester')
                                    cross_accounts['{}'.format(x_account)]['xreq_node'] = xreq_node
                    except KeyError:
                        continue
            

            ## Account ID and Alias
            with Cluster('Account: {}'.format(account_dict['account_alias']), graph_attr = { 'margin': '150', 'bgcolor': 'white', 'penwidth': '5'}):
                
                ## Global S3 Buckets
                s3_overflow = {}
                ## Diagram S3's in alternate Regions
                for s3 in account_dict['s3']:
                    if s3['region'] == None:
                        s3_node = SimpleStorageServiceS3(s3['Name'])
                    else:
                        ## If the S3 bucket isn't in one of our known AZ's, 
                        ## append to a list for the new region
                        if s3['region'] in s3_overflow.keys():
                            s3_overflow[s3['region']].append(s3)
                        else:    
                            ## If the S3 in a region that doesn't have an existing AZ,
                            ## create a new key for the region and put the nodes in it
                            for az in account_dict['az']:
                                if az['RegionName'] != s3['region']:
                                    s3_overflow[s3['region']] = []
                                    s3_overflow[s3['region']].append(s3)

                ## Create new cluster for each region in s3_overflow 
                for region in account_dict['regions']:
                    if region in s3_overflow.keys():
                        with Cluster(region,  graph_attr = { 'bgcolor': 'white', 'style': 'dashed', 'pencolor': 'blue' }):
                            for s3 in s3_overflow[region]:
                                s3_node = SimpleStorageServiceS3(s3['Name'])
                
                ## TIER 3:  VPC CLUSTER
                ## Contains: VPC, CAVP, VPC Peering, Internet Gateways, Load balancers, S3 buckets
                ## -------------------------------------------------------------------------------
                
                ## VPC
                for v in range(len(account_dict['vpc'])):
                    ## Dynamically add contents of VPC Cluster
                    with Cluster(account_dict['vpc'][v]['VpcId'], graph_attr = { 'bgcolor': 'white' }):
                        
                        ## CAVP and VPC Peering
                        account_dict['vpc'][v]['RequestNodes'] = []
                        account_dict['vpc'][v]['AcceptNodes'] = []

                        ## Create VPC Peering nodes, but connections can only be made once
                        ## all Requester and Accepter nodes have been created.  Store the nodes
                        ## in a list for later reference, as dynamically created nodes can't be
                        ## referred to uniquely and will need to be iterated upon later.
                        for req in account_dict['vpc'][v]['PeerRequest']:
                            if req['RequesterVpcInfo']['OwnerId'] == account_dict['account_id']:
                                req_node = VPCPeering('VPC Peering - Requester')
                                cross_accounts[req['VpcPeeringConnectionId']]['req_node'] = req_node

                            
                        for acc in account_dict['vpc'][v]['PeerAccept']:
                            if acc['AccepterVpcInfo']['OwnerId'] == account_dict['account_id']:
                                acc_node = VPCPeering('VPC Peering - Accepter')
                                cross_accounts[acc['VpcPeeringConnectionId']]['acc_node'] = acc_node
                        
                        ## Internet Gateway
                        try:
                            ## Check if Internet Gateway exists
                            if account_dict['igw']:
                                for igw in account_dict['igw']:
                                    for attach in igw['Attachments']:
                                        ## If the IGW is attached to the VPC and available
                                        ## add it to igws list, which we will attach the 
                                        ## previous ingress point to
                                        if attach['VpcId'] == account_dict['vpc'][v]['VpcId'] and attach['State'] == 'attached':
                                            internet_gw = InternetGateway(igw['InternetGatewayId'])
                                            igws.append(internet_gw)
                                            ig_check = True
                            if len(igws) > 0:
                                ## Append igws list to ingress list as the next connection point
                                self.ingress.append(igws)
                        except KeyError:
                            ig_check = False
                        
                        ## Load Balancer
                        try:
                            for elb in account_dict['elb']:
                                ## Check if a WAF is associated with the Load Balancer
                                #waf_check = check_key(elb)
                                elastic_lb = ElasticLoadBalancing('{} ({})'.format(elb['DNSName'], elb['Scheme']))
                                for az in elb['AvailabilityZones']:
                                    elb_tuple = elastic_lb, az['SubnetId']
                                    self.elb_subnets.append(elb_tuple)
                                if elb['Scheme'] == 'internet-facing' and elb['State'] == 'active':
                                    ## If the Load Balancer is internet-facing, a WAF should be put in place
                                    self.ingress.append(elastic_lb)
                                    elb_check = True
                        except KeyError:
                            elb_check = False

                        ## TIER 4:  REGION CLUSTER
                        ## Contains: S3 buckets, WAF Regional, DynamoDB
                        ## -------------------------------------------------------------------------------
                        region_list = self.kill_dupes(account_dict['regions'])

                        for r in range(len(region_list)):
                            for a in range(len(account_dict['az'])):
                                if account_dict['az'][a]['RegionName'] == region_list[r]:
                                    with Cluster(region_list[r],  graph_attr = self.region_sheet):
                                        
                                        for s3 in account_dict['s3']:
                                            if s3['region'] == region_list[r]:
                                                s3_node = SimpleStorageServiceS3(s3['Name'])
                                        ## WAF Regional
                                            ## PLACEHOLDER
                                        ## DynamoDB
                                        for ddb in account_dict['ddb']:
                                            ddb_region = account_dict['ddb'][ddb]['TableArn'].split(':')[3]
                                            if ddb_region == region_list[r]:
                                                ddb_node = Dynamodb(account_dict['ddb'][ddb]['TableName'])

                                        ## TIER 5:  AVAILABILITY ZONE (AZ) CLUSTER
                                        ## Contains: RDS 
                                        ## -------------------------------------------------------------------------------
                                        with Cluster(account_dict['az'][a]['ZoneName'], graph_attr = { 'bgcolor': 'white', 'style': 'dashed', 'pencolor': 'orange' }):
                                            
                                            ## Dynamically add RDS
                                            for rds in account_dict['rds']:
                                                if rds['AvailabilityZone'] == account_dict['az'][a]['ZoneName']:
                                                    rds_node = RDS(rds['DBName'])

                                            ## TIER 6:  SUBNET CLUSTER
                                            ## Contains: Security Groups, EC2 Instances 
                                            ## -------------------------------------------------------------------------------
                                            for s in range(len(account_dict['az'][a]['Subnets'])):
                                                with Cluster(account_dict['az'][a]['Subnets'][s]['SubnetId']):
                                                    for rezzie in account_dict['az'][a]['Subnets'][s]['ec2']:
                                                        for instance in rezzie['Instances']:
                                                            ec2_name = self.get_name_tag(instance, 'EC2')
                                                            ec2_instance = EC2('{} ({})'.format(ec2_name, instance['InstanceType']))
                                                            self.ec2_instances.append(ec2_instance)
                                                            ## If there is a load balancer, and the load balancer connects
                                                            ## to the subnet of the EC2 instance, connect the ELB to the
                                                            ## EC2 instance in the diagram
                                                            for elb_tuple in self.elb_subnets:
                                                                if account_dict['az'][a]['Subnets'][s]['SubnetId'] == elb_tuple[1]:
                                                                    self.ingress [-1] >> elb_tuple[0] >> ec2_instance

            for i in range(len(self.ingress)):
                try:
                    self.ingress[i] >> self.ingress[i+1]
                except IndexError:
                    error = "Dead end, baby."

            for conn in cross_accounts:
                try:
                    req_node = cross_accounts[conn]['xreq_node']
                    acc_node = cross_accounts[conn]['acc_node']
                    req_node >> acc_node
                except KeyError:
                    continue

           
        
    def check_cross_account_refs(self, account_dict):
        ## There will be references to objects in other AWS Accounts,
        ## so we need a way to reference other account aliases by ID
        
        account_refs = {}
        ## Each nested dict in account_refs should look like this:
        ##{
        #   'VpcConnectionId' {
        #       'xacc_account': AccountId,
        #       'xacc_vpc': VpcId,
        #       'xacc_node: VPCPeering Node,
        #       'xreq_account': AccountId,
        #       'xreq_vpc': VpcId,
        #       'xreq_node: VPCPeering Node, 
        #   }
        # }

        ## Use Case: VPC Peering
        for vpc in account_dict['vpc']:
            ## First, find cross account references in Accepter peering connections
            for acc in vpc['PeerAccept']:
                
                conn = acc['VpcPeeringConnectionId']
                acc_owner = acc['AccepterVpcInfo']['OwnerId']
                acc_vpc = acc['AccepterVpcInfo']['VpcId']
                if acc_vpc != vpc['VpcId']:
                    account_refs['{}'.format(conn)] = {
                        'xacc_account':  acc_owner, 
                        'xacc_vpc':  acc_vpc
                    }
                req_owner = acc['RequesterVpcInfo']['OwnerId']
                req_vpc = acc['RequesterVpcInfo']['VpcId']
                if req_vpc != vpc['VpcId']:
                    account_refs['{}'.format(conn)] = {
                        'xreq_account':  req_owner, 
                        'xreq_vpc':  req_vpc
                    }
        return account_refs

    def check_key(self, dict, key): 
        ## Loop through keys looking for a value and return boolean  
        if key in dict.keys(): 
            return True 
        else: 
            return False

    def get_acc_node(self, req_peer):
        for vpc in account_dict['vpc']:
            for acc in vpc['AcceptNodes']:
                print(acc)
                if acc.label == req_peer.label:
                    return acc

    def get_account_refs(self, account_id, account_refs_dict):
        ## Given an account id, we use account_reference.json to marry that to its alias
        alias = account_refs_dict[account_id]
        return alias

    def get_name_tag(self, obj_dict, default_label):
        for tag in obj_dict['Tags']:
            if tag['Key'] == 'Name':
                return tag['Value']
            elif default_label:
                return default_label
            else:
                return 'Name Unknown'

    def kill_dupes(self, dupe_list):
        ## Remove duplicate entries from a list
        dedupe_list = list(dict.fromkeys(dupe_list))

        return dedupe_list

    def mount_efs(self, mode):
        ## In order to diagram EFS, we need to determine which
        ## subnet the EFS Mount Target is in
        for efs in account_dict['efs']:
            for mt in efs['MountTargets']:
                efs_subnet = mt['SubnetId']
                efs_az = mt['AvailabilityZoneId']
                efs_vpc = mt['VpcId']

                ## If the EFS Mount Target is in an AZ and subnet not yet associated
                ## in our diagram, but is in the this VPC, create the node in the VPC
                if mode == 'az':
                    for az in account_dict['az']:
                        if az['ZoneId'] == efs_az:
                            efs_node = ElasticFileSystemEFS(efs['Name'])
                            return efs_node
                        else:
                            return None
                elif mode == 'subnet':
                    for az in account_dict['az']:
                        for subnet in az['Subnets']:
                            if subnet['SubnetId'] == efs_subnet:
                                efs_node = ElasticFileSystemEFS(efs['Name'])
                                return efs_node
                            else:
                                return None
                elif mode == 'vpc':
                    for vpc in account_dict['vpc']:
                        if subnet['VpcId'] == efs_vpc:
                            efs_node = ElasticFileSystemEFS(efs['Name'])
                            return efs_node
                        else:
                            return None