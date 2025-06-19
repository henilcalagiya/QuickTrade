from .config import GOOGLE_ANALYTICS_ID

def google_analytics(request):
    """Add Google Analytics ID to all templates"""
    return {
        'GOOGLE_ANALYTICS_ID': GOOGLE_ANALYTICS_ID
    } 