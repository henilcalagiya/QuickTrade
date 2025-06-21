# Quick Trade - Trading Platform

A Django-based trading platform that integrates with Zerodha and Fyers APIs for automated trading.

## Features

- **Multi-Broker Support**: Integration with Zerodha Kite and Fyers APIs
- **Real-time Trading**: Execute trades with real-time market data
- **User Authentication**: Secure login and session management
- **Dashboard**: Comprehensive trading dashboard with portfolio overview
- **Responsive Design**: Modern, mobile-friendly interface

## Technology Stack

- **Backend**: Django 4.2.0
- **Database**: PostgreSQL
- **Static Files**: Django's built-in static file handling

## Prerequisites

- Python 3.8+
- PostgreSQL installed and running
- pip (Python package installer)

## Local Development Setup

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

4. **Set up PostgreSQL database**
   ```bash
   # Create a new PostgreSQL database
   createdb quicktrade_dev
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE quicktrade_dev;
   \q
   ```

5. **Set up environment variables (optional)**
   Create a `.env` file in the root directory:
   ```env
   DB_USER=your_postgres_username
   DB_PASSWORD=your_postgres_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   Open your browser and go to `http://127.0.0.1:8000`

## API Configuration

### Zerodha API Setup

1. Create an account on [Zerodha](https://zerodha.com)
2. Generate API credentials from the Kite developer console
3. Configure redirect URL: `http://127.0.0.1:8000/zerodha/callback/`

### Fyers API Setup

1. Create an account on [Fyers](https://fyers.in)
2. Generate API credentials from the Fyers developer console
3. Configure redirect URL: `http://127.0.0.1:8000/fyers/auth/`

## Security Considerations

- **API Keys**: Never commit API keys to version control
- **Session Security**: Sessions are stored securely in the database
- **Environment Variables**: Use environment variables for sensitive data

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database credentials in environment variables
   - Ensure database `quicktrade_dev` exists

2. **Migration Issues**
   - Make sure PostgreSQL is accessible
   - Check database permissions

3. **Static Files Not Loading**
   - Ensure static files are in the correct directory
   - Check Django's static file configuration

4. **API Authentication Issues**
   - Verify redirect URLs are correctly configured
   - Check API credentials are valid

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section above 