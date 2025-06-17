import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .auth.zerodha_auth import ZerodhaAuth
from .auth.fyers_auth import FyersAuth
from .kite_trade import KiteApp
from functools import wraps
from .fyers_utils import get_ltp

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
                return redirect(login_url)
            else:
                return render(request, 'zerodha_login.html', {'error': 'Failed to generate login URL'})
        except Exception:
            return render(request, 'zerodha_login.html', {'error': 'Failed to connect to Zerodha. Please check your credentials.'})
    
    # GET request - show login form
    return render(request, 'zerodha_login.html')

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
                redirect_uri = data.get('redirect_uri')
                response_type = data.get('response_type', 'code')  # Default to 'code'
            else:
                client_id = request.POST.get('client_id')
                client_secret = request.POST.get('client_secret')
                redirect_uri = request.POST.get('redirect_uri')
                response_type = request.POST.get('response_type', 'code')  # Default to 'code'
            
            # Validate required fields
            if not all([client_id, client_secret, redirect_uri]):
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
            # If GET request, show the form with the correct redirect URL
            redirect_uri = request.build_absolute_uri('/fyers/auth/')
            return render(request, 'fyers_login.html', {'redirect_uri': redirect_uri})
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
    secret = request.session.get('fyers_secret')
    
    if not client_id or not secret:
        return redirect('fyers_login')
    
    try:
        # Initialize Fyers auth
        fyers = FyersAuth(client_id, secret)
        
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
        request.session.pop('fyers_secret', None)
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
        
        # Get current prices
        try:
            nifty_ltp = get_ltp(request, 'NIFTY')
            banknifty_ltp = get_ltp(request, 'BANKNIFTY')
        except Exception as e:
            print(f"Error fetching LTP: {str(e)}")
            nifty_ltp = 0
            banknifty_ltp = 0
        
        return render(request, 'dashboard.html', {
            'positions': portfolio['positions'],
            'orders': portfolio['orders'],
            'history': portfolio['history'],
            'nifty_ltp': nifty_ltp,
            'banknifty_ltp': banknifty_ltp
        })
    except Exception as e:
        print(f"Error in dashboard: {str(e)}")
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
        print(f"Error in fyers_auth_redirect: {str(e)}")
        return redirect('/login/?error=Authentication failed')

@csrf_exempt
@require_http_methods(["POST"])
def store_fyers_credentials(request):
    """Store Fyers credentials in Django session"""
    try:
        data = json.loads(request.body)
        
        # Initialize FyersAuth to check for existing valid token
        fyers = FyersAuth(
            client_id=data.get('client_id'),
            client_secret=data.get('client_secret'),
            redirect_uri=data.get('redirect_uri')
        )
        
        # Check if we have a valid token
        if fyers.is_token_valid():
            # Store credentials in session
            request.session['fyers_client_id'] = data.get('client_id')
            request.session['fyers_client_secret'] = data.get('client_secret')
            request.session['fyers_redirect_uri'] = data.get('redirect_uri')
            request.session['fyers_access_token'] = fyers.access_token
            if fyers.refresh_token:
                request.session['fyers_refresh_token'] = fyers.refresh_token
                
            return JsonResponse({
                'status': 'success',
                'message': 'Valid token found',
                'redirect': '/dashboard/'
            })
        
        # Store credentials in session
        request.session['fyers_client_id'] = data.get('client_id')
        request.session['fyers_client_secret'] = data.get('client_secret')
        request.session['fyers_redirect_uri'] = data.get('redirect_uri')
        request.session['fyers_state'] = data.get('state')
        
        return JsonResponse({
            'status': 'success',
            'message': 'Credentials stored successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

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
        print(f"User input: {user_quantity} lots, Actual quantity: {actual_quantity}")
            
        # Check authentication
        api_key = request.session.get('api_key')
        access_token = request.session.get('access_token')
        fyers_client_id = request.session.get('fyers_client_id')
        fyers_access_token = request.session.get('fyers_access_token')
        
        if not all([api_key, access_token, fyers_client_id, fyers_access_token]):
            return JsonResponse({
                'error': 'Not authenticated',
                'details': 'Please login first'
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
                index=index,
                direction=direction,
                quantity=actual_quantity,
                request=request
            )
            return JsonResponse({
                'success': True,
                'order_id': order_id,
                'message': f'Order placed successfully for {user_quantity} lots'
            })
        except Exception as e:
            error_message = str(e)
            return JsonResponse({
                'error': 'Failed to place order',
                'details': error_message
            }, status=500)
                
    except json.JSONDecodeError:
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
        print("Exiting all positions")
        KiteApp(request=request).exit_all_positions()

        return JsonResponse({
            'status': 'success',
            'message': 'All positions exited successfully'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
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

        # Get Fyers credentials from session
        fyers_client_id = request.session.get('fyers_client_id')
        fyers_access_token = request.session.get('fyers_access_token')
        
        if not fyers_client_id or not fyers_access_token:
            return JsonResponse({
                'status': 'error',
                'message': 'Fyers credentials not found in session'
            }, status=401)

        # Map index to Fyers symbol
        symbol_map = {
            "NIFTY": "NSE:NIFTY50-INDEX",
            "BANKNIFTY": "NSE:NIFTYBANK-INDEX"
        }
        
        fyers_symbol = symbol_map.get(index)
        if not fyers_symbol:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid index: {index}'
            }, status=400)

        # Get LTP using Fyers API
        ltp = get_ltp(
            client_id=fyers_client_id,
            access_token=fyers_access_token,
            script_name=fyers_symbol
        )

        return JsonResponse({
            'status': 'success',
            'index': index,
            'price': ltp
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
