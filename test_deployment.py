#!/usr/bin/env python3
"""
Test script for Slide Generator API deployment
"""

import requests
import json
import sys

def test_deployment(base_url):
    """Test the deployed API"""
    
    print(f"🧪 Testing deployment at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            data = response.json()
            print(f"   Status: {data['status']}")
            print(f"   Version: {data['version']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Get layouts
    print("\n2. Testing layouts endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/layouts")
        if response.status_code == 200:
            layouts = response.json()
            print(f"✅ Layouts endpoint passed: {layouts}")
        else:
            print(f"❌ Layouts endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Layouts endpoint error: {e}")
    
    # Test 3: Get themes
    print("\n3. Testing themes endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/themes")
        if response.status_code == 200:
            themes = response.json()
            print(f"✅ Themes endpoint passed: {themes}")
        else:
            print(f"❌ Themes endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Themes endpoint error: {e}")
    
    # Test 4: Generate presentation
    print("\n4. Testing presentation generation...")
    try:
        data = {
            "topic": "Test Deployment",
            "num_slides": 3,
            "theme": "modern"
        }
        response = requests.post(f"{base_url}/api/v1/generate", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Presentation generation passed")
            print(f"   Filename: {result['filename']}")
            print(f"   Download URL: {result['download_url']}")
            print(f"   Processing time: {result['processing_time']}s")
            
            # Test 5: Download file
            print("\n5. Testing file download...")
            file_id = result['download_url'].split('/')[-1]
            download_url = f"{base_url}/api/v1/download/{file_id}"
            
            download_response = requests.get(download_url)
            if download_response.status_code == 200:
                print("✅ File download passed")
                print(f"   File size: {len(download_response.content)} bytes")
            else:
                print(f"❌ File download failed: {download_response.status_code}")
                
        else:
            print(f"❌ Presentation generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Presentation generation error: {e}")
    
    # Test 6: API Documentation
    print("\n6. Testing API documentation...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print(f"❌ API documentation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API documentation error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Deployment testing complete!")
    print(f"📚 API Documentation: {base_url}/docs")
    print(f"🔗 Health Check: {base_url}/api/v1/health")
    
    return True

if __name__ == "__main__":
    # Default URL - replace with your actual Render URL
    base_url = "https://slide-generator-ai.onrender.com"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    test_deployment(base_url) 