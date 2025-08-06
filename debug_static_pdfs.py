#!/usr/bin/env python
"""
Debug script to check static PDF setup on Render
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

from django.conf import settings
from authportal_backend.core.models import EBooklet

def main():
    print("🔍 Debugging static PDF setup...")
    
    # Check Django settings
    print(f"\n📁 BASE_DIR: {settings.BASE_DIR}")
    print(f"📁 STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"📁 STATIC_URL: {settings.STATIC_URL}")
    print(f"📁 STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    
    # Check if static/pdfs directory exists
    static_pdfs_dir = settings.BASE_DIR / 'static' / 'pdfs'
    print(f"\n📂 Static PDFs directory: {static_pdfs_dir}")
    print(f"📂 Directory exists: {static_pdfs_dir.exists()}")
    
    if static_pdfs_dir.exists():
        pdf_files = list(static_pdfs_dir.glob('*.pdf'))
        print(f"📄 PDF files found: {len(pdf_files)}")
        for pdf_file in pdf_files:
            print(f"   - {pdf_file.name}")
    
    # Check database
    try:
        ebooklets = EBooklet.objects.all()
        print(f"\n📚 Total ebooklets in database: {ebooklets.count()}")
        
        for ebooklet in ebooklets:
            static_filename = getattr(ebooklet, 'static_pdf_filename', 'FIELD_NOT_EXISTS')
            print(f"   - ID {ebooklet.id}: {ebooklet.name} -> {static_filename}")
            
            if static_filename and static_filename != 'FIELD_NOT_EXISTS':
                static_file_path = static_pdfs_dir / static_filename
                file_exists = static_file_path.exists() if static_pdfs_dir.exists() else False
                print(f"     File exists: {file_exists}")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # Check staticfiles directory
    staticfiles_dir = settings.STATIC_ROOT / 'pdfs'
    print(f"\n📂 Staticfiles PDFs directory: {staticfiles_dir}")
    print(f"📂 Directory exists: {staticfiles_dir.exists()}")
    
    if staticfiles_dir.exists():
        collected_pdfs = list(staticfiles_dir.glob('*.pdf'))
        print(f"📄 Collected PDF files: {len(collected_pdfs)}")
        for pdf_file in collected_pdfs:
            print(f"   - {pdf_file.name}")

if __name__ == '__main__':
    main()
