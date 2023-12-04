import json
import botocore.exceptions as ClientError
import boto3
import csv
import time

s3 = boto3.client('s3')
sqs = boto3.client('sqs')
dynamodb = boto3.client('dynamodb')


def emailCampaign(event, context):
    try :
         # Get the S3 bucket and key from the S3 event
        s3_bucket = event['Records'][0]['s3']['bucket']['name']
        s3_key = event['Records'][0]['s3']['object']['key']
        print(event)
        

        # Read data from CSV file in S3
        s3_response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        csv_data = s3_response['Body'].read().decode('utf-8')

        # Parse CSV data
        csv_reader = csv.DictReader(csv_data.splitlines())


        for row in csv_reader:
            # Assuming 'email' is the column header containing email addresses
            email = row.get('Email')
            if email is not None and email == '':
                table_name = 'SQSMessage-prod'
                data_to_insert = {
                    "emailId": {
                        "S": email
                        },
                    "mailSent": {
                        "BOOL": False
                        }
                    }
                print("this is data to insert",data_to_insert)
                saved_item = dynamodb.put_item(
                                TableName=table_name,
                                Item=data_to_insert
                                )
                sqs_queue_url = 'https://sqs.ap-southeast-1.amazonaws.com/978606118148/email-campaign'
                sqs_message = email
            
                print(sqs_message)
                delay_seconds = 1
                response = sqs.send_message(QueueUrl=sqs_queue_url, MessageBody=json.dumps(sqs_message), DelaySeconds=delay_seconds)
                print("this is the response:", response)
            

        print("SuccessFully send to SQS")
    

    except Exception as e :
        print(f"An exception occurred: {e}")
