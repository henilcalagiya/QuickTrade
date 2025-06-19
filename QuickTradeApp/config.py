"""
Configuration settings for QuickTradeApp
"""
import os

def get_base_url():
    """Get the current base URL of the application"""
    try:
        # Check if we're in production (on Render)
        if os.environ.get('RENDER'):
            # Get the service URL from environment
            service_url = os.environ.get('RENDER_EXTERNAL_URL')
            if service_url:
                return service_url
        # Default to localhost for development
        return 'http://127.0.0.1:8000'
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