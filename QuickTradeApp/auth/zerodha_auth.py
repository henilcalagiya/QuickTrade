from kiteconnect import KiteConnect

class ZerodhaAuth:
    def __init__(self, api_key, api_secret):
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required")
            
        self.api_key = api_key
        self.api_secret = api_secret
        self.kite = KiteConnect(api_key=api_key)
        
    def is_token_valid(self, access_token):
        """Check if the token is valid"""
        try:
            if not access_token:
                return False
                
            # Set the access token
            self.kite.set_access_token(access_token)
            
            # Try to get profile to validate token
            profile = self.kite.profile()
            return bool(profile)
            
        except Exception:
            return False
            
    def get_login_url(self):
        """Generate Zerodha login URL"""
        try:
            # Direct URL format as per Zerodha documentation
            login_url = f"https://kite.trade/connect/login?api_key={self.api_key}"
            return login_url
        except Exception as e:
            raise
            
    def generate_session(self, request_token):
        """Generate session using request token"""
        try:
            if not request_token:
                raise ValueError("Request token is required")
                
            # Direct session generation as per Zerodha documentation
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            
            if not data:
                raise ValueError("Empty response from Zerodha API")
                
            if 'access_token' not in data:
                raise ValueError("Access token missing in response")
                
            return data
            
        except Exception as e:
            raise
            
    def get_profile(self, access_token):
        """Get user profile"""
        try:
            if not access_token:
                raise ValueError("Access token is required")
                
            self.kite.set_access_token(access_token)
            profile = self.kite.profile()
            if not profile:
                raise ValueError("Empty profile response")
            return profile
        except Exception as e:
            raise 