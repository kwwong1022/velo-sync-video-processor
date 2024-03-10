import os
from dotenv import load_dotenv

load_dotenv()

VIDEO_PROCESS_TABLE = f'velo-sync-video-process-table-{os.getenv("STAGE")}'

S3_STORAGE_BUCKET = f'velo-sync-storage-bucket-{os.getenv("STAGE")}'

SUFFIX_MP4 = '.mp4'