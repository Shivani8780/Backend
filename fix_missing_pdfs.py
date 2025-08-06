#!/usr/bin/env python
"""
Quick fix for the 2 missing PDF mappings on Render
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

from authportal_backend.core.models import EBooklet
from django.conf import settings

def main():
    print("🔧 Fixing missing PDF mappings...")
    
    # Fix the 2 missing PDFs
    fixes = [
        {'name': 'B1 Boys', 'filename': 'B1_Boys.pdf'},
        {'name': 'Divorce Girls', 'filename': 'Divorce_Girls.pdf'}
    ]
    
    for fix in fixes:
        try:
            ebooklet = EBooklet.objects.get(name=fix['name'])
            
            # Check if the PDF file exists
            static_pdf_path = os.path.join(settings.BASE_DIR, 'static', 'pdfs', fix['filename'])
            if os.path.exists(static_pdf_path):
                ebooklet.static_pdf_filename = fix['filename']
                ebooklet.save()
                print(f"✅ Fixed: {fix['name']} -> {fix['filename']}")
            else:
                print(f"❌ File not found: {static_pdf_path}")
                
        except EBooklet.DoesNotExist:
            print(f"❌ Ebooklet not found: {fix['name']}")
    
    # Verify all mappings
    print("\n📊 Final status:")
    ebooklets = EBooklet.objects.all()
    mapped_count = 0
    
    for ebooklet in ebooklets:
        static_filename = getattr(ebooklet, 'static_pdf_filename', None)
        if static_filename:
            mapped_count += 1
            print(f"✅ {ebooklet.name} -> {static_filename}")
        else:
            print(f"❌ {ebooklet.name} -> NO MAPPING")
    
    print(f"\n🎯 Result: {mapped_count}/{ebooklets.count()} PDFs mapped")
    
    if mapped_count == ebooklets.count():
        print("🎉 All PDFs are now mapped! Static PDF serving should work.")
    else:
        print("⚠️ Some PDFs still missing. Check file names and paths.")

if __name__ == '__main__':
    main()
