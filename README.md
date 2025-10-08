# RAN Insight Pro

A comprehensive Radio Access Network (RAN) analysis and monitoring platform with advanced KPI analysis, anomaly detection, and AI-powered insights.

## 🚀 Features

### Frontend (Next.js)
- **Modern UI**: Built with Next.js 15, React 19, and Tailwind CSS
- **Interactive Dashboards**: Real-time KPI visualization with Recharts
- **File Upload**: Drag-and-drop CSV file upload interface
- **Responsive Design**: Mobile-first responsive design
- **Dark/Light Mode**: Theme switching support
- **Component Library**: Comprehensive UI components with Radix UI

### Backend (FastAPI)
- **KPI Analysis**: Upload and analyze CSV files containing RTWP, SINR, and PRB data
- **Anomaly Detection**: Statistical anomaly detection with configurable thresholds
- **Correlation Analysis**: Advanced correlation analysis between KPI metrics
- **AI Integration**: GPT-powered analysis and insights generation
- **PDF Reporting**: Generate comprehensive PDF reports
- **Firmware Management**: Track and validate firmware versions
- **Health Monitoring**: Comprehensive health checks and monitoring
- **Before/After Comparison**: Compare network performance before and after changes

## 🏗️ Architecture

```
ran-insight-pro/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   ├── ai-findings.tsx   # AI insights component
│   ├── file-upload.tsx   # File upload component
│   ├── kpi-chart.tsx     # KPI visualization
│   └── theme-provider.tsx # Theme management
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic
│   │   ├── db/         # Database layer
│   │   └── utils/      # Utilities
│   ├── tests/          # Test files
│   ├── requirements.txt # Python dependencies
│   └── main.py         # FastAPI application
├── hooks/              # Custom React hooks
├── lib/               # Utility libraries
└── public/            # Static assets
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ran-insight-pro
```

### 2. Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```
The frontend will be available at http://localhost:3000

### 3. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env
# Edit .env with your configuration

# Start the server
python main.py
```
The backend API will be available at http://localhost:8000

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📊 Data Processing Pipeline

1. **Upload**: CSV file uploaded via the web interface
2. **Parse**: Data cleaned and standardized by the backend
3. **Analyze**: Statistical analysis and anomaly detection
4. **Correlate**: Correlation analysis between metrics
5. **AI Summary**: GPT-powered insights generation
6. **Store**: Results stored in SQLite database
7. **Visualize**: Interactive charts and dashboards
8. **Report**: PDF report generation available

## 🔧 Configuration

### Frontend Environment Variables
Create a `.env.local` file in the root directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Environment Variables
Edit the `.env` file in the backend directory:
```env
DATABASE_URL=sqlite:///./ran_insight.db
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
LOG_LEVEL=INFO
```

## 📁 Project Structure

### Frontend Components
- **File Upload**: Handles CSV file uploads with validation
- **KPI Charts**: Interactive visualizations using Recharts
- **AI Findings**: Displays AI-generated insights
- **Theme Provider**: Manages dark/light mode switching

### Backend Services
- **Parser Service**: CSV parsing and data cleaning
- **Anomaly Service**: Statistical anomaly detection
- **Correlation Service**: Advanced correlation analysis
- **AI Summary Service**: GPT-powered insights
- **Report Generator**: PDF report creation

## 🧪 Testing

### Frontend Testing
```bash
npm run lint
npm run build
```

### Backend Testing
```bash
cd backend
python tests/test_basic.py
```

## 🚀 Deployment

### Frontend (Vercel)
The frontend is configured for Vercel deployment:
```bash
npm run build
# Deploy to Vercel
```

### Backend (Production)
For production deployment:
1. Use PostgreSQL instead of SQLite
2. Set up proper authentication
3. Configure CORS for your domain
4. Set up monitoring and logging
5. Use environment variables for secrets
6. Consider using Docker for containerization

## 🛠️ Development

### Tech Stack
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11+, SQLAlchemy
- **Database**: SQLite (development), PostgreSQL (production)
- **AI**: OpenAI GPT integration
- **Charts**: Recharts
- **UI Components**: Radix UI
- **Styling**: Tailwind CSS

### Available Scripts
```bash
# Frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint

# Backend
python main.py       # Start FastAPI server
python run.py        # Alternative startup script
```

## 📝 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints
- `POST /analyze/` - Analyze KPI data
- `GET /analyze/{upload_id}` - Get analysis results
- `POST /compare/before-after` - Compare datasets
- `GET /report/pdf/{upload_id}` - Generate PDF report
- `GET /health/` - Health check

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of RAN Insight Pro. All rights reserved.

## 🆘 Support

For support and questions:
- Check the API documentation at http://localhost:8000/docs
- Review the backend README in the `backend/` directory
- Open an issue in the repository

---

**RAN Insight Pro** - Advanced RAN analysis and monitoring platform
