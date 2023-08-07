import boto3

def stop_instance(event, context):
    region = 'ap-southeast-1'
    instance_id = 'i-00235257bb448a4ea'  
    ec2_client = boto3.client('ec2', region_name=region)
    autoscaling_client = boto3.client('autoscaling', region_name=region)
    response = autoscaling_client.suspend_processes(
        AutoScalingGroupName='ecs-infra-uat-ECSAutoScalingGroup-1WIMAH939PIJG',
            ScalingProcesses=[
                'Launch',
                'Terminate',
                'HealthCheck',
                'ReplaceUnhealthy',
                'AlarmNotification',
                'ScheduledActions',
                'AddToLoadBalancer'
            ]
        )
    print("Auto Scaling processes suspended successfully.")
    response_stop = ec2_client.stop_instances(InstanceIds=[instance_id])
    print("Instance stopped:")
    print(response_stop)
    return {
        'statusCode': 200,
        'body': 'Instance stop executed successfully!'
    }
   
if __name__ == "_main_":
    stop_instance(None, None)


