import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from .auth.zerodha_auth import ZerodhaAuth
from .auth.fyers_auth import FyersAuth
from .kite_trade import KiteApp
from functools import wraps
from .fyers_utils import get_ltp, get_market_data_simple, FyersService, get_next_expiry_sdk
from .config import FYERS_REDIRECT_URL, ZERODHA_REDIRECT_URL, GOOGLE_ANALYTICS_ID

def is_authenticated(request):
    """Check if user is authenticated with both Zerodha and Fyers"""
    try:
        # Check Zerodha authentication
        api_key = request.session.get('api_key')
        api_secret = request.session.get('api_secret')
        access_token = request.session.get('access_token')
        
        if not all([api_key, api_secret, access_token]):
            return False
            
        # Check Fyers authentication
        client_id = request.session.get('fyers_client_id')
        client_secret = request.session.get('fyers_client_secret')
        redirect_uri = request.session.get('fyers_redirect_uri')
        fyers_access_token = request.session.get('fyers_access_token')
        
        if not all([client_id, client_secret, redirect_uri, fyers_access_token]):
            return False
            
        # Initialize both auth clients to validate tokens
        try:
            # Validate Zerodha token
            zerodha = ZerodhaAuth(api_key=api_key, api_secret=api_secret)
            zerodha.kite.set_access_token(access_token)
            zerodha_profile = zerodha.kite.profile()
            
            if not zerodha_profile:
                return False
            
            # Validate Fyers token
            fyers = FyersAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
            if not fyers.is_token_valid(fyers_access_token):
                return False
            
            return True
            
        except Exception:
            return False
            
    except Exception:
        return False

