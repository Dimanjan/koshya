#!/bin/bash

# Start Development Server Script
echo "🚀 Starting Voucher System..."

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Start Django development server
echo "🌐 Starting Django development server..."
echo "API will be available at: http://localhost:8000/api/"
echo "Admin panel at: http://localhost:8000/admin/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver

