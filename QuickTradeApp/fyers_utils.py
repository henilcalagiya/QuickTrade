from fyers_apiv3 import fyersModel
from django.http import HttpRequest
from .auth.fyers_auth import FyersAuth
from datetime import date, datetime, timedelta


def get_ltp(request: HttpRequest, index: str) -> float:
    """
    Get the Last Traded Price (LTP) for a given script from Fyers API.
    
    Args:
        request (HttpRequest): Django request object containing session data
        script_name (str): Script name in format 'NSE:SYMBOL-EQ' (e.g., 'NSE:SBIN-EQ')
    
    Returns:
        float: Last Traded Price of the script
    """
    try:
        # Get the LTP for the index using Fyers API
        script_name = f"NSE:{index.upper()}-INDEX"
        if index.upper() == 'BANKNIFTY':
            script_name = "NSE:NIFTYBANK-INDEX"
        elif index.upper() == 'NIFTY':
            script_name = "NSE:NIFTY50-INDEX"
        
        # Get credentials from session
        client_id = request.session.get('fyers_client_id')
        access_token = request.session.get('fyers_access_token')
        
        if not client_id or not access_token:
            raise Exception("Fyers credentials not found in session")
        
        # Initialize the FyersModel instance
        fyers = fyersModel.FyersModel(
            client_id=client_id,
            token=access_token,
            is_async=False,
            log_path=""
        )
        
        # Prepare the data for quotes request
        data = {
            "symbols": script_name
        }
        
        # Get quotes from Fyers
        response = fyers.quotes(data=data)
        
        # Check if the response is successful
        if response.get("s") == "ok" and response.get("code") == 200:
            # Extract LTP from the response
            # The response structure is different for indices
            if "INDEX" in script_name:
                # For indices, the LTP is in a different location
                ltp = response["d"][0]["v"]["lp"]
            else:
                ltp = response["d"][0]["v"]["lp"]
            return float(ltp)
        else:
            error_msg = f"Failed to get LTP. Response: {response}"
            raise Exception(error_msg)
            
    except Exception as e:
        raise Exception(f"Error getting LTP: {str(e)}")


class FyersService:
    """Service class for Fyers API operations"""
    
    def __init__(self, request):
        self.request = request
        self.fyers = self._init_fyers()
    
    def _init_fyers(self):
        """Initialize Fyers instance"""
        try:
            client_id = self.request.session.get('fyers_client_id')
            client_secret = self.request.session.get('fyers_client_secret')
            redirect_uri = self.request.session.get('fyers_redirect_uri')
            
            if all([client_id, client_secret, redirect_uri]):
                return FyersAuth(client_id, client_secret, redirect_uri)
            else:
                raise ValueError("Fyers credentials not found")
        except Exception as e:
            raise Exception(f"Fyers initialization failed: {str(e)}")
    
    def get_index_price(self, index):
        """Get current price of an index"""
        if not self.fyers:
            raise Exception("Fyers not initialized")
        
        try:
            symbol_map = {
                "NIFTY": "NSE:NIFTY50-INDEX",
                "BANKNIFTY": "NSE:NIFTYBANK-INDEX"
            }
            
            symbol = symbol_map.get(index.upper())
            if not symbol:
                raise ValueError(f"Invalid index: {index}")
            
            return get_ltp(self.request, index)
        except Exception as e:
            raise Exception(f"Failed to get {index} price: {str(e)}")
    
    def get_market_data(self):
        """Get prices and expiry dates for both indices"""
        try:
            market_data = {'prices': {}, 'expiry_dates': {}}
            
            # Get prices
            for index in ['NIFTY', 'BANKNIFTY']:
                try:
                    market_data['prices'][index] = self.get_index_price(index)
                except Exception as e:
                    market_data['prices'][index] = None
            
            # Get expiry dates using the new function
            try:
                market_data['expiry_dates'] = get_all_expiry_dates_sdk(self.request)
            except Exception as e:
                market_data['expiry_dates'] = {}
            
            return market_data
        except Exception as e:
            raise Exception(f"Failed to get market data: {str(e)}")
    
    def is_authenticated(self):
        """Check if Fyers is authenticated"""
        try:
            if not self.fyers:
                return False
            
            access_token = self.request.session.get('fyers_access_token')
            return access_token and self.fyers.is_token_valid(access_token)
        except Exception:
            return False


