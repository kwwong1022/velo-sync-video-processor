import json
import boto3

def app(event, context):
    # boto3 test code
    session = boto3.Session()

    s3 = session.resource('s3')

    my_bucket = s3.Bucket('velo-sync-storage-bucket-dev')

    for my_bucket_object in my_bucket.objects.all():
        print(my_bucket_object.key)


    # Health check result
    return {
        "statusCode": 200, 
        "body": json.dumps({
            "message": "Go Serverless v3.0! Your function executed successfully!",
            "input": event,
        })
    }
