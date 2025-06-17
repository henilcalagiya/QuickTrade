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
            Exception: For API or other errors
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
            except Exception as e:
                raise Exception(f"Error getting LTP: {str(e)}")
                
            # Generate trading symbol
            try:
                trading_symbol = generate_trading_symbol(request, index, direction, ltp)
            except Exception as e:
                raise Exception(f"Error generating trading symbol: {str(e)}")
                
            # Initialize Kite Connect
            try:
                kite = KiteConnect(api_key=api_key, access_token=access_token)
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
                raise Exception(f"Error placing order: {str(e)}")
                
        except Exception as e:
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

    def get_position_summary(self):
        """Get summary of current positions"""
        try:
            positions = self.positions()
            summary = {
                "total_positions": len(positions.get("net", [])),
                "total_pnl": sum(pos.get("pnl", 0) for pos in positions.get("net", [])),
                "positions": positions.get("net", [])
            }
            return summary
        except Exception as e:
            return {
                "total_positions": 0,
                "total_pnl": 0,
                "positions": []
            }

    def margins(self):
        return self.kite.margins()

    def exit_all_positions(self):
        try:
            positions = self.kite.positions()["net"]
            if not positions:
                return

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
                except Exception:
                    continue

        except Exception as e:
            raise