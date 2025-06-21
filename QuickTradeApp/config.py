"""
Configuration settings for QuickTradeApp
"""
import os

# Base URL - use environment variable or default to Render URL
BASE_URL = os.environ.get('BASE_URL', 'https://quicktrade-9zj5.onrender.com')

# API Redirect URLs
FYERS_REDIRECT_URL = f"{BASE_URL}/fyers/auth/"
ZERODHA_REDIRECT_URL = f"{BASE_URL}/zerodha/callback/"

# Google Analytics Configuration
GOOGLE_ANALYTICS_ID = os.environ.get('GA_MEASUREMENT_ID', '')  # Empty string if no GA ID provided 