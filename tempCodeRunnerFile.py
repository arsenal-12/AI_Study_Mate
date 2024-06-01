from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from bs4 import BeautifulSoup
import requests
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi

def summarize_youtube_video(youtube_video):
    try:
        # Extract the video ID from the URL
        video_id = youtube_video.split("v=")[1]

        # Fetch the video transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine the transcript text into a single string
        result = " ".join([item['text'] for item in transcript])

        # Initialize the summarizer pipeline
        summarizer = pipeline('summarization', model = "sshleifer/distilbart-cnn-12-6")

        # Split the text into chunks of up to 1000 characters each
        chunk_size = 1000
        chunks = [result[i:i + chunk_size] for i in range(0, len(result), chunk_size)]

        # Summarize each chunk
        summarized_text = []
        for chunk in chunks:
            summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
            summary_text = summary[0]['summary_text']
            summarized_text.append(summary_text)

        # Combine summarized chunks into a single string
        final_summary = " ".join(summarized_text)
        return final_summary
    except Exception as e:
        return str(e)

