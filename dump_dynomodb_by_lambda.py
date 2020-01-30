import json
import os
import boto3
import datetime
from datetime import date
import logging

JSON_INDENT=2
TABLE_NAME='dynamodb_db'
SCHEMA_FILE = "schema.json"
DATA_DIR = "data"

def jsonConverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def backup_dynamodb_shema(dynamodbClient, s3Bucket, versionDate):
    table_desc = dynamodbClient.describe_table(TableName=TABLE_NAME)
    s3Bucket.Object('dynamodb/current').put(Body=versionDate)
    s3Bucket.Object('dynamodb/dumps/'+versionDate+'/dynamodb_db/'+SCHEMA_FILE).put(Body=json.dumps(table_desc, default=jsonConverter))
   
def backup_dynamodb_data(dynamodbClient, s3Bucket, versionDate):
    i = 1
    scanned_table = dynamodbClient.scan(TableName=TABLE_NAME)
    s3Bucket.Object('dynamodb/dumps/'+versionDate+'/dynamodb_db/'+DATA_DIR+'/'+str(i).zfill(4) + ".json").put(Body=json.dumps(scanned_table, default=jsonConverter))

    try:
        last_evaluated_key = scanned_table["LastEvaluatedKey"]
    except KeyError:
        logging.error("EXCEEDED THROUGHPUT ON TABLE " + TABLE_NAME + ".  BACKUP FOR IT IS USELESS.")
 
    while True:
        i += 1
        try:
            scanned_table = dynamodbClient.scan(TableName=TABLE_NAME, ExclusiveStartKey=last_evaluated_key)
            s3Bucket.Object('dynamodb/dumps/'+versionDate+'/dynamodb_db/'+DATA_DIR+'/'+str(i).zfill(4) + ".json").put(Body=json.dumps(scanned_table, default=jsonConverter))

        except Exception:
            logging.error("EXCEEDED THROUGHPUT ON TABLE " + TABLE_NAME + ".  BACKUP FOR IT IS USELESS.")
            break

        try:
            last_evaluated_key = scanned_table["LastEvaluatedKey"]
        except KeyError:
            break
 

def lambda_handler(event, context):
    dynamodbClient = boto3.client('dynamodb')
    versionDate = date.today().strftime("%m-%d-%Y")
    s3Bucket = boto3.resource('s3').Bucket(os.environ['backup_bucket'])
    
    backup_dynamodb_data(dynamodbClient, s3Bucket, versionDate)
    backup_dynamodb_shema(dynamodbClient, s3Bucket, versionDate)
        
    return {
         'statusCode': 200,
    }