def login_required(view_func):
    """Custom login required decorator"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_authenticated(request):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@require_http_methods(["GET", "POST"])
def login(request):
    """Handle login - redirects to appropriate login page based on session state"""
    # Check if we have valid Zerodha credentials
    api_key = request.session.get('api_key')
    api_secret = request.session.get('api_secret')
    access_token = request.session.get('access_token')
    
    if all([api_key, api_secret, access_token]):
        # Initialize Zerodha auth
        zerodha = ZerodhaAuth(api_key, api_secret)
        try:
            # Verify if token is still valid
            profile = zerodha.get_profile(access_token)
            if profile:
                # Check if we have Fyers credentials
                fyers_client_id = request.session.get('fyers_client_id')
                fyers_client_secret = request.session.get('fyers_client_secret')
                fyers_access_token = request.session.get('fyers_access_token')
                
                if all([fyers_client_id, fyers_client_secret, fyers_access_token]):
                    # Both Zerodha and Fyers are authenticated, go to dashboard
                    return redirect('dashboard')
                else:
                    # Only Zerodha is authenticated, go to Fyers login
                    return redirect('fyers_login')
        except Exception:
            # Clear invalid session data
            request.session.flush()
    
    # No valid session, go to Zerodha login
    return redirect('zerodha_login')

@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def zerodha_login(request):
    """Handle Zerodha login"""
    # Clear any existing session data
    request.session.flush()
    
    if request.method == "POST":
        try:
            api_key = request.POST.get('api_key')
            api_secret = request.POST.get('api_secret')
            
            if not api_key or not api_secret:
                return render(request, 'zerodha_login.html', {'error': 'API Key and Secret are required'})
            
            # Initialize Zerodha auth
            zerodha = ZerodhaAuth(api_key, api_secret)
            login_url = zerodha.get_login_url()
            
            if login_url:
                # Store credentials in session
                request.session['api_key'] = api_key
                request.session['api_secret'] = api_secret
                request.session['zerodha_redirect_uri'] = ZERODHA_REDIRECT_URL
                return redirect(login_url)
            else:
                return render(request, 'zerodha_login.html', {'error': 'Failed to generate login URL'})
        except Exception:
            return render(request, 'zerodha_login.html', {'error': 'Failed to connect to Zerodha. Please check your credentials.'})
    
    # GET request - show login form with redirect URL
    return render(request, 'zerodha_login.html', {'ZERODHA_REDIRECT_URL': ZERODHA_REDIRECT_URL})

@require_http_methods(["GET"])
def zerodha_callback(request):
    """Handle Zerodha OAuth callback"""
    request_token = request.GET.get('request_token')
    if not request_token:
        return redirect('zerodha_login')
    
    # Get stored credentials
    api_key = request.session.get('api_key')
    api_secret = request.session.get('api_secret')
    
    if not api_key or not api_secret:
        return redirect('zerodha_login')
    
    try:
        # Initialize Zerodha auth
        zerodha = ZerodhaAuth(api_key, api_secret)
        
        # Generate session
        data = zerodha.generate_session(request_token)
        if data and 'access_token' in data:
            # Store access token in session
            request.session['access_token'] = data['access_token']
            # Redirect to Fyers login
            return redirect('fyers_login')
    except Exception:
        # Clear session data on error
        request.session.flush()
        return redirect('zerodha_login')
    
    return redirect('zerodha_login')

@require_http_methods(["GET", "POST"])
def fyers_login(request):
    """Handle Fyers login form display and submission"""
    try:
        if request.method == 'POST':
            # Get form data - could be form data or JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                client_id = data.get('client_id')
                client_secret = data.get('client_secret')
            else:
                client_id = request.POST.get('client_id')
                client_secret = request.POST.get('client_secret')
            
            # Validate required fields
            if not all([client_id, client_secret]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'All fields are required'
                }, status=400)
            
            # Validate client_id format
            if not client_id.endswith('-100'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Client ID must be in format XXXXX-100'
                }, status=400)
            
            # Use redirect URI from config
            redirect_uri = FYERS_REDIRECT_URL
            response_type = "code"
            
            # Store in session for callback
            request.session['fyers_client_id'] = client_id
            request.session['fyers_client_secret'] = client_secret
            request.session['fyers_redirect_uri'] = redirect_uri
            request.session['fyers_response_type'] = response_type
            
            # Initialize FyersAuth with form data
            fyers = FyersAuth(client_id, client_secret, redirect_uri)
            
            # Generate auth URL with response_type
            auth_url = fyers.generate_auth_code(response_type)
            
            # Check if auth URL was generated
            if not auth_url:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to generate Fyers authorization URL'
                }, status=500)
            
            # Return JSON response with auth URL
            return JsonResponse({
                'status': 'success',
                'auth_url': auth_url
            })
        else:
            # If GET request, show the form with the redirect URL from config
            return render(request, 'fyers_login.html', {'FYERS_REDIRECT_URL': FYERS_REDIRECT_URL})
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def fyers_callback(request):
    """Handle Fyers OAuth callback"""
    auth_code = request.GET.get('auth_code')
    if not auth_code:
        return redirect('fyers_login')
    
    # Get stored credentials
    client_id = request.session.get('fyers_client_id')
    client_secret = request.session.get('fyers_client_secret')
    redirect_uri = request.session.get('fyers_redirect_uri')
    
    if not all([client_id, client_secret, redirect_uri]):
        return redirect('fyers_login')
    
    try:
        # Initialize Fyers auth
        fyers = FyersAuth(client_id, client_secret, redirect_uri)
        
        # Generate access token
        data = fyers.generate_access_token(auth_code)
        if data and 'access_token' in data:
            # Store access token in session
            request.session['fyers_access_token'] = data['access_token']
            # Redirect to dashboard
            return redirect('dashboard')
    except Exception as e:
        # Clear Fyers session data on error
        request.session.pop('fyers_client_id', None)
        request.session.pop('fyers_client_secret', None)
        request.session.pop('fyers_access_token', None)
    
    return redirect('fyers_login')

@login_required
@require_http_methods(["GET"])
def dashboard(request):
    """Handle dashboard view"""
    try:
        # Get Zerodha credentials
        api_key = request.session.get('api_key')
        api_secret = request.session.get('api_secret')
        access_token = request.session.get('access_token')
        
        if not all([api_key, api_secret, access_token]):
            return redirect('login')
        
        # Initialize Kite client
        kite = KiteApp(request=request)
        
        # Get portfolio data
        portfolio = kite.get_portfolio()
        
        # Get market data including expiry dates using FyersService
        market_data = get_market_data_simple(request)
        
        # Get expiry dates for both indices using the new function
        expiry_dates = {}
        try:
            # Check if we already have expiry data in session for NIFTY
            nifty_expiry = request.session.get('nifty_expiry_date')
            nifty_type = request.session.get('nifty_expiry_type')
            
            if nifty_expiry and nifty_type:
                expiry_dates['NIFTY'] = {
                    'date': nifty_expiry,
                    'type': nifty_type
                }
            else:
                # Get expiry for NIFTY from API if not in session
                nifty_expiry = get_next_expiry_sdk(request, "NIFTY")
                if nifty_expiry:
                    nifty_type = request.session.get('nifty_expiry_type', 'WEEKLY')
                    expiry_dates['NIFTY'] = {
                        'date': nifty_expiry,
                        'type': nifty_type
                    }
            
            # Check if we already have expiry data in session for BANKNIFTY
            banknifty_expiry = request.session.get('banknifty_expiry_date')
            banknifty_type = request.session.get('banknifty_expiry_type')
            
            if banknifty_expiry and banknifty_type:
                expiry_dates['BANKNIFTY'] = {
                    'date': banknifty_expiry,
                    'type': banknifty_type
                }
            else:
                # Get expiry for BANKNIFTY from API if not in session
                banknifty_expiry = get_next_expiry_sdk(request, "BANKNIFTY")
                if banknifty_expiry:
                    banknifty_type = request.session.get('banknifty_expiry_type', 'WEEKLY')
                    expiry_dates['BANKNIFTY'] = {
                        'date': banknifty_expiry,
                        'type': banknifty_type
                    }
            
        except Exception as e:
            expiry_dates = {}
        
        return render(request, 'dashboard.html', {
            'positions': portfolio['positions'],
            'orders': portfolio['orders'],
            'history': portfolio['history'],
            'expiry_dates': expiry_dates,
            'index_prices': market_data.get('prices', {})
        })
    except Exception as e:
        return render(request, 'QuickTradeApp/error.html', {'error': str(e)})

@require_http_methods(["GET"])
def logout(request):
    """Handle logout"""
    request.session.flush()
    return redirect('login')

@require_http_methods(["GET"])
def fyers_auth_redirect(request):
    """Handle Fyers auth redirect and automatically process the auth code"""
    try:
        # Get the auth code from URL parameters
        auth_code = request.GET.get('auth_code')
        state = request.GET.get('state')
        
        if not auth_code:
            return redirect('/login/?error=No auth code received')
            
        # Get stored credentials
        client_id = request.session.get('fyers_client_id')
        client_secret = request.session.get('fyers_client_secret')
        redirect_uri = request.session.get('fyers_redirect_uri')
        
        if not all([client_id, client_secret, redirect_uri]):
            return redirect('/login/?error=Missing Fyers credentials')
            
        # Initialize Fyers auth
        fyers = FyersAuth(client_id, client_secret, redirect_uri)
        
        # Generate access token
        token_data = fyers.generate_access_token(auth_code)
        if not token_data or 'access_token' not in token_data:
            return redirect('/login/?error=Failed to generate access token')
            
        # Store access token in session
        request.session['fyers_access_token'] = token_data['access_token']
        request.session['fyers_refresh_token'] = token_data.get('refresh_token')
        
        # Redirect to dashboard
        return redirect('dashboard')
        
    except Exception as e:
        return redirect('/login/?error=Authentication failed')

@ensure_csrf_cookie
def place_order(request):
    """Place an order for the given index and direction"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
        
    try:
        # Get parameters from request
        data = json.loads(request.body)
        index = data.get('index')
        direction = data.get('direction')
        user_quantity = int(data.get('quantity', 1)) # Default to 1 lot if quantity not specified

        if not all([index, direction, user_quantity]):
            return JsonResponse({
                'error': 'Missing required parameters',
                'details': {
                    'index': index,
                    'direction': direction,
                    'quantity': user_quantity
                }
            }, status=400)
            
        # Calculate actual quantity based on lot size
        lot_sizes = {
            'NIFTY': 75,
            'BANKNIFTY': 30
        }
        lot_size = lot_sizes.get(index.upper())
        if not lot_size:
            return JsonResponse({
                'error': 'Invalid index',
                'details': f'Unknown index: {index}'
            }, status=400)
            
        actual_quantity = user_quantity * lot_size
            
        # Check authentication
        api_key = request.session.get('api_key')
        access_token = request.session.get('access_token')
        fyers_client_id = request.session.get('fyers_client_id')
        fyers_access_token = request.session.get('fyers_access_token')
        
        # For order placement, we need both Zerodha and Fyers credentials
        # Zerodha for order placement, Fyers for LTP and symbol generation
        if not all([api_key, access_token, fyers_client_id, fyers_access_token]):
            missing_creds = []
            if not api_key or not access_token:
                missing_creds.append("Zerodha")
            if not fyers_client_id or not fyers_access_token:
                missing_creds.append("Fyers")
            
            return JsonResponse({
                'error': f'Not authenticated with {", ".join(missing_creds)}',
                'details': f'Please login with {", ".join(missing_creds)} first'
            }, status=401)
            
        # Initialize KiteApp
        try:
            kite = KiteApp(
                api_key=api_key,
                access_token=access_token
            )
        except Exception as e:
            return JsonResponse({
                'error': 'Failed to initialize trading app',
                'details': str(e)
            }, status=500)
            
        # Place the order
        try:
            order_id = kite.place_order(
                request=request,
                index=index,
                direction=direction,
                quantity=actual_quantity
            )
            return JsonResponse({
                'success': True,
                'order_id': order_id,
                'message': f'Order placed successfully for {user_quantity} lots'
            })
        except Exception as e:
            error_message = str(e)
            
            # Check if this is a detailed Kite error
            if error_message.startswith('KITE_ERROR:'):
                # Parse the detailed error information
                parts = error_message.split(':', 4)  # Split into 5 parts
                if len(parts) >= 5:
                    error_code = parts[1]
                    user_message = parts[2]
                    suggestion = parts[3]
                    original_error = parts[4]
                    
                    return JsonResponse({
                        'success': False,
                        'error': user_message,
                        'error_code': error_code,
                        'suggestion': suggestion,
                        'details': original_error,
                        'order_info': {
                            'index': index,
                            'direction': direction,
                            'quantity': user_quantity,
                            'actual_quantity': actual_quantity
                        }
                    }, status=400)
                else:
                    # Fallback if parsing fails
                    return JsonResponse({
                        'success': False,
                        'error': 'Order placement failed',
                        'details': error_message
                    }, status=500)
            else:
                # Handle other types of errors
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to place order',
                    'details': error_message
                }, status=500)
                
    except json.JSONDecodeError as e:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def exit_all(request):
    """Handle exiting all positions"""
    try:
        # Exit all positions using KiteApp
        result = KiteApp(request=request).exit_all_positions()

        if result['success']:
            return JsonResponse({
                'success': True,
                'message': result['message'],
                'exited_positions': result['exited_positions'],
                'failed_positions': result['failed_positions'],
                'details': result['details']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['message'],
                'exited_positions': result['exited_positions'],
                'failed_positions': result['failed_positions'],
                'details': result['details']
            }, status=400)

    except Exception as e:
        error_message = str(e)
        
        # Check if this is a detailed exit error
        if error_message.startswith('EXIT_ALL_ERROR:'):
            parts = error_message.split(':', 3)
            if len(parts) >= 4:
                error_code = parts[1]
                user_message = parts[2]
                original_error = parts[3]
                
                return JsonResponse({
                    'success': False,
                    'error': user_message,
                    'error_code': error_code,
                    'details': original_error
                }, status=500)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to exit positions',
                    'details': error_message
                }, status=500)
        else:
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred',
                'details': error_message
            }, status=500)

