import boto3
import json
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

def send_email(subject, body, to_email, pdf_local_file_path):
    ses_client = boto3.client('ses', region_name='ap-southeast-1')

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = "info@moversly.com"
    to_email = to_email.replace('"','')
    toEmail = []
    toEmail.append(to_email)
    print("this is toEmail : ",toEmail)
    msg['To'] = ', '.join(toEmail)

    # Attach the HTML body to the email
    html_body = MIMEText(body, 'html')
    msg.attach(html_body)

    with open(pdf_local_file_path, 'rb') as file:
        attachment_data = file.read()

    attachment = MIMEApplication(pdf_local_file_path)
    attachment.add_header('Content-Disposition', 'attachment', filename='Moversly.pdf')
    msg.attach(attachment)

    try:
        response = ses_client.send_raw_email(
            Source=msg['From'],
            Destinations=toEmail,
            RawMessage={'Data': msg.as_string()}
        )
        print("Email sent! Message ID:", response['MessageId'])
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

def put_data_into_dynamodb(table_name, email):
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table(table_name)
    print("this is email in put item :",email)
    email = email.replace('"','')
    item = {
        "emailId": email,
        "mailSent": True,
        "timeToDelete": None
    }
    print("this is the item writing to table :",item)
    try:
        response = table.put_item(Item=item)
        print("PutItem succeeded:", response)
        return True
    except ClientError as e:
        print(f"Error putting data into DynamoDB: {e}")
        return False

def lambda_handler(event, context):
    stringified_record = json.dumps(event.get('Records', [])[0])
    record = json.loads(stringified_record)
    print(record)
    # email = event['Records'][0]['body']
    # print("email is :",email)
    event_source = ['Records'][0]['eventSource']
    event_name = ['Records'][0]['eventName']
    if event_name is not None and event_name is 'REMOVE' :
        bucket_name = 'email.campaign-prod'
        html_file_key = 'email_campaign.html'
        html_local_file_path = '/tmp/email_campaign.html'
        table_name = 'SQSMessage-prod'
        email = event['Records'][0]['dynamodb']['Keys']['emailId']['S']
        print("email is :",email)
        retrieved_item = get_data_from_dynamodb(table_name, email)
        print("Retrieved Item : ", retrieved_item)
        mailSent = retrieved_item['mailSent']
        if retrieved_item is not None and mailSent is False :
            # Download the HTML template from S3
            html_download_success = download_html_template_from_s3(bucket_name, html_file_key, html_local_file_path)
            # Download the PDF from S3
            pdf_file_key = 'Moversly.pdf'
            pdf_local_file_path = '/tmp/Moversly.pdf'
            pdf_download_success = download_pdf_from_s3(bucket_name, pdf_file_key, pdf_local_file_path)

            if html_download_success and pdf_download_success:
                # Read the content of the HTML template
                email_body = get_html_template_content(html_local_file_path)
                if email_body:
                    email_subject = 'Move Management Software'
                    recipient_email = email
                    send_email(email_subject, email_body, recipient_email, pdf_local_file_path)
                    put_success = put_data_into_dynamodb(table_name, email)
                    if put_success:
                        print("Data put into DynamoDB successfully.")
                    else:
                        print("Failed to put data into DynamoDB.")