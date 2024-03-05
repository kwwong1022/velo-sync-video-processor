import boto3
import cv2 as cv
import tempfile

s3 = boto3.client('s3')
s3_response = s3.get_object(Bucket='velo-sync-storage-bucket-dev', Key='video/dog.mp4')
video_bytes = s3_response['Body'].read()

temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=True)
temp_file.write(video_bytes)
vidcap = cv.VideoCapture(temp_file.name)

fourcc = cv.VideoWriter_fourcc(*'mp4v')
frame_rate = 30
size = (int(vidcap.get(3)), int(vidcap.get(4)))
output_video = cv.VideoWriter(temp_file.name, fourcc, frame_rate, size)

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

s3.upload_file(temp_file.name, 'velo-sync-storage-bucket-dev', 'video/dog_modified.mp4')
temp_file.close()