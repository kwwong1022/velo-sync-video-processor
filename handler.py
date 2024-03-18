import json
import gpxpy
import tempfile
import gpxpy.gpx
import cv2 as cv
import xml.etree.ElementTree as ET
from src.constant.constant import S3_STORAGE_BUCKET, SUFFIX_MP4
from src.lib.common import get_video_process, get_s3_file, put_s3_file
from src.lib.metric import get_gpx_metric
from src.lib.style import get_display_items

def app(event, context):
    print('Event: ' + json.dumps(event))

    # Retrieve file keys from database
    video_process = get_video_process('c7e6d89d-c0f5-4e35-a472-ac44d3bcbb8b')
    video_key = video_process['videoKey']
    gpx_key = video_process['gpxKey']
    style_key = video_process['styleKey']

    # Retrieve files from s3
    video_bytes = get_s3_file(video_key).read()
    gpx_bytes = get_s3_file(gpx_key).read()
    style_bytes = get_s3_file(style_key).read()

    # Prepare video
    temp_video_file = tempfile.NamedTemporaryFile(suffix=SUFFIX_MP4, delete=True)
    temp_video_file.write(video_bytes)
    input_video = cv.VideoCapture(temp_video_file.name)
    temp_video_file.close()

    # Prepare style & data
    style_str = style_bytes.decode('utf-8')
    style_element = ET.fromstring(style_str)
    vid_offset = style_element.find('vidconf').find('offset').text
    display_items = get_display_items(style_element)
    gpx_metric = get_gpx_metric(gpx_bytes)

    # Create output video
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    fps = input_video.get(cv.CAP_PROP_FPS)
    size = (int(input_video.get(3)), int(input_video.get(4)))  # 3: width, 4: height
    temp_video_file = tempfile.NamedTemporaryFile(suffix=SUFFIX_MP4, delete=True)
    output_video = cv.VideoWriter(temp_video_file.name, fourcc, fps, size)

    frame_count = 0

    while(True): 
        ret, frame = input_video.read() 

        if ret: 
            cv.putText(frame, 'TEXT ON VIDEO', (50, 50), 
                cv.FONT_HERSHEY_SIMPLEX, 
                1, (0, 255, 255), 2, cv.LINE_4)
                
            output_video.write(frame)
            frame_count += 1
        
        else:
            break

    output_video.release()
    input_video.release()

    # Upload output video to s3
    # put_s3_file(temp_video_file.name, S3_STORAGE_BUCKET, '71c2b411-5ad7-4e24-9fc9-469d8c1d7f97/c7e6d89d-c0f5-4e35-a472-ac44d3bcbb8b.mp4')
    temp_video_file.close()

    # Health check result
    return {
        "statusCode": 200, 
        "body": json.dumps({
            "message": "Video processed and uploaded to s3 successfully",
            "input": event,
        })
    }

# For localhost test
app({}, {})