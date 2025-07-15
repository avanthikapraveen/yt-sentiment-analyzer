import firebase_admin
from firebase_admin import credentials, firestore
import datetime

cred = credentials.Certificate("firebase_key.json") 
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def log_analysis(video_id, sentiment_data, feedback=None):
    doc_ref = db.collection("analyses").document()
    log_entry = {
        "video_id": video_id,
        "positive": sentiment_data.get("positive",0), 
        "negative": sentiment_data.get("negative", 0),
        "neutral": sentiment_data.get("neutral", 0),
        "summary": sentiment_data.get("summary", ""),
        "feedback": feedback,
        "timestamp": datetime.datetime.now()
    }
    doc_ref.set(log_entry)