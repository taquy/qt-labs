# Qt Stock Analysis

A web application for analyzing and tracking stock data with real-time updates and interactive visualizations.

## Features

- Real-time stock data updates using Server-Sent Events (SSE)
- Interactive stock comparison charts
- Stock list management with add/remove functionality
- Export data to CSV and PDF formats
- User authentication system
- PostgreSQL database for data storage
- Docker support for easy deployment

## Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd qt-stock-analysis
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required Python packages:
```bash
pip install -r requirements.txt
```

4. Set up the database using Docker:
```bash
# Start PostgreSQL container
docker-compose up -d

# Install Flask-Migrate for database management
pip install Flask-Migrate

# Initialize database migrations
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration to create database tables
flask db upgrade
```

## Configuration

The application uses the following default configuration (can be modified in `config.py`):

- Database: PostgreSQL
  - Database name: qtstock
  - Username: qtstock
  - Password: qtstock123
  - Host: localhost
  - Port: 5432

- Admin user:
  - Username: admin
  - Password: admin123

## Environment Variables

The application uses environment variables for configuration. A sample `.env.example` file is provided with the following sections:

- **Flask Configuration**: Basic Flask app settings
- **Database Configuration**: Database connection settings
- **Admin User Configuration**: Default admin credentials
- **API Configuration**: Rate limiting and timeout settings
- **Stock Data Configuration**: Cache and request limits
- **Logging Configuration**: Log level and file settings
- **CORS Configuration**: Allowed origins for cross-origin requests

To set up your environment:
1. Copy `.env.example` to `.env`
2. Update the values in `.env` with your configuration
3. Never commit your actual `.env` file to version control

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Log in using the default admin credentials:
- Username: admin
- Password: admin123

## Project Structure

```
qt-stock-analysis/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models.py           # Database models
├── scrape.py           # Stock data scraping module
├── get_stock_lists.py  # Stock list management
├── templates/          # HTML templates
│   ├── index.html     # Main application page
│   └── login.html     # Login page
├── static/            # Static files (CSS, JS)
├── migrations/        # Database migrations
└── docker-compose.yml # Docker configuration
```

## Database Schema

### User Table
- id (Primary Key)
- username (Unique)
- password_hash

### Stock Table
- id (Primary Key)
- symbol (Unique)
- name
- last_updated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 