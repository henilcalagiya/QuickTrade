from datetime import datetime, timedelta, date
import pytz

def is_expired(expiry_str: str) -> bool:
    today = date.today()
    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
    return today > expiry_date

def is_monthly_expiry(expiry_date: date) -> bool:
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).date()
    last_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    return expiry_date == last_of_month

def fetch_and_store_expiry(request, fyers, index: str) -> date:
    try:
        # Map the index to the correct symbol format
        symbol_map = {
            "NIFTY": "NSE:NIFTY50-INDEX",
            "BANKNIFTY": "NSE:NIFTYBANK-INDEX"
        }
        
        symbol = symbol_map.get(index.upper())
        if not symbol:
            raise ValueError(f"Invalid index: {index}")

        # Prepare data for optionchain API
        data = {
            "symbol": symbol,
            "strikecount": 1,
            "timestamp": ""
        }
        
        # Make the API call
        response = fyers.optionchain(data=data)

        if not response or response.get('code') != 200:
            raise ValueError(f"Failed to fetch data for {index}")

        # Extract expiry dates from response
        expiry_data = response.get('data', {}).get('expiryData', [])
        if not expiry_data:
            raise ValueError(f"No expiry data found for {index}")

        # Get the nearest expiry date (first one in the list)
        nearest_expiry = expiry_data[0]
        expiry_date = datetime.strptime(nearest_expiry['date'], '%d-%m-%Y').date()
        
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

        return expiry_date

    except Exception as e:
        raise

def get_strike_price(ltp: float, index: str) -> int:
    if index.upper() == 'NIFTY':
        strike_interval = 50
    elif index.upper() == 'BANKNIFTY':
        strike_interval = 100
    else:
        raise ValueError(f"Invalid index: {index}")

    strike = round(ltp / strike_interval) * strike_interval
    return int(strike)

def get_expiry_date(request, fyers, index: str) -> tuple[date, str]:
    """
    Get the expiry date and type for the given index from session or fetch new if needed
    
    Args:
        request: Django request object
        fyers: Fyers API instance
        index: Index name ('NIFTY' or 'BANKNIFTY')
        
    Returns:
        tuple: (expiry_date, expiry_type)
    """
    # Get index-specific session keys
    expiry_key = f"{index.lower()}_expiry_date"
    type_key = f"{index.lower()}_expiry_type"
    
    # Get stored values
    expiry_str = request.session.get(expiry_key)
    expiry_type = request.session.get(type_key)

    # If no expiry stored or expired, fetch new
    if not expiry_str or is_expired(expiry_str):
        expiry_date = fetch_and_store_expiry(request, fyers, index)
        # Get the updated expiry type after fetching new expiry
        expiry_type = request.session.get(type_key)
        return expiry_date, expiry_type

    # Return stored expiry
    return datetime.strptime(expiry_str, "%Y-%m-%d").date(), expiry_type

def generate_trading_symbol(request, index: str, direction: str, ltp: float) -> str:
    """
    Generate trading symbol according to Fyers format
    
    Args:
        request: Django request object
        index: Index name ('NIFTY' or 'BANKNIFTY')
        direction: 'CE' or 'PE'
        ltp: Last traded price
        
    Returns:
        str: Trading symbol in Fyers format
    """
    if index.upper() not in ['NIFTY', 'BANKNIFTY']:
        raise ValueError(f"Invalid index: {index}")
        
    # Get expiry date and type from session
    expiry_key = f"{index.lower()}_expiry_date"
    type_key = f"{index.lower()}_expiry_type"
    
    expiry_str = request.session.get(expiry_key)
    expiry_type = request.session.get(type_key)
    
    if not expiry_str:
        raise ValueError(f"No expiry date found for {index}")
        
    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
    
    # Get strike price
    strike = get_strike_price(ltp, index)
    
    # Get year in YY format
    year = str(expiry_date.year)[-2:]
    
    # Generate symbol based on expiry type
    if expiry_type == "MONTHLY":
        # Monthly format: <INDEX><YY><MMM><STRIKE><CE|PE>
        month = expiry_date.strftime("%b").upper()  # Gets first 3 letters of month
        symbol = f"{index}{year}{month}{strike}{direction}"
    else:
        # Weekly format: <INDEX><YY><M><DD><STRIKE><CE|PE>
        month_code = get_month_code(expiry_date.month)
        day = expiry_date.strftime("%d")
        symbol = f"{index}{year}{month_code}{day}{strike}{direction}"
    
    return symbol

def get_month_code(month: int) -> str:
    """
    Get the month code for weekly expiry format
    
    Args:
        month: Month number (1-12)
        
    Returns:
        str: Month code (1-9, O, N, D)
    """
    if 1 <= month <= 9:
        return str(month)
    elif month == 10:
        return 'O'
    elif month == 11:
        return 'N'
    elif month == 12:
        return 'D'
    else:
        raise ValueError(f"Invalid month number: {month}")