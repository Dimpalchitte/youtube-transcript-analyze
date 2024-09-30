from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import (
    BartTokenizer,
    BartForConditionalGeneration,
    pipeline,
    BertTokenizer,
    BertForTokenClassification,
    AutoTokenizer,
    AutoModelForQuestionAnswering
)
import torch
import os
import re

app = Flask(__name__)

# Define the base directory for models and transcripts
base_dir = r'C:\Users\yadav\OneDrive\Desktop\Love Poject\youtube-transcript-analyze'
transcript_file_path = os.path.join(base_dir, 'transcript.txt')

# Define the paths to the model directories
summarization_path = os.path.join(base_dir, 'models', 'summarization')
sentiment_analysis_path = os.path.join(base_dir, 'models', 'sentiment-analysis')
keyword_extraction_path = os.path.join(base_dir, 'models', 'keyword-extraction')
qa_model_path = os.path.join(base_dir, 'models', 'question-answering')

# Load models locally for faster inference
summarization_tokenizer = BartTokenizer.from_pretrained(summarization_path)
summarization_model = BartForConditionalGeneration.from_pretrained(summarization_path)
sentiment_analyzer = pipeline("sentiment-analysis", model=sentiment_analysis_path, tokenizer=sentiment_analysis_path)
keyword_tokenizer = BertTokenizer.from_pretrained(keyword_extraction_path)
keyword_model = BertForTokenClassification.from_pretrained(keyword_extraction_path)
qa_tokenizer = AutoTokenizer.from_pretrained(qa_model_path)
qa_model = AutoModelForQuestionAnswering.from_pretrained(qa_model_path)
qa_pipeline = pipeline('question-answering', model=qa_model, tokenizer=qa_tokenizer)

# Utility function to extract video ID from URL
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

# Function to get transcript
def fetch_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([x['text'] for x in transcript_list])
        return transcript
    except Exception as e:
        print(f"Error fetching transcript for video ID {video_id}: {e}")
        return "Transcript not available"

# Function to save transcript to a file
def save_transcript_to_file(transcript):
    with open(transcript_file_path, 'w') as file:
        file.write(transcript)

# Function to read transcript from a file
def read_transcript_from_file():
    if os.path.exists(transcript_file_path):
        with open(transcript_file_path, 'r') as file:
            return file.read()
    return ""

# Function to delete the transcript file
def delete_transcript_file():
    if os.path.exists(transcript_file_path):
        os.remove(transcript_file_path)

# Function to split transcript into chunks
def split_text(text, max_length=512):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_length = len(qa_tokenizer.encode(word, add_special_tokens=False))
        if current_length + word_length > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        
        current_chunk.append(word)
        current_length += word_length
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

# Answering specific user questions
def answer_question(question):
    transcript = read_transcript_from_file()
    chunks = split_text(transcript)
    
    answers = []
    for chunk in chunks:
        inputs = {
            'question': question,
            'context': chunk
        }
        result = qa_pipeline(inputs)
        answers.append(result)
    
    # Rank answers based on their score and return the best one
    if answers:
        answers.sort(key=lambda x: x['score'], reverse=True)
        return answers[0]['answer']
    
    return "No answer found"

# Summarization Route
@app.route('/summarize', methods=['POST'])
def summarize_transcript_route():
    try:
        transcript = read_transcript_from_file()
        inputs = summarization_tokenizer(
            [transcript],
            max_length=1024,
            return_tensors='pt',
            truncation=True
        )
        summary_ids = summarization_model.generate(
            inputs['input_ids'],
            max_length=150,
            min_length=50,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )
        summary = summarization_tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        )
        return jsonify({'summary': summary})
    except Exception as e:
        print(f"Error summarizing transcript: {e}")
        return jsonify({'error': 'Failed to summarize transcript'}), 500

# Sentiment Analysis Route
@app.route('/sentiment', methods=['POST'])
def analyze_sentiment_route():
    try:
        transcript = read_transcript_from_file()
        max_length = 512
        truncated_transcript = transcript[:max_length]
        sentiment = sentiment_analyzer(truncated_transcript)
        sentiment_label = sentiment[0]['label']
        sentiment_score = sentiment[0]['score']
        return jsonify({'sentiment': {'label': sentiment_label, 'score': sentiment_score}})
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return jsonify({'error': 'Failed to analyze sentiment'}), 500

# Keyword Extraction Route
@app.route('/keywords', methods=['POST'])
def extract_keywords_route():
    try:
        transcript = read_transcript_from_file()
        tokens = keyword_tokenizer(
            transcript,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        outputs = keyword_model(**tokens)
        predictions = torch.argmax(outputs.logits, dim=2)
        tokens_with_labels = [
            (token, label) for token, label in zip(tokens.tokens(), predictions[0].tolist())
        ]
        keywords = [token for token, label in tokens_with_labels if label != 0]
        keyword_text = keyword_tokenizer.convert_tokens_to_string(keywords)
        return jsonify({'keywords': keyword_text})
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return jsonify({'error': 'Failed to extract keywords'}), 500

# Transcript Route
@app.route('/transcript', methods=['POST'])
def get_transcript_route():
    try:
        url = request.form['url']
        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        # Delete old transcript file if it exists
        delete_transcript_file()
        
        # Fetch and save new transcript
        transcript = fetch_transcript(video_id)
        save_transcript_to_file(transcript)
        return jsonify({'transcript': transcript})
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return jsonify({'error': 'Failed to fetch transcript'}), 500

# Question Answering Route
@app.route('/answer', methods=['POST'])
def answer_question_route():
    try:
        question = request.form['question']
        if not question:
            return jsonify({'error': 'Missing question'}), 400
        answer = answer_question(question)
        return jsonify({'answer': answer})
    except Exception as e:
        print(f"Error answering question: {e}")
        return jsonify({'error': 'Failed to answer question'}), 500

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
