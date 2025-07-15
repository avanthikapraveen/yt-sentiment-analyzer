from googleapiclient.discovery import build
import re
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

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

def analyze_sentiments(comments: list[str]) -> dict:
    
    prompt = (
        """You are a YouTube comment sentiment analyzer.
        Given a list of viewer comments, classify each as:
        - Positive
        - Negative
        - Neutral
        Then:
        1. Count how many comments fall into each category.
        2. Give a 5-6 line summary that reflects the general audience sentiment.
        3. Ignore irrelevant or spammy comments (like emojis or "first", "nice").
        The comments may be in multiple languages. Please analyze them accordingly.
        Return the result as a JSON in this format:
        {
            "positive": [number],
            "neutral": [number],
            "negative": [number],
            "summary": "<short overall summary>"
        }
        Here are the comments:"""
    )
    full_prompt = prompt + "\n".join(f"- {comment}" for comment in comments[:50])
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        response = model.generate_content(contents=[{"role": 'user', "parts": [full_prompt]}])
        text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        text = re.sub(r'\\(?![\\/"bfnrtu])', r'\\\\', text)
        return json.loads(text)
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")
        return None
