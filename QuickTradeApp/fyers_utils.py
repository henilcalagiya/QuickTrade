from fyers_apiv3 import fyersModel
from django.http import HttpRequest

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
