"""
Configuration settings for QuickTradeApp
"""
import os

# Get the base URL from environment variable
# BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:8000')

# BASE_URL = 'http://127.0.0.1:8000' # Local Development
BASE_URL = 'https://quicktrade-9zj5.onrender.com' # Production

# API Redirect URLs
FYERS_REDIRECT_URL = f"{BASE_URL}/fyers/auth/"
ZERODHA_REDIRECT_URL = f"{BASE_URL}/zerodha/callback/"

# Google Analytics Configuration
GOOGLE_ANALYTICS_ID = os.environ.get('GA_MEASUREMENT_ID', '')  # Empty string if no GA ID provided 