import boto3
from ..constant.constant import VIDEO_PROCESS_TABLE, S3_STORAGE_BUCKET

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def get_video_process(process_id):
    video_process_table = dynamodb.Table(VIDEO_PROCESS_TABLE)
    return video_process_table.query(
        KeyConditionExpression = 'id = :id',
        ExpressionAttributeValues = {':id': process_id},
        Limit=1,
    )

def get_s3_file(key):
    s3_response = s3.get_object(Bucket=S3_STORAGE_BUCKET, Key=key)
    return s3_response['Body']

def put_s3_file(path, bucket, filename):
    s3.upload_file(path, bucket, filename)