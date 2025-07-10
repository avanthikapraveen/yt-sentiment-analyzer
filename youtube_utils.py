from googleapiclient.discovery import build
import re
import os
from dotenv import load_dotenv

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

print(extract_video_id("https://www.youtube.com/watch?v=abc123XYZ_9"))  # abc123XYZ_9
print(extract_video_id("https://youtu.be/abc123XYZ_9"))                 # abc123XYZ_9
print(extract_video_id("https://youtube.com/shorts/abc123XYZ_9"))      # abc123XYZ_9
print(extract_video_id("https://notyoutube.com/watch?v=abc123XYZ_9"))  # abc123XYZ_9 (but maybe shouldn't!)
print(extract_video_id("invalid_url"))                                  # None
