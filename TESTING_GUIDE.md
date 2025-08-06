# InvestWise-Predictor Testing Guide

## 🧪 Testing the Complete Functionality

### Prerequisites
Before testing, ensure you have:
- Python 3.8+ installed
- Node.js 16+ installed
- PostgreSQL or SQLite for database
- Redis (optional, for caching)

## 🚀 Quick Start Testing

### 1. Backend Setup & Testing

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser

# Start the Django development server
python manage.py runserver
```

The backend should now be running at `http://localhost:8000`

### 2. Frontend Setup & Testing

```bash
# Navigate to frontend directory (open new terminal)
cd frontend

# Install dependencies
npm install

# Start the React development server
npm start
```

The frontend should now be running at `http://localhost:3000`

## 🔧 Testing Individual Components

### Backend API Testing

#### 1. Test Authentication Endpoints
```bash
# Test user registration
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# Test user login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

#### 2. Test Prediction Endpoints (with JWT token)
```bash
# Create a prediction (replace YOUR_JWT_TOKEN)
curl -X POST http://localhost:8000/api/v1/predictions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "symbol": "AAPL",
    "prediction_type": "price",
    "time_horizon": "1M"
  }'

# Get predictions
curl -X GET http://localhost:8000/api/v1/predictions/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get prediction analytics
curl -X GET http://localhost:8000/api/v1/predictions/analytics/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3. Test Investment Endpoints
```bash
# Add an investment
curl -X POST http://localhost:8000/api/v1/investments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "investment_type": "stock",
    "shares": 10,
    "purchase_price": 150.00
  }'

# Get investments
curl -X GET http://localhost:8000/api/v1/investments/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Frontend Component Testing

#### 1. Manual UI Testing Checklist

**Authentication Flow:**
- [ ] Register new user with validation
- [ ] Login with correct credentials
- [ ] Login with incorrect credentials (should fail)
- [ ] Logout functionality
- [ ] Token persistence across page refreshes

**Dashboard:**
- [ ] Dashboard loads with stats cards
- [ ] Charts render correctly
- [ ] Recent predictions display
- [ ] Navigation menu works

**Predictions:**
- [ ] Create new prediction form
- [ ] Prediction form validation
- [ ] Prediction list displays correctly
- [ ] Prediction filtering works
- [ ] Prediction analytics charts

**Investments:**
- [ ] Add new investment modal
- [ ] Investment form validation
- [ ] Investment table displays
- [ ] Gain/loss calculations
- [ ] Delete investment functionality

**Profile:**
- [ ] Profile information loads
- [ ] Profile update functionality
- [ ] Form validation

**Notifications:**
- [ ] Notifications display
- [ ] Mark as read functionality
- [ ] Mark all as read
- [ ] Delete notifications

**Feedback:**
- [ ] Submit feedback form
- [ ] Form validation
- [ ] Feedback history display
- [ ] Rating system

#### 2. Browser Testing
Test in multiple browsers:
- Chrome
- Firefox
- Safari
- Edge

#### 3. Responsive Testing
Test on different screen sizes:
- Desktop (1920x1080)
- Tablet (768x1024)
- Mobile (375x667)

## 🎯 Specific Feature Testing

### AI Prediction System
1. **Test Different Prediction Types:**
   - Price predictions for various symbols
   - Trend analysis (Bullish/Bearish/Neutral)
   - Volatility assessments
   - Risk evaluations

2. **Test Time Horizons:**
   - 1 Day predictions
   - 1 Week predictions
   - 1 Month predictions
   - 3 Month predictions
   - 1 Year predictions

3. **Verify Confidence Scores:**
   - Check confidence percentages (should be 60-95%)
   - Verify confidence calculation logic

### Portfolio Management
1. **Investment Tracking:**
   - Add various investment types (stock, bond, ETF, crypto)
   - Test gain/loss calculations
   - Verify current value updates

2. **Portfolio Analytics:**
   - Test diversification scoring
   - Check portfolio value calculations
   - Verify investment type distribution

### Real-time Features
1. **Live Updates:**
   - Test notification updates
   - Check dashboard refresh
   - Verify prediction status changes

## 🔍 Error Testing

### Backend Error Handling
1. **Authentication Errors:**
   - Invalid credentials
   - Expired tokens
   - Missing authorization headers

2. **Validation Errors:**
   - Invalid data formats
   - Missing required fields
   - Invalid stock symbols

3. **Database Errors:**
   - Duplicate entries
   - Foreign key constraints
   - Invalid queries

### Frontend Error Handling
1. **Network Errors:**
   - API connection failures
   - Timeout errors
   - Invalid responses

2. **User Input Errors:**
   - Form validation
   - Invalid file uploads
   - Cross-site scripting prevention

## 🧪 Automated Testing

### Backend Unit Tests
```bash
# Run Django tests
cd backend
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend Unit Tests
```bash
# Run React tests
cd frontend
npm test

# Run with coverage
npm test -- --coverage
```

