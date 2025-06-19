from datetime import datetime, timedelta, date
import pytz

def get_strike_price(ltp: float, index: str) -> int:
    if index.upper() == 'NIFTY':
        strike_interval = 50
    elif index.upper() == 'BANKNIFTY':
        strike_interval = 100
    else:
        raise ValueError(f"Invalid index: {index}")

    strike = round(ltp / strike_interval) * strike_interval
    return int(strike)

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