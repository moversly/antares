import json
import boto3
from botocore.exceptions import ClientError
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

dynamodb = boto3.client('dynamodb')
ses_client = boto3.client('ses')
s3 = boto3.resource('s3')

def emailScheduler(event, context):
    try :
        for record in event['Records']:
            if record['eventName'] == 'REMOVE':
                deleted_id = record['dynamodb']['OldImage']
                deleted_item = record['dynamodb']['OldImage']['emailSchedule']['M']
                cc_email_item = record['dynamodb']['OldImage']['emailSchedule']['M']['ccEmail']['L']
                OrderId = deleted_id.get('orderId')
                SendMail = deleted_id.get('sendMail')
                SenderEmail = deleted_item.get('senderEmail')
                ReceiverEmail = deleted_item.get('receiverEmail')
                Message = deleted_item.get('message')
                Subject = deleted_item.get('subject')
                order_id = OrderId.get('S')
                send_mail = SendMail.get('BOOL')
                sender_email = SenderEmail.get('S')
                receiver_email = ReceiverEmail.get('S')
                message = Message.get('S')
                subject = Subject.get('S')
                cc_email = [item['S'] for item in cc_email_item]
                cc_email.append(receiver_email)
                destinations = cc_email
                file_name = None
                CHARSET = "utf-8"
                BUCKET_NAME = "email-scheduler-attachments-test"
                msg = MIMEMultipart()
                msg['Subject'] = subject
                msg['From'] = sender_email
                msg['To'] = receiver_email
                htmlpart = MIMEText(message.encode(CHARSET), 'html', CHARSET)
                msg.attach(htmlpart)
                if file_name is not None:
                    KEY = order_id + '/' + file_name
                    TMP_FILE_NAME = '/tmp/' + file_name
                    s3.meta.client.download_file(BUCKET_NAME, KEY, TMP_FILE_NAME)
                    ATTACHMENT = TMP_FILE_NAME
                    att = MIMEApplication(open(ATTACHMENT, 'rb').read())
                    att.add_header('Content-Disposition','attachment',filename = file_name)
                    msg.attach(att)  
                if send_mail is False :
                    print("Email was deleted successfully !")
                else :
                    response = ses_client.send_raw_email(
                        Source = sender_email,
                        Destinations = destinations,
                        RawMessage = { 'Data':msg.as_string() }
                        )
                    print("Email was sent successfully !",response)
                    
    except ClientError as e :
        print(e.response['Error']['Message'])

            



