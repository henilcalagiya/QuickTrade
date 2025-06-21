# Quick Trade - Advanced Trading Platform

A comprehensive Django-based automated trading platform that integrates with Zerodha and Fyers APIs for real-time options trading on NIFTY and BANKNIFTY indices.

## 🚀 Features

### Core Trading Features
- **Multi-Broker Integration**: Seamless integration with Zerodha Kite and Fyers APIs
- **Real-time Trading**: Execute options trades with live market data
- **Automated Symbol Generation**: Dynamic option symbol creation based on current market prices
- **Portfolio Management**: Comprehensive view of positions, orders, and trading history
- **One-Click Trading**: Quick CALL/PUT order placement with customizable lot sizes
- **Bulk Position Management**: Exit all positions with a single click

### Technical Features
- **Responsive Design**: Modern, mobile-friendly interface built with Bootstrap 5
- **Real-time Updates**: Live price feeds and portfolio updates
- **Session Management**: Secure authentication with both brokers
- **Error Handling**: Comprehensive error parsing and user-friendly messages
- **Analytics Integration**: Google Analytics 4 for user tracking

## 🏗️ Architecture Overview

### System Architecture
```
Frontend (Bootstrap + JavaScript)
    ↓ AJAX calls
Django Views & Controllers
    ↓ API integration
Broker Services (Zerodha/Fyers)
    ↓ Data persistence
Session Storage + JSON Files
```

### Component Structure
```
QuickTradePortal/          # Django project settings
├── settings.py            # Application configuration
├── urls.py               # Main URL routing
└── wsgi.py              # WSGI application

QuickTradeApp/            # Main application
├── views.py             # HTTP request handlers
├── urls.py              # URL patterns
├── auth/                # Authentication modules
│   ├── zerodha_auth.py  # Zerodha OAuth integration
│   └── fyers_auth.py    # Fyers OAuth integration
├── kite_trade.py        # Zerodha trading operations
├── fyers_utils.py       # Fyers market data utilities
├── symbol_generator.py  # Option symbol generation
├── json_storage.py      # File-based data persistence
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── dashboard.html   # Main trading interface
│   ├── zerodha_login.html
│   └── fyers_login.html
└── static/              # Static assets
    └── images/          # Logo files
```

## 🛠️ Technology Stack

### Backend
- **Django 4.2.0**: Web framework
- **Python 3.11**: Programming language
- **SQLite3**: Database (development)
- **Gunicorn**: WSGI server
- **WhiteNoise**: Static file serving

### Frontend
- **Bootstrap 5.3.2**: UI framework
- **Font Awesome 6.4.0**: Icons
- **Google Fonts**: Typography (Poppins & Montserrat)
- **Vanilla JavaScript**: Interactive functionality

### Third-Party APIs
- **Zerodha KiteConnect v4.1.0**: Trading operations
- **Fyers API v3.1.7**: Market data and quotes
- **Google Analytics 4**: User analytics

### Deployment
- **Render.com**: Cloud hosting platform
- **Python-dotenv**: Environment management
- **Pytz**: Timezone handling

## 📊 User Flow & Authentication

### Authentication Process
1. **Initial Access**: Users land on root URL which checks session state
2. **Zerodha Authentication**: 
   - Enter API key and secret
   - Redirect to Zerodha OAuth flow
   - Receive request token and generate access token
3. **Fyers Authentication**:
   - Enter client ID (format: XXXXX-100) and secret
   - Redirect to Fyers OAuth flow
   - Receive auth code and generate access token
4. **Dashboard Access**: Full trading interface with portfolio data

### URL Structure
```
/                           # Smart redirect based on auth state
/zerodha/login/            # Zerodha credentials input
/zerodha/callback/         # Zerodha OAuth callback
/fyers/login/             # Fyers credentials input
/fyers/auth/              # Fyers OAuth redirect
/fyers/callback/          # Fyers OAuth callback
/dashboard/               # Main trading interface
/logout/                  # Session cleanup
```

