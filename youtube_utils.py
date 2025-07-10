from googleapiclient.discovery import build
import re
import os
from dotenv import load_dotenv

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def get_video_comments(video_url, max_comments = 50):
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid Youtube video URL")
    youtube = build("youtube", "v3", developerKey = YOUTUBE_API_KEY)
    comments = []
    next_page_token = None
    while len(comments) < max_comments:
        response = youtube.commentThreads().list( 
            part = 'snippet',
            videoId = video_id,
            maxResults = min(100, max_comments - len(comments)),
            pageToken = next_page_token
        ).execute()
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return comments
