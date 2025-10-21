#!/bin/bash

# Voucher System Setup Script
echo "🚀 Setting up Voucher System..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser (interactive)
echo "👤 Creating superuser..."
echo "You'll be prompted to create a superuser account."
python manage.py createsuperuser

echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the server: python manage.py runserver"
echo ""
echo "The API will be available at: http://localhost:8000/api/"

