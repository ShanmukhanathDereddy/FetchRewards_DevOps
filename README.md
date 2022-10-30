# Fetch Rewards DevOps

## Description
 
Develop an automation program that takes a YAML configuration file as input and deploys a Linux AWS EC2 instance with two volumes and two users.

Here are some guidelines followed:

- Used Python and Boto3 to create resources
- Not used configuration management, provisioning, or IaC tools such as Ansible, CloudFormation, Terraform, etc.

## Outcome:

- Run the program
- Deploys the virtual machine
- SSH into the instance as user1 and user2
- Read from and write to each of two volumes

## Setup:

First ensure to install python3, pip, awscli, boto3 and pyyaml on the machine. I have used Ubuntu So On Ubuntu run the following commands

`sudo apt-get install python3`

`pip3 install awscli boto3 pyyaml`

Second need to create an AWS User with Programmatic access and with full permission to EC2.

![alt text](http://url/to/img.png)


The Script in `config.yaml` will provision the VM, users and volumes

`python fetchRewards.py`

The image may take a minute to initialize. (Pending status)

A key-pair is created fetchrewards-keypair.pem. If you see this error,

Be sure to change the mode to read-only.

`chmod 400 fetchrewards-keypair.pem`

## Testing

SSH into the instance with the new keypair or your user1 or user2 keypair. The instance public IP should be displayed after the deployment runs, or see in your AWS console.

`ssh -i fetchrewards-keypair.pem ec2-user@--instance public ip goes here--`

`ssh -i mykeypair.pem user1@--instance public ip goes here--`


##Resources

https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#how-to-generate-your-own-key-and-import-it-to-aws
https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console
https://blog.ipswitch.com/how-to-create-an-ec2-instance-with-python 
https://boto3.amazonaws.com/v1/documentation/api/latest/index.html 
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/authorizing-access-to-an-instance.html 
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ec2-example-security-group.html 
