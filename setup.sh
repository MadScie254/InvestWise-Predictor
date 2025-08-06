#!/bin/bash

# InvestWise Predictor Setup Script
echo "🚀 Setting up InvestWise Predictor..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Setup Backend
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚙️ Created .env file from template. Please update with your configuration."
fi

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
echo "👤 Creating superuser..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

cd ..

# Setup Frontend
echo "🎨 Setting up Frontend..."
cd frontend

# Install dependencies
npm install

# Build for development
npm run dev

cd ..

echo "✅ Setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Update backend/.env with your database and API keys"
echo "2. Start the backend server: cd backend && python manage.py runserver"
echo "3. Start the frontend server: cd frontend && npm start"
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "📚 For more information, see README.md"
