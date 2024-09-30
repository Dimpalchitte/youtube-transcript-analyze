from transformers import (
    BartForConditionalGeneration,
    BartTokenizer,
    BertForTokenClassification,
    BertTokenizer,
    AutoModelForQuestionAnswering,
    AutoModelForSequenceClassification,  # Add this line to import the model
    AutoTokenizer,
    pipeline
)
import os

# Create models directory if it doesn't exist
os.makedirs('./models/summarization', exist_ok=True)
os.makedirs('./models/sentiment-analysis', exist_ok=True)
os.makedirs('./models/keyword-extraction', exist_ok=True)
os.makedirs('./models/question-answering', exist_ok=True)

# Summarization model
model_name = "facebook/bart-large-cnn"
summarization_model = BartForConditionalGeneration.from_pretrained(model_name)
summarization_tokenizer = BartTokenizer.from_pretrained(model_name)
summarization_model.save_pretrained('./models/summarization/')
summarization_tokenizer.save_pretrained('./models/summarization/')

# Sentiment analysis model
sentiment_model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
sentiment_model.save_pretrained('./models/sentiment-analysis/')
sentiment_tokenizer.save_pretrained('./models/sentiment-analysis/')

# Keyword extraction model
keyword_model_name = "dbmdz/bert-large-cased-finetuned-conll03-english"
keyword_model = BertForTokenClassification.from_pretrained(keyword_model_name)
keyword_tokenizer = BertTokenizer.from_pretrained(keyword_model_name)
keyword_model.save_pretrained('./models/keyword-extraction/')
keyword_tokenizer.save_pretrained('./models/keyword-extraction/')

# Question-Answering model
qa_model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
qa_model = AutoModelForQuestionAnswering.from_pretrained(qa_model_name)
qa_tokenizer = AutoTokenizer.from_pretrained(qa_model_name)
qa_model.save_pretrained('./models/question-answering/')
qa_tokenizer.save_pretrained('./models/question-answering/')