## 🔧 API Endpoints

### Trading Operations
```http
POST /place_order/        # Place new options order
POST /exit_all/          # Exit all positions
POST /exit_position/     # Exit specific position
GET  /get_index_price/   # Get current index price
```

### Request/Response Format
```json
{
  "success": true,
  "message": "Order placed successfully",
  "order_id": "123456789",
  "error_code": "SUCCESS",
  "suggestion": "Monitor your position"
}
```

## 🎯 Trading Features

### Supported Instruments
- **NIFTY**: Strike interval 50, Lot size 75
- **BANKNIFTY**: Strike interval 100, Lot size 30

### Order Types
- **Market Orders**: Immediate execution at current market price
- **MIS (Margin Intraday Square-off)**: Intraday positions
- **Options**: CE (Call) and PE (Put) options

### Symbol Generation
```python
# Monthly format: <INDEX><YY><MMM><STRIKE><CE|PE>
# Example: NIFTY24JAN19500CE

# Weekly format: <INDEX><YY><M><DD><STRIKE><CE|PE>  
# Example: NIFTY2411519500CE
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Git
- Modern web browser
- Zerodha and Fyers trading accounts

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Quick-Trade
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   BASE_URL=http://127.0.0.1:8000
   GA_MEASUREMENT_ID=your-ga-id
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   Open your browser and go to `http://127.0.0.1:8000`

## 🔐 API Configuration

### Zerodha API Setup

1. **Create Developer Account**
   - Go to [Zerodha Developer Console](https://developers.kite.trade/apps)
   - Click "Create New App"

2. **Configure App Settings**
   - **Type**: Select "Personal"
   - **App Name**: Enter your app name
   - **Zerodha Client ID**: Enter your Zerodha client ID
   - **Redirect URL**: `http://127.0.0.1:8000/zerodha/callback/` (local) or `https://your-domain.com/zerodha/callback/` (production)
   - **Description**: Brief description of your app

3. **Get Credentials**
   - Copy the generated API Key and API Secret

### Fyers API Setup

1. **Create API Account**
   - Go to [Fyers API Dashboard](https://myapi.fyers.in/)
   - Click "Create New App"

2. **Configure App Settings**
   - **App Name**: Enter your app name
   - **Redirect URL**: `http://127.0.0.1:8000/fyers/auth/` (local) or `https://your-domain.com/fyers/auth/` (production)
   - **App Permissions**: Enable all required permissions
   - **Terms**: Accept API usage terms

3. **Get Credentials**
   - Copy the generated Client ID (format: XXXXX-100) and Client Secret

## 🌐 Deployment

### Render.com Deployment

1. **Connect Repository**
   - Link your GitHub repository to Render
   - Configure build settings

2. **Environment Variables**
   ```env
   PYTHON_VERSION=3.11.0
   DJANGO_SETTINGS_MODULE=QuickTradePortal.settings
   SECRET_KEY=<auto-generated>
   DEBUG=False
   WEB_CONCURRENCY=4
   BASE_URL=https://your-app-name.onrender.com
   ```

3. **Build Configuration**
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn QuickTradePortal.wsgi:application`

### Production Considerations

1. **Database Migration**
   ```python
   # settings.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.environ.get('DB_NAME'),
           'USER': os.environ.get('DB_USER'),
           'PASSWORD': os.environ.get('DB_PASSWORD'),
           'HOST': os.environ.get('DB_HOST'),
           'PORT': os.environ.get('DB_PORT'),
       }
   }
   ```

2. **Security Settings**
   ```python
   # settings.py
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_BROWSER_XSS_FILTER = True
   SECURE_CONTENT_TYPE_NOSNIFF = True
   ```

## 🔧 Configuration

### Settings Customization

#### Base Configuration
```python
# QuickTradePortal/settings.py
BASE_URL = os.environ.get('BASE_URL', 'https://your-domain.com')
FYERS_REDIRECT_URL = f"{BASE_URL}/fyers/auth/"
ZERODHA_REDIRECT_URL = f"{BASE_URL}/zerodha/callback/"
```

#### Session Configuration
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_CACHE_ALIAS = 'default'
```

