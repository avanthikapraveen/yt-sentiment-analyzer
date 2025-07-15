import streamlit as st
from youtube_utils import get_video_comments, analyze_sentiments
import pandas as pd
import plotly.express as px
from firebase_utils import log_analysis
from youtube_utils import extract_video_id

st.set_page_config(page_title = "YouTube Sentiment Analyzer", layout = "centered", initial_sidebar_state = "collapsed")
st.title("YouTube Comment Sentiment Analyzer")
video_url = st.text_input("Paste your YouTube video URL here")
if st.button("Analyze Comments"):
    if not video_url:
        st.warning("Please paste a YouTube link first")
    else:
        with st.spinner("Fetching comments..."):
            comments = get_video_comments(video_url, max_comments = 30)

        if not comments:
            st.error("No comments found or failed to fetch.")
        else:
            st.success("Fetched comments successfully!")

            with st.spinner("Analyzing sentiment using Gemini..."):
                result = analyze_sentiments(comments)

            if not result:
                st.error("Gemini analysis failed.")
            else:
                st.session_state["last_result"] = result
                st.session_state["last_url"] = video_url

if "last_result" in st.session_state and "last_url" in st.session_state:
    result = st.session_state["last_result"]
    video_url = st.session_state["last_url"]

    st.markdown("### Sentiment Analysis Result")
    summary = result.get("summary", "No summary available")
    st.markdown(f"> *{summary}*")
    st.markdown("### Sentiment Breakdown")
    data = {
        "Sentiment": ["Positive", "Negative", "Neutral"],
        "Count": [
            result.get("positive", 0),
            result.get("negative", 0),
            result.get("neutral", 0)
        ]
    }

    df = pd.DataFrame(data)
    fig = px.pie(
        df,
        names="Sentiment",
        values="Count",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig)

    st.markdown("### Was this analysis useful?")
    if "feedback_given" not in st.session_state:
        st.session_state["feedback_given"] = False

    col1, col2 = st.columns(2)

    if not st.session_state["feedback_given"]:
        if col1.button("👍 Helpful"):
            feedback = "helpful"
        elif col2.button("👎 Not Helpful"):
            feedback = "not helpful"
        else:
            feedback = None

        if feedback:
            video_id = extract_video_id(video_url)
            log_analysis(video_id=video_id, sentiment_data=result, feedback=feedback)
            st.session_state["feedback_given"] = True
            st.success("✅ Your feedback has been saved. Thanks!")
    else:
        st.info("You have already submitted feedback for this analysis.")
