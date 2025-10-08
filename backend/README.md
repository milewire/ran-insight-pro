# RAN Insight Pro Backend

Advanced RAN (Radio Access Network) analysis and monitoring API built with FastAPI.

## Features

- **KPI Analysis**: Upload and analyze CSV files containing RTWP, SINR, and PRB data
- **Anomaly Detection**: Statistical anomaly detection with configurable thresholds
- **Correlation Analysis**: Advanced correlation analysis between KPI metrics
- **AI Integration**: GPT-powered analysis and insights generation
- **PDF Reporting**: Generate comprehensive PDF reports
- **Firmware Management**: Track and validate firmware versions
- **Health Monitoring**: Comprehensive health checks and monitoring
- **Before/After Comparison**: Compare network performance before and after changes

## Architecture

```
backend/
├── app/
│   ├── routers/          # API endpoints
│   │   ├── analyze.py    # KPI analysis endpoints
│   │   ├── compare.py    # Before/after comparison
│   │   ├── report.py     # PDF report generation
│   │   ├── firmware.py   # Firmware management
│   │   └── health.py     # Health monitoring
│   ├── services/         # Business logic
│   │   ├── parser.py     # CSV parsing and cleaning
│   │   ├── anomaly.py    # Anomaly detection
│   │   ├── correlation.py # Correlation analysis
│   │   ├── ai_summary.py # AI integration
│   │   └── report_gen.py # PDF generation
│   ├── db/              # Database layer
│   │   ├── models.py    # SQLAlchemy models
│   │   └── session.py   # Database session
│   └── utils/           # Utilities
│       ├── logger.py    # Structured logging
│       └── auth.py      # Authentication
├── tests/               # Test files
├── requirements.txt     # Dependencies
├── main.py             # FastAPI application
└── run.py              # Server startup script
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Run the Server**
   ```bash
   python run.py
   ```

4. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Analysis
- `POST /analyze/` - Analyze KPI data from CSV file
- `GET /analyze/{upload_id}` - Get analysis results
- `GET /analyze/` - List all analyses

### Comparison
- `POST /compare/before-after` - Compare before/after data
- `POST /compare/baseline` - Compare with baseline

### Reports
- `GET /report/pdf/{upload_id}` - Generate PDF report
- `GET /report/summary/{upload_id}` - Get report summary
- `GET /report/list` - List all reports

### Firmware
- `GET /firmware/` - List firmware versions
- `POST /firmware/` - Log firmware version
- `GET /firmware/node/{node_id}/history` - Get node firmware history

### Health
- `GET /health/` - Comprehensive health check
- `GET /health/simple` - Simple health check
- `GET /health/history` - Health check history

## Data Processing Pipeline

1. **Upload**: CSV file uploaded via API
2. **Parse**: Data cleaned and standardized
3. **Analyze**: Statistical analysis and anomaly detection
4. **Correlate**: Correlation analysis between metrics
5. **AI Summary**: GPT-powered insights generation
6. **Store**: Results stored in database
7. **Report**: PDF report generation available

## Database Schema

- **uploads**: File upload metadata
- **kpi_data**: Parsed KPI measurements
- **analysis_results**: Analysis results and AI summaries
- **firmware_log**: Firmware version tracking
- **health_checks**: Health monitoring data

## Configuration

Key environment variables:

- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API key for AI analysis
- `SECRET_KEY`: JWT secret key
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Testing

Run basic tests:
```bash
python tests/test_basic.py
```

## Development

The backend uses:
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **Pandas**: Data processing
- **OpenAI**: AI analysis
- **ReportLab**: PDF generation
- **Structlog**: Structured logging

## Production Deployment

For production deployment:

1. Use PostgreSQL instead of SQLite
2. Set up proper authentication
3. Configure CORS for your domain
4. Set up monitoring and logging
5. Use environment variables for secrets
6. Consider using Docker for containerization

## License

This project is part of RAN Insight Pro.
