"""
Configuration settings for QuickTradeApp
"""
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
import os

def get_base_url():
    """Get the current base URL of the application"""
    try:
        # Try to get the current site
        current_site = get_current_site(None)
        return f"http://{current_site.domain}"
    except:
        # If that fails, use the default
        return 'http://127.0.0.1:8000'

# Get the base URL
BASE_URL = get_base_url()

# API Redirect URLs
FYERS_REDIRECT_URL = f"{BASE_URL}/fyers/auth/"
ZERODHA_REDIRECT_URL = f"{BASE_URL}/zerodha/callback/"

# Google Analytics Configuration
GOOGLE_ANALYTICS_ID = os.environ.get('GA_MEASUREMENT_ID', 'G-XXXXXXXXXX') 