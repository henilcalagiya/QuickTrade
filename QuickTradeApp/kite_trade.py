from kiteconnect import KiteConnect
from datetime import datetime
from .fyers_utils import get_ltp
from .symbol_generator import generate_trading_symbol


class KiteApp:
    # Products
    PRODUCT_MIS = "MIS"
    PRODUCT_CNC = "CNC"
    PRODUCT_NRML = "NRML"
    PRODUCT_CO = "CO"

    # Order types
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_SLM = "SL-M"
    ORDER_TYPE_SL = "SL"

    # Varities
    VARIETY_REGULAR = "regular"
    VARIETY_CO = "co"
    VARIETY_AMO = "amo"

    # Transaction type
    TRANSACTION_TYPE_BUY = "BUY"
    TRANSACTION_TYPE_SELL = "SELL"

    # Validity
    VALIDITY_DAY = "DAY"
    VALIDITY_IOC = "IOC"

    # Exchanges
    EXCHANGE_NSE = "NSE"
    EXCHANGE_BSE = "BSE"
    EXCHANGE_NFO = "NFO"
    EXCHANGE_CDS = "CDS"
    EXCHANGE_BFO = "BFO"
    EXCHANGE_MCX = "MCX"

    def __init__(self, request=None, api_key=None, access_token=None):
        """Initialize with either request object or direct credentials"""
        if request:
            # Initialize with request object to get credentials from session
            api_key = request.session.get('api_key')
            access_token = request.session.get('access_token')
            
            if not api_key or not access_token:
                raise Exception("Kite credentials not found in session")
            
            self.kite = KiteConnect(api_key=api_key)
            self.kite.set_access_token(access_token)
            self.request = request  # Store request for later use
        elif api_key and access_token:
            # Initialize with direct credentials
            self.kite = KiteConnect(api_key=api_key)
            self.kite.set_access_token(access_token)
            self.request = None
        else:
            raise Exception("Either request object or api_key and access_token must be provided")

    def get_profile(self):
        return self.kite.get_profile()

    def place_order(self, request, index, direction, quantity):
        """
        Place an order for the given index and direction
        
        Args:
            request: Django request object containing session data
            index (str): Index name (e.g., 'NIFTY', 'BANKNIFTY')
            direction (str): Option direction ('CE' or 'PE')
            quantity (int): Number of lots to trade
            
        Returns:
            dict: Order response from Kite
            
        Raises:
            ValueError: If inputs are invalid
            Exception: For API or other errors with detailed error info
        """
        try:
            # Validate inputs
            if not index or not direction or not quantity:
                raise ValueError("Index, direction and quantity are required")
                
            if direction not in ['CE', 'PE']:
                raise ValueError("Direction must be either 'CE' or 'PE'")
                
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
                
            # Validate session
            api_key = request.session.get('api_key')
            access_token = request.session.get('access_token')
            
            if not api_key or not access_token:
                raise ValueError("Kite credentials not found in session")
                
            # Get LTP for the index
            try:
                ltp = get_ltp(request, index=index)
                if not ltp:
                    raise Exception(f"Unable to get LTP for {index}")
            except Exception as e:
                raise Exception(f"Error getting LTP for {index}: {str(e)}")
                
            # Generate trading symbol
            try:
                trading_symbol = generate_trading_symbol(request, index, direction, ltp)
                if not trading_symbol:
                    raise Exception(f"Unable to generate trading symbol for {index} {direction}")
            except Exception as e:
                raise Exception(f"Error generating trading symbol for {index} {direction}: {str(e)}")
                
            # Initialize Kite Connect
            try:
                kite = KiteConnect(api_key=api_key)
                kite.set_access_token(access_token)
            except Exception as e:
                raise Exception(f"Error initializing Kite Connect: {str(e)}")
                
            # Place order
            try:
                order_response = kite.place_order(
                    variety=self.VARIETY_REGULAR,
                    exchange=self.EXCHANGE_NFO,
                    tradingsymbol=trading_symbol,
                    transaction_type=self.TRANSACTION_TYPE_BUY,
                    quantity=quantity,
                    product=self.PRODUCT_MIS,
                    order_type=self.ORDER_TYPE_MARKET,
                    price=None,
                    validity=self.VALIDITY_DAY
                )
                
                return order_response
                
            except Exception as e:
                # Use the new error parsing method
                additional_info = {
                    'index': index,
                    'direction': direction,
                    'quantity': quantity,
                    'trading_symbol': trading_symbol,
                    'ltp': ltp
                }
                raise Exception(self._parse_kite_error(e, 'place_order', additional_info))
                
        except Exception as e:
            # Re-raise the exception with all the context
            raise

    def positions(self):
        """Get current positions"""
        try:
            positions = self.kite.positions()
            return positions
        except Exception as e:
            return {"net": []}

    def orders(self):
        """Get current orders"""
        try:
            orders = self.kite.orders()
            return orders
        except Exception as e:
            return []

    def order_history(self):
        """Get today's order history sorted by latest first"""
        try:
            # Get all orders
            orders = self.kite.orders()
            # Filter orders from today
            today = datetime.now().date()
            filtered_orders = [
                order for order in orders 
                if order.get('order_timestamp').date() == today
            ]
            # Sort by timestamp in descending order (latest first)
            sorted_orders = sorted(filtered_orders, key=lambda x: x.get('order_timestamp'), reverse=True)
            return sorted_orders
        except Exception as e:
            return []

    def get_portfolio(self):
        """Get complete portfolio data including positions, orders and history"""
        try:
            portfolio = {
                "positions": self.positions(),
                "orders": self.orders(),
                "history": self.order_history()
            }
            return portfolio
        except Exception as e:
            return {
                "positions": {"net": []},
                "orders": [],
                "history": []
            }

    def exit_all_positions(self):
        """
        Exit all open positions
        
        Returns:
            dict: Summary of exit operations with success/failure details
            
        Raises:
            Exception: If there are critical errors during the process
        """
        try:
            positions = self.kite.positions()["net"]
            if not positions:
                return {
                    'success': True,
                    'message': 'No open positions to exit',
                    'exited_positions': 0,
                    'failed_positions': 0,
                    'details': []
                }

            exit_results = []
            successful_exits = 0
            failed_exits = 0

            for pos in positions:
                try:
                    if pos["product"] == "MIS" and pos["exchange"] == "NFO" and pos["quantity"] != 0:
                        order_id = self.kite.place_order(
                            variety="regular",
                            exchange=pos["exchange"],
                            tradingsymbol=pos["tradingsymbol"],
                            transaction_type="SELL" if pos["quantity"] > 0 else "BUY",
                            quantity=abs(pos["quantity"]),
                            product=pos["product"],
                            order_type="MARKET",
                            validity="DAY"
                        )
                        
                        exit_results.append({
                            'symbol': pos["tradingsymbol"],
                            'status': 'success',
                            'order_id': order_id,
                            'quantity': abs(pos["quantity"]),
                            'transaction_type': "SELL" if pos["quantity"] > 0 else "BUY"
                        })
                        successful_exits += 1
                        
                except Exception as e:
                    error_message = str(e)
                    error_details = {
                        'symbol': pos["tradingsymbol"],
                        'status': 'failed',
                        'error_message': error_message,
                        'quantity': abs(pos["quantity"]),
                        'transaction_type': "SELL" if pos["quantity"] > 0 else "BUY"
                    }
                    
                    # Parse common exit errors
                    if 'insufficient holdings' in error_message.lower():
                        error_details['error_code'] = 'INSUFFICIENT_HOLDINGS'
                        error_details['user_message'] = f'Insufficient holdings for {pos["tradingsymbol"]}'
                    elif 'position already closed' in error_message.lower():
                        error_details['error_code'] = 'POSITION_CLOSED'
                        error_details['user_message'] = f'Position for {pos["tradingsymbol"]} is already closed'
                    elif 'market closed' in error_message.lower():
                        error_details['error_code'] = 'MARKET_CLOSED'
                        error_details['user_message'] = 'Market is currently closed'
                    elif 'token expired' in error_message.lower():
                        error_details['error_code'] = 'TOKEN_EXPIRED'
                        error_details['user_message'] = 'Your session has expired'
                    else:
                        error_details['error_code'] = 'EXIT_ERROR'
                        error_details['user_message'] = f'Failed to exit {pos["tradingsymbol"]}'
                    
                    exit_results.append(error_details)
                    failed_exits += 1

            return {
                'success': failed_exits == 0,
                'message': f'Exited {successful_exits} positions successfully, {failed_exits} failed',
                'exited_positions': successful_exits,
                'failed_positions': failed_exits,
                'details': exit_results
            }

        except Exception as e:
            error_message = str(e)
            raise Exception(f"EXIT_ALL_ERROR:CRITICAL_ERROR:Failed to process exit all positions:{error_message}")

    def _parse_kite_error(self, error, operation_type, additional_info=None):
        """
        Parse Kite API errors and return detailed error information
        
        Args:
            error: The exception object
            operation_type: Type of operation ('place_order', 'exit_position', 'cancel_order', 'exit_all')
            additional_info: Additional context information
            
        Returns:
            str: Formatted error string with detailed information
        """
        error_message = str(error)
        error_details = {
            'error_type': 'Kite API Error',
            'error_message': error_message,
            'operation_type': operation_type
        }
        
        if additional_info:
            error_details.update(additional_info)
        
        # Parse common Kite error patterns
        if 'insufficient funds' in error_message.lower():
            error_details['error_code'] = 'INSUFFICIENT_FUNDS'
            error_details['user_message'] = 'Insufficient funds in your account'
            error_details['suggestion'] = 'Please check your account balance and margin requirements'
        elif 'insufficient holdings' in error_message.lower():
            error_details['error_code'] = 'INSUFFICIENT_HOLDINGS'
            error_details['user_message'] = 'Insufficient holdings for this operation'
            error_details['suggestion'] = 'The position may have already been closed or modified'
        elif 'invalid symbol' in error_message.lower():
            error_details['error_code'] = 'INVALID_SYMBOL'
            error_details['user_message'] = 'Invalid trading symbol'
            error_details['suggestion'] = 'The option contract may not be available or may have expired'
        elif 'market closed' in error_message.lower():
            error_details['error_code'] = 'MARKET_CLOSED'
            error_details['user_message'] = 'Market is currently closed'
            error_details['suggestion'] = 'Please try during market hours (9:15 AM - 3:30 PM IST)'
        elif 'after market order' in error_message.lower() or 'amo' in error_message.lower():
            error_details['error_code'] = 'MARKET_CLOSED'
            error_details['user_message'] = 'Market is currently closed'
            error_details['suggestion'] = 'Please try during market hours (9:15 AM - 3:30 PM IST)'
        elif 'order rejected' in error_message.lower():
            error_details['error_code'] = 'ORDER_REJECTED'
            error_details['user_message'] = 'Order was rejected by the exchange'
            error_details['suggestion'] = 'Please check order parameters and try again'
        elif 'position already closed' in error_message.lower():
            error_details['error_code'] = 'POSITION_CLOSED'
            error_details['user_message'] = 'Position is already closed'
            error_details['suggestion'] = 'The position may have been closed by another order'
        elif 'order not found' in error_message.lower():
            error_details['error_code'] = 'ORDER_NOT_FOUND'
            error_details['user_message'] = 'Order not found'
            error_details['suggestion'] = 'The order may have already been executed or cancelled'
        elif 'token expired' in error_message.lower():
            error_details['error_code'] = 'TOKEN_EXPIRED'
            error_details['user_message'] = 'Your session has expired'
            error_details['suggestion'] = 'Please login again to continue trading'
        elif 'rate limit' in error_message.lower():
            error_details['error_code'] = 'RATE_LIMIT'
            error_details['user_message'] = 'Too many requests. Please wait a moment'
            error_details['suggestion'] = 'Please wait a few seconds before trying again'
        else:
            error_details['error_code'] = 'KITE_API_ERROR'
            error_details['user_message'] = error_message  # Show original Kite error
            error_details['suggestion'] = 'Please check your parameters and try again'
        
        # Return formatted error string
        return f"KITE_ERROR:{error_details['error_code']}:{error_details['user_message']}:{error_details['suggestion']}:{error_message}"

    def exit_position(self, symbol):
        """
        Exit a specific position
        
        Args:
            symbol (str): Trading symbol to exit
            
        Returns:
            str: Order ID of the exit order
            
        Raises:
            Exception: If there are errors during the process
        """
        try:
            # Get current positions
            positions = self.kite.positions()["net"]
            target_position = None
            
            # Find the position with the given symbol
            for pos in positions:
                if pos["tradingsymbol"] == symbol and pos["quantity"] != 0:
                    target_position = pos
                    break
                    
            if not target_position:
                raise Exception(f"No open position found for {symbol}")
                
            # Place exit order
            order_id = self.kite.place_order(
                variety="regular",
                exchange=target_position["exchange"],
                tradingsymbol=target_position["tradingsymbol"],
                transaction_type="SELL" if target_position["quantity"] > 0 else "BUY",
                quantity=abs(target_position["quantity"]),
                product=target_position["product"],
                order_type="MARKET",
                validity="DAY"
            )
            
            return order_id
            
        except Exception as e:
            # Parse and raise detailed error
            additional_info = {
                'symbol': symbol,
                'operation': 'exit_position'
            }
            raise Exception(self._parse_kite_error(e, 'exit_position', additional_info))