@require_http_methods(["GET"])
def get_index_price(request):
    """Get current price of an index using Fyers API"""
    try:
        index = request.GET.get('index', '').upper()
        if not index:
            return JsonResponse({
                'status': 'error',
                'message': 'Index parameter is required'
            }, status=400)

        # Use FyersService to get index price
        try:
            fyers_service = FyersService(request)
            price = fyers_service.get_index_price(index)
            
            return JsonResponse({
                'status': 'success',
                'index': index,
                'price': price
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to get {index} price: {str(e)}'
            }, status=500)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def exit_position(request):
    """Handle exiting a specific position"""
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol')
        
        if not symbol:
            return JsonResponse({
                'success': False,
                'error': 'Symbol is required'
            }, status=400)
            
        # Check authentication
        api_key = request.session.get('api_key')
        access_token = request.session.get('access_token')
        
        if not api_key or not access_token:
            return JsonResponse({
                'success': False,
                'error': 'Not authenticated with Zerodha',
                'details': 'Please login with Zerodha first'
            }, status=401)
            
        # Initialize KiteApp
        try:
            kite = KiteApp(
                api_key=api_key,
                access_token=access_token
            )
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to initialize trading app',
                'details': str(e)
            }, status=500)
            
        # Exit the position
        try:
            order_id = kite.exit_position(symbol)
            
            return JsonResponse({
                'success': True,
                'order_id': order_id,
                'message': f'Successfully exited position for {symbol}'
            })
            
        except Exception as e:
            error_message = str(e)
            
            # Check if this is a detailed Kite error
            if error_message.startswith('KITE_ERROR:'):
                parts = error_message.split(':', 4)
                if len(parts) >= 5:
                    error_code = parts[1]
                    user_message = parts[2]
                    suggestion = parts[3]
                    original_error = parts[4]
                    
                    return JsonResponse({
                        'success': False,
                        'error': user_message,
                        'error_code': error_code,
                        'suggestion': suggestion,
                        'details': original_error
                    }, status=400)
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Failed to exit position',
                        'details': error_message
                    }, status=500)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to exit position',
                    'details': error_message
                }, status=500)
                
    except json.JSONDecodeError as e:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=500)
