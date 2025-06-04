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
from urllib.parse import quote_plus
import re
from datetime import datetime, timedelta # Ensure timedelta is imported
import pandas as pd

# ----------------------- Page Configuration -----------------------
st.set_page_config(
    page_title="🔍 Enhanced Urdu News Intelligence Hub",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🔍"
)

# ----------------------- Configuration -----------------------
GOOGLE_API_KEY = "AIzaSyCBnb59C5dzeTxS1TUKFvcldm_1RImhDr4"
SEARCH_ENGINE_ID = "a10f121089fe344cc"

# ----------------------- Custom CSS Styling -----------------------
def inject_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Header */
    .main-header {
        background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.3);
        text-align: center;
        animation: fadeInDown 1s ease-out;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-title {
        font-size: 3.8rem;
        font-weight: 700;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f39c12);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: gradientShift 3s ease-in-out infinite;
    }
    
    @keyframes gradientShift {
        0%, 100% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(20deg); }
    }
    
    .main-subtitle {
        font-size: 1.4rem;
        color: rgba(255,255,255,0.9);
        font-weight: 400;
        margin-bottom: 1rem;
        letter-spacing: 0.5px;
    }
    
    /* Enhanced Glass Card Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: fadeInUp 0.8s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.8s;
    }
    
    .glass-card:hover::before {
        left: 100%;
    }
    
    .glass-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
        border-color: rgba(255, 255, 255, 0.4);
    }
    
    /* Login Card */
    .login-card {
        max-width: 450px;
        margin: 5rem auto;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 3.5rem;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        text-align: center;
        animation: zoomIn 1s ease-out;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.6s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.05) !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35) !important;
        background: linear-gradient(45deg, #ff5252, #26a69a) !important;
    }
    
    /* Enhanced Text Area */
    .stTextArea textarea {
        background: rgba(20, 20, 20, 0.9) !important;
        color: #ffffff !important;
        border: 2px solid rgba(78, 205, 196, 0.5) !important;
        border-radius: 20px !important;
        font-size: 1.2rem !important;
        padding: 1.5rem !important;
        transition: all 0.4s ease !important;
        backdrop-filter: blur(15px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
        font-family: 'Roboto', sans-serif !important;
        line-height: 1.6 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #4ecdc4 !important;
        box-shadow: 0 0 30px rgba(78, 205, 196, 0.5) !important;
        background: rgba(15, 15, 15, 0.95) !important;
        transform: scale(1.02) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
        font-style: italic;
    }
    
    /* Enhanced Results Cards */
    .result-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.18), rgba(255,255,255,0.08));
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 2.5rem;
        margin: 2rem 0;
        border: 1px solid rgba(255,255,255,0.25);
        text-align: center;
        animation: bounceIn 1s ease-out;
        position: relative;
        overflow: hidden;
        transition: all 0.4s ease;
    }
    
    .result-card::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(transparent, rgba(255,255,255,0.1), transparent);
        animation: rotate 4s linear infinite;
        pointer-events: none;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .result-real {
        border-left: 6px solid #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15), rgba(76, 175, 80, 0.05));
        box-shadow: 0 0 30px rgba(76, 175, 80, 0.3);
    }
    
    .result-fake {
        border-left: 6px solid #f44336;
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.15), rgba(244, 67, 54, 0.05));
        box-shadow: 0 0 30px rgba(244, 67, 54, 0.3);
    }
    
    .result-enhanced {
        border-left: 6px solid #FF9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.15), rgba(255, 152, 0, 0.05));
        box-shadow: 0 0 30px rgba(255, 152, 0, 0.3);
    }
    
    .result-sentiment {
        border-left: 6px solid #2196F3;
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.15), rgba(33, 150, 243, 0.05));
        box-shadow: 0 0 30px rgba(33, 150, 243, 0.3);
    }
    
    /* Enhanced Verification Badge */
    .verification-badge {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        border-radius: 30px;
        font-size: 1rem;
        font-weight: 600;
        margin: 0.8rem;
        backdrop-filter: blur(15px);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .verification-badge:hover {
        transform: scale(1.1);
    }
    
    .badge-verified {
        background: rgba(76, 175, 80, 0.25);
        color: #4CAF50;
        border: 2px solid rgba(76, 175, 80, 0.4);
        box-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
    }
    
    .badge-unverified {
        background: rgba(244, 67, 54, 0.25);
        color: #f44336;
        border: 2px solid rgba(244, 67, 54, 0.4);
        box-shadow: 0 0 20px rgba(244, 67, 54, 0.3);
    }
    
    .badge-limited {
        background: rgba(255, 193, 7, 0.25);
        color: #FFC107;
        border: 2px solid rgba(255, 193, 7, 0.4);
        box-shadow: 0 0 20px rgba(255, 193, 7, 0.3);
    }
    
    /* Enhanced Animations */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-80px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(80px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes zoomIn {
        from { opacity: 0; transform: scale(0.3); }
        to { opacity: 1; transform: scale(1); }
    }
    
    @keyframes bounceIn {
        0% { opacity: 0; transform: scale(0.2) rotate(-5deg); }
        50% { opacity: 1; transform: scale(1.1) rotate(2deg); }
        70% { transform: scale(0.95) rotate(-1deg); }
        100% { opacity: 1; transform: scale(1) rotate(0deg); }
    }
    
    /* Enhanced Stats Cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.25), rgba(255,255,255,0.15));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1);
        animation: shimmer 2s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    .stat-card:hover {
        transform: scale(1.08) rotate(1deg);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(45deg, #4ecdc4, #45b7d1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: rgba(255,255,255,0.9);
        font-weight: 500;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Enhanced Source Cards */
    .source-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4ecdc4;
        transition: all 0.4s ease;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        position: relative;
    }
    
    .source-card:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateX(10px) translateY(-2px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border-left-color: #ff6b6b;
    }
    
    .source-title {
        color: #4ecdc4;
        font-weight: 600;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    .source-snippet {
        color: rgba(255, 255, 255, 0.85);
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Loading Animation */
    .loading-spinner {
        border: 4px solid rgba(255,255,255,0.1);
        border-left: 4px solid #4ecdc4;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Progress Bar Enhancement */
    .progress-container {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 5px;
        margin: 1.5rem 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .progress-bar {
        height: 25px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1);
        border-radius: 12px;
        transition: width 3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
    }
    
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(45deg, transparent 33%, rgba(255,255,255,0.3) 33%, rgba(255,255,255,0.3) 66%, transparent 66%);
        background-size: 30px 30px;
        animation: move 2s linear infinite;
    }
    
    @keyframes move {
        0% { background-position: 0 0; }
        100% { background-position: 30px 30px; }
    }
    
    /* Enhanced Footer */
    .footer {
        text-align: center;
        padding: 3rem;
        background: rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        margin-top: 4rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #f39c12);
        animation: gradientMove 3s ease-in-out infinite;
    }
    
    @keyframes gradientMove {
        0%, 100% { transform: translateX(-100%); }
        50% { transform: translateX(100%); }
    }
     /* Instructions Card (from google_veri.py, adapted for current styling) */
    .instructions {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.15), rgba(255, 215, 0, 0.08)); /* Gold-ish tones */
        border-left: 5px solid #FFD700; /* Gold */
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 215, 0, 0.3);
        color: rgba(255,255,255,0.9);
    }
    .instructions h4 {
        color: #FFD700; /* Gold */
        margin-bottom: 1rem;
    }
    .instructions ol {
        font-size: 1.1rem;
        line-height: 1.8;
        padding-left: 20px; /* Indent list */
    }
     .instructions p {
        margin-top: 1.5rem;
        font-style: italic;
        color: rgba(255,255,255,0.8);
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        .main-subtitle {
            font-size: 1.1rem;
        }
        .glass-card, .result-card, .instructions {
            padding: 1.5rem;
            margin: 1rem 0;
        }
        .stButton > button {
            padding: 0.8rem 1.5rem !important;
            font-size: 1rem !important;
        }
        .stat-number {
            font-size: 2.5rem;
        }
        .stat-label {
            font-size: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------------- Enhanced Search Functions -----------------------
class EnhancedFakeNewsDetector:
    def __init__(self, api_key, search_engine_id):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        # Enhanced trusted sources for Pakistani/Urdu news
        self.trusted_domains = [
            'dawn.com', 'geo.tv', 'ary.digital', 'samaa.tv', 'thenews.com.pk',
            'tribune.com.pk', 'dailytimes.com.pk', 'nation.com.pk', 'bbc.com',
            'cnn.com', 'reuters.com', 'ap.org', 'dunya.com.pk', 'dunyanews.tv',
            'jang.com.pk', 'nawaiwaqt.com.pk', 'urdu.geo.tv', 'urdu.arynews.tv',
            'bbc.com/urdu', 'voaurdu.com', 'dw.com/ur', 'express.pk',
            'khabrain.com', 'mashriqtv.pk', '92news.hd.pk', 'channelnewsasia.com',
            'aljazeera.com', 'aljazeera.net' # Moved Aljazeera to trusted
        ]
        self.semi_trusted_domains = [ # Domains that are generally reliable but might have opinion pieces or varied content
            'wikipedia.org', 'alarabiya.net',
            'aaj.tv', 'hum.tv', '24news.hd', 'capital.tv', 'ptv.com.pk',
            'urdupoint.com', 'dailypakistan.com.pk'
        ]
        self.questionable_domains = [ # Social media, blogs, known unreliable sources
            'blogspot.com', 'wordpress.com', 'facebook.com', 'twitter.com', 'x.com',
            'whatsapp.com', 'telegram.org', 'youtube.com', # Corrected potential YouTube link part
            'tiktok.com', 'dailymotion.com', 'vimeo.com', '*.wixsite.com', '*.weebly.com'
        ]
        
    def clean_urdu_text(self, text):
        """Clean and normalize Urdu text for better search"""
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[۔،؍؎؏ؘؙؚؐؑؒؓؔؕؖؗ؛؞؟]', '', text)
        return text
        
    def extract_key_phrases(self, text):
        text = self.clean_urdu_text(text)
        urdu_stop_words = {
            'کے', 'کا', 'کی', 'میں', 'سے', 'کو', 'اور', 'یہ', 'وہ', 'تھا', 'ہے', 'تھے', 'ہیں',
            'پر', 'نے', 'کر', 'کرنے', 'والا', 'والے', 'والی', 'گا', 'گے', 'گی', 'دیا', 'دی',
            'جا', 'جانے', 'ہوا', 'ہوئی', 'ہوئے', 'بھی', 'تک', 'لیے', 'بعد', 'پہلے', 'اب',
            'جب', 'تو', 'لیکن', 'اگر', 'کیونکہ', 'ان', 'اس', 'ہی', 'کہ', 'جو', 'کیا', 'کہا',
            'ایک', 'دو', 'تین', 'ہوں', 'گے', 'گی', 'تک', 'ساتھ', 'ہمارے', 'ہمارا', 'تمہارے', 'تمہارا',
            'اپنا', 'اپنے', 'اپنی', 'انہیں', 'انہوں', 'کچھ', 'کوئی', 'کیسے', 'کیوں', 'کب', 'کہاں'
        }
        words = text.split()
        filtered_words = [word for word in words if word not in urdu_stop_words and len(word) > 2]
        phrases = []
        if not filtered_words: # Fallback if all words are stop words or too short
             return [text[:100]] if text else []


        # Single important words (entities, names) - less emphasis if too many phrases
        # for word in filtered_words:
        #     if len(word) > 4:
        #         phrases.append(word)
        
        # Two-word phrases
        for i in range(len(filtered_words) - 1):
            phrase = ' '.join(filtered_words[i:i+2])
            phrases.append(phrase)
        
        # Three-word phrases for context
        for i in range(len(filtered_words) - 2):
            phrase = ' '.join(filtered_words[i:i+3])
            phrases.append(phrase)

        # Four-word phrases if available
        for i in range(len(filtered_words) - 3):
            phrase = ' '.join(filtered_words[i:i+4])
            phrases.append(phrase)

        if not phrases and filtered_words: # If no multi-word phrases, use longest single words
            phrases.extend(sorted(filtered_words, key=len, reverse=True))
        elif not phrases and not filtered_words and text: # Absolute fallback
            phrases.append(text[:100])


        unique_phrases = list(set(phrases))
        # Prioritize longer phrases and those appearing earlier in the text (crude proxy for importance)
        unique_phrases.sort(key=lambda p: (len(p.split()), -text.find(p) if text.find(p) != -1 else float('-inf')), reverse=True)
        return unique_phrases[:5] # Return top 5 diverse phrases
    
    def search_google(self, query, num_results=7): # Reduced num_results slightly
        if not self.api_key or not self.search_engine_id:
            st.error("Google API credentials not configured in the script.")
            return {"error": "Google API credentials not configured"}
            
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': num_results,
                'lr': 'lang_ur',
                'hl': 'ur',
                'gl': 'pk',
                'safe': 'active',
                'dateRestrict': 'm3' # More recent: last 3 months
            }
            
            response = requests.get(self.base_url, params=params, timeout=12) # Slightly increased timeout
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            return {"error": "Search request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Search request failed: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "Invalid response from search API"}
    
    def analyze_source_credibility(self, url):
        if not url: return "unknown"
        url_lower = url.lower()
        
        for trusted in self.trusted_domains:
            if trusted in url_lower:
                return "high"
        for semi_trusted in self.semi_trusted_domains:
            if semi_trusted in url_lower:
                return "medium"
        for questionable_domain in self.questionable_domains:
            if questionable_domain in url_lower:
                return "low"
        # Check for generic TLDs that are often less credible for news
        if any(tld in url_lower for tld in ['.info', '.biz', '.top', '.xyz', '.icu']):
            return "low"
            
        return "medium" # Default to medium for unknown, but not explicitly questionable sources
    
    def calculate_similarity_score(self, original_text, search_results):
        if not search_results or 'items' not in search_results:
            return 0
        
        original_text_cleaned = self.clean_urdu_text(original_text)
        original_words = set(original_text_cleaned.lower().split())
        if not original_words: return 0

        similarity_scores = []
        
        for item in search_results['items']:
            snippet = item.get('snippet', '')
            title = item.get('title', '')
            
            combined_text = self.clean_urdu_text(title + ' ' + snippet)
            search_words = set(combined_text.lower().split())
            
            if search_words:
                intersection = len(original_words.intersection(search_words))
                union = len(original_words.union(search_words))
                jaccard = intersection / union if union > 0 else 0
                
                # Consider overlap with original text as more important
                overlap_original = intersection / len(original_words)
                
                # Weighted similarity
                similarity = (jaccard * 0.4) + (overlap_original * 0.6) 
                similarity_scores.append(similarity)
        
        return max(similarity_scores) if similarity_scores else 0
    
    def enhanced_verification(self, text):
        key_phrases = self.extract_key_phrases(text)
        verification_results = {
            'searches_performed': 0,
            'sources_found': 0,
            'credible_sources': 0, # medium + high
            'high_credible_sources': 0, # high only
            'similarity_score': 0,
            'verification_status': 'unverified', # Default
            'sources': [],
            'analysis': {},
            'search_queries': []
        }
        
        if not key_phrases:
            verification_results['analysis']['message'] = "خبر سے اہم جملے نہیں نکالے جا سکے۔ براہ کرم لمبی خبر فراہم کریں۔ (Could not extract meaningful phrases. Please provide longer news text.)"
            verification_results['verification_status'] = 'error_no_phrases'
            return verification_results
        
        search_strategies = []
        if key_phrases:
            search_strategies.append(key_phrases[0]) # Most important phrase
        if len(key_phrases) > 1:
             search_strategies.append(f'"{key_phrases[0]}" OR "{key_phrases[1]}"') # Exact search for top two phrases
        if len(key_phrases) > 2 : # Broader search with more terms
            search_strategies.append(f'{key_phrases[0]} {key_phrases[1]} {key_phrases[2]}')

        # Fallback: Use a snippet of the original text if strategies are weak
        if not search_strategies or len(key_phrases[0]) < 10 : # if the best phrase is too short
            search_strategies.append(self.clean_urdu_text(text[:120])) # Search with a longer snippet


        all_sources_data = [] # Store tuples of (source_info, similarity_to_this_source_content)
        max_overall_similarity = 0
        
        # Progress bar for searches
        search_progress = st.progress(0)
        
        for i, strategy in enumerate(list(set(search_strategies))[:3]): # Limit to 3 unique, effective searches
            if not strategy.strip(): continue # Skip empty strategies

            verification_results['search_queries'].append(strategy)
            search_results_json = self.search_google(strategy)
            verification_results['searches_performed'] += 1
            
            search_progress.progress((i + 1) / min(len(search_strategies), 3))

            if 'error' in search_results_json:
                # Optionally log this error or show a minor warning
                # st.warning(f"Search query '{strategy}' failed: {search_results_json['error']}")
                continue # Skip to next strategy if one search fails
                
            if 'items' in search_results_json and search_results_json['items']:
                current_search_similarity = self.calculate_similarity_score(text, search_results_json)
                max_overall_similarity = max(max_overall_similarity, current_search_similarity)

                for item in search_results_json['items']:
                    link = item.get('link', '')
                    credibility = self.analyze_source_credibility(link)
                    source_info = {
                        'title': item.get('title', ''),
                        'link': link,
                        'snippet': item.get('snippet', ''),
                        'credibility': credibility,
                        'displayLink': item.get('displayLink', ''),
                        'query_source': strategy # track which query found this
                    }
                    all_sources_data.append(source_info)
        
        search_progress.empty() # Remove progress bar after completion

        unique_sources = []
        seen_links = set()
        for source in all_sources_data:
            if source['link'] and source['link'] not in seen_links:
                unique_sources.append(source)
                seen_links.add(source['link'])
        
        # Sort sources: high credibility first, then by how they were found (earlier queries are better)
        unique_sources.sort(key=lambda s: (s['credibility'] != 'high', s['credibility'] != 'medium', 
                                           verification_results['search_queries'].index(s['query_source']) 
                                           if s['query_source'] in verification_results['search_queries'] else 99))

        verification_results['sources'] = unique_sources[:10] # Keep top 10 diverse sources
        verification_results['sources_found'] = len(unique_sources)
        
        verification_results['high_credible_sources'] = len([s for s in unique_sources if s['credibility'] == 'high'])
        verification_results['credible_sources'] = verification_results['high_credible_sources'] + \
                                                   len([s for s in unique_sources if s['credibility'] == 'medium'])
        verification_results['similarity_score'] = max_overall_similarity
        
        # Refined Verification Status Logic
        if verification_results['high_credible_sources'] >= 2 and max_overall_similarity > 0.35:
            verification_results['verification_status'] = 'verified'
        elif verification_results['high_credible_sources'] >= 1 and max_overall_similarity > 0.30:
            verification_results['verification_status'] = 'verified'
        elif verification_results['credible_sources'] >= 2 and max_overall_similarity > 0.25:
            verification_results['verification_status'] = 'partially_verified'
        elif verification_results['sources_found'] > 0 and max_overall_similarity > 0.15: # Some sources with some similarity
            verification_results['verification_status'] = 'limited_evidence'
        else:
            verification_results['verification_status'] = 'unverified'

        if not unique_sources and verification_results['verification_status'] not in ['error_no_phrases']:
             verification_results['verification_status'] = 'no_sources_found'


        verification_results['analysis'] = {
            'message': self._generate_analysis_message(verification_results),
            'confidence': self._calculate_confidence(verification_results)
        }
        
        return verification_results
    
    def _generate_analysis_message(self, results):
        status = results['verification_status']
        high_cred = results['high_credible_sources']
        cred = results['credible_sources']
        total = results['sources_found']
        sim = results['similarity_score']

        if status == 'verified':
            return f"تصدیق شدہ: {high_cred} اعلیٰ معتبر اور کُل {cred} معتبر ذرائع ملے جن میں مواد کی مماثلت {sim:.1%} ہے۔ (Verified: Found {high_cred} high-credibility and total {cred} credible sources with {sim:.1%} content similarity.)"
        elif status == 'partially_verified':
            return f"جزوی تصدیق شدہ: {cred} معتبر ذرائع ({high_cred} اعلیٰ) ملے، مواد کی مماثلت {sim:.1%} ہے۔ (Partially Verified: Found {cred} credible sources ({high_cred} high) with {sim:.1%} similarity.)"
        elif status == 'limited_evidence':
            return f"محدود شواہد: کُل {total} ذرائع ملے ({cred} معتبر)، مواد کی مماثلت {sim:.1%}۔ (Limited Evidence: Found {total} sources ({cred} credible), with {sim:.1%} similarity.)"
        elif status == 'no_sources_found':
             return "کوئی متعلقہ بیرونی ذرائع نہیں ملے۔ خبر کی تصدیق نہیں ہو سکی۔ (No relevant external sources found. News could not be verified.)"
        elif status == 'error_no_phrases':
            return results['analysis'].get('message', "خبر سے اہم جملے نہیں نکالے جا سکے۔ (Could not extract key phrases.)")
        else: # Unverified
            return f"غیر تصدیق شدہ: کُل {total} ذرائع ملے ({cred} معتبر)، مواد کی مماثلت {sim:.1%}۔ خبر کی آزادانہ تصدیق مشکل ہے۔ (Unverified: {total} sources ({cred} credible) found with {sim:.1%} similarity. Independent verification is difficult.)"

    def _calculate_confidence(self, results): # Confidence in the verification process itself
        # Max score 1.0
        # High credible sources contribute more
        high_cred_score = min(results['high_credible_sources'] * 0.25, 0.5) # Max 0.5 from high cred
        # Medium credible sources
        medium_cred_score = min((results['credible_sources'] - results['high_credible_sources']) * 0.1, 0.2) # Max 0.2 from medium
        # Similarity score
        similarity_score_component = results['similarity_score'] * 0.3 # Max 0.3 from similarity
        
        # Number of searches performed (max 0.1 if all 3 searches run)
        # search_eff_score = min(results['searches_performed'] / 3 * 0.1, 0.1)

        confidence = high_cred_score + medium_cred_score + similarity_score_component
        return min(confidence, 1.0) # Ensure it's capped at 1.0


# ----------------------- Load Models -----------------------
@st.cache_resource
def load_models():
    try:
        # Ensure these paths are correct relative to your app's execution directory
        fake_news_model_path = "models/saved_model_distilbert_multilingual_fake_news"
        sentiment_model_path = "models/saved_model_sentiment_90"
        
        fake_news_model = AutoModelForSequenceClassification.from_pretrained(fake_news_model_path)
        fake_news_tokenizer = AutoTokenizer.from_pretrained(fake_news_model_path)
        
        sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_path)
        sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_path)
        
        return fake_news_model, fake_news_tokenizer, sentiment_model, sentiment_tokenizer
    except Exception as e:
        st.error(f"ماڈلز لوڈ کرنے میں خرابی: {str(e)} (Error loading models: {str(e)})")
        st.error("براہ کرم یقینی بنائیں کہ ماڈل فائلیں 'models/saved_model_distilbert_multilingual_fake_news' اور 'models/saved_model_sentiment_90' فولڈرز میں موجود ہیں۔ (Please ensure model files exist in 'models/saved_model_distilbert_multilingual_fake_news' and 'models/saved_model_sentiment_90' folders.)")
        return None, None, None, None

