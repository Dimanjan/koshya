# 🎫 Koshya Voucher System

A comprehensive digital voucher management platform designed for businesses to create, distribute, and track digital vouchers with secure payment processing.

## 🏢 Business Overview

### What is Koshya Voucher System?
Koshya Voucher System is a complete digital voucher solution that allows businesses to:
- **Create digital vouchers** with customizable amounts (Rs 100, 200, 500)
- **Distribute vouchers** to customers with unique codes
- **Process payments** using voucher codes at point of sale
- **Track transactions** with complete audit trails
- **Manage voucher lifecycle** (active, disabled, sold states)

### 🎯 Target Use Cases
- **Restaurants & Cafes**: Gift vouchers, loyalty rewards, promotional offers
- **Retail Stores**: Store credit, gift cards, promotional vouchers
- **Service Businesses**: Prepaid services, membership credits
- **Event Management**: Ticket vouchers, access passes
- **Corporate Gifting**: Employee rewards, client gifts

### 💼 Business Benefits
- **💰 Revenue Generation**: Prepaid vouchers provide immediate cash flow
- **🎁 Customer Retention**: Gift vouchers encourage repeat visits
- **📊 Analytics**: Complete transaction tracking and reporting
- **🔒 Security**: Secure voucher codes prevent fraud
- **📱 Digital First**: No physical cards needed, mobile-friendly
- **⚡ Real-time**: Instant voucher validation and payment processing

## 🌟 Key Features

### 🎫 Voucher Management
- **Create Vouchers**: Generate vouchers with initial balance (Rs 100, 200, 500)
- **Bulk Creation**: Create multiple vouchers at once for efficiency
- **Unique Codes**: Each voucher gets a unique 8-character code
- **Balance Tracking**: Real-time balance updates for all transactions

### 💳 Payment Processing
- **Public Payment API**: Customers can pay using voucher codes
- **Instant Validation**: Real-time balance checking and validation
- **Secure Transactions**: All payments are logged and tracked
- **Multiple Payment Amounts**: Support for any payment amount up to voucher balance

### 🔄 Voucher Lifecycle Management
- **Active Vouchers**: Ready for use, can be recharged or used for payments
- **Disabled Vouchers**: Temporarily disabled, can be re-enabled
- **Sold Vouchers**: Marked as sold, code copied to clipboard
- **Transaction History**: Complete audit trail of all voucher activities

### 👥 User Management
- **Admin Accounts**: Create multiple admin users for different locations
- **Role-based Access**: Admins see only their vouchers, superadmins see all
- **Secure Authentication**: Token-based authentication for API access
- **User Registration**: Easy account creation with simplified password requirements

### 📊 Business Intelligence
- **Real-time Statistics**: Total vouchers, active vouchers, total balance
- **Transaction Reports**: Complete history of all voucher activities
- **Performance Metrics**: Track voucher usage and revenue
- **Audit Trail**: Full compliance and tracking capabilities

## 🚀 Getting Started

### Quick Start (Recommended)
```bash
# 1. Clone the repository
git clone <repository-url>
cd koshya

# 2. Run automated setup
chmod +x setup.sh
./setup.sh

# 3. Start the system
chmod +x start.sh
./start.sh
```

### Access Points
- **🌐 Web Dashboard**: `http://localhost:8000/` - User-friendly interface
- **🔧 Admin Panel**: `http://localhost:8000/admin/` - Django admin interface
- **📡 API Endpoints**: `http://localhost:8000/api/` - Programmatic access

## 💼 Business Workflows

### 1. Creating Vouchers
1. **Login** to the dashboard
2. **Set voucher amount** (Rs 100, 200, or 500)
3. **Choose quantity** (create multiple vouchers at once)
4. **Generate vouchers** with unique codes
5. **Distribute** codes to customers

### 2. Customer Payment Process
1. **Customer provides** voucher code at checkout
2. **Staff enters** code and payment amount
3. **System validates** voucher and balance
4. **Payment processes** instantly if valid
5. **Receipt generated** with remaining balance

