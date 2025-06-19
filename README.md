# Quick Trade - ATM Options Trading Platform

A Django-based web application specifically designed for ATM (At-The-Money) options trading on Zerodha for Nifty and BankNifty indices. The platform uses Fyers API for live market data while executing trades exclusively through Zerodha.

## 🚀 Features

### Trading Capabilities
- **ATM Options Trading**: Specialized for At-The-Money options on Nifty and BankNifty
- **Zerodha Integration**: Full OAuth authentication and trading execution
- **Live Market Data**: Real-time price feeds from Fyers API
- **Quick Order Placement**: Streamlined interface for options trading
- **Position Management**: View and manage open options positions
- **Bulk Operations**: Exit all positions with a single click

### Market Data
- **Fyers Integration**: Live market data for accurate pricing
- **Real-time Updates**: Continuous price feeds for indices and options
- **ATM Calculation**: Automatic At-The-Money strike price identification

### Security & Authentication
- **OAuth 2.0 Flow**: Secure authentication for Zerodha
- **Session Management**: Persistent login sessions
- **CSRF Protection**: Built-in security against cross-site request forgery
- **Environment Variables**: Secure credential management

### User Interface
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, intuitive interface with Bootstrap styling
- **Real-time Updates**: Live price updates and order status
- **Options-Focused**: Interface optimized for options trading

## 🏗️ Project Structure

```
Quick Trade/
├── QuickTradePortal/          # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Django configuration
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # WSGI application
│   └── asgi.py              # ASGI application
├── QuickTradeApp/            # Main Django application
│   ├── auth/                # Broker authentication modules
│   │   ├── zerodha_auth.py  # Zerodha OAuth implementation
│   │   └── fyers_auth.py    # Fyers authentication (for market data)
│   ├── templates/           # HTML templates
│   │   ├── base.html        # Base template
│   │   ├── dashboard.html   # Main trading dashboard
│   │   ├── zerodha_login.html
│   │   ├── fyers_login.html
│   │   └── fyers_callback.html
│   ├── static/              # Static files (CSS, JS, images)
│   │   └── images/
│   │       ├── fyers_logo.svg
│   │       └── zerodha_logo.svg
│   ├── views.py             # Main application views
│   ├── urls.py              # App URL routing
│   ├── config.py            # Configuration settings
│   ├── kite_trade.py        # Zerodha trading logic
│   ├── fyers_utils.py       # Fyers market data utilities
│   └── symbol_generator.py  # Options symbol mapping utilities
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── render.yaml             # Render deployment configuration
├── db.sqlite3              # SQLite database (development)
└── logs/                   # Application logs
    ├── fyersApi.log
    └── fyersRequests.log
```

## 🛠️ Technology Stack

### Backend
- **Django 4.2.0**: Web framework
- **Python 3.9+**: Programming language
- **SQLite/PostgreSQL**: Database (SQLite for development, PostgreSQL for production)

### Broker APIs
- **KiteConnect 4.1.0**: Zerodha trading API (for order execution)
- **Fyers API v3**: Fyers API (for live market data only)

### Deployment
- **Render**: Cloud hosting platform
- **Gunicorn**: WSGI HTTP Server
- **WhiteNoise**: Static file serving

### Frontend
- **Bootstrap**: CSS framework
- **jQuery**: JavaScript library
- **Chart.js**: Charting library

## 📋 Prerequisites

Before running this application, you need:

1. **Python 3.9 or higher**
2. **Zerodha Trading Account** with API access (for trading)
3. **Fyers Trading Account** with API access (for market data only)
4. **API Credentials** from both brokers

### Zerodha API Setup (Trading)
1. Log in to your Zerodha account
2. Go to Console → API → Create API Key
3. Set redirect URL to: `http://your-domain/zerodha/callback/`
4. Note down API Key and Secret
5. Enable options trading permissions

### Fyers API Setup (Market Data)
1. Log in to your Fyers account
2. Go to API → Create App
3. Set redirect URL to: `http://your-domain/fyers/auth/`
4. Note down Client ID and Secret
5. Ensure market data permissions are enabled

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Quick-Trade
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

### 5. Database Setup
```bash
python manage.py migrate
```

### 6. Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`

## 🌐 Deployment

### Render Deployment
This project is configured for deployment on Render:

