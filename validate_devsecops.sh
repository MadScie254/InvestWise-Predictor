#!/bin/bash

# InvestWise Predictor - DevSecOps Validation Script
# This script validates the security hardening and setup

set -e

echo "🔍 InvestWise Predictor DevSecOps Validation"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo ""
echo "1. Checking repository hygiene..."

# Check for cache files
if [ -z "$(find . -name "__pycache__" -o -name "*.pyc" 2>/dev/null)" ]; then
    print_status 0 "No Python cache files found"
else
    print_status 1 "Python cache files still present"
fi

# Check .gitignore exists
if [ -f ".gitignore" ]; then
    print_status 0 ".gitignore file exists"
else
    print_status 1 ".gitignore file missing"
fi

# Check .env.example exists
if [ -f "backend/.env.example" ]; then
    print_status 0 ".env.example template exists"
else
    print_status 1 ".env.example template missing"
fi

# Check actual .env file doesn't exist
if [ ! -f "backend/.env" ]; then
    print_status 0 "No actual .env file in repository"
else
    print_status 1 "Actual .env file found - should not be committed"
fi

echo ""
echo "2. Checking security configurations..."

# Check for hardcoded secrets in base.py
if grep -q "django-insecure" backend/investwise/settings/base.py; then
    print_status 1 "Hardcoded secret key found in base.py"
else
    print_status 0 "No hardcoded secrets in base.py"
fi

# Check DEBUG default
if grep -q "DEBUG.*False" backend/investwise/settings/base.py; then
    print_status 0 "DEBUG defaults to False"
else
    print_status 1 "DEBUG does not default to False"
fi

echo ""
echo "3. Checking CI/CD pipeline..."

if [ -f ".github/workflows/ci.yml" ]; then
    print_status 0 "CI/CD workflow exists"
else
    print_status 1 "CI/CD workflow missing"
fi

echo ""
echo "4. Checking documentation..."

if [ -f "SECURITY.md" ]; then
    print_status 0 "SECURITY.md exists"
else
    print_status 1 "SECURITY.md missing"
fi

if grep -q "Local Development Setup" README.md; then
    print_status 0 "README.md updated with setup instructions"
else
    print_status 1 "README.md missing setup instructions"
fi

echo ""
echo "5. Checking test configuration..."

if [ -f "backend/pytest.ini" ]; then
    print_status 0 "pytest configuration exists"
else
    print_status 1 "pytest configuration missing"
fi

if grep -q "AuthenticationTestCase" backend/apps/tests.py; then
    print_status 0 "Authentication tests added"
else
    print_status 1 "Authentication tests missing"
fi

echo ""
echo "6. Environment variable validation..."

print_warning "Remember to set these environment variables:"
echo "  - DJANGO_SECRET_KEY (required, minimum 50 characters)"
echo "  - DJANGO_DEBUG (False for production)" 
echo "  - DJANGO_ALLOWED_HOSTS (comma-separated list)"
echo "  - DJANGO_DATABASE_URL (for production PostgreSQL)"

echo ""
echo "7. Quick syntax check..."

# Check Python syntax
cd backend
python -m py_compile manage.py
print_status $? "manage.py syntax check"

python -m py_compile investwise/settings/base.py
print_status $? "base.py syntax check"

python -m py_compile apps/views.py
print_status $? "views.py syntax check"

cd ..

echo ""
echo "🎉 DevSecOps validation complete!"
echo ""
echo "Next steps:"
echo "1. Copy backend/.env.example to backend/.env"
echo "2. Update .env with your actual values"
echo "3. Run: cd backend && python manage.py migrate --settings=investwise.settings.local"
echo "4. Run: cd backend && python manage.py runserver --settings=investwise.settings.local"
echo ""
echo "For production deployment:"
echo "1. Set DJANGO_ENV=production"
echo "2. Ensure all required environment variables are set"
echo "3. Run security audit: bandit -r backend/ && safety check"