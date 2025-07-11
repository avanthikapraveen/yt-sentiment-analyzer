from googleapiclient.discovery import build
import re
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

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

def analyze_sentiments(comments):
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    prompt = (
        "You're an AI that analyzes YouTube comments.\n"
        "Given a list of comments, classify each as Positive, Negative, or Neutral.\n"
        "Return your response like this:\n\n"
        "- Positive:\n  - comment1\n  - comment2\n"
        "- Neutral:\n  - comment3\n"
        "- Negative:\n  - comment4\n\n"
        "Here are the comments:\n"
    )
    full_prompt = prompt + "\n".join(f"- {comment}" for comment in comments[:30])

    response = model.generate_content(contents=[{"role": 'user', "parts": [full_prompt]}])
    print(response.text)
    return response.text
