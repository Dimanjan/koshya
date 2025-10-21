# Koshya Voucher System - Complete API Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Edge Cases & Error Handling](#edge-cases--error-handling)
5. [Rate Limiting & Security](#rate-limiting--security)
6. [Testing](#testing)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Koshya Voucher System provides a comprehensive API for managing digital vouchers with features including:
- **Voucher Management**: Create, recharge, disable, enable, and track vouchers
- **Payment Processing**: Public payment endpoint for voucher-based transactions
- **User Management**: Registration and authentication
- **Transaction History**: Complete audit trail of all voucher activities
- **Role-Based Access**: Admin and superuser permissions

### Base URL
```
http://localhost:8000/api/
```

### Content Type
All requests must include:
```
Content-Type: application/json
```

---

## 🔐 Authentication

### Token-Based Authentication
The API uses Django REST Framework token authentication. Include the token in the Authorization header:

```http
Authorization: Token your_auth_token_here
```

### Getting an Authentication Token

#### Register New User
```http
POST /api/register/
```

**Request Body:**
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
    "message": "User created successfully",
    "user_id": 5,
    "username": "newuser"
}
```

#### Login to Get Token
```http
POST /api/get-token/
```

**Request Body:**
```json
{
    "username": "newuser",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": {
        "id": 5,
        "username": "newuser",
        "email": "user@example.com",
        "is_staff": true,
        "is_superuser": false
    }
}
```

---

## 🚀 API Endpoints

### 1. User Management

#### Register User
```http
POST /api/register/
```
- **Authentication**: None required
- **Description**: Creates a new user account
- **All registered users are automatically granted staff privileges**

#### Get Authentication Token
```http
POST /api/get-token/
```
- **Authentication**: None required
- **Description**: Authenticates user and returns token

### 2. Voucher Management

#### List Vouchers
```http
GET /api/vouchers/
```
- **Authentication**: Required (Token)
- **Description**: Lists all active vouchers for the authenticated user
- **Response**: Array of voucher objects

#### Create Voucher
```http
POST /api/vouchers/
```
- **Authentication**: Required (Token)
- **Description**: Creates a new voucher with initial value

**Request Body:**
```json
{
    "initial_value": 500
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "code": "ABC12345",
    "current_balance": 500.00,
    "total_loaded": 500.00,
    "creator": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_staff": true,
        "is_superuser": true
    },
    "created_at": "2024-01-20T10:30:00Z",
    "updated_at": "2024-01-20T10:30:00Z",
    "transactions": [
        {
            "id": 1,
            "amount": 500.00,
            "transaction_type": "recharge",
            "description": "Initial voucher creation with Rs 500",
            "created_at": "2024-01-20T10:30:00Z"
        }
    ]
}
```

#### Get Voucher Details
```http
GET /api/vouchers/{id}/
```
- **Authentication**: Required (Token)
- **Description**: Retrieves detailed information about a specific voucher

#### Disable Voucher
```http
DELETE /api/vouchers/{id}/
```
- **Authentication**: Required (Token)
- **Description**: Soft disables a voucher (doesn't delete it)

**Response (200 OK):**
```json
{
    "message": "Voucher ABC12345 has been disabled successfully",
    "voucher_code": "ABC12345",
    "disabled_at": "2024-01-20T10:35:00Z"
}
```

#### Enable Voucher
```http
POST /api/vouchers/{id}/enable/
```
- **Authentication**: Required (Token)
- **Description**: Re-enables a previously disabled voucher

#### Mark Voucher as Sold
```http
POST /api/vouchers/{id}/mark-sold/
```
- **Authentication**: Required (Token)
- **Description**: Marks a voucher as sold (copies code to clipboard in frontend)

#### Get Disabled Vouchers
```http
GET /api/vouchers/disabled/
```
- **Authentication**: Required (Token)
- **Description**: Lists all disabled vouchers for the authenticated user

#### Get Sold Vouchers
```http
GET /api/vouchers/sold/
```
- **Authentication**: Required (Token)
- **Description**: Lists all sold vouchers for the authenticated user

### 3. Voucher Operations

#### Recharge Voucher
```http
POST /api/vouchers/{code}/recharge/
```
- **Authentication**: Required (Token)
- **Description**: Adds funds to an existing voucher

**Request Body:**
```json
{
    "amount": 200
}
```

**Valid Amounts**: 100, 200, 500

**Response (200 OK):**
```json
{
    "message": "Voucher ABC12345 recharged with Rs 200",
    "new_balance": 700.00,
    "transaction": {
        "id": 2,
        "amount": 200.00,
        "transaction_type": "recharge",
        "description": "Recharge of Rs 200",
        "created_at": "2024-01-20T10:40:00Z"
    }
}
```

### 4. Public Payment API

#### Make Payment
```http
POST /api/pay/
```
- **Authentication**: None required
- **Description**: Public endpoint for making payments using voucher codes

**Request Body:**
```json
{
    "voucher_code": "ABC12345",
    "amount": 150.50
}
```

**Response (200 OK):**
```json
{
    "message": "Payment of Rs 150.50 successful",
    "voucher_code": "ABC12345",
    "remaining_balance": 349.50,
    "transaction_id": 3
}
```

#### Check Voucher Balance
```http
GET /api/vouchers/<code>/balance/
```
- **Authentication**: None required
- **Description**: Public endpoint to check voucher balance and status

**Response (200 OK) - Active Voucher:**
```json
{
    "voucher_code": "ABC12345",
    "balance": 500.00,
    "status": "active",
    "message": "Voucher is active and ready for use"
}
```

**Response (200 OK) - Disabled Voucher:**
```json
{
    "voucher_code": "ABC12345",
    "balance": 500.00,
    "status": "disabled",
    "message": "Voucher is disabled"
}
```

**Response (200 OK) - Sold Voucher:**
```json
{
    "voucher_code": "ABC12345",
    "balance": 500.00,
    "status": "sold",
    "message": "Voucher has been sold"
}
```

**Response (404 Not Found) - Invalid Voucher:**
```json
{
    "error": "Voucher not found",
    "voucher_code": "INVALID123"
}
```

### 5. Statistics

#### Get Statistics
```http
GET /api/statistics/
```
- **Authentication**: Required (Token)
- **Description**: Returns comprehensive voucher statistics

**Response (200 OK):**
```json
{
    "total_vouchers": 25,
    "active_vouchers": 20,
    "disabled_vouchers": 3,
    "sold_vouchers": 2,
    "total_balance": 12500.00
}
```

---

## ⚠️ Edge Cases & Error Handling

### 1. Payment Edge Cases

#### Insufficient Balance
```json
{
    "voucher_code": "ABC12345",
    "amount": 1000.00
}
```
**Error Response (400 Bad Request):**
```json
{
    "error": "Insufficient balance. Available: Rs 500.00, Required: Rs 1000.00"
}
```

#### Invalid Voucher Code
```json
{
    "voucher_code": "INVALID123",
    "amount": 100.00
}
```
**Error Response (400 Bad Request):**
```json
{
    "error": "Invalid voucher code"
}
```

#### Disabled Voucher Payment
```json
{
    "voucher_code": "DISABLED123",
    "amount": 100.00
}
```
**Error Response (400 Bad Request):**
```json
{
    "error": "Voucher is disabled or sold and cannot be used for payments."
}
```

#### Sold Voucher Payment
```json
{
    "voucher_code": "SOLD123",
    "amount": 100.00
}
```
**Error Response (400 Bad Request):**
```json
{
    "error": "Voucher is disabled or sold and cannot be used for payments."
}
```

#### Negative Payment Amount
```json
{
    "voucher_code": "ABC12345",
    "amount": -100.00
}
```
**Error Response (400 Bad Request):**
```json
{
    "amount": ["Ensure this value is greater than or equal to 0.01."]
}
```

#### Zero Payment Amount
```json
{
    "voucher_code": "ABC12345",
    "amount": 0.00
}
```
**Error Response (400 Bad Request):**
```json
{
    "amount": ["Ensure this value is greater than or equal to 0.01."]
}
```

### 2. Recharge Edge Cases

#### Invalid Recharge Amount
```json
{
    "amount": 999
}
```
**Error Response (400 Bad Request):**
```json
{
    "amount": ["Amount must be 100, 200, or 500"]
}
```

#### Recharge Disabled Voucher
```http
POST /api/vouchers/DISABLED123/recharge/
```
**Error Response (404 Not Found):**
```json
{
    "error": "Voucher not found, disabled, or sold."
}
```

### 3. Authentication Edge Cases

#### Invalid Credentials
```json
{
    "username": "nonexistent",
    "password": "wrongpassword"
}
```
**Error Response (401 Unauthorized):**
```json
{
    "error": "Invalid credentials or insufficient permissions"
}
```

#### Duplicate Username Registration
```json
{
    "username": "existinguser",
    "email": "new@example.com",
    "password": "password123"
}
```
**Error Response (400 Bad Request):**
```json
{
    "error": "Username already exists"
}
```

#### Unauthorized Access
```http
GET /api/vouchers/
# Without Authorization header
```
**Error Response (401 Unauthorized):**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 4. Data Validation Edge Cases

#### Missing Required Fields
```json
{
    "username": "testuser"
    // Missing password
}
```
**Error Response (400 Bad Request):**
```json
{
    "error": "Username and password are required"
}
```

#### Malformed JSON
```json
{
    "username": "testuser",
    "password": "testpass"
    // Missing closing brace
}
```
**Error Response (400 Bad Request):**
```json
{
    "detail": "JSON parse error - Expecting ',' delimiter: line 3 column 1 (char 45)"
}
```

---

## 🛡️ Rate Limiting & Security

### Security Features
1. **Token Authentication**: All protected endpoints require valid tokens
2. **Role-Based Access**: Users can only access their own vouchers (unless superuser)
3. **Input Validation**: All inputs are validated and sanitized
4. **SQL Injection Protection**: Django ORM prevents SQL injection
5. **XSS Protection**: Django's built-in XSS protection
6. **CSRF Protection**: Enabled for all state-changing operations

### Rate Limiting
- **No built-in rate limiting** (can be added with Django REST Framework throttling)
- **Recommended**: Implement rate limiting for production use
- **Suggested limits**:
  - 100 requests per minute per user
  - 10 payment requests per minute per IP
  - 5 registration attempts per minute per IP

### Password Requirements
- **Minimum length**: 8 characters
- **No complexity requirements** (simplified for ease of use)
- **Frontend validation**: Password confirmation handled on client side

---

## 🧪 Testing

### Running Edge Case Tests
```bash
cd test_edge_cases
python test_edge_cases.py
```

### Test Coverage
The edge case tests cover:
- ✅ Insufficient balance payments
- ✅ Invalid voucher codes
- ✅ Disabled/sold voucher payments
- ✅ Negative/zero payment amounts
- ✅ Invalid recharge amounts
- ✅ Duplicate username registration
- ✅ Invalid login credentials
- ✅ Unauthorized access attempts
- ✅ Malformed JSON requests
- ✅ Missing required fields

### Manual Testing Checklist
- [ ] Create voucher with valid amount
- [ ] Recharge voucher with valid amount
- [ ] Make payment with sufficient balance
- [ ] Try payment with insufficient balance
- [ ] Try payment with invalid voucher code
- [ ] Disable voucher and try payment
- [ ] Mark voucher as sold and try payment
- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Try accessing protected endpoints without token

---

## 📝 Examples

### Complete Payment Flow
```bash
# 1. Create voucher
curl -X POST http://localhost:8000/api/vouchers/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your_token_here" \
  -d '{"initial_value": 500}'