@st.cache_resource
def load_enhanced_detector():
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        st.warning("گوگل API کیز کنفیگر نہیں ہیں۔ سرچ کی تصدیق کی خصوصیت محدود ہو گی۔ (Google API keys are not configured. Search verification feature will be limited.)", icon="⚠️")
    return EnhancedFakeNewsDetector(GOOGLE_API_KEY, SEARCH_ENGINE_ID)

# ----------------------- Initialize Session State -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False # Set to True to bypass login for development
if "username" not in st.session_state:
    st.session_state.username = "Test User" # Default for dev
if "analysis_count" not in st.session_state:
    st.session_state.analysis_count = 0

def login(username):
    st.session_state.logged_in = True
    st.session_state.username = username

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.analysis_count = 0 # Reset count on logout

# ----------------------- Apply Custom CSS -----------------------
inject_custom_css()

# ----------------------- Login Screen -----------------------
if not st.session_state.logged_in:
    st.markdown("""
    <div class="login-card">
        <h1 style="color: #333; margin-bottom: 2rem; font-size: 3.5rem;">🔍</h1>
        <h2 style="color: #333; margin-bottom: 1rem; font-family: 'Poppins', sans-serif;">Enhanced News Intelligence Hub</h2>
        <p style="color: #555; margin-bottom: 2rem; font-family: 'Roboto', sans-serif;">گوگل سرچ کی تصدیق کے ساتھ جدید اردو خبروں کے تجزیاتی پلیٹ فارم تک رسائی کے لیے اپنا نام درج کریں۔</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username_input = st.text_input("", placeholder="یہاں اپنا نام درج کریں...", label_visibility="collapsed", key="login_username")
        if st.button("🚀 پلیٹ فارم میں داخل ہوں", use_container_width=True, key="login_button"):
            if username_input.strip():
                login(username_input.strip())
                st.success(f"🎉 خوش آمدید, {username_input.strip()}!")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("⚠ براہ کرم جاری رکھنے کے لیے ایک درست نام درج کریں۔")
    st.stop()

# ----------------------- Main App Interface -----------------------

# Header
st.markdown(f"""
<div class="main-header">
    <h1 class="main-title">🔍 Enhanced News Intelligence Hub</h1>
    <p class="main-subtitle">AI + Google Search سے چلنے والا اردو خبروں کا تجزیہ اور تصدیق</p>
    <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">خوش آمدید, <strong>{st.session_state.username}</strong> 👋</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h2 style="color: white; margin-bottom: 1.5rem; font-family: 'Poppins', sans-serif;">⚙️ کنٹرول پینل</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{st.session_state.analysis_count}</div>
        <div class="stat-label">مکمل تجزیے</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.2); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    api_configured = bool(GOOGLE_API_KEY and SEARCH_ENGINE_ID)
    status_color = "#4CAF50" if api_configured else "#f44336"
    status_text = "کنفیگرڈ" if api_configured else "کنفیگرڈ نہیں"
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); border-radius: 15px; padding: 1.5rem; margin: 1rem 0; border: 1px solid rgba(255,255,255,0.2);">
        <h4 style="color: white; margin-bottom: 1rem; font-family: 'Poppins', sans-serif;">🔧 API کی حیثیت</h4>
        <p style="color: {status_color}; font-weight: 600;">سرچ API: {status_text}</p>
        {'' if api_configured else '<p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">بہتر تصدیق کے لیے API کیز کو کنفیگر کریں۔</p>'}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 لاگ آؤٹ", use_container_width=True, key="logout_button"):
        logout()
        st.rerun()
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.2); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.1); border-radius: 15px; padding: 1.5rem; margin: 1rem 0; border: 1px solid rgba(255,255,255,0.2);">
        <h4 style="color: white; margin-bottom: 1rem; font-family: 'Poppins', sans-serif;">💡 جدید خصوصیات</h4>
        <ul style="color: rgba(255,255,255,0.85); font-size: 0.95rem; padding-left: 20px; list-style-type: '✨ ';">
            <li>AI ماڈل کا تجزیہ</li>
            <li>گوگل سرچ کی تصدیق</li>
            <li>ذرائع کا اعتباری تجزیہ</li>
            <li>کثیر سطحی شناخت</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Load models and detector
