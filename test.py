import boto3
import cv2 as cv
import numpy as np
import tempfile


# retrieve video from s3 by keyname
s3 = boto3.client('s3')
response = s3.get_object(Bucket='velo-sync-storage-bucket-dev', Key='video/dog.mp4')
video_bytes = response['Body'].read()
print(response)


# Save the video as a temporary file
temp_file = tempfile.NamedTemporaryFile(delete=False)
temp_file.write(video_bytes)
temp_file.close()

# Open the temporary file with OpenCV
cap = cv.VideoCapture(temp_file.name)

# Read until video is completed 
while(cap.isOpened()): 
      
# Capture frame-by-frame 
    ret, frame = cap.read() 
    if ret == True: 
    # Display the resulting frame 
        cv.imshow('Frame', frame) 
          
    # Press Q on keyboard to exit 
        if cv.waitKey(25) & 0xFF == ord('q'): 
            break
  
# Break the loop
    else:
        break
  
cap.release()
cv.destroyAllWindows() 


# upload processed video to s3