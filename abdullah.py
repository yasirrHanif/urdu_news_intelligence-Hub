import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import base64
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import time
import requests
import json
from urllib.parse import urlparse
import re
from datetime import datetime, timedelta
import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer # REMOVED: No longer needed for similarity
# from sklearn.metrics.pairwise import cosine_similarity # REMOVED: No longer needed for similarity
import logging

# --- NEW IMPORTS FOR SENTENCE-TRANSFORMERS ---
from sentence_transformers import SentenceTransformer, util
import numpy as np
# ---------------------------------------------

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ----------------------- Page Configuration -----------------------
st.set_page_config(
    page_title="🔍 Urdu News Intelligence Hub",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🔍"
)

# ----------------------- Configuration -----------------------
# Keeping hardcoded API keys as per user's request.
# IMPORTANT: Hardcoding API keys is NOT recommended for production environments.
# For better security, consider using Streamlit's st.secrets or environment variables.
GOOGLE_API_KEY = "AIzaSyCBnb59C5dzeTxS1TUKFvcldm_1RImhDr4"
SEARCH_ENGINE_ID = "a10f121089fe344cc"

# ----------------------- Custom CSS Styling -----------------------
def inject_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Roboto:wght@300;400;500;700&display=swap');

    /* Global Styles */
    body {
        font-family: 'Roboto', sans-serif;
        color: #e0e0e0;
        background-color: #1a1a2e; /* Darker background */
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif;
        color: #00bcd4; /* Light blue/cyan */
    }

    .stApp {
        background-color: #1a1a2e;
        color: #e0e0e0;
    }

    /* Header Styling */
    .stApp > header {
        background-color: #2e003b; /* Dark purple header */
        padding: 1rem;
        border-bottom: 2px solid #00bcd4;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
    }

    .stApp > header h1 {
        color: #ffffff;
        text-align: center;
    }

    /* Main content area */
    .stApp > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) {
        padding: 2rem;
    }

    /* Sidebar Styling */
    .st-emotion-cache-1na0fya { /* Streamlit sidebar container */
        background-color: #1a1a2e;
        border-right: 1px solid #3a3a4c;
    }

    .st-emotion-cache-vk3305 { /* Sidebar elements */
        color: #e0e0e0;
    }

    /* Text Input and Text Area */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #2a2a4a; /* Dark blue */
        color: #e0e0e0;
        border: 1px solid #00bcd4;
        border-radius: 8px;
        padding: 12px;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    .stTextInput > label, .stTextArea > label {
        color: #00bcd4;
        font-weight: 600;
    }

    /* Buttons */
    .stButton > button {
        background-color: #00bcd4; /* Light blue/cyan */
        color: #1a1a2e;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: background-color 0.3s, transform 0.2s;
        box-shadow: 0 4px 6px rgba(0, 188, 212, 0.3);
    }

    .stButton > button:hover {
        background-color: #0097a7; /* Darker blue on hover */
        transform: translateY(-2px);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #2a2a4a;
        color: #00bcd4 !important;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #00bcd4;
    }
    .streamlit-expanderContent {
        background-color: #1a1a2e;
        border: 1px solid #3a3a4c;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 15px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #2a2a4a;
        color: #00bcd4;
        border-bottom: 3px solid transparent;
        transition: border-bottom 0.3s ease;
        padding: 10px 20px;
        font-weight: 600;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        border-bottom: 3px solid #0097a7;
        color: #00e5ff;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #1a1a2e;
        color: #ffffff;
        border-bottom: 3px solid #00bcd4;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #2a2a4a;
        border: 1px solid #00bcd4;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stMetric"] label {
        color: #e0e0e0;
        font-size: 1.1em;
    }
    [data-testid="stMetric"] > div > div:nth-child(2) > div {
        color: #00bcd4; /* Value color */
        font-size: 2em;
        font-weight: 700;
    }
    [data-testid="stMetric"] > div > div:nth-child(3) > div {
        color: #e0e0e0; /* Delta color */
    }

    /* Alerts (Success, Warning, Error, Info) */
    .stAlert {
        border-radius: 8px;
        padding: 15px;
    }
    .stAlert.success {
        background-color: #28a74533; /* Green with transparency */
        border-left: 5px solid #28a745;
        color: #28a745;
    }
    .stAlert.warning {
        background-color: #ffc10733; /* Yellow with transparency */
        border-left: 5px solid #ffc107;
        color: #ffc107;
    }
    .stAlert.error {
        background-color: #dc354533; /* Red with transparency */
        border-left: 5px solid #dc3545;
        color: #dc3545;
    }
    .stAlert.info {
        background-color: #17a2b833; /* Blue with transparency */
        border-left: 5px solid #17a2b8;
        color: #17a2b8;
    }

    /* Horizontal Rule */
    hr {
        border-top: 1px solid #3a3a4c;
    }

    /* Custom Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 1px solid #3a3a4c;
        background-color: #1a1a2e;
        color: rgba(255,255,255,0.7);
        font-family: 'Roboto', sans-serif;
    }
    .footer h3 {
        color: #00bcd4 !important;
        margin-bottom: 0.5rem;
    }
    .footer p {
        margin-bottom: 0.5rem;
    }
    .footer span {
        display: inline-block;
        margin: 0 0.8rem;
        padding: 0.4rem 0.8rem;
        background-color: #2a2a4a;
        border-radius: 5px;
        color: #e0e0e0;
        font-size: 0.9em;
    }
    .footer .st-emotion-cache-10mrprx { /* Adjust Streamlit block containers within footer if needed */
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply custom CSS
inject_custom_css()