# 2. Make payment (public endpoint)
curl -X POST http://localhost:8000/api/pay/ \
  -H "Content-Type: application/json" \
  -d '{"voucher_code": "ABC12345", "amount": 150.50}'

# 3. Check remaining balance
curl -X GET http://localhost:8000/api/vouchers/1/ \
  -H "Authorization: Token your_token_here"
```

### Bulk Voucher Creation
```bash
# Create multiple vouchers
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/vouchers/ \
    -H "Content-Type: application/json" \
    -H "Authorization: Token your_token_here" \
    -d '{"initial_value": 200}'
done
```

### User Registration and Login
```bash
# Register new user
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepass123"
  }'

# Login to get token
curl -X POST http://localhost:8000/api/get-token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepass123"
  }'
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Authentication credentials were not provided"
**Cause**: Missing or invalid Authorization header
**Solution**: Include valid token in Authorization header
```http
Authorization: Token your_token_here
```

#### 2. "Invalid voucher code"
**Cause**: Voucher doesn't exist or is disabled/sold
**Solution**: Check voucher status and ensure it's active

#### 3. "Insufficient balance"
**Cause**: Payment amount exceeds voucher balance
**Solution**: Check voucher balance before making payment

#### 4. "Username already exists"
**Cause**: Trying to register with existing username
**Solution**: Use different username or login with existing account

#### 5. "Voucher not found, disabled, or sold"
**Cause**: Trying to recharge disabled/sold voucher
**Solution**: Enable voucher first or use different voucher

### Debug Mode
Enable debug logging by setting Django's `DEBUG = True` in settings.py for detailed error messages.

### Log Files
Check Django logs for detailed error information:
```bash
# View Django logs
python manage.py runserver --verbosity=2
```

### Health Check
Test API availability:
```bash
curl -X GET http://localhost:8000/api/statistics/ \
  -H "Authorization: Token your_token_here"
```

---

## 📊 API Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required or failed |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

---

## 🔄 API Versioning

Current API version: **v1**
- No versioning implemented yet
- All endpoints are under `/api/`
- Future versions will use `/api/v2/` format

---

## 📞 Support

For issues or questions:
1. Check this documentation first
2. Run the edge case tests
3. Check Django logs for detailed error messages
4. Verify authentication tokens are valid
5. Ensure all required fields are provided

---

*Last updated: January 2024*
*API Version: 1.0*
