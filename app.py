import streamlit as st
from youtube_utils import get_video_comments, analyze_sentiments
import pandas as pd
import plotly.express as px

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
                    names = "Sentiment",
                    values = "Count",
                    color_discrete_sequence = px.colors.qualitative.Set3
                )
                st.plotly_chart(fig)

                

