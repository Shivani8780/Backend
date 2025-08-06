#!/usr/bin/env python
"""
Test script to debug static PDF serving on Render
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
from django.contrib.auth import get_user_model

User = get_user_model()

def test_static_pdf_access():
    print("🔍 Testing static PDF access...")
    
    # Check settings
    print(f"\n📁 Settings:")
    print(f"BASE_DIR: {settings.BASE_DIR}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    
    # Check directories
    static_dir = settings.BASE_DIR / 'static' / 'pdfs'
    staticfiles_dir = settings.STATIC_ROOT / 'pdfs'
    
    print(f"\n📂 Directory checks:")
    print(f"Source static/pdfs exists: {static_dir.exists()}")
    print(f"Collected staticfiles/pdfs exists: {staticfiles_dir.exists()}")
    
    if static_dir.exists():
        source_files = list(static_dir.glob('*.pdf'))
        print(f"Source PDF files: {len(source_files)}")
        for f in source_files:
            print(f"  - {f.name}")
    
    if staticfiles_dir.exists():
        collected_files = list(staticfiles_dir.glob('*.pdf'))
        print(f"Collected PDF files: {len(collected_files)}")
        for f in collected_files:
            print(f"  - {f.name}")
    
    # Test database
    print(f"\n📚 Database test:")
    try:
        ebooklets = EBooklet.objects.all()[:3]  # Test first 3
        for ebooklet in ebooklets:
            static_filename = getattr(ebooklet, 'static_pdf_filename', 'NO_FIELD')
            print(f"ID {ebooklet.id}: {ebooklet.name} -> {static_filename}")
            
            if static_filename and static_filename != 'NO_FIELD':
                # Check if file exists in both locations
                source_path = static_dir / static_filename
                collected_path = staticfiles_dir / static_filename
                print(f"  Source exists: {source_path.exists()}")
                print(f"  Collected exists: {collected_path.exists()}")
                
                # Test URL construction
                static_url = f"{settings.STATIC_URL}pdfs/{static_filename}"
                print(f"  Static URL: {static_url}")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # Test user access
    print(f"\n👤 User access test:")
    try:
        users = User.objects.all()[:1]
        if users:
            user = users[0]
            print(f"Test user: {user.username}")
            
            # Check user selections
            from authportal_backend.core.models import UserEBookletSelection
            selections = UserEBookletSelection.objects.filter(user=user, approved=True)[:2]
            print(f"User has {selections.count()} approved selections")
            
            for selection in selections:
                print(f"  Selection: {selection.view_option}")
                for ebooklet in selection.ebooklet.all():
                    print(f"    - {ebooklet.name}")
        else:
            print("No users found")
            
    except Exception as e:
        print(f"❌ User access error: {e}")

if __name__ == '__main__':
    test_static_pdf_access()
