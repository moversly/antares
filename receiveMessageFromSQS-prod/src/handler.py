import boto3
import json
import datetime
from botocore.exceptions import NoCredentialsError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from botocore.exceptions import ClientError
s3_client = boto3.client('s3')


def download_html_template_from_s3(bucket_name, key, local_file_path):
    try:
        # Download the HTML file from S3
        s3_client.download_file(bucket_name, key, local_file_path)
        print(f"HTML template downloaded successfully to {local_file_path}")
        return True
    except Exception as e:
        print(f"Error downloading HTML template: {e}")
        return False

def download_pdf_from_s3(bucket_name, key, local_file_path):
    s3_client = boto3.client('s3')

    try:
        # Download the PDF file from S3
        s3_client.download_file(bucket_name, key, local_file_path)
        print(f"PDF downloaded successfully to {local_file_path}")
        return True
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return False

def get_html_template_content(local_file_path):
    try:
        # Read the content of the HTML file
        with open(local_file_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
        return template_content
    except Exception as e:
        print(f"Error reading HTML template content: {e}")
        return None

def send_email(subject, body, to_email, pdf_local_file_path,from_email):
    ses_client = boto3.client('ses', region_name='ap-southeast-1')

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    to_email = to_email.replace('"','')
    toEmail = []
    toEmail.append(to_email)
    print("this is toEmail : ",toEmail)
    msg['To'] = ', '.join(toEmail)
    msg['Bcc'] = 'moverslytrade@gmail.com'

    # Attach the HTML body to the email
    html_body = MIMEText(body, 'html')
    msg.attach(html_body)

    if pdf_local_file_path is not None:
        with open(pdf_local_file_path, 'rb') as file:
            attachment_data = file.read()
            attachment = MIMEApplication(open(pdf_local_file_path, 'rb').read())
            attachment.add_header('Content-Disposition', 'attachment', filename='Moversly.pdf')
            msg.attach(attachment)

    try:
        response = ses_client.send_raw_email(
            Source=msg['From'],
            Destinations=[msg['To'], msg['Bcc']],
            RawMessage={'Data': msg.as_string()}
        )
        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code == 200:
            print("Email sent! Email id :", toEmail," status code: ",status_code)
        else :
            print("Email is not sent!", toEmail," status code: ",status_code)

    except Exception as e:
        print("Error sending email:", str(e))

def get_data_from_dynamodb(table_name, key_value):
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table(table_name)
    print("this is the key value",key_value)
    key_value = key_value.replace('"','')

    try:
        response = table.get_item(
            Key={
                'emailId': key_value
            }
        )
        print("response is :",response)
        if 'Item' in response :
            item = response.get('Item')
            return item
        else :
            return 'Item doesnt exist'
    except ClientError as e:
        print(f"Error getting data from DynamoDB: {e}")
        return None

def put_data_into_dynamodb(table_name, email,item):
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table(table_name)
    print("this is email in put item :",email)
    email = email.replace('"','')
    current_time = datetime.datetime.utcnow()
    epoch_time = int(current_time.timestamp())
    mail_sent_time =str(epoch_time)
    fileName = item.get('fileName')
    uploadTime = item.get('uploadTime')
    write_item = {
        "emailId": email,
        "mailSent": True,
        "fileName": fileName,
        "uploadTime": uploadTime,
        "mailSentTime": mail_sent_time,
        "bucketName": item.get('bucketName')
    }
    print("this is the item writing to table :",write_item)
    try:
        response = table.put_item(Item=write_item)
        print("PutItem succeeded:", response)
        return True
    except ClientError as e:
        print(f"Error putting data into DynamoDB: {e}")
        return False

def lambda_handler(event, context):
    print(event)
    # stringified_record = json.dumps(event.get('Records', [])[0])
    # record = json.loads(stringified_record)
    # print(record)
    for record in event['Records']:
        email = record['body']
        # email = event['Records']['body']
        print("email is :",email)
        if email is not None and email != '':
            
            
            table_name = 'SQSMessage-prod'
            retrieved_item = get_data_from_dynamodb(table_name, email)
            bucket_name = retrieved_item['bucketName']
            print("bucket name is",bucket_name)
            print("Retrieved Item : ", retrieved_item)
            mailSent = retrieved_item['mailSent']
            if retrieved_item is not None and mailSent is False :

                if bucket_name == 'email.campaign.send.message.to.sqs-prod' :
                    template_bucket_name = 'email.campaign-prod'
                    html_file_key = 'email_campaign.html'
                    html_local_file_path = '/tmp/email_campaign.html'

                    # Download the HTML template from S3
                    html_download_success = download_html_template_from_s3(template_bucket_name, html_file_key, html_local_file_path)
                    # Download the PDF from S3
                    pdf_file_key = 'Moversly.pdf'
                    pdf_local_file_path = '/tmp/Moversly.pdf'
                    pdf_download_success = download_pdf_from_s3(template_bucket_name, pdf_file_key, pdf_local_file_path)

                    if html_download_success and pdf_download_success:   
                        # Read the content of the HTML template
                        email_body = get_html_template_content(html_local_file_path)
                        if email_body:
                            email_subject = 'Move Management Software'
                            recipient_email = email
                            send_email(email_subject, email_body, recipient_email, pdf_local_file_path,"info@moversly.com")
                            put_success = put_data_into_dynamodb(table_name, email, retrieved_item)
                            if put_success:
                                print("Data put into DynamoDB successfully.")
                            else:
                                print("Failed to put data into DynamoDB.")
                elif bucket_name == 'apac.email.campaign.send.message.to.sqs-prod':
                    template_bucket_name = 'email.campaign-prod'
                    html_file_key = 'apac_email_campaign.html'
                    html_local_file_path = '/tmp/apac_email_campaign.html'
                    # Download the HTML template from S3
                    html_download_success = download_html_template_from_s3(template_bucket_name, html_file_key, html_local_file_path)

                    if html_download_success :   
                        # Read the content of the HTML template
                        email_body = get_html_template_content(html_local_file_path)
                        if email_body:
                            email_subject = ' Reliable International Mover For Your Relocation '
                            recipient_email = email
                            send_email(email_subject, email_body, recipient_email, None, "contact@apacmobility.com")
                            put_success = put_data_into_dynamodb(table_name, email, retrieved_item)
                            if put_success:
                                print("Data put into DynamoDB successfully.")
                            else:
                                print("Failed to put data into DynamoDB.")

                
                