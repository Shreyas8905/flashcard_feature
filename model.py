import os  # <-- This line was missing

from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)

genai.configure(api_key="YOUR_API_KEY")

def extract_video_id(url):
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"
def generate_flashcards(transcript):
    prompt = f"""
    Convert the following transcript of youtube video into paragraphs(each paragraph should be atmost 100 words), don't add headings and do not include any content except the video content:
    Transcript: {transcript}
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    
    if response:
        print(f"Generated flashcards: {response.text}")  # Log the generated flashcards
        return response.text
    else:
        print("Error generating flashcards.")  # Log error if response is empty or invalid
        return "Error generating flashcards."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    youtube_url = data.get("youtube_url")

    if not youtube_url:
        return jsonify({"error": "No YouTube URL provided."})

    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL."})

    transcript = get_youtube_transcript(video_id)
    if "Error" in transcript:
        return jsonify({"error": transcript})

    flashcards = generate_flashcards(transcript)

    return jsonify({"flashcards": flashcards})

if __name__ == '__main__':
    # Dynamically use the port set by the environment (if any), otherwise fallback to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
