import json
import boto3

sqs = boto3.client('sqs')
ses_client = boto3.client('ses', region_name='ap-southeast-1')


def send_message_sqs(event,context) :
    try:
        for record in event['Records']:
            data = record['body']
            received_object = json.loads(data)
            print("this is the object received :",received_object)
            recipient_email = "prajualnandu@gmail.com"
            subject = "Apac Engineering Service Booking"
            body = "Customer Details :\n\n"
            for key,value in received_object.items():           
                body += f"{key}: {value}\n"
            response = ses_client.send_email(
                Source='sales@moversly.com',
                Destination={'ToAddresses': [recipient_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
            }
            )

    except Exception as e :
        print(f"An exception occurred: {e}")
