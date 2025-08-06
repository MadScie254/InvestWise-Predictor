# InvestWise Predictor Setup Script for Windows
Write-Host "🚀 Setting up InvestWise Predictor..." -ForegroundColor Green

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed. Please install Node.js 16 or higher." -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "📦 Setting up Backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment
python -m venv venv
& "venv\Scripts\Activate.ps1"

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "⚙️ Created .env file from template. Please update with your configuration." -ForegroundColor Cyan
}

# Run migrations
Write-Host "🗄️ Running database migrations..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
Write-Host "👤 Creating superuser..." -ForegroundColor Yellow
try {
    python manage.py createsuperuser --noinput --username admin --email admin@example.com
} catch {
    Write-Host "Superuser already exists or creation failed." -ForegroundColor Yellow
}

Set-Location ..

# Setup Frontend
Write-Host "🎨 Setting up Frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install dependencies
npm install

# Build for development
npm run dev

Set-Location ..

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Next steps:" -ForegroundColor Cyan
Write-Host "1. Update backend/.env with your database and API keys"
Write-Host "2. Start the backend server: cd backend && python manage.py runserver"
Write-Host "3. Start the frontend server: cd frontend && npm start"
Write-Host "4. Open http://localhost:3000 in your browser"
Write-Host ""
Write-Host "📚 For more information, see README.md" -ForegroundColor Cyan
