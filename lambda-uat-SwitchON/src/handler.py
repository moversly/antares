import boto3

def start_instance(event, context):
    region = 'ap-southeast-1'
    instance_id = 'i-00235257bb448a4ea'
    ec2_client = boto3.client('ec2', region_name=region)
    autoscaling_client = boto3.client('autoscaling', region_name=region)  
    response_start = ec2_client.start_instances(InstanceIds=[instance_id])
    response = autoscaling_client.resume_processes(
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
    print("Instance started for working hours:")
    print(response_start)
    return {
        'statusCode': 200,
        'body': 'Instance start during working hours executed successfully!'
    }

if __name__ == "_main_":
    start_instance(None, None)