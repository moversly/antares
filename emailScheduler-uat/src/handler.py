import json
import boto3
import datetime
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
                login_user_data = record['dynamodb']['OldImage']['loginUser']['M']
                cc_email_item = record['dynamodb']['OldImage']['emailSchedule']['M']['ccEmail']['L']
                if (deleted_id.get('intervalDays') is not None):
                    IntervalDays = deleted_id.get('intervalDays')
                    interval_days = IntervalDays.get('N')
                    interval_days = int(interval_days)
                    current_time = datetime.datetime.utcnow()
                    new_time = current_time + datetime.timedelta(days=interval_days)
                    epoch_time = int(new_time.timestamp())
                OrderId = deleted_id.get('orderId')
                SendMail = deleted_id.get('sendMail')
                Reminder = deleted_id.get('reminder')
                QuoteMail = deleted_item.get('quoteFollowUp')
                SenderEmail = deleted_item.get('senderEmail')
                ReceiverEmail = deleted_item.get('receiverEmail')
                Message = deleted_item.get('message')
                Subject = deleted_item.get('subject')
                FromCountry = deleted_item.get('fromCountry')
                ToCountry = deleted_item.get('toCountry')
                CustomerGivenName = deleted_item.get('customerGivenName')
                CustomerFamilyName = deleted_item.get('customerFamilyName')
                QuoteUrl = deleted_item.get('quoteUrl')
                QuoteId = deleted_item.get('quoteId')
                UniqueId = deleted_item.get('uniqueId')
                loginUserGivenName = login_user_data.get('loginUserGivenName')
                loginUserFamilyName = login_user_data.get('loginUserFamilyName')
                loginUserPhone  = login_user_data.get('loginUserPhone')
                loginUserEmail  = login_user_data.get('loginUserEmail')
                moverName = login_user_data.get('moverName')
                moverWebsite = login_user_data.get('moverWebsite')
                moverLogo = deleted_id.get('logoUrl')
                flag = True
                if all(vars is not None for vars in [QuoteUrl,QuoteId,UniqueId,moverWebsite]) :
                    quote_url = QuoteUrl.get('S')
                    quote_id = QuoteId.get('S')
                    unique_id = UniqueId.get('S')
                    mover_website = moverWebsite.get('S')
                else :
                    flag = False
                if all(vars is not None for vars in [OrderId,SenderEmail,ReceiverEmail,Message,Subject,FromCountry,ToCountry,CustomerGivenName,CustomerFamilyName,loginUserGivenName,loginUserPhone,loginUserEmail,moverName,moverLogo]):
                    order_id = OrderId.get('S')
                    send_mail = SendMail.get('BOOL')
                    reminder = Reminder.get('BOOL')
                    quote_mail = QuoteMail.get('BOOL')
                    sender_email = SenderEmail.get('S')
                    receiver_email = ReceiverEmail.get('S')
                    message = Message.get('S')
                    subject = Subject.get('S')
                    from_country = FromCountry.get('S')
                    to_country = ToCountry.get('S')
                    customer_given_name = CustomerGivenName.get('S')
                    login_user_givenName = loginUserGivenName.get('S')
                    login_user_familyName = loginUserFamilyName.get('S')
                    login_user_phone = loginUserPhone.get('S')
                    login_user_email = loginUserEmail.get('S')
                    mover_name = moverName.get('S')
                    mover_logo = moverLogo.get('S')
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
                    if all(vars is not None for vars in [sender_email,receiver_email]) :
                        send_mail = True
                    else :
                        send_mail = False
                    if reminder :
                        if all(vars is not None for vars in [login_user_givenName,login_user_familyName,login_user_phone,login_user_email,mover_name,mover_logo,customer_given_name,from_country,to_country]) :
                            message = message.replace("$loginUserGivenName",login_user_givenName).replace("$loginUserFamilyName",login_user_familyName).replace("$loginUserPhone",login_user_phone).replace("$loginUserEmail",login_user_email).replace("$moverName",mover_name).replace("$logo",mover_logo).replace("$givenName",customer_given_name).replace("$fromCountry",from_country).replace("$toCountry",to_country)
                        else :
                            send_mail = False
                        if quote_mail :
                            if flag :
                                if all(vars is not None for vars in [quote_id,quote_url,unique_id,mover_website,order_id]) :
                                    message = message.replace("$quoteId",quote_id).replace("$uniqueId",unique_id).replace("$moverWebsite",mover_website).replace("$orderId",order_id).replace("$quotePdfUrl",quote_url) 
                                else :
                                    send_mail = False
                            else :
                                send_mail = False
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
                    if reminder and send_mail :
                        deleted_id['timeToDelete'] = {'N' : str(epoch_time)}
                        table_name = 'EmailSchedule-uat'
                        saved_item = dynamodb.put_item(
                            TableName=table_name,
                            Item=deleted_id
                            )
                    if send_mail is False :
                        print("Email was deleted successfully !")
                    else :
                        response = ses_client.send_raw_email(
                            Source = sender_email,
                            Destinations = destinations,
                            RawMessage = { 'Data':msg.as_string() }
                            )
                        print("Email was sent successfully !",response)
                else :
                    print("Email was deleted successfully !")    
    except ClientError as e :
        print(e.response['Error']['Message'])

            



