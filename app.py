"""
This script will check the instance health status and take action.
Created By: 7.vivek.raj@gmail.com
"""
import boto3, urllib3, json, os, concurrent.futures
from datetime import datetime
http = urllib3.PoolManager()

"""
Veriables
"""

# Get the values of environment variables
slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
channel_name = os.environ.get('CHANNEL_NAME')
region_name = os.environ.get('REGION_NAME')


# Initialize the EC2 client
session = boto3.Session(region_name=region_name)
ec2 = session.client('ec2')

# Retrieve the instance status
def check_instance():
    """
    Instance Status Check
    """
    failedStausInstance = []
    response = ec2.describe_instance_status()
    for instance in response['InstanceStatuses']:
        if instance['SystemStatus']['Status'] and instance['InstanceStatus']['Status'] != 'ok':
            if instance['SystemStatus']['Status'] and instance['InstanceStatus']['Status'] != 'initializing' and instance['InstanceStatus']['Status'] != 'insufficient-data':
                failedStausInstance.append({
                    "InstanceId": instance['InstanceId'],
                    "SystemStatus": instance['SystemStatus']['Status'],
                    "InstanceStatus": instance['InstanceStatus']['Status']
                })
            else:
                print(str(datetime.now()) + " Working fine " + instance['InstanceId'])
        else:
            print(str(datetime.now()) + " Working fine " + instance['InstanceId'])
            
    print(failedStausInstance)
    return failedStausInstance

def describe_instance(failedStausInstance):
    """
    Checking Instance Tag
    """
    alert = []
    response = ec2.describe_instances()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            for StatusFailed in failedStausInstance:
                if instance['InstanceId'] == StatusFailed['InstanceId']:
                    instanceTagKeys = [tag['Key'] for tag in instance['Tags']]
                    if 'Role' in instanceTagKeys:
                        roleTag = next((tag for tag in instance['Tags'] if tag['Key'] == 'Role'), None)
                        if roleTag['Value'] == 'eks-node':
                            nameTag = next((tag for tag in instance['Tags'] if tag['Key'] == 'Name'), None)
                            if nameTag:
                                for interface in instance['NetworkInterfaces']:
                                    alert.append({
                                        "Name": nameTag['Value'],
                                        "InstanceId": instance['InstanceId'],
                                        "PrivateIpAddress": instance['PrivateIpAddress'],
                                        "OwnerId": interface['OwnerId'],
                                        "Role": "eks-node",
                                        "InstanceStatus": StatusFailed['InstanceStatus'],
                                        "SystemStatus": StatusFailed['SystemStatus']
                                    })
                        else:
                            nameTag = next((tag for tag in instance['Tags'] if tag['Key'] == 'Name'), None)
                            if nameTag:
                                for interface in instance['NetworkInterfaces']:
                                    alert.append({
                                        "Name": nameTag['Value'],
                                        "InstanceId": instance['InstanceId'],
                                        "PrivateIpAddress": instance['PrivateIpAddress'],
                                        "OwnerId": interface['OwnerId'],
                                        "Role": "standalone-node",
                                        "InstanceStatus": StatusFailed['InstanceStatus'],
                                        "SystemStatus": StatusFailed['SystemStatus']
                                    })
                    else:
                        nameTag = next((tag for tag in instance['Tags'] if tag['Key'] == 'Name'), None)
                        if nameTag:
                            for interface in instance['NetworkInterfaces']:
                                alert.append({
                                    "Name": nameTag['Value'],
                                    "InstanceId": instance['InstanceId'],
                                    "PrivateIpAddress": instance['PrivateIpAddress'],
                                    "OwnerId": interface['OwnerId'],
                                    "Role": "standalone-node",
                                    "InstanceStatus": StatusFailed['InstanceStatus'],
                                    "SystemStatus": StatusFailed['SystemStatus']
                                })

    return alert

def stop_instance(alert):
    """
    Stops Instances
    """
    eks_instances = [inst for inst in alert if inst['Role'] == 'eks-node']
    eks_instance_ids = [inst['InstanceId'] for inst in eks_instances]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(stop_instance_parallel, instance_id) for instance_id in eks_instance_ids]
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

    for instance_alert in alert:
        instance_id = instance_alert['InstanceId']
        
        if instance_alert['Role'] == 'standalone-node':
            response = ec2.stop_instances(InstanceIds=[instance_id])
            print(f'Instance {instance_id} stopping: {response}')
            waiter = ec2.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=[instance_id])
            instance = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
            print(f'Instance {instance_id} stopped: {instance["State"]["Name"]}')

            print(f'Starting instance {instance_id}...')
            response = ec2.start_instances(InstanceIds=[instance_id])
            print(f'Instance {instance_id} started: {response}')
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id])
            instance = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
            print(f'Instance {instance_id} running: {instance["State"]["Name"]}')

def stop_instance_parallel(instance_id):
    response = ec2.stop_instances(InstanceIds=[instance_id]) 
    return f'Instance {instance_id} stopped: {response}'

def alert_trigger(alert):
    for alerts in alert:
        slack = []
        slack.append(
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Instance Hardware Failure Alert || severity: critical"
                            }
                }
                    )
        slack.append(
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*InstanceID:*\n"  + "`" + alerts['InstanceId'] + "`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Name:*\n"  + "`" + alerts['Name'] + "`"
                        }
                    ]
                }
                )
        slack.append(
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*InstanceStatus:*\n" + alerts['InstanceStatus']
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*SystemStatus:*\n" + alerts['SystemStatus']
                        }
                    ]
                }
                )
        slack.append(
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*techteam:*\npplus-devops"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*priority:*\nP0"
                        }
                    ]
                }
                )
        slack.append(
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Node Type:*\n"+ alerts['Role']
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*PrivateIpAddress:*\n" + alerts['PrivateIpAddress']
                        }
                    ]
                }
                )
        msg = {
                "channel": channel_name,
                "username": "Instance Hardware Failure Alert",
                "icon_emoji": "alert",
                "blocks": slack
            }
        encoded_msg = json.dumps(msg).encode('utf-8')
        resp = http.request('POST',slack_webhook_url, body=encoded_msg)



instances_to_stop = check_instance()
instance_details = describe_instance(instances_to_stop)
alert_trigger(instance_details)
stop_instance(instance_details)