# Simple convenience functions
def get_market_data_simple(request):
    """Get market data with error handling"""
    try:
        return FyersService(request).get_market_data()
    except Exception as e:
        return {'prices': {}, 'expiry_dates': {}}


def get_next_expiry_sdk(request, index="NIFTY"):
    """
    Get next expiry date using Fyers SDK and save to session
    
    Args:
        request: Django request object
        index: Index name ('NIFTY' or 'BANKNIFTY')
    
    Returns:
        str: Next expiry date or None if failed
    """
    try:
        # Get credentials from session
        client_id = request.session.get('fyers_client_id')
        access_token = request.session.get('fyers_access_token')
        
        if not client_id or not access_token:
            return None
        
        # Map index to symbol
        symbol_map = {
            "NIFTY": "NSE:NIFTY50-INDEX",
            "BANKNIFTY": "NSE:NIFTYBANK-INDEX"
        }
        
        symbol = symbol_map.get(index.upper())
        if not symbol:
            return None
        
        # Initialize FyersModel instance
        fyers = fyersModel.FyersModel(
            client_id=client_id,
            token=access_token,
            is_async=False,
            log_path=""
        )
        
        # Get option chain data which includes expiry dates
        data = {
            "symbol": symbol,
            "strikecount": 1,
            "timestamp": ""
        }
        
        response = fyers.optionchain(data=data)
        
        if response and response.get('code') == 200:
            expiry_data = response.get('data', {}).get('expiryData', [])
            if expiry_data:
                # Get the first (nearest) expiry date
                nearest_expiry = expiry_data[0]
                expiry_date_str = nearest_expiry.get('date')
                if expiry_date_str:
                    # Convert date string to date object
                    expiry_date = datetime.strptime(expiry_date_str, '%d-%m-%Y').date()
                    
                    # Determine if it's monthly or weekly expiry
                    # Monthly expiry is typically the last Thursday of the month
                    last_day_of_month = (expiry_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                    last_thursday = last_day_of_month - timedelta(days=((last_day_of_month.weekday() - 3) % 7))
                    
                    is_monthly = expiry_date == last_thursday
                    expiry_type = "MONTHLY" if is_monthly else "WEEKLY"
                    
                    # Save in session with index-specific keys
                    session_key = f"{index.lower()}_expiry_date"
                    request.session[session_key] = expiry_date.strftime("%Y-%m-%d")
                    
                    # Save expiry type
                    type_key = f"{index.lower()}_expiry_type"
                    request.session[type_key] = expiry_type
                    
                    return expiry_date.strftime("%Y-%m-%d")
                else:
                    return None
            else:
                return None
        else:
            return None
            
    except Exception as e:
        return None


def get_all_expiry_dates_sdk(request):
    """
    Get expiry dates for both NIFTY and BANKNIFTY and save to session
    
    Args:
        request: Django request object
    
    Returns:
        dict: Dictionary with expiry dates and types for both indices
    """
    try:
        result = {}
        
        # Get expiry for NIFTY
        nifty_expiry = get_next_expiry_sdk(request, "NIFTY")
        if nifty_expiry:
            nifty_type = request.session.get('nifty_expiry_type', 'WEEKLY')
            result['NIFTY'] = {
                'date': nifty_expiry,
                'type': nifty_type
            }
        
        # Get expiry for BANKNIFTY
        banknifty_expiry = get_next_expiry_sdk(request, "BANKNIFTY")
        if banknifty_expiry:
            banknifty_type = request.session.get('banknifty_expiry_type', 'WEEKLY')
            result['BANKNIFTY'] = {
                'date': banknifty_expiry,
                'type': banknifty_type
            }
        
        return result
        
    except Exception as e:
        return {}
