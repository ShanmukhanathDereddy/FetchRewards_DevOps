#! /usr/bin/python3
'''
Fetch Rewards Coding Assessment - DevOps Engineer

Shanmukhanath Dereddy
dereddyshanmukhanath@gmail.com
'''

import yaml
import boto3
from collections import defaultdict
import traceback

# IP range of machines requiring SSH access
MYIP = '0.0.0.0/0'


with open('config.yaml', 'r') as conff:
    try:
        conf = yaml.safe_load(conff)
    except yaml.YAMLError as e:
        print(e)

try:
    ec2 = boto3.resource('ec2')
    conf = conf['server']
    vol1 = conf['volumes'][0]
    vol2 = conf['volumes'][1]
    user1 = conf['users'][0]
    user2 = conf['users'][1]

    # create keypairs
    outfile = open('fetchrewards-keypair.pem', 'w')
    
    key_pair = ec2.create_key_pair(KeyName='fetchrewards-keypair')
    outfile.write(str(key_pair.key_material))
    
    ami = conf['ami_type']
    ami += '-' + conf['virtualization_type']
    ami += '-' + conf['architecture']

    user_data = '#!/bin/bash\n'
    # mount vol2
    user_data += 'mkfs.%s %s\n'        % (vol2['type'], vol2['device'])
    user_data += 'mkdir %s\n'          % (vol2['mount'])
    user_data += 'mount -o rw %s %s\n' % (vol2['device'], vol2['mount'])
    # create user1
    user_data += 'adduser %s\n'        % (user1['login'])
    user_data += 'mkdir /home/%s/.ssh\n' % (user1['login'])
    user_data += 'touch /home/%s/.ssh/authorized_keys\n' % (user1['login'])
    user_data += 'echo %s > /home/%s/.ssh/authorized_keys\n' % (user1['ssh_key'], user1['login'])
    # create user2
    user_data += 'adduser %s\n'        % (user2['login'])
    user_data += 'mkdir /home/%s/.ssh\n' % (user2['login'])
    user_data += 'touch /home/%s/.ssh/authorized_keys\n' % (user2['login'])
    user_data += 'echo %s > /home/%s/.ssh/authorized_keys\n' % (user2['ssh_key'], user2['login'])

    # create a new EC2 instance
    instances = ec2.create_instances(
        KeyName='fetchrewards-keypair',
        ImageId='ami-089a545a9ed9893b6',
        InstanceType=conf['instance_type'],
        MinCount=conf['min_count'],
        MaxCount=conf['max_count'],
        UserData=user_data,
        BlockDeviceMappings=[
            {
                'DeviceName': vol1['device'],
                'Ebs': {
                    'VolumeSize': vol1['size_gb']
                }
            },
            {
                'DeviceName': vol2['device'],
                'Ebs': {
                    'VolumeSize': vol2['size_gb']
                }
            }
        ]
    )
    # wait for instance initialization
    print('Instance created, initialization pending ... ')
    instanceIds=[instances[0].id]
    waiter = ec2.meta.client.get_waiter('instance_running')
    waiter.wait(InstanceIds=instanceIds)
    print(' ... running!')

    print('Authorizing security group ingress for SSH ...')
    try:
        # allow inbound ssh rules
        client = boto3.client('ec2')
        describe = client.describe_instances()
        sgId = describe['Reservations'][-1]['Instances'][0]['SecurityGroups'][0]['GroupId']
        resp = client.authorize_security_group_ingress(
            GroupId=sgId,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': MYIP}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': MYIP}]}
        ])
        # (same as via cli)
        # $> aws ec2 describe-instance-attribute --instance-id instance_id --attribute groupSet
        # $> aws ec2 authorize-security-group-ingress --group-id security_group_id --protocol tcp --port 22 --cidr MYIP
    except Exception as e:
        traceback.print_exc()
        print(' .. ')

    print('Instance public ip address:')
    instance = list(filter(lambda x: x['Instances'][0]['InstanceId']==instances[0].id, describe['Reservations']))
    print(instance[0]['Instances'][0]['PublicIpAddress'])

except Exception as e:
    print(type(e).__name__)
    print('Could not create instance.')
    traceback.print_exc()