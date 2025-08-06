# InvestWise-Predictor API Testing Guide

## Quick API Test Commands

### 1. Health Check (Backend Running)
```bash
curl http://localhost:8000/api/health/
```

### 2. User Registration
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 3. User Login
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### 4. Get Predictions (with JWT token)
```bash
curl -X GET http://localhost:8000/api/predictions/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### 5. Create New Prediction
```bash
curl -X POST http://localhost:8000/api/predictions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "symbol": "AAPL",
    "prediction_type": "price",
    "time_horizon": "1M"
  }'
```

### 6. Get Dashboard Statistics
```bash
curl -X GET http://localhost:8000/api/dashboard/stats/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### 7. Get User Investments
```bash
curl -X GET http://localhost:8000/api/investments/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### 8. Create Investment
```bash
curl -X POST http://localhost:8000/api/investments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "symbol": "TSLA",
    "investment_type": "stock",
    "amount": 1000,
    "quantity": 10
  }'
```

### 9. Get Notifications
```bash
curl -X GET http://localhost:8000/api/notifications/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### 10. Submit Feedback
```bash
curl -X POST http://localhost:8000/api/feedback/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "rating": 5,
    "comment": "Great prediction accuracy!",
    "feature": "predictions"
  }'
```

## PowerShell Commands for Windows

Replace `curl` with `Invoke-RestMethod` for PowerShell:

### User Registration (PowerShell)
```powershell
$body = @{
    username = "testuser"
    email = "test@example.com"
    password = "testpass123"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/register/" -Method POST -Body $body -ContentType "application/json"
```

### User Login (PowerShell)
```powershell
$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/login/" -Method POST -Body $loginBody -ContentType "application/json"
$token = $response.access
```

### Get Predictions (PowerShell)
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/predictions/" -Method GET -Headers $headers
```

## Testing Workflow

1. **Start Backend**:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Start Frontend** (new terminal):
   ```bash
   cd frontend
   npm start
   ```

3. **Test API endpoints** using the commands above

4. **Test Frontend** by visiting `http://localhost:3000`

## Expected API Responses

### Successful Registration:
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  },
  "message": "User created successfully"
}
```

### Successful Login:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "testuser"
  }
}
```

### Prediction Response:
```json
{
  "id": 1,
  "symbol": "AAPL",
  "predicted_value": 175.50,
  "confidence": 85,
  "prediction_type": "price",
  "created_at": "2024-01-01T12:00:00Z"
}
```

## Performance Testing

Test with multiple concurrent requests:

```bash
# Install Apache Bench (ab) or use built-in tools
# Test 100 requests with 10 concurrent connections
ab -n 100 -c 10 http://localhost:8000/api/health/
```

This guide will help you verify that all API endpoints are working correctly!