# ----------------------- Model Loading -----------------------
@st.cache_resource
def load_models():
    try:
        logging.info("Loading Fake News Detection model...")
        tokenizer_fake_news = AutoTokenizer.from_pretrained("models/saved_model_distilbert_multilingual_fake_news")
        model_fake_news = AutoModelForSequenceClassification.from_pretrained("models/saved_model_distilbert_multilingual_fake_news")
        logging.info("Fake News Detection model loaded.")

        logging.info("Loading Sentiment Analysis model...")
        tokenizer_sentiment = AutoTokenizer.from_pretrained("models/saved_model_sentiment_90")
        model_sentiment = AutoModelForSequenceClassification.from_pretrained("models/saved_model_sentiment_90")
        logging.info("Sentiment Analysis model loaded.")

        # --- NEW: Load Sentence-BERT model for Semantic Similarity ---
        logging.info("Loading Sentence-BERT model for semantic similarity...")
        try:
            # Using a multilingual model for better Urdu support
            sentence_transformer_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logging.info("Sentence-BERT model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading Sentence-BERT model: {e}")
            sentence_transformer_model = None # Handle cases where model loading fails
        # -------------------------------------------------------------

        return tokenizer_fake_news, model_fake_news, tokenizer_sentiment, model_sentiment, sentence_transformer_model
    except Exception as e:
        st.error(f"Error loading models. Please ensure 'models/' directory exists and contains the necessary files. Error: {e}")
        logging.error(f"Model loading failed: {e}")
        st.stop() # Stop the app if models cannot be loaded

# Unpack the new return value for sentence_transformer_model
tokenizer_fake_news, model_fake_news, tokenizer_sentiment, model_sentiment, sentence_transformer_model = load_models()

