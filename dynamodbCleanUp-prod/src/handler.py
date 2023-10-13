import json
import boto3
from datetime import datetime

dynamodb = boto3.client('dynamodb')
destination_table_name = 'ClosedLeadsData-prod'
backup_table_name ='Audit-prod'
current_time = datetime.now()
epoch_time = int(current_time.timestamp())

def cleanUp(event, context):
    for record in event['Records']:
        if record['eventName'] == 'REMOVE':
            dynamodb_data = record['dynamodb']['OldImage']
            payload = record['dynamodb']['OldImage']['payload']['M']
            new_item = {'id' : dynamodb_data['id'],
                        'userInfo' : payload.get('userInfo'),
                        'scheduleShipment' : payload.get('scheduleShipment')
                        }
            write_to_destination_table(destination_table_name,new_item)
            backup_item = {'orderId' : dynamodb_data['id'],
                           'date' : {'N' : str(epoch_time)}
                           }
            for attribute_name, attribute_value in dynamodb_data.items():
                if attribute_name == 'timeToDelete':
                    backup_item[attribute_name] = {'NULL': True}
                if (attribute_name != 'id' and attribute_name != 'timeToDelete'):
                    backup_item[attribute_name] = attribute_value
            write_to_destination_table(backup_table_name,backup_item)
    

def write_to_destination_table(table_name,data):
    try:
        response = dynamodb.put_item(
            TableName=table_name,
            Item=data
        )
        print("Item written to destination table:", response)
        print("order details :",data)
    except Exception as e:
        print("Error writing to destination table:", e)


if __name__ == "_main_":
    cleanUp(None, None)