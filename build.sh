#!/usr/bin/env bash
set -o errexit

echo "🚀 Starting Render deployment build..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files first
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create ebooklets in database
echo "📚 Creating ebooklets in database..."
python manage.py create_ebooklets

# Set up static PDF mappings
echo "🔗 Setting up static PDF mappings..."
python manage.py setup_static_pdfs

# Fix any missing PDF mappings
echo "🔧 Fixing missing PDF mappings..."
python fix_missing_pdfs.py

echo "✅ Build completed successfully!"

# if [[ $CREATE_SUPERUSER ]]; then
#     python manage.py createsuperuser --no-input
# fi
