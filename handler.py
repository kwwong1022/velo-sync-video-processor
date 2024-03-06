import json
import boto3
import tempfile
import cv2 as cv

def app(event, context):
    # Setup aws s3 client
    s3 = boto3.client('s3')

    # Retrieve video from s3
    bucket = 'velo-sync-storage-bucket-dev'
    key = 'video/dog.mp4'
    suffix = '.mp4'
    s3_response = s3.get_object(Bucket=bucket, Key=key)
    video_bytes = s3_response['Body'].read()

    # Save video to temp file to create video capture
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=True)
    temp_file.write(video_bytes)
    vidcap = cv.VideoCapture(temp_file.name)

    # Create output video
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    fps = 30
    size = (int(vidcap.get(3)), int(vidcap.get(4)))  # 3: width, 4: height
    output_video = cv.VideoWriter(temp_file.name, fourcc, fps, size)

    while(True): 
        ret, frame = vidcap.read() 

        if ret == True: 
            cv.putText(frame, 'TEXT ON VIDEO', (50, 50), 
                    cv.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 255, 255), 2, cv.LINE_4)
            
            output_video.write(frame)
    
        else:
            break

    output_video.release()
    vidcap.release()

    # Upload output video to s3
    temp_file_name = temp_file.name
    s3.upload_file(temp_file.name, 'velo-sync-storage-bucket-dev', 'video/dog_modified.mp4')
    temp_file.close()

    # Health check result
    return {
        "statusCode": 200, 
        "body": json.dumps({
            "message": "Video processed and uploaded to s3 successfully",
            "temp_file_name": temp_file_name,
            "input": event,
        })
    }
