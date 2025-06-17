# import fyersModel
from fyers_apiv3 import fyersModel
import urllib.parse

class FyersAuth:
    def __init__(self, client_id, client_secret, redirect_uri):
        # Validate client_id format (should be in format XXXXX-100)
        if not client_id or "-" not in client_id or not client_id.endswith("-100"):
            pass
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        
    def is_token_valid(self, access_token):
        """Check if token is valid by making a test API call"""
        try:
            if not access_token:
                return False
                
            # Initialize FyersModel with the access token
            session = fyersModel.FyersModel(
                token=access_token,
                is_async=False,
                client_id=self.client_id
            )
            
            # Try to get profile to validate token
            response = session.get_profile()
            
            # Check if the response indicates a valid token
            if response and response.get("code") == 200:
                return True
            else:
                return False
            
        except Exception:
            return False
            
    def generate_auth_code(self, response_type="code"):
        """Generate Fyers auth code URL"""
        try:
            session = fyersModel.SessionModel(
                client_id=self.client_id,
                secret_key=self.client_secret,
                redirect_uri=self.redirect_uri,
                response_type=response_type,
                grant_type="authorization_code"
            )
            
            # Generate auth URL
            auth_url = session.generate_authcode()
            
            # Ensure response_type parameter is in the URL
            if auth_url and f"response_type={response_type}" not in auth_url:
                if "?" in auth_url:
                    auth_url += f"&response_type={response_type}"
                else:
                    auth_url += f"?response_type={response_type}"
            
            # If auth_url is None or empty, construct it manually
            if not auth_url:
                base_url = "https://api-t1.fyers.in/api/v3/generate-authcode"
                params = {
                    "client_id": self.client_id,
                    "redirect_uri": urllib.parse.quote(self.redirect_uri),
                    "response_type": response_type,
                    "state": "state"  # Optional state parameter
                }
                auth_url = f"{base_url}?client_id={params['client_id']}&redirect_uri={params['redirect_uri']}&response_type={params['response_type']}&state={params['state']}"
            
            return auth_url
            
        except Exception:
            return None

    def generate_access_token(self, auth_code):
        """Generate access token using auth code"""
        try:
            session = fyersModel.SessionModel(
                client_id=self.client_id,
                secret_key=self.client_secret,
                redirect_uri=self.redirect_uri,
                grant_type="authorization_code"
            )
            
            session.set_token(auth_code)
            response = session.generate_token()
            
            if response and 'access_token' in response:
                self.access_token = response['access_token']
                return response
                
            return None
            
        except Exception:
            return None 