1. **Fork/Clone** the repository to your Render account
2. **Create a new Web Service** and connect your repository
3. **Set Environment Variables**:
   - `SECRET_KEY`: Django secret key
   - `DEBUG`: False (for production)
   - `DATABASE_URL`: PostgreSQL connection string (auto-generated)

The `render.yaml` file contains the deployment configuration.

### Manual Deployment
For other platforms:

1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static file serving
4. Configure environment variables
5. Run with Gunicorn: `gunicorn QuickTradePortal.wsgi:application`

## 📱 Usage Guide

### 1. Initial Setup
1. Visit the application URL
2. You'll be redirected to Zerodha login
3. Enter your Zerodha API credentials (for trading)
4. Complete OAuth authentication
5. Enter your Fyers API credentials (for market data)
6. Complete Fyers authentication

### 2. Trading Dashboard
Once authenticated, you'll see the main dashboard with:
- **Account Overview**: Zerodha balance and positions
- **Market Watch**: Live Nifty and BankNifty prices from Fyers
- **ATM Options**: Current ATM strike prices for both indices
- **Order Placement**: Buy/sell options order forms
- **Position Management**: Current options positions and P&L

### 3. Placing ATM Options Orders
1. Select the index (Nifty/BankNifty)
2. Choose option type (Call/Put)
3. Verify ATM strike price (auto-calculated)
4. Enter quantity
5. Click "Place Order" (executed on Zerodha)

### 4. Managing Positions
- View all open options positions
- Monitor P&L in real-time
- Exit individual positions
- Use "Exit All" for bulk position closure

## 🔧 Configuration

### Broker Configuration
Update `QuickTradeApp/config.py` for custom redirect URLs:
```python
FYERS_REDIRECT_URL = "https://your-domain/fyers/auth/"
ZERODHA_REDIRECT_URL = "https://your-domain/zerodha/callback/"
```

### Session Settings
Configure session timeout in `settings.py`:
```python
SESSION_COOKIE_AGE = 86400  # 24 hours
```

## 🔒 Security Considerations

1. **API Credentials**: Never commit API keys to version control
2. **Environment Variables**: Use environment variables for sensitive data
3. **HTTPS**: Always use HTTPS in production
4. **Session Security**: Regularly rotate session keys
5. **Rate Limiting**: Implement rate limiting for API calls

## 📊 API Endpoints

### Authentication
- `GET /` - Login redirect
- `GET/POST /zerodha/login/` - Zerodha authentication (trading)
- `GET /zerodha/callback/` - Zerodha OAuth callback
- `GET/POST /fyers/login/` - Fyers authentication (market data)
- `GET /fyers/auth/` - Fyers OAuth redirect
- `GET /fyers/callback/` - Fyers OAuth callback

### Trading (Zerodha)
- `GET /dashboard/` - Main trading dashboard
- `POST /place_order/` - Place options orders
- `POST /exit_all/` - Exit all positions

### Market Data (Fyers)
- `GET /get_index_price/` - Get live index prices

### Session
- `GET /logout/` - Logout and clear session

## 🎯 Trading Strategy

This platform is specifically designed for:
- **ATM Options Trading**: At-The-Money options on Nifty and BankNifty
- **Quick Execution**: Streamlined interface for rapid order placement
- **Real-time Data**: Live market data from Fyers for accurate pricing
- **Position Management**: Easy monitoring and exit of options positions

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API credentials for both brokers
   - Check redirect URLs match broker settings
   - Ensure proper OAuth flow completion

2. **Order Placement Failures**
   - Verify sufficient balance in Zerodha account
   - Check market hours (9:15 AM - 3:30 PM IST)
   - Ensure options trading is enabled
   - Validate ATM strike price calculation

3. **Market Data Issues**
   - Check Fyers API connectivity
   - Verify market data permissions
   - Ensure proper authentication

4. **Session Timeouts**
   - Re-authenticate with both brokers
   - Clear browser cache and cookies

### Logs
Check application logs in the `logs/` directory:
- `fyersApi.log`: Fyers API interactions (market data)
- `fyersRequests.log`: Fyers request details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This application is for educational and personal use only. Options trading involves substantial risk of loss and is not suitable for all investors. ATM options trading can be highly volatile. The developers are not responsible for any financial losses incurred through the use of this software.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review broker API documentation

---

**Note**: This application is specifically designed for ATM options trading on Zerodha using live market data from Fyers. Ensure compliance with broker terms of service and regulatory requirements before use. Options trading involves significant risk and should only be undertaken by experienced traders. 