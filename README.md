# Synthetic Data Generation Service

A comprehensive web service for generating synthetic datasets based on client requests. The service provides a complete workflow from request submission to data generation and secure delivery.

## Features

- **Client Portal**: Submit data generation requests with customizable parameters
- **Admin Dashboard**: Manage and process requests with real-time status updates
- **Synthetic Data Generation**: ML-powered generation of various data types
- **Privacy Controls**: Multiple privacy levels with differential privacy techniques
- **Secure Storage**: Local and cloud storage options (AWS S3, Google Cloud, Azure)
- **Authentication**: JWT-based authentication for clients and admins
- **RESTful API**: Complete API for integration with external systems

## Supported Data Types

1. **Health Records**: Patient demographics, vital signs, diagnoses, medications
2. **Financial Data**: Transaction records, account information, credit scores
3. **Sensor Logs**: IoT sensor readings (temperature, humidity, pressure, motion)
4. **Customer Data**: Customer profiles, purchase history, preferences
5. **Research Data**: Scientific datasets with configurable features

## Privacy Levels

- **Low**: Minimal privacy protection, direct identifiers removed
- **Medium**: Moderate protection with noise addition
- **High**: Strong protection with data generalization
- **Maximum**: Maximum protection with heavy noise and generalization

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd synthetic-data-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configuration
nano .env
```

### 3. Database Setup

```bash
# The database will be created automatically on first run
# For production, update DATABASE_URL in .env to use PostgreSQL
```

### 4. Run the Application

```bash
# Start the development server
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## Usage

### 1. Register and Login

- Visit http://localhost:8000
- Register as a client or admin
- Login with your credentials

### 2. Submit a Request (Client)

- Go to "New Request" page
- Select data type, size, and privacy level
- Add optional parameters in JSON format
- Submit the request

### 3. Process Requests (Admin)

- Go to "Admin Panel"
- View all pending requests
- Click "Process Request" to start generation
- Monitor processing status

### 4. Download Data (Client)

- Go to "My Requests" page
- Find completed requests
- Click "Download" to get the generated dataset

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/client` - Register as client
- `POST /api/v1/auth/register/admin` - Register as admin
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user info

### Requests (Client)
- `POST /api/v1/request/` - Create new request
- `GET /api/v1/request/` - Get my requests
- `GET /api/v1/request/{id}` - Get specific request
- `PUT /api/v1/request/{id}` - Update request
- `DELETE /api/v1/request/{id}` - Delete request

### Admin
- `GET /api/v1/admin/requests` - Get all requests
- `GET /api/v1/admin/requests/pending` - Get pending requests
- `POST /api/v1/admin/requests/{id}/process` - Process request
- `GET /api/v1/admin/stats` - Get statistics

### Storage
- `GET /api/v1/storage/download/{id}` - Get download link
- `GET /api/v1/storage/download/{id}/file` - Direct file download

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./synthetic_data.db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `STORAGE_TYPE` | Storage backend (`local`, `s3`) | `local` |
| `LOCAL_STORAGE_PATH` | Local storage directory | `./storage` |
| `AWS_ACCESS_KEY_ID` | AWS access key | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - |
| `S3_BUCKET_NAME` | S3 bucket name | - |

### Storage Options

#### Local Storage
```env
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./storage
```

#### AWS S3
```env
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

## Development

### Project Structure

```
synthetic-data-service/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration settings
├── database.py            # Database connection and session
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── auth_utils.py          # Authentication utilities
├── synthetic_generator.py # Data generation logic
├── storage_manager.py     # Storage abstraction layer
├── routers/               # API route modules
│   ├── auth.py           # Authentication routes
│   ├── requests.py       # Client request routes
│   ├── admin.py          # Admin routes
│   └── storage.py        # Storage routes
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── client_request.html
│   ├── client_requests.html
│   └── admin_requests.html
├── static/               # Static files
│   └── style.css         # Custom styles
└── requirements.txt      # Python dependencies
```

### Adding New Data Types

1. Add new enum value to `DataType` in `models.py`
2. Implement generation method in `synthetic_generator.py`
3. Update frontend templates to include new option

### Adding New Privacy Levels

1. Add new enum value to `PrivacyLevel` in `models.py`
2. Implement privacy transformations in `synthetic_generator.py`
3. Update frontend templates

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup

1. Use PostgreSQL for production database
2. Set strong JWT secret key
3. Configure cloud storage (S3, GCS, or Azure)
4. Set up reverse proxy (nginx)
5. Enable HTTPS
6. Configure monitoring and logging

## Security Considerations

- Change default JWT secret key
- Use HTTPS in production
- Implement rate limiting
- Add input validation
- Regular security updates
- Monitor access logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs`