### Integration Tests
```bash
# Test API endpoints
cd backend
python manage.py test apps.tests.test_api

# Test authentication flow
python manage.py test apps.tests.test_auth
```

## 📊 Performance Testing

### Load Testing
1. **API Performance:**
   - Test concurrent prediction requests
   - Measure response times
   - Check database query efficiency

2. **Frontend Performance:**
   - Page load times
   - Bundle size optimization
   - Memory usage monitoring

### Database Performance
```bash
# Check query performance
python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)
```

## 🔐 Security Testing

### Authentication Security
1. **JWT Token Validation:**
   - Token expiration handling
   - Invalid token rejection
   - Token refresh mechanism

2. **Password Security:**
   - Password strength requirements
   - Password hashing verification
   - Brute force protection

### API Security
1. **Input Validation:**
   - SQL injection prevention
   - XSS protection
   - CSRF token validation

2. **Access Control:**
   - User data isolation
   - Admin privilege separation
   - Resource authorization

## 📱 Mobile Testing

### Responsive Design
1. **Layout Testing:**
   - Navigation menu collapse
   - Table responsive behavior
   - Form field adaptation

2. **Touch Interactions:**
   - Button tap targets
   - Swipe gestures
   - Pinch-to-zoom handling

## 🎨 UI/UX Testing

### Visual Testing
1. **Design Consistency:**
   - Color scheme adherence
   - Typography consistency
   - Icon alignment

2. **Animation Testing:**
   - Smooth transitions
   - Loading states
   - Hover effects

### Accessibility Testing
1. **WCAG Compliance:**
   - Keyboard navigation
   - Screen reader compatibility
   - Color contrast ratios

## 📈 Analytics Testing

### Dashboard Metrics
1. **Data Accuracy:**
   - Prediction statistics
   - Portfolio calculations
   - Performance metrics

2. **Chart Functionality:**
   - Chart.js rendering
   - Data point accuracy
   - Interactive features

## 🛠️ Development Testing

### Code Quality
```bash
# Backend linting
cd backend
flake8 .
black .

# Frontend linting
cd frontend
npm run lint
npm run format
```

### Build Testing
```bash
# Frontend production build
cd frontend
npm run build

# Check build size
npm run analyze
```

## 🚀 Deployment Testing

### Environment Testing
1. **Development Environment:**
   - Local database connection
   - Debug mode functionality
   - Hot reload testing

2. **Production Environment:**
   - Production database connection
   - Static file serving
   - HTTPS configuration

### Docker Testing
```bash
# Build Docker containers
docker-compose build

# Run containers
docker-compose up

# Test container communication
docker-compose exec web python manage.py test
```

## 📋 Testing Checklist

### Pre-deployment Checklist
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Security tests pass
- [ ] Performance tests pass
- [ ] UI/UX tests pass
- [ ] Mobile responsive tests pass
- [ ] Cross-browser tests pass
- [ ] API documentation complete
- [ ] Error handling verified
- [ ] Production configuration tested

### Post-deployment Checklist
- [ ] Production database migrations
- [ ] Static files served correctly
- [ ] SSL certificates working
- [ ] API endpoints accessible
- [ ] User registration working
- [ ] Email notifications working
- [ ] Backup systems functional
- [ ] Monitoring systems active

---

## 🎉 Testing Success Criteria

Your InvestWise-Predictor is considered fully functional when:

✅ Users can register and authenticate successfully  
✅ AI predictions generate with confidence scores  
✅ Portfolio management tracks investments accurately  
✅ Dashboard displays real-time analytics  
✅ All API endpoints respond correctly  
✅ Frontend components render without errors  
✅ Mobile responsiveness works across devices  
✅ Error handling prevents crashes  
✅ Security measures protect user data  
✅ Performance meets acceptable standards  

**Happy Testing!** 🚀
