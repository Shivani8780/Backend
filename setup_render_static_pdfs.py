#!/usr/bin/env python
"""
Script to set up static PDFs on Render deployment
Run this after deployment to enable static PDF serving
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authportal_backend.deployment_settings')
django.setup()

from django.core.management import call_command
from authportal_backend.core.models import EBooklet

def main():
    print("🚀 Setting up static PDFs for Render deployment...")
    
    try:
        # Step 1: Run migrations
        print("\n1️⃣ Running migrations...")
        call_command('migrate', verbosity=1)
        print("✅ Migrations completed")
        
        # Step 2: Create ebooklets in database
        print("\n2️⃣ Creating ebooklets in database...")
        call_command('create_ebooklets', verbosity=1)
        print("✅ Ebooklets created")
        
        # Step 3: Set up static PDF mappings
        print("\n3️⃣ Setting up static PDF mappings...")
        call_command('setup_static_pdfs', verbosity=1)
        print("✅ Static PDF mappings completed")
        
        # Step 4: Collect static files
        print("\n4️⃣ Collecting static files...")
        call_command('collectstatic', '--noinput', verbosity=1)
        print("✅ Static files collected")
        
        # Step 5: Verify setup
        print("\n5️⃣ Verifying setup...")
        ebooklets_count = EBooklet.objects.count()
        static_pdfs_count = EBooklet.objects.exclude(static_pdf_filename__isnull=True).exclude(static_pdf_filename='').count()
        
        print(f"📊 Total ebooklets: {ebooklets_count}")
        print(f"📊 Ebooklets with static PDFs: {static_pdfs_count}")
        
        if static_pdfs_count > 0:
            print("🎉 Static PDF setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Your PDFs should now be served as static files")
            print("2. Check the frontend - PDF loading should work")
            print("3. Static PDFs will be served from /static/pdfs/ URLs")
        else:
            print("⚠️ Warning: No static PDFs were set up. Check if PDF files exist in static/pdfs/")
            
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
