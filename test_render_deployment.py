#!/usr/bin/env python
"""
Test script to verify Render deployment is working correctly
Run this on your deployed Render instance to debug the 500 error
"""
import requests
import json

# Replace with your actual Render backend URL
BACKEND_URL = "https://auth-ebooklet-backend.onrender.com"

def test_endpoints():
    print("🔍 Testing Render deployment endpoints...")
    
    # Test basic connectivity
    print(f"\n1. Testing basic connectivity to {BACKEND_URL}")
    try:
        response = requests.get(f"{BACKEND_URL}/api/ebooklets/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} ebooklets")
            for ebooklet in data[:3]:  # Show first 3
                print(f"     - ID {ebooklet['id']}: {ebooklet['name']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Connection error: {e}")
    
    # Test debug endpoint (requires login)
    print(f"\n2. Testing debug endpoint (you'll need to be logged in)")
    print(f"   Visit: {BACKEND_URL}/api/ebooklet/1/pdf-debug/")
    print(f"   This will show detailed debug info about static PDF setup")
    
    # Test static file access
    print(f"\n3. Testing static file access")
    static_urls = [
        f"{BACKEND_URL}/static/pdfs/B1_Boys.pdf",
        f"{BACKEND_URL}/static/pdfs/Divorce_Girls.pdf",
        f"{BACKEND_URL}/static/pdfs/B3 Boys.pdf"
    ]
    
    for url in static_urls:
        try:
            response = requests.head(url, timeout=10)
            print(f"   {url}")
            print(f"     Status: {response.status_code}")
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'unknown')
                content_length = response.headers.get('content-length', 'unknown')
                print(f"     Content-Type: {content_type}")
                print(f"     Content-Length: {content_length}")
            else:
                print(f"     Error: Not accessible")
        except Exception as e:
            print(f"     Connection error: {e}")
    
    print(f"\n4. Manual testing steps:")
    print(f"   a) Login to your frontend")
    print(f"   b) Try to view a PDF")
    print(f"   c) Check browser console for detailed error messages")
    print(f"   d) Visit debug endpoint: {BACKEND_URL}/api/ebooklet/1/pdf-debug/")
    
    print(f"\n5. If PDFs still don't work, run these on Render:")
    print(f"   python test_static_pdf.py")
    print(f"   python debug_static_pdfs.py")

if __name__ == '__main__':
    test_endpoints()
