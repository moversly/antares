import json
import botocore.exceptions as ClientError
import boto3
import csv

s3 = boto3.client('s3')
sqs = boto3.client('sqs')
dynamodb = boto3.client('dynamodb')


def emailCampaign(event, context):
    try:
        s3_bucket = event['Records'][0]['s3']['bucket']['name']
        s3_key = event['Records'][0]['s3']['object']['key']
        print(event)
        s3_response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        csv_data = s3_response['Body'].read().decode('latin-1')
        csv_reader = csv.DictReader(csv_data.splitlines())         

        print("S3 bucket name : ",s3_bucket)

        for row in csv_reader:
            email = row.get('Email')
            if email is not None and email != '':
                sqs_queue_url = 'https://sqs.ap-southeast-1.amazonaws.com/978606118148/email-campaign'
                sqs_message = f"{email},{s3_bucket}"
                print("Message sending to SQS :",sqs_message)
                delay_seconds = 1
                response = sqs.send_message(QueueUrl=sqs_queue_url, MessageBody=json.dumps(
                    sqs_message), DelaySeconds=delay_seconds)
                print("Response : ", response)
        print("SuccessFully send to SQS")

    except Exception as e:
        print(f"An exception occurred: {e}")
