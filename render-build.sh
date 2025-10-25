#!/bin/bash
# Render deployment script for Project Samarth

echo "🚀 Starting Project Samarth deployment on Render..."

# Upgrade pip and install build tools first
echo "📦 Installing build dependencies..."
pip install --upgrade pip
pip install --upgrade setuptools==68.2.2 wheel==0.41.2

# Install dependencies with specific versions
echo "📚 Installing Python packages..."
pip install Flask==2.3.3
pip install Flask-CORS==4.0.0
pip install requests==2.31.0
pip install python-dotenv==1.0.0
pip install gunicorn==21.2.0
pip install python-dateutil==2.8.2
pip install pytz==2023.3

# Install pandas and numpy with pre-compiled wheels
echo "📊 Installing data processing libraries..."
pip install --only-binary=all pandas==1.5.3
pip install --only-binary=all numpy==1.24.3

echo "✅ All dependencies installed successfully!"
echo "🌾 Project Samarth is ready for deployment!"