with st.spinner("🔄 AI ماڈلز اور جدید ڈیٹیکٹر لوڈ ہو رہے ہیں۔۔۔"):
    fake_news_model, fake_news_tokenizer, sentiment_model, sentiment_tokenizer = load_models()
    enhanced_detector = load_enhanced_detector()

if fake_news_model is None or sentiment_model is None:
    st.error("❌ ماڈلز لوڈ کرنے میں ناکامی۔ براہ کرم ماڈل کے راستے چیک کریں۔")
    st.stop()

# Instructions
with st.expander("📋 اس پلیٹ فارم کو کیسے استعمال کریں؟", expanded=False):
    st.markdown("""
    <div class="instructions">
        <h4>🚀 جدید شناختی عمل:</h4>
        <ol>
            <li><strong>AI تجزیہ:</strong> ہمارے تربیت یافتہ ماڈلز متن کی ساخت اور نمونوں کا تجزیہ کرتے ہیں۔</li>
            <li><strong>گوگل سرچ:</strong> اہم جملے تصدیق کے لیے ویب پر تلاش کیے جاتے ہیں۔</li>
            <li><strong>ذرائع کا تجزیہ:</strong> ملنے والے ذرائع کی ساکھ اور اعتبار کا جائزہ لیا جاتا ہے۔</li>
            <li><strong>مشترکہ نتیجہ:</strong> AI اور سرچ کے نتائج جامع تجزیہ فراہم کرتے ہیں۔</li>
        </ol>
        <p>🔬 یہ جدید طریقہ بہتر درستگی کے لیے کثیر سطحی تصدیق فراہم کرتا ہے۔</p>
    </div>
    """, unsafe_allow_html=True)

# Main input area
st.markdown("""
<div class="glass-card">
    <h3 style="color: white; text-align: center; margin-bottom: 1.5rem; font-family: 'Poppins', sans-serif;">📝 جدید تجزیہ کے لیے خبر کا متن درج کریں</h3>
</div>
""", unsafe_allow_html=True)

news_text = st.text_area(
    "",
    height=250, # Increased height
    placeholder="یہاں اردو میں اپنی خبر لکھیں یا پیسٹ کریں... (Write or paste your Urdu news here...)",
    label_visibility="collapsed",
    key="news_text_input"
)

# Action buttons
col1_actions, col2_actions = st.columns(2) # Simplified to two columns for broader buttons
with col1_actions:
    check_news = st.button("🔍 جعلی خبر کی جدید شناخت", use_container_width=True, key="check_news_button")
with col2_actions:
    analyze_sentiment = st.button("💭 جذبات کا تجزیہ", use_container_width=True, key="analyze_sentiment_button")

# ----------------------- Prediction Functions -----------------------
def predict_fake_news(text):
    if not text.strip(): return None, [0.5, 0.5] # Handle empty text
    inputs = fake_news_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = fake_news_model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        predicted_class = torch.argmax(probs).item()
    return predicted_class, probs[0].tolist()

def predict_sentiment(text):
    if not text.strip(): return None, [0.33, 0.34, 0.33] # Handle empty text
    inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = sentiment_model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        predicted_class = torch.argmax(probs).item()
    return predicted_class, probs[0].tolist()