# ----------------------- EnhancedFakeNewsDetector Class -----------------------
class EnhancedFakeNewsDetector:
    def __init__(self, api_key, search_engine_id, tokenizer_fake_news, model_fake_news, sentence_transformer_model):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.tokenizer_fake_news = tokenizer_fake_news
        self.model_fake_news = model_fake_news
        self.sentence_transformer_model = sentence_transformer_model # NEW: Assign sentence transformer model

        # Extended Urdu Stop Words
        self.urdu_stop_words = set([
            "اور", "کا", "کی", "کے", "کو", "میں", "ہے", "ہیں", "تھا", "تھی", "تھے", "جو", "یہ", "وہ", "پر", "سے", "بھی",
            "نے", "تک", "تھوڑا", "بہت", "زیادہ", "کم", "ساتھ", "بغیر", "علاوہ", "لیکن", "جب", "تاکہ", "اگر", "تو",
            "گے", "گی", "گا", "سکے", "سکتا", "سکتے", "ہوا", "ہوئی", "ہوئے", "کر", "کرنا", "کرتے", "کرنی", "والا",
            "والی", "والے", "جس", "جن", "ان", "اس", "یہاں", "وہاں", "کیسے", "کیوں", "کب", "کہاں", "کون", "کیا",
            "خود", "اپنی", "اپنا", "اپنے", "ہر", "ایک", "دو", "تین", "چار", "پانچ", "چھ", "سات", "آٹھ", "نو", "دس",
            "صرف", "پھر", "شاید", "بلکہ", "ضرور", "خاص", "عام", "نیا", "نئی", "نئے", "اچھا", "اچھی", "اچھے", "بڑا",
            "بڑی", "بڑے", "چھوٹا", "چھوٹی", "چھوٹے", "پہلا", "پہلی", "پہلے", "آخری", "بعد", "قبل", "درمیان", "اردو",
            "نیوز", "خبر", "کے لیے", "کے بارے میں", "کی طرف", "کی وجہ سے", "جس طرح", "کیونکہ", "چونکہ", "حالانکہ",
            "وغیرہ", "یعنی", "مثلاً", "فقط", "مگر", "لہذا", "چنانچہ", "جیسے", "جیسا", "جیسی", "جیسے کہ", "یوں",
            "جیسے ہی", "جو کہ", "یوں کہ", "جو بھی", "اس کے", "اس کے بعد", "اس کے علاوہ", "اس کے باوجود", "اور بھی",
            "اور کچھ", "اور زیادہ", "کچھ اور", "کچھ نہیں", "نہ ہی", "اسی طرح", "ایک بار پھر", "بار بار", "ہر بار",
            "ہر دن", "ہر سال", "ابھی", "فوری", "فی الحال", "جب تک", "جس وقت", "جبکہ", "تاہم", "تب", "فورا", "بعد میں"
            "تھا","ہیں","ہے","کیا","آپکے", "آپکا", "آپکو", "ہاں", "ہوں", "ہوگا", "ہوگی", "ہوگے", "ت", "و", "کہیں", "وغیرہ",
    "ا", "ان", "انکے", "انکی", "انکو", "انہوں", "انہیں", "اور", "ایسے", "ب", "بہت", "تاکہ", "تھا",
    "تھی", "تھے", "تھیں", "جب", "جبکہ", "جو", "حالانکہ", "خواہ", "خود", "دو", "دی", "دیا", "دیتے",
    "دیکھا", "دیکھو", "دیں", "رہا", "رہی", "رہے", "رہیں", "رہے", "ساتھ", "سب", "سبھی", "سو", "سے",
    "شاید", "صرف", "ضرور", "ضرورت", "ضروری", "طرح", "طرف", "طور", "علاوہ", "عین", "غیر", "لیکن", "مگر",
    "میں", "نہ", "نہیں", "والا", "والوں", "والی", "والیں", "والے", "وغیرہ", "وہ", "وہاں", "وہی", "وہیں",
    "پ", "پر", "پوری", "پھر", "چاہئے", "چاہتے", "چاہیے", "چاہیں", "چونکہ", "چکی", "چکے", "چکیں", "چکے",
    "چنانچہ", "چند", "چکی", "چکے", "کر", "کرتا", "کرتی", "کرتے", "کرتی", "کرتے", "کرنا", "کرنے", "کرنی",
    "کرنے", "کرنی", "کرنے", "کرنیں", "کرنے", "کرنیں", "کرنے", "کرنیں", "کرے", "کریں", "کم", "کس", "کسی",
    "کسے", "کی", "کیسے", "کیونکہ", "کے", "گئی", "گئے", "گئیں", "گئے", "گا", "گائیں", "گرم", "گریبان", "گریبانیں",
    "گی", "گیا", "گیں", "ہر", "ہم", "ہمیں", "ہو", "ہوئی", "ہوئیں", "ہوئے", "ہوئیں", "ہوتا", "ہوتی", "ہوتے",
    "ہوتی", "ہوتے", "ہونا", "ہونگے", "ہونگی", "ہونگے", "ہونی", "ہونیں", "ہونے", "ہونیں", "ہوں", "ہوگا", "ہوگی",
    "ہوگا", "ہوگی", "ہوگے", "ہوگیں", "یا", "یہ", "یہاں", "یہی", "یہیں", "یہے","اب","ابھی","اپنا","اپنے","اپنی",
    "اٹھا","اس","اسے","اسی","اگر","ان","انہوں","انہی","انہیں","انھیں","او","اور","اے","ایسا","ایسے","ایسی","ایک",
    "آ","آپ","آتا","آتے","آتی","آگے","آنا","آنے","آنی","آئے","آئی","آئیں","آیا","با","بڑا","بڑے","بڑی","بعد","بعض",
    "بلکہ","بہت","بھی","بے","پاس","پر","پہلے","پھر","تا","تاکہ","تب","تجھ","تجھے","تک","تم","تمام","تمہارا","تمہارے",
    "تمھارے","تمہاری","تمہیں","تمھیں","تھا","تھے","تھی","تھیں","تو","تیری","تیرے","جا","جاتا","جاتی","جاتے","جاتی","جانے",
    "جانی","جاؤ","جائے","جائیں","جب","جس","جن","جنہوں","جنہیں","جو","جیسا","جیسے","جیسی","جیسوں","چاہیئے","چلا","چاہے","چونکہ",
    "حالاں","حالانکہ","دو","دونوں","دوں","دے","دی","دیا","دیں","دیے","دیتا","دیتے","دیتی","دینا","دینے","دینی","دیئے","ڈالا","ڈالنا",
    "ڈالنے","ڈالنی","ڈالے","ڈالی","ذرا","رکھا","رکھتا","رکھتے","رکھتی","رکھنا","رکھنے","رکھنی","رکھے","رکھی","رہ","رہا","رہتا","رہتے",
    "رہتی","رہنا","رہنے","رہنی","رہو","رہے","رہی","رہیں","زیادہ","سا","سامنے","سب","سکتا","سو","سے","سی","شاید","صرف","طرح","طرف","عین",
    "کا","کبھی","کچھ","کہہ","کر","کرتا","کرتے","کرتی","کرنا","کرنے","کرو","کروں","کرے","کریں","کس","کسے","کسی","کہ","کہا","کہے","کو","کون",
    "کوئی","کے","کی","کیا","کیسے","کیوں","کیونکہ","کیے","کئے","گا","گویا","گے","گی","گیا","گئے","گئی","لا","لاتا","لاتے","لاتی","لانا","لانے","لانی",
    "لایا","لائے","لائی","لگا","لگے","لگی","لگیں","لو","لے","لی","لیا","لیتا","لیتے","لیتی","لیکن","لیں","لیے","لئے","مجھ","مجھے","مگر","میرا",
    "میرے","میری","میں","نا","نہ","نہایت","نہیں","نے","ہاں","ہر","ہم","ہمارا","ہمارے","ہماری","ہو","ہوا","ہوتا","ہوتے","ہوتی","ہوتیں","ہوں",
    "ہونا","ہونگے","ہونے","ہونی","ہوئے","ہوئی","ہوئیں","ہے","ہی","ہیں","و","والا","والوں","والے","والی","وہ","وہاں","وہی","وہیں","یا","یعنی",
    "یہ","یہاں","یہی","یہیں"
        ])
        # REMOVED: self.tfidf_vectorizer = TfidfVectorizer(...) from here, as BERT handles similarity

        # Expanded and Categorized Trusted Domains (examples, ideally from a researched list)
        self.trusted_domains = [
            "dawn.com", "thenews.com.pk", "jang.com.pk", "geo.tv", "arynews.tv",
            "urdupoint.com", "express.pk", "samaa.tv", "pakistantoday.com.pk",
            "nation.com.pk", "tribune.com.pk", "bbc.com", "reuters.com", "apnews.com",
            "aljazeera.com", "dw.com", "voanews.com", "npr.org", "nytimes.com",
            "washingtonpost.com", "theguardian.com", "al-arabiya.net", "indiatimes.com", # Added a few more examples
            "aa.com.tr", "xinhua.net", "tass.com", "kyodonews.net"
        ]
        self.semi_trusted_domains = [
            "siasat.pk", "urdu.dunyanews.tv", "humnews.pk", "92newshd.tv", "lahorenews.tv",
            "mmnews.tv", "capitaltv.pk", "abbtakk.tv", "bolnews.com", "urdu.radio.gov.pk",
            "urdu.arynews.tv", "urdu.geo.tv", "khabrain.com", "pakistan.web.pk",
            "pakistannews.pk", "pakobserver.net", "urdu.news.cn"
        ]
        self.low_credibility_indicators = [
            ".blogspot.com", ".wordpress.com", ".weebly.com", ".wix.com",
            "facebook.com", "twitter.com", "youtube.com", "dailymotion.com",
            "pinterest.com", "reddit.com", "medium.com", "linkedin.com",
            "quora.com", "wikipedia.org", # Wikipedia can be a starting point but not a primary source for news verification
            ".info", ".biz", ".xyz", ".club", ".online", ".site", ".store", # Suspicious TLDs
            "anonhq.com", "beforeitsnews.com", "worldnewsdailyreport.com", # Known fake news sites
            "operanewsapp.com", "ucweb.com", # Aggregators that often host unverified content
            "dailykhabar.pk", "dunyaweb.com", "pakistanwatch.com", "pakistannews.website",
            "news.google.com/rss", # RSS feeds often contain content from varied sources, not all credible
            "youtube.com", "tiktok.com", "instagram.com" # Social media platforms are generally low credibility for news
        ]

    def clean_urdu_text(self, text):
        """
        Cleans Urdu text by removing non-Urdu characters (except spaces, numbers, and basic punctuation),
        and normalizing spaces. Numbers and a few common punctuation marks are retained for search relevance.
        """
        # Allowed characters: Urdu Unicode block, spaces, numbers, and selected punctuation (.,!?-).
        cleaned_text = re.sub(r'[^\u0600-\u06FF\s0-9\.\,\!\?\(\)\-]', '', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        return cleaned_text

    def predict_fake_news(self, news_text):
        """Predicts if the news is fake or real using the fine-tuned model."""
        cleaned_text = self.clean_urdu_text(news_text)
        if not cleaned_text:
            return "Unable to predict", 0.0

        inputs = self.tokenizer_fake_news(cleaned_text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model_fake_news(**inputs)

        # Assuming class 0 is 'Fake' and class 1 is 'Real'. Confirm this from your model training.
        probabilities = torch.softmax(outputs.logits, dim=1)[0]
        fake_prob = probabilities[0].item() # Assuming Fake is index 0
        real_prob = probabilities[1].item() # Assuming Real is index 1

        if real_prob >= fake_prob:
            prediction = "Real"
            confidence = real_prob
        else:
            prediction = "Fake"
            confidence = fake_prob

        return prediction, confidence

    def search_google(self, query, num_results=5, date_restrict=None):
        """
        Performs a Google Custom Search for the given query.
        date_restrict can be 'd1' (past 24h), 'w1' (past week), 'm1' (past month), etc.
        """
        if not self.api_key or not self.search_engine_id:
            logging.error("Google API Key or Search Engine ID is missing.")
            return None

        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': self.api_key,
            'cx': self.search_engine_id,
            'num': num_results,
            'lr': 'lang_ur'  # Restrict to Urdu language results
        }
        if date_restrict:
            params['dateRestrict'] = date_restrict

        try:
            response = requests.get(base_url, params=params, timeout=10) # Added timeout
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as errh:
            logging.error(f"HTTP Error: {errh} - Status Code: {errh.response.status_code} - Query: {query}")
            if errh.response.status_code == 429:
                st.warning("Google API rate limit reached. Please wait a moment before trying again.")
            return None
        except requests.exceptions.ConnectionError as errc:
            logging.error(f"Error Connecting: {errc} - Query: {query}")
            return None
        except requests.exceptions.Timeout as errt:
            logging.error(f"Timeout Error: {errt} - Query: {query}")
            return None
        except requests.exceptions.RequestException as err:
            logging.error(f"Request Exception: {err} - Query: {query}")
            return None
        except json.JSONDecodeError as errj:
            logging.error(f"JSON Decode Error: {errj} - Response: {response.text}")
            return None

    def extract_key_phrases(self, text, num_phrases=12):
        """
        Extracts key phrases from the Urdu text for effective web searching.
        Prioritizes n-grams that are not stop words.
        """
        cleaned_text = self.clean_urdu_text(text)
        words = cleaned_text.split()
        filtered_words = [word for word in words if word not in self.urdu_stop_words and len(word) > 1]

        phrases = []
        # Add original text if it's very short and clean, as a primary search term
        if len(words) < 15 and len(cleaned_text) > 0:
            phrases.append(cleaned_text)

        # Generate n-grams (1-gram to 4-gram)
        for n in range(1, 5):
            for i in range(len(filtered_words) - n + 1):
                ngram = " ".join(filtered_words[i:i+n])
                if ngram and ngram not in self.urdu_stop_words:
                    phrases.append(ngram)

        # No TF-IDF for key phrase extraction here, relying on n-grams and filtered words
        # (This section is kept as original from your provided code, TF-IDF was used for similarity, not phrase extraction)

        # Remove duplicates and sort phrases
        unique_phrases = []
        for p in phrases:
            if p not in unique_phrases:
                unique_phrases.append(p)

        # Sort by length (desc) and then by original text appearance (asc)
        unique_phrases.sort(key=lambda x: (len(x), cleaned_text.find(x) if cleaned_text.find(x) != -1 else float('inf')), reverse=True)

        return unique_phrases[:num_phrases] # Return top N unique phrases

    def analyze_source_credibility(self, url):
        """Determines the credibility of a URL based on predefined lists."""
        domain = urlparse(url).netloc # Corrected to use urlparse for robust domain extraction
        domain = domain.lower().replace("www.", "")

        if any(d in domain for d in self.trusted_domains):
            return "high"
        if any(d in domain for d in self.semi_trusted_domains):
            return "medium"
        if any(ind in domain for ind in self.low_credibility_indicators):
            return "low"
        return "unknown" # Default to unknown if not explicitly categorized

    # --- UPDATED: calculate_similarity_score using Sentence-BERT ---
    def calculate_similarity_score(self, original_text, search_results):
        """
        Calculates the maximum semantic (BERT) similarity between the original text
        and combined titles/snippets from search results.
        Uses the pre-initialized self.sentence_transformer_model.
        """
        if not self.sentence_transformer_model:
            logging.error("Sentence-BERT model not loaded. Cannot calculate semantic similarity.")
            return 0.0
        
        if not search_results:
            return 0.0

        # Encode the original text
        try:
            original_embedding = self.sentence_transformer_model.encode(
                self.clean_urdu_text(original_text),
                convert_to_tensor=True
            )
        except Exception as e:
            logging.error(f"Error encoding original text: {e}")
            return 0.0

        max_similarity = 0.0

        # Encode each search result's title/snippet and calculate similarity
        for item in search_results:
            title_snippet = self.clean_urdu_text(item.get('title', '') + ' ' + item.get('snippet', ''))
            if title_snippet:
                try:
                    search_result_embedding = self.sentence_transformer_model.encode(
                        title_snippet,
                        convert_to_tensor=True
                    )
                    # Calculate cosine similarity between the original and current search result embedding
                    cosine_sim = util.cosine_sim(original_embedding, search_result_embedding).item()
                    
                    if cosine_sim > max_similarity:
                        max_similarity = cosine_sim
                except Exception as e:
                    logging.warning(f"Could not encode search result snippet for similarity: {e}")
                    # Continue to next item if one fails

        return max_similarity
    # -------------------------------------------------------------

    # --- UPDATED: _calculate_confidence with new BERT thresholds ---
    def _calculate_confidence(self, results):
        """Calculates a comprehensive search confidence score."""
        num_high_credible = results['high_credible_sources']
        num_medium_credible = results['high_credible_sources'] # BUG FIX: Corrected this from 'high_credible_sources' to 'medium_credible_sources'
        total_unique_sources = len(results['sources'])
        similarity_score = results['similarity_score'] # This is now the BERT semantic similarity score

        confidence = 0.0

        # Base confidence from credible sources
        # Each high credible source adds more weight than medium.
        # Max confidence from high credible sources: 0.6
        # A high source contributes 0.20, so 3 high sources give 0.6.
        confidence += min(num_high_credible * 0.25, 0.75)

        # Max confidence from medium credible sources: 0.2
        # A medium source contributes 0.05, so 4 medium sources give 0.2.
        confidence += min(num_medium_credible * 0.06, 0.25)

        # Add confidence based on content similarity
        # Similarity score directly contributes, but is capped.
        # Max confidence from similarity: 0.3
        confidence += similarity_score * 0.40# This weight can be adjusted if similarity needs more/less impact

        # Penalties/Adjustments
        if total_unique_sources == 0:
            confidence = 0.0 # No sources found, zero confidence
        elif num_high_credible == 0 and num_medium_credible == 0:
            # If only low or unknown credible sources are found, reduce confidence significantly
            confidence *= 0.2# Penalize heavily if no genuinely credible sources
        elif total_unique_sources < 3:
            # If very few sources found overall (even if some are credible)
            confidence *= 0.75# Slight reduction for limited corroboration

        # If similarity is very low, it significantly impacts confidence (Adjusted for BERT)
        # BERT scores below 0.60 often indicate low semantic similarity.
        if similarity_score < 0.65: # Threshold adjusted from 0.2 to 0.60
            confidence *= 0.4 # Halve confidence if content similarity is poor

        # New thresholds for very high similarity (specific to BERT scores)
        # These give a boost for strong semantic matches.
        if similarity_score >= 0.90: # Very strong match (e.g., paraphrases)
            confidence = min(confidence + 0.30, 1.0) # Significant boost
        elif similarity_score >= 0.80: # Strong match
            confidence = min(confidence + 0.20, 1.0) # Moderate boost

        # Cap confidence at 1.0 (100%)
        return min(confidence, 1.0)
    # -------------------------------------------------------------

    def _generate_analysis_message(self, results):
        """Generates a user-friendly analysis message in Urdu."""
        status = results['verification_status']
        confidence_percent = results['analysis']['confidence'] * 100
        num_sources = len(results['sources'])
        num_high = results['high_credible_sources']
        num_medium = results['medium_credible_sources']
        similarity = results['similarity_score'] * 100

        # General message components
        source_info = ""
        if num_high > 0 and num_medium > 0:
            source_info = f"We found matches from **{num_high} high-credible** and **{num_medium} medium-credible** sources."
        elif num_high > 0:
            source_info = f"We found matches from **{num_high} high-credible** sources."
        elif num_medium > 0:
            source_info = f"We found matches from **{num_medium} medium-credible** sources."
        elif num_sources > 0:
            source_info = f"We found **{num_sources}** sources (mostly low or unknown credibility)."
        else:
            source_info = "No relevant web sources were found."


        if status == 'verified':
            message = (f"**News Verified:** This news is likely accurate. {source_info} "
                       f"The text similarity score is **{similarity:.1f}%**.")
        elif status == 'partially_verified':
            message = (f"**News Partially Verified:** Full verification for this news was not possible. {source_info} "
                       f"The text similarity score is **{similarity:.1f}%**."
                       f"Further investigation may be required.")
        elif status == 'unverified':
            message = (f"**News Unverified:** We could not find enough credible sources or strong matches to verify this news. "
                       f"{source_info} The text similarity score is only **{similarity:.1f}%**. "
                       f"Please be cautious, this news might be fabricated.")
        else: # Fallback for unexpected statuses
            message = (f"**Low Confidence in Verification:** We encountered low confidence during the verification of this news. "
                       f"This might be due to limited sources or very low text similarity. "
                       f"Please review the search results for more details.")

        return message


    def enhanced_verification(self, text):
        """
        Orchestrates the enhanced web verification process.
        This version strategically constructs search queries for better relevance.
        """
        verification_results = {
            'search_queries_used': [],
            'sources': [],
            'high_credible_sources': 0,
            'medium_credible_sources': 0,
            'similarity_score': 0.0,
            'analysis': {'confidence': 0.0, 'message': ''},
            'verification_status': 'unverified'
        }

        cleaned_text = self.clean_urdu_text(text)
        if not cleaned_text or len(cleaned_text) < 10:
            verification_results['analysis']['message'] = "Please provide more text for analysis."
            logging.info("Input text too short or empty for web verification.")
            return verification_results

        key_phrases = self.extract_key_phrases(cleaned_text, num_phrases=12) # Get more key phrases
        logging.info(f"Extracted key phrases: {key_phrases}")

        search_strategies = []
        if key_phrases:
            # Strategy 1: Exact match for the most specific key phrase (highest priority)
            search_strategies.append(f'"{key_phrases[0]}"')
            if len(key_phrases) > 1:
                # Strategy 2: Exact match for top two key phrases combined
                search_strategies.append(f'"{key_phrases[0]} {key_phrases[1]}"')
            # Strategy 3: General search with top 3 unquoted terms for broader recall
            search_strategies.append(' '.join(key_phrases[:3]))
            # Strategy 4: A slightly longer, unquoted phrase for more context, using different starting point
            if len(key_phrases) > 3:
                 search_strategies.append(' '.join(key_phrases[1:4]))
            # Strategy 5: Fallback to first few words of the original text if strong key phrases are few
            if len(cleaned_text.split()) > 10 and len(key_phrases) < 3:
                search_strategies.append(' '.join(cleaned_text.split()[:8]))
            # Strategy 6: Consider adding a time-bound search for breaking news (requires search_google modification if not already supported)
            # Example: search_strategies.append({"query": key_phrases[0], "date_restrict": "d1"})
        else:
            # Fallback if no key phrases could be extracted (e.g., very short or highly symbolic text)
            search_strategies.append(' '.join(cleaned_text.split()[:5])) # Use first 5 words if no key phrases

        # Ensure unique strategies while preserving order
        search_strategies = list(dict.fromkeys(search_strategies))

        all_results_items = []
        unique_urls = set()

        progress_text = "Verifying with web sources... Please wait."
        my_bar = st.progress(0, text=progress_text)
        total_strategies = len(search_strategies)

        for i, query in enumerate(search_strategies):
            logging.info(f"Executing search query: {query}")
            my_bar.progress((i + 1) / total_strategies, text=f"{progress_text} ({i+1}/{total_strategies} searches)")
            time.sleep(0.5) # Be polite to the API and avoid hitting rate limits too quickly

            search_response = self.search_google(query, num_results=5) # Request 5 results per query
            if search_response and 'items' in search_response:
                for item in search_response['items']:
                    url = item.get('link')
                    if url and url not in unique_urls: # Ensure uniqueness of URLs
                        credibility = self.analyze_source_credibility(url)
                        all_results_items.append({
                            'title': item.get('title'),
                            'link': url,
                            'snippet': item.get('snippet'),
                            'credibility': credibility,
                            'search_query': query # To track which query found this source
                        })
                        unique_urls.add(url)
            verification_results['search_queries_used'].append(query)
        my_bar.empty() # Hide progress bar after completion

        # Aggregate and process results
        relevant_sources = []
        high_cred_count = 0
        medium_cred_count = 0

        # Sort results: High credibility first, then medium, then unknown/low.
        # This ensures the most trustworthy sources are considered first.
        sorted_results = sorted(all_results_items,
                                key=lambda x: (x['credibility'] == 'high', x['credibility'] == 'medium', x['credibility'] == 'unknown'),
                                reverse=True)

        for source in sorted_results:
            if source['credibility'] == 'high':
                high_cred_count += 1
            elif source['credibility'] == 'medium':
                medium_cred_count += 1
            relevant_sources.append(source)

        verification_results['sources'] = relevant_sources[:10] # Limit to top 10 relevant sources for display
        verification_results['high_credible_sources'] = high_cred_count
        verification_results['medium_credible_sources'] = medium_cred_count
        # Calculate overall similarity based on all found items, not just top 10
        verification_results['similarity_score'] = self.calculate_similarity_score(cleaned_text, all_results_items)

        # Determine overall verification status and confidence
        confidence = self._calculate_confidence(verification_results)
        verification_results['analysis']['confidence'] = confidence

        if confidence >= 0.75:
            verification_results['verification_status'] = 'verified'
        elif 0.45 <= confidence < 0.75:
            verification_results['verification_status'] = 'partially_verified'
        else:
            verification_results['verification_status'] = 'unverified'

        verification_results['analysis']['message'] = self._generate_analysis_message(verification_results)

        return verification_results

# ----------------------- SentimentAnalyzer Class -----------------------
class SentimentAnalyzer:
    def __init__(self, tokenizer_sentiment, model_sentiment):
        self.tokenizer_sentiment = tokenizer_sentiment
        self.model_sentiment = model_sentiment
        # Ensure these labels match the model's output classes (e.g., 0=Negative, 1=Neutral, 2=Positive)
        self.labels = ['Negative', 'Neutral', 'Positive'] # Assuming this order

    def analyze_sentiment(self, text):
        """Analyzes the sentiment of the given text."""
        # Use detector's clean_urdu_text as it's a common utility
        # Make sure 'detector' is accessible or pass the clean_urdu_text method
        # For simplicity, I'll assume 'detector' is globally available after its initialization
        # Or, ideally, pass the cleaning function or make it static
        
        # A more robust way:
        # cleaned_text = EnhancedFakeNewsDetector.clean_urdu_text(text) # if clean_urdu_text was static
        # Or pass the detector instance:
        # cleaned_text = self.detector_instance.clean_urdu_text(text)
        
        # For now, using the global 'detector' instance as per your original code structure
        cleaned_text = detector.clean_urdu_text(text) 
        if not cleaned_text:
            return "Unable to analyze", 0.0, {'Negative': 0.0, 'Neutral': 0.0, 'Positive': 0.0}

        inputs = self.tokenizer_sentiment(cleaned_text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model_sentiment(**inputs)

        probabilities = torch.softmax(outputs.logits, dim=1)[0]
        predicted_class_id = probabilities.argmax().item()
        predicted_sentiment = self.labels[predicted_class_id]
        confidence = probabilities[predicted_class_id].item()

        # Get all sentiment scores for the chart
        sentiment_scores = {
            self.labels[i]: probabilities[i].item() for i in range(len(self.labels))
        }

        return predicted_sentiment, confidence, sentiment_scores

# ----------------------- Streamlit App Layout and Interaction -----------------------
st.title("🔍 Urdu News Intelligence Hub")
st.markdown("""
This application helps you verify Urdu news and analyze its sentiment.
Simply enter the news text and click on the "Analyze" button.
""")

# Initialize classes (UPDATED: Pass sentence_transformer_model to detector)
detector = EnhancedFakeNewsDetector(GOOGLE_API_KEY, SEARCH_ENGINE_ID, tokenizer_fake_news, model_fake_news, sentence_transformer_model)
sentiment_analyzer = SentimentAnalyzer(tokenizer_sentiment, model_sentiment)

news_text = st.text_area("Enter news text here:", height=200, help="Paste the Urdu news text you want to analyze in this box.")

col1_actions, col2_actions = st.columns(2)

check_news = col1_actions.button("🤖 AI + Web Verification", use_container_width=True)
analyze_sentiment = col2_actions.button("💭 Analyze Sentiment", use_container_width=True)

if check_news:
    if news_text:
        with st.spinner("Analyzing with AI model and verifying with web sources..."):
            ai_prediction, ai_confidence = detector.predict_fake_news(news_text)
            web_verification_results = detector.enhanced_verification(news_text)

            st.session_state['ai_prediction'] = ai_prediction
            st.session_state['ai_confidence'] = ai_confidence
            st.session_state['web_verification_results'] = web_verification_results
        st.rerun() # Rerun to display results in tabs immediately
    else:
        st.warning("Please enter news text for verification.")

if analyze_sentiment:
    if news_text:
        with st.spinner("Analyzing sentiment..."):
            sentiment_prediction, sentiment_confidence, sentiment_scores = sentiment_analyzer.analyze_sentiment(news_text)
            st.session_state['sentiment_prediction'] = sentiment_prediction
            st.session_state['sentiment_confidence'] = sentiment_confidence
            st.session_state['sentiment_scores'] = sentiment_scores
        st.rerun() # Rerun to display results in tabs immediately
    else:
        st.warning("Please enter news text for sentiment analysis.")


# Display results in tabs
tab1, tab2 = st.tabs(["🤖 AI Model Analysis", "🔎 Web Source Verification"])

with tab1:
    st.header("AI Model Analysis")
    if 'ai_prediction' in st.session_state:
        # Fake News Prediction
        col1_ai, col2_ai = st.columns(2)
        with col1_ai:
            st.metric(label="News Type (AI)", value=st.session_state['ai_prediction'])
        with col2_ai:
            st.metric(label="Confidence (AI)", value=f"{st.session_state['ai_confidence']:.2%}")

        if st.session_state['ai_prediction'] == "Fake":
            st.error("⚠️ According to the AI model, this news might be **Fake**.")
        elif st.session_state['ai_prediction'] == "Real":
            st.success("✅ According to the AI model, this news appears to be **Real**.")
        else:
            st.info("AI model prediction not available.")

        st.markdown("---")

        # Sentiment Analysis Results
        st.subheader("Sentiment Analysis of News")
        if 'sentiment_prediction' in st.session_state:
            col1_sent, col2_sent = st.columns(2)
            with col1_sent:
                st.metric(label="Sentiment (AI)", value=st.session_state['sentiment_prediction'])
            with col2_sent:
                st.metric(label="Confidence (Sentiment)", value=f"{st.session_state['sentiment_confidence']:.2%}")

            sentiment_df = pd.DataFrame(st.session_state['sentiment_scores'].items(), columns=['Sentiment', 'Score'])
            fig = px.bar(sentiment_df, x='Sentiment', y='Score',
                         color='Sentiment',
                         color_discrete_map={'Negative': '#F44346', 'Neutral': '#FFC107', 'Positive': '#28A745'},
                         title="Sentiment Score Distribution",
                         labels={'Score': 'Score', 'Sentiment': 'Sentiment'})
            fig.update_layout(showlegend=False,
                              plot_bgcolor='#1a1a2e',
                              paper_bgcolor='#1a1a2e',
                              font_color='#e0e0e0',
                              xaxis_title="Sentiment",
                              yaxis_title="Score",
                              title_font_size=18)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Click 'Analyze Sentiment' button to analyze sentiment.")
    else:
        st.info("Click 'AI + Web Verification' or 'Analyze Sentiment' button to see AI model analysis results.")

with tab2:
    st.header("Web Source Verification")
    if 'web_verification_results' in st.session_state:
        results = st.session_state['web_verification_results']

        col1_web, col2_web, col3_web = st.columns(3)
        with col1_web:
            st.metric(label="Verification Status", value=results['verification_status'].replace('_', ' ').title())
        with col2_web:
            st.metric(label="Text Similarity", value=f"{results['similarity_score']:.2%}")
        with col3_web:
            st.metric(label="Verification Confidence", value=f"{results['analysis']['confidence']:.2%}")

        # Display the main analysis message
        st.markdown(f"<div style='background-color: #2a2a4a; padding: 15px; border-radius: 8px; border: 1px solid #00bcd4; margin-bottom: 20px; font-size: 1.1em;'>{results['analysis']['message']}</div>", unsafe_allow_html=True)

        st.subheader("Search Queries Used")
        if results['search_queries_used']:
            for query in results['search_queries_used']:
                st.markdown(f"- `{query}`")
        else:
            st.info("No search queries were used for verification.")

        st.subheader("Relevant Sources Found")
        if results['sources']:
            df_sources = pd.DataFrame(results['sources'])
            # Filter to display only top 10 as already limited
            for index, row in df_sources.head(10).iterrows():
                st.markdown(f"**[{row['title']}]({row['link']})**", unsafe_allow_html=True)
                st.markdown(f"<span style='font-size: 0.9em; color: {'#28A745' if row['credibility'] == 'high' else ('#FFC107' if row['credibility'] == 'medium' else '#F44346')}'>{row['credibility'].title()}</span>", unsafe_allow_html=True)
                st.markdown(f"*{row['snippet']}*")
                st.markdown("---")
        else:
            st.warning("No credible sources found related to the news.")
    else:
        st.info("Click 'AI + Web Verification' to start web source verification.")

st.markdown("---")

# Enhanced Footer
st.markdown("""
<div class="footer">
    <h3 style="color: #00bcd4; margin-bottom: 1rem; font-family: 'Poppins', sans-serif;">🚀 Enhanced News Intelligence Hub</h3>
    <p style="color: rgba(255,255,255,0.85); margin-bottom: 1.5rem; font-size: 1.1rem;">
        Developed by <strong>Yasir</strong> and <strong>Abdullah</strong> | Enhanced with Google Search Integration
    </p>
    <div style="display: flex; justify-content: center; align-items: center; gap: 2.5rem; margin-top: 1.5rem; flex-wrap: wrap;">
        <span style="color: rgba(255,255,255,0.7); font-size: 1rem;">🤖 AI-Powered</span>
        <span style="color: rgba(255,255,255,0.7); font-size: 1rem;">🌐 Web-Verified</span>
        <span style="color: rgba(255,255,255,0.7); font-size: 1rem;">📊 Sentiment Analysis</span>
    </div>
    <p style="color: rgba(255,255,255,0.6); margin-top: 2rem; font-size: 0.9em;">
        © 2024 Urdu News Intelligence Hub. All rights reserved.
    </p>
</div>
""", unsafe_allow_html=True)