### 3. Voucher Management
1. **View all vouchers** in organized tabs (Active, Disabled, Sold)
2. **Recharge vouchers** with additional funds
3. **Disable vouchers** if needed (can be re-enabled)
4. **Mark as sold** when distributed to customers
5. **Track statistics** and performance metrics

## 🛡️ Security & Compliance

### Security Features
- **🔐 Token Authentication**: Secure API access with time-limited tokens
- **👤 Role-based Access**: Admins can only access their own vouchers
- **🛡️ Input Validation**: All inputs are validated and sanitized
- **📝 Audit Logging**: Complete transaction history for compliance
- **🔒 Secure Codes**: Unique voucher codes prevent duplication

### Business Compliance
- **📊 Transaction Tracking**: Every payment and recharge is logged
- **👥 User Management**: Track which admin created which vouchers
- **⏰ Timestamps**: All activities are timestamped for audit purposes
- **🔄 State Management**: Clear voucher states (active, disabled, sold)

## 📈 Business Analytics

### Dashboard Statistics
- **Total Vouchers**: Complete count of all created vouchers
- **Active Vouchers**: Currently usable vouchers
- **Total Balance**: Sum of all active voucher balances
- **Disabled Vouchers**: Temporarily disabled vouchers
- **Sold Vouchers**: Vouchers distributed to customers

### Transaction Insights
- **Payment History**: Complete record of all payments
- **Recharge Activity**: Track when vouchers are topped up
- **Usage Patterns**: Understand customer behavior
- **Revenue Tracking**: Monitor voucher-based revenue

## 🔧 Technical Implementation

### Architecture
- **Backend**: Django REST Framework with SQLite database
- **Frontend**: Modern HTML5/CSS3/JavaScript interface
- **API**: RESTful API with comprehensive documentation
- **Authentication**: Token-based authentication system

### Key Technologies
- **Django 4.2**: Robust web framework
- **Django REST Framework**: API development
- **SQLite**: Lightweight database for development
- **Token Authentication**: Secure API access
- **Role-based Permissions**: Granular access control

## 📚 API Documentation

### Core Endpoints
- **Authentication**: `/api/get-token/` - Get access token
- **Voucher Management**: `/api/vouchers/` - Create and manage vouchers
- **Payment Processing**: `/api/pay/` - Public payment endpoint
- **Statistics**: `/api/statistics/` - Business metrics and analytics

### Integration Examples
```bash
# Create voucher
curl -X POST http://localhost:8000/api/vouchers/ \
  -H "Authorization: Token your-token" \
  -d '{"initial_value": 500}'

# Process payment
curl -X POST http://localhost:8000/api/pay/ \
  -d '{"voucher_code": "ABC12345", "amount": 150.00}'
```

## 🎯 Business Use Cases

### Restaurant Chain
- **Gift Vouchers**: Customers buy vouchers as gifts
- **Loyalty Rewards**: Reward frequent customers
- **Promotional Campaigns**: Special offers and discounts
- **Corporate Catering**: Prepaid meal vouchers for employees

### Retail Store
- **Store Credit**: Return/exchange vouchers
- **Gift Cards**: Digital gift card system
- **Promotional Offers**: Discount vouchers
- **Employee Benefits**: Staff meal vouchers

### Service Business
- **Prepaid Services**: Advance payment for services
- **Membership Credits**: Loyalty program points
- **Gift Certificates**: Service vouchers as gifts
- **Corporate Accounts**: B2B service vouchers

## 📞 Support & Documentation

### Documentation Files
- **📖 API Documentation**: Complete API reference with examples
- **🎨 Frontend Guide**: User interface documentation
- **🧪 Testing Guide**: Comprehensive edge case testing
- **🔧 Setup Guide**: Detailed installation instructions

### Getting Help
- **📚 Documentation**: Comprehensive guides and examples
- **🧪 Testing**: Built-in edge case testing suite
- **🔍 Troubleshooting**: Common issues and solutions
- **📊 Analytics**: Business intelligence and reporting

---

## 🚀 Ready to Start?

1. **Run the setup script** to get started quickly
2. **Access the dashboard** at `http://localhost:8000/`
3. **Create your first vouchers** and start accepting payments
4. **Monitor your business** with real-time analytics

**Koshya Voucher System** - Your complete digital voucher solution! 🎫✨