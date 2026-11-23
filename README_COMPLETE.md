The application that runs is in `web`. This note describes an earlier draft and is not the current system.

# InvestWise-Predictor: an earlier draft

A comprehensive, production-ready AI-powered investment prediction platform built with FastAPI, Next.js, and advanced MLOps infrastructure.

## 📋 Overview

InvestWise-Predictor is a full-stack financial prediction system that leverages machine learning to provide investment insights for the Kenyan market. The system includes a FastAPI backend, ML microservice, Next.js frontend, complete CI/CD pipeline, and Kubernetes deployment infrastructure.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   ML Service   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (FastAPI)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │    MLflow       │
│   Database      │    │    Cache        │    │   Tracking      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ Features

### 🤖 Machine Learning
- **Multiple Algorithms**: LightGBM, XGBoost, Random Forest, Linear Regression
- **Feature Engineering**: Lag features, moving averages, interaction terms
- **Model Explainability**: SHAP values for prediction interpretability
- **Experiment Tracking**: MLflow for model versioning and management
- **Automated Training**: Scheduled retraining with performance monitoring

### 🔐 Security & Authentication
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Redis-based API rate limiting
- **Input Validation**: Comprehensive data validation with Pydantic
- **CORS Protection**: Configurable cross-origin resource sharing

### 📊 Data Processing
- **Real-time Predictions**: Fast API endpoints for investment predictions
- **Data Validation**: Robust input validation and error handling
- **Feature Preprocessing**: Automated data cleaning and transformation
- **Market Data Management**: CRUD operations for financial indicators

### 🚀 DevOps & Infrastructure
- **Containerization**: Docker multi-stage builds for all services
- **Orchestration**: Kubernetes deployment with Helm charts
- **CI/CD**: GitHub Actions with automated testing and deployment
- **Infrastructure as Code**: Terraform for AWS infrastructure
- **Monitoring**: Prometheus metrics and health checks

## 📁 Project Structure

```
InvestWise-Predictor/
├── 🔧 Infrastructure & DevOps
│   ├── .github/workflows/          # CI/CD pipelines
│   ├── infrastructure/terraform/   # Infrastructure as Code
│   ├── k8s/helm/                  # Kubernetes Helm charts
│   └── ml/orchestrator/           # Prefect workflow orchestration
│
├── 🐍 Backend Services
│   ├── backend/                   # FastAPI main application
│   │   ├── app/                   # Application code
│   │   │   ├── api/v1/           # API endpoints
│   │   │   ├── core/             # Configuration & security
│   │   │   ├── db/               # Database models & CRUD
│   │   │   └── utils/            # Utilities & helpers
│   │   ├── tests/                # Comprehensive test suite
│   │   └── alembic/              # Database migrations
│   │
│   └── ml_service/               # ML microservice
│       ├── app/                  # ML service code
│       │   ├── models/           # Model loading & management
│       │   └── explainers/       # SHAP explanations
│       └── tests/                # ML service tests
│
├── 🧠 Machine Learning
│   └── ml/
│       ├── training/             # Model training pipeline
│       │   ├── train.py          # Main training script
│       │   └── data_utils.py     # Data processing utilities
│       └── orchestrator/         # Workflow orchestration
│
├── 🎨 Frontend
│   └── frontend/                 # Next.js application
│       ├── src/                  # Source code
│       │   ├── app/              # App router pages
│       │   ├── components/       # Reusable components
│       │   └── lib/              # Utilities & configurations
│       └── tests/                # Frontend tests
│
└── 📊 Data
    ├── raw/                      # Raw CSV data files
    ├── processed/                # Processed features
    └── cleaned/                  # Cleaned datasets
```

## 🚦 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/InvestWise-Predictor.git
cd InvestWise-Predictor

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 2. Generate Sample Data

```bash
# Generate realistic sample data for training and testing
python scripts/generate_sample_data.py
```

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. ML Service Setup

```bash
# Navigate to ML service directory
cd ml_service

# Install dependencies
pip install -r requirements.txt

# Train initial models
cd ../ml/training
python train.py

# Start ML service
cd ../../ml_service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 6. Docker Deployment

```bash
# Build and run all services
docker-compose up --build

# Or run in production mode
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/investwise_db
POSTGRES_USER=investwise_user
POSTGRES_PASSWORD=investwise_password
POSTGRES_DB=investwise_db

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Service
ML_SERVICE_URL=http://localhost:8001
MLFLOW_TRACKING_URI=http://localhost:5000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret

# AWS (for production)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-west-2
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

### ML Service Tests

```bash
cd ml_service
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:e2e  # End-to-end tests
```

### Integration Tests

```bash
# Run all tests
python test_complete_functionality.py
```

## 📊 API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info

### Prediction Endpoints

- `POST /api/v1/predict/` - Make prediction
- `POST /api/v1/predict/explain` - Get prediction explanation
- `GET /api/v1/predict/history` - Get prediction history

### Data Management

- `GET /api/v1/data/market` - Get market data
- `POST /api/v1/data/market` - Add market data
- `GET /api/v1/metrics` - Get system metrics

### Health Checks

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system health

## 🚀 Deployment

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
cd k8s/helm/investwise
helm install investwise . -f values.yaml

# Or use terraform for infrastructure
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### AWS Deployment

1. **Infrastructure Setup**:
   ```bash
   cd infrastructure/terraform
   terraform init
   terraform apply
   ```

2. **Container Deployment**:
   ```bash
   # Build and push images
   docker build -t your-registry/investwise-backend backend/
   docker build -t your-registry/investwise-ml-service ml_service/
   docker build -t your-registry/investwise-frontend frontend/
   
   # Deploy to EKS
   kubectl apply -f k8s/
   ```

3. **CI/CD Setup**:
   - Configure GitHub Actions secrets
   - Push to main branch triggers deployment

## 📈 Monitoring & Observability

### Metrics Available

- **API Metrics**: Request rate, latency, errors
- **ML Metrics**: Prediction accuracy, model performance
- **System Metrics**: CPU, memory, disk usage
- **Business Metrics**: User registrations, predictions made

### Monitoring Stack

- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **MLflow**: ML experiment tracking
- **CloudWatch**: AWS infrastructure monitoring

## 🔒 Security Features

- **Authentication**: JWT-based user authentication
- **Authorization**: Role-based access control
- **Input Validation**: Comprehensive data validation
- **Rate Limiting**: API rate limiting with Redis
- **HTTPS**: SSL/TLS encryption
- **Secret Management**: AWS Secrets Manager integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Development Team**: InvestWise Engineers
- **ML Team**: Data Scientists & ML Engineers
- **DevOps Team**: Infrastructure & Platform Engineers

## 🆘 Support

For support, email support@investwise.com or create an issue on GitHub.

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Architecture Guide](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guide](CONTRIBUTING.md)

---

⭐ **Star this repository if you find it helpful!**

Built with ❤️ by the InvestWise Team