def create_modern_pie_chart(probs, labels, colors):
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=probs,
        hole=0.5, # Increased hole size
        textinfo='label+percent',
        textfont_size=15, # Increased font size
        marker=dict(colors=colors, line=dict(color='rgba(255,255,255,0.7)', width=2)),
        pull=[0.05 if p == max(probs) else 0 for p in probs], # Pull out largest slice
        showlegend=True,
        insidetextorientation='radial'
    )])
    fig.update_layout(
        font=dict(family="Poppins, sans-serif", size=14, color='white'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450, # Increased height
        margin=dict(t=60, b=60, l=40, r=40), # Adjusted margins
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font_size=12)
    )
    return fig

def create_modern_bar_chart(probs, labels, colors):
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=probs,
        marker=dict(color=colors, line=dict(color='rgba(255,255,255,0.7)', width=1.5)),
        text=[f'{p:.1%}' for p in probs],
        textposition='outside', # Text outside bars
        textfont=dict(size=14, color='white'),
        width=[0.6] * len(labels) # Bar width
    )])
    fig.update_layout(
        font=dict(family="Poppins, sans-serif", size=14, color='white'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450, # Increased height
        xaxis=dict(showgrid=False, zeroline=False, tickfont_size=13),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.25)', zeroline=False, tickfont_size=13, range=[0, max(probs) * 1.2 if probs else 1]),
        margin=dict(t=50, b=50, l=50, r=50)
    )
    return fig