#### Static Files
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## 🛡️ Security Features

### Authentication Security
- **OAuth 2.0**: Secure token-based authentication
- **Session Management**: Secure session storage with cache backend
- **CSRF Protection**: Built-in CSRF token validation
- **Input Validation**: Comprehensive form and API input validation

### Data Security
- **Environment Variables**: Sensitive data stored in environment variables
- **Secure Headers**: Security headers for production deployment
- **HTTPS Enforcement**: SSL/TLS encryption for all communications

### API Security
- **Rate Limiting**: Built-in request throttling
- **Error Handling**: Secure error messages without exposing sensitive data
- **Token Validation**: Regular token validation and refresh

## 📈 Monitoring & Analytics

### Google Analytics Integration
```javascript
// Automatic event tracking
gtag('event', 'login', {
    event_category: 'Authentication',
    event_label: 'Zerodha'
});

gtag('event', 'trade', {
    event_category: 'Trading',
    event_label: 'Order Placement'
});
```

### Error Tracking
- **Django Logging**: Structured logging for debugging
- **User Notifications**: Real-time error notifications
- **Error Parsing**: Detailed error analysis and user guidance

## 🔄 Scalability Roadmap

### Phase 1: Database & User Management
- [ ] Migrate to PostgreSQL
- [ ] Implement Django User model
- [ ] Add user registration and management
- [ ] Encrypt sensitive data

### Phase 2: Performance Optimization
- [ ] Implement Redis caching
- [ ] Add API response caching
- [ ] Optimize database queries
- [ ] Implement connection pooling

### Phase 3: Real-time Features
- [ ] WebSocket integration for live updates
- [ ] Real-time price feeds
- [ ] Live portfolio updates
- [ ] Push notifications

### Phase 4: Advanced Features
- [ ] Celery for background tasks
- [ ] Advanced order types (SL, SL-M)
- [ ] Strategy automation
- [ ] Risk management tools

### Phase 5: Enterprise Features
- [ ] Multi-user support
- [ ] Role-based access control
- [ ] Audit logging
- [ ] API rate limiting

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database status
python manage.py check --database default

# Reset database
python manage.py flush
```

#### API Authentication Issues
- Verify redirect URLs match exactly
- Check API credentials format
- Ensure proper permissions are enabled
- Clear browser cache and cookies

#### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --no-input

# Check static file configuration
python manage.py check --deploy
```

#### Session Issues
```bash
# Clear session data
python manage.py clearsessions

# Check session configuration
python manage.py shell
>>> from django.conf import settings
>>> print(settings.SESSION_ENGINE)
```

### Debug Mode
```python
# Enable debug mode for development
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards
- Follow PEP 8 Python style guide
- Add docstrings to all functions and classes
- Include type hints for function parameters
- Write comprehensive error handling
- Add comments for complex logic

### Testing
```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check this README and inline code comments
- **Issues**: Create an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas

### Community
- **GitHub Issues**: [Report bugs or request features](https://github.com/your-repo/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/your-repo/discussions)

### Professional Support
For enterprise support and custom development:
- **Email**: support@quicktrade.com
- **Documentation**: [https://docs.quicktrade.com](https://docs.quicktrade.com)

## 📊 Project Status

### Current Version
- **Version**: 1.0.0
- **Status**: Production Ready
- **Last Updated**: December 2024

### Roadmap
- **Q1 2025**: Database migration and user management
- **Q2 2025**: Performance optimization and caching
- **Q3 2025**: Real-time features and WebSocket integration
- **Q4 2025**: Advanced trading features and automation

---

**Disclaimer**: This software is for educational and personal use only. Trading involves substantial risk of loss and is not suitable for all investors. Please ensure you understand the risks involved before trading. 