# ----------------------- Results Display -----------------------
if check_news and news_text.strip():
    st.session_state.analysis_count += 1
    
    tab1, tab2 = st.tabs(["🤖 AI ماڈل کا تجزیہ", "🔍 گوگل سرچ کی تصدیق"])
    
    with tab1:
        st.markdown("<h3 style='color: white; text-align: center; margin-bottom:1.5rem; font-family:\"Poppins\", sans-serif;'>🤖 AI ماڈل کا تجزیہ</h3>", unsafe_allow_html=True)
        with st.spinner("🔍 AI ماڈلز کے ساتھ تجزیہ کیا جا رہا ہے۔۔۔"):
            # time.sleep(0.5) # Simulate delay
            ai_label, ai_prob = predict_fake_news(news_text)
        
        if ai_label is not None:
            ai_confidence_percent = max(ai_prob) * 100
            if ai_label == 1: # Real news
                st.markdown(f"""
                <div class="result-card result-real">
                    <h2 style="color: #4CAF50; margin-bottom: 1rem;">✅ AI ماڈل: خبر حقیقی ہے</h2>
                    <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem;">AI ماڈل اس خبر کو <strong>حقیقی اور قابل اعتماد</strong> قرار دیتا ہے۔</p>
                    <div style="background: rgba(76, 175, 80, 0.25); border-radius: 15px; padding: 1.2rem; margin-top: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <p style="color: rgba(255,255,255,0.85); margin: 0; font-size:1.1rem;">AI ماڈل کا اعتماد: <strong>{ai_confidence_percent:.1f}%</strong></p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else: # Fake news
                st.markdown(f"""
                <div class="result-card result-fake">
                    <h2 style="color: #f44336; margin-bottom: 1rem;">❌ AI ماڈل: ممکنہ طور پر جعلی خبر</h2>
                    <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem;">AI ماڈل اس خبر میں <strong>ممکنہ غلط معلومات</strong> کا پتہ چلاتا ہے۔</p>
                     <div style="background: rgba(244, 67, 54, 0.25); border-radius: 15px; padding: 1.2rem; margin-top: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <p style="color: rgba(255,255,255,0.85); margin: 0; font-size:1.1rem;">AI ماڈل کا اعتماد: <strong>{ai_confidence_percent:.1f}%</strong></p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h4 style='color: white; text-align: center; margin-top: 2.5rem; margin-bottom:1rem; font-family:\"Poppins\", sans-serif;'>AI تجزیہ کی تقسیم</h4>", unsafe_allow_html=True)
            fig_ai = create_modern_pie_chart(ai_prob, ['جعلی (Fake)', 'حقیقی (Real)'], ['#ff6b6b', '#4ecdc4'])
            st.plotly_chart(fig_ai, use_container_width=True)
        else:
            st.warning("AI تجزیہ کے لیے متن خالی ہے۔ (Text is empty for AI analysis.)")

    with tab2:
        st.markdown("<h3 style='color: white; text-align: center; margin-bottom:1.5rem; font-family:\"Poppins\", sans-serif;'>🔍 گوگل سرچ کی تصدیق</h3>", unsafe_allow_html=True)
        if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
             st.error("گوگل سرچ کی تصدیق کے لیے API کیز کنفیگر نہیں ہیں۔ براہ کرم اسکرپٹ میں API کیز شامل کریں۔ (API keys not configured for Google Search verification. Please add API keys to the script.)", icon="🚨")
        else:
            with st.spinner("🔍 گوگل سرچ کی تصدیق کی جا رہی ہے۔۔۔ اس میں کچھ وقت لگ سکتا ہے۔"):
                verification_results = enhanced_detector.enhanced_verification(news_text)
            
            status = verification_results['verification_status']
            status_colors = {
                'verified': '#4CAF50', 'partially_verified': '#FFC107', 
                'limited_evidence': '#2196F3', 'unverified': '#f44336',
                'no_sources_found': '#E0E0E0', 'error_no_phrases': '#FFA07A'
            }
            status_icons = {
                'verified': '✅', 'partially_verified': '⚠️', 
                'limited_evidence': '🔎', 'unverified': '❌',
                'no_sources_found': '🤷‍♂️', 'error_no_phrases': '❗'
            }
            status_titles = {
                'verified': 'تصدیق شدہ', 'partially_verified': 'جزوی تصدیق شدہ',
                'limited_evidence': 'محدود شواہد', 'unverified': 'غیر تصدیق شدہ',
                'no_sources_found': 'کوئی ذریعہ نہیں ملا', 'error_no_phrases': 'کلیدی جملے نہیں ملے'
            }

            current_status_color = status_colors.get(status, '#757575')
            current_status_icon = status_icons.get(status, '❓')
            current_status_title = status_titles.get(status, 'نامعلوم حیثیت')

            st.markdown(f"""
            <div class="result-card result-enhanced" style="border-left-color: {current_status_color}; box-shadow: 0 0 30px {current_status_color}60;">
                <h2 style="color: {current_status_color}; margin-bottom: 1rem;">{current_status_icon} {current_status_title.upper()}</h2>
                <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem;">{verification_results['analysis']['message']}</p>
                <div style="background: {current_status_color}33; border-radius: 15px; padding: 1.2rem; margin-top: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <p style="color: rgba(255,255,255,0.85); margin: 0; font-size:1.1rem;">
                        کل ملے ذرائع: <strong>{verification_results['sources_found']}</strong> | 
                        معتبر (اعلیٰ/درمیانہ): <strong>{verification_results['credible_sources']}</strong> ({verification_results['high_credible_sources']} اعلیٰ) | 
                        مواد کی مماثلت: <strong>{verification_results['similarity_score']:.1%}</strong> |
                        تصدیقی اعتماد: <strong>{verification_results['analysis']['confidence']:.1%}</strong>
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h4 style='color: white; text-align: center; margin-top: 2.5rem; margin-bottom:1rem; font-family:\"Poppins\", sans-serif;'>🏷️ تصدیقی بیجز</h4>", unsafe_allow_html=True)
            
            cols_badges = st.columns(3)
            with cols_badges[0]:
                badge_class_sf = "badge-verified" if verification_results['sources_found'] >= 3 else ("badge-limited" if verification_results['sources_found'] > 0 else "badge-unverified")
                st.markdown(f'<div class="verification-badge {badge_class_sf}">📊 {verification_results["sources_found"]} ذرائع ملے</div>', unsafe_allow_html=True)
            
            with cols_badges[1]:
                badge_class_cs = "badge-verified" if verification_results['high_credible_sources'] >= 1 else ("badge-limited" if verification_results['credible_sources'] > 0 else "badge-unverified")
                st.markdown(f'<div class="verification-badge {badge_class_cs}">🏆 {verification_results["credible_sources"]} معتبر ذرائع ({verification_results["high_credible_sources"]} اعلیٰ)</div>', unsafe_allow_html=True)
            
            with cols_badges[2]:
                sim_pct = verification_results['similarity_score'] * 100
                badge_class_sim = "badge-verified" if sim_pct >= 30 else ("badge-limited" if sim_pct > 10 else "badge-unverified")
                st.markdown(f'<div class="verification-badge {badge_class_sim}">🎯 {sim_pct:.0f}% مماثلت</div>', unsafe_allow_html=True)

            if verification_results['sources']:
                st.markdown("<h4 style='color: white; margin-top: 2.5rem; margin-bottom:1rem; font-family:\"Poppins\", sans-serif;'>📰 ملے ہوئے ذرائع (اوپر 5)</h4>", unsafe_allow_html=True)
                cred_emoji = {'high': '🟢', 'medium': '🟡', 'low': '🔴', 'unknown': '⚪'}
                for i, source in enumerate(verification_results['sources'][:5]):
                    cred_color = {'high': '#4CAF50', 'medium': '#FFC107', 'low': '#f44336', 'unknown': '#9E9E9E'}.get(source['credibility'], '#9E9E9E')
                    st.markdown(f"""
                    <div class="source-card" style="border-left-color: {cred_color};">
                        <div class="source-title">
                            <a href="{source['link']}" target="_blank" style="color: #58D68D; text-decoration: none; font-weight:bold;">
                                {source['title'][:120]}{'...' if len(source['title']) > 120 else ''}
                            </a>
                            <span style="color: {cred_color}; font-size: 0.9rem; margin-left: 1rem; background-color: rgba(0,0,0,0.2); padding: 3px 8px; border-radius: 10px;">
                                {cred_emoji.get(source['credibility'], '')} {source['credibility'].title()} Credibility
                            </span>
                        </div>
                        <div class="source-snippet" style="color:rgba(255,255,255,0.8);">{source['snippet'][:250]}{'...' if len(source['snippet']) > 250 else ''}</div>
                        <p style="font-size:0.8rem; color:rgba(255,255,255,0.6); margin-top:0.5rem;">ماخذ: {source['displayLink']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            if verification_results['search_queries']:
                with st.expander("استعمال شدہ تلاش کے سوالات دیکھیں", expanded=False):
                    for q_idx, q_item in enumerate(verification_results['search_queries']):
                        st.code(f"{q_idx+1}: {q_item}", language="text")
elif check_news and not news_text.strip():
    st.error("براہ کرم تجزیہ کے لیے خبر کا متن درج کریں۔ (Please enter news text for analysis.)", icon="❗")


# ----------------------- Sentiment Analysis -----------------------
if analyze_sentiment and news_text.strip():
    st.session_state.analysis_count += 1
    st.markdown("<h3 style='color: white; text-align: center; margin-top:2rem; margin-bottom:1.5rem; font-family:\"Poppins\", sans-serif;'>💭 خبر کے جذبات کا تجزیہ</h3>", unsafe_allow_html=True)
    
    with st.spinner("💭 جذبات کا تجزیہ کیا جا رہا ہے۔۔۔"):
        # time.sleep(0.5) # Simulate delay
        sentiment_label, sentiment_probs = predict_sentiment(news_text)
    
    if sentiment_label is not None:
        sentiment_map = {0: 'منفی', 1: 'غیر جانبدار', 2: 'مثبت'} # Negative, Neutral, Positive
        sentiment = sentiment_map.get(sentiment_label, "نامعلوم")
        
        sentiment_colors = {'مثبت': '#4CAF50', 'غیر جانبدار': '#FFC107', 'منفی': '#f44336', "نامعلوم": "#9E9E9E"}
        sentiment_icons = {'مثبت': '😊', 'غیر جانبدار': '😐', 'منفی': '😞', "نامعلوم": "❓"}
        
        current_sent_color = sentiment_colors.get(sentiment, "#9E9E9E")
        current_sent_icon = sentiment_icons.get(sentiment, "❓")
        
        st.markdown(f"""
        <div class="result-card result-sentiment" style="border-left-color: {current_sent_color}; box-shadow: 0 0 30px {current_sent_color}60;">
            <h2 style="color: {current_sent_color}; margin-bottom: 1rem;">{current_sent_icon} جذبات: {sentiment.upper()}</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem;">خبر کا جذباتی لہجہ <strong>{sentiment}</strong> ہے۔</p>
            <div style="background: {current_sent_color}33; border-radius: 15px; padding: 1.2rem; margin-top: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <p style="color: rgba(255,255,255,0.85); margin: 0; font-size:1.1rem;">اعتماد: <strong>{max(sentiment_probs) * 100:.1f}%</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h4 style='color: white; text-align: center; margin-top: 2.5rem; margin-bottom:1rem; font-family:\"Poppins\", sans-serif;'>جذبات کی تقسیم</h4>", unsafe_allow_html=True)
        labels_sentiment = ['منفی (Negative)', 'غیر جانبدار (Neutral)', 'مثبت (Positive)']
        colors_sentiment = ['#f44336', '#FFC107', '#4CAF50']
        fig_sentiment = create_modern_bar_chart(sentiment_probs, labels_sentiment, colors_sentiment)
        st.plotly_chart(fig_sentiment, use_container_width=True)
    else:
        st.warning("جذبات کے تجزیے کے لیے متن خالی ہے۔ (Text is empty for sentiment analysis.)")

elif analyze_sentiment and not news_text.strip():
    st.error("براہ کرم جذبات کے تجزیہ کے لیے خبر کا متن درج کریں۔ (Please enter news text for sentiment analysis.)", icon="❗")

# Enhanced Footer
st.markdown("""
<div class="footer">
    <h3 style="color: white; margin-bottom: 1rem; font-family: 'Poppins', sans-serif;">🚀 Enhanced News Intelligence Hub</h3>
    <p style="color: rgba(255,255,255,0.85); margin-bottom: 1.5rem; font-size: 1.1rem;">
        <strong>یاسر</strong> اور <strong>عبداللہ</strong> کا بنایا ہوا | گوگل سرچ انٹیگریشن کے ساتھ بہتر بنایا گیا
    </p>
    <div style="display: flex; justify-content: center; align-items: center; gap: 2.5rem; margin-top: 1.5rem; flex-wrap: wrap;">
        <span style="color: rgba(255,255,255,0.7); font-size: 1rem;">🤖 AI سے چلنے والا</span>
        <span style="color: rgba(255,255,255,0.7); font-size: 1rem;">🔍 سرچ سے تصدیق شدہ</span>
        <span style="color: rgba(255,255,255,0.7); font-size: 1rem;">🔒 محفوظ</span>
        <span style="color: rgba(255,255,255,0.7); font-size: 1rem;">⚡ تیز رفتار</span>
        <span style="color: rgba(255,255,255,0.7); font-size: 1rem;">🎯 درست</span>
    </div>
    <p style="color: rgba(255,255,255,0.6); font-size: 0.95rem; margin-top: 2rem; line-height: 1.6;">
        مشین لرننگ کو ریئل ٹائم ویب سرچ کے ساتھ ملا کر کثیر سطحی تصدیق
    </p>
</div>
""", unsafe_allow_html=True)