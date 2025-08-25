#!/usr/bin/env python3
"""
Enhanced API Test Script
Tests all new features: topic data, image generation, different layouts
"""

import requests
import json
import time

BASE_URL = "https://slide-generator-ai.onrender.com/api/v1"

def test_basic_endpoints():
    """Test basic API endpoints"""
    print("🧪 Testing Basic Endpoints")
    print("=" * 50)
    
    # Health check
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health Check: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data['status']}")
        print(f"   Version: {data['version']}")
    
    # Layouts
    response = requests.get(f"{BASE_URL}/layouts")
    print(f"✅ Layouts: {response.status_code}")
    if response.status_code == 200:
        layouts = response.json()
        print(f"   Available: {layouts}")
    
    # Themes
    response = requests.get(f"{BASE_URL}/themes")
    print(f"✅ Themes: {response.status_code}")
    if response.status_code == 200:
        themes = response.json()
        print(f"   Available: {themes}")

def test_topic_data_endpoints():
    """Test topic data endpoints"""
    print("\n📚 Testing Topic Data Endpoints")
    print("=" * 50)
    
    # Available topics
    response = requests.get(f"{BASE_URL}/topics")
    print(f"📋 Available Topics: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Topics: {data.get('topics', [])}")
        print(f"   Total: {data.get('total_topics', 0)}")
    
    # Specific topic data
    topics_to_test = ["ai", "machine_learning", "cloud_computing", "business_strategy"]
    for topic in topics_to_test:
        response = requests.get(f"{BASE_URL}/topics/{topic}")
        print(f"📊 {topic.title()} Data: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Title: {data['data']['title']}")
            print(f"   Slides: {len(data['data']['slides'])}")
    
    # Topic statistics
    response = requests.get(f"{BASE_URL}/topics/ai/statistics")
    print(f"📈 AI Statistics: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Stats: {data['statistics']}")
    
    # Topic trends
    response = requests.get(f"{BASE_URL}/topics/ai/trends")
    print(f"📈 AI Trends: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Trends: {data['trends']}")

def test_image_generation():
    """Test image generation endpoints"""
    print("\n🖼️ Testing Image Generation")
    print("=" * 50)
    
    # Image suggestions
    topics = ["Artificial Intelligence", "Machine Learning", "Cloud Computing"]
    for topic in topics:
        response = requests.get(f"{BASE_URL}/image-suggestions/{topic}")
        print(f"🖼️ {topic} Suggestions: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Suggestions: {len(data['suggestions'])} items")

def test_different_layouts():
    """Test presentations with different layout parameters"""
    print("\n🎨 Testing Different Layout Parameters")
    print("=" * 50)
    
    # Test 1: All bullet points
    print("📝 Test 1: All bullet points layout")
    data = {
        "topic": "Artificial Intelligence",
        "num_slides": 4,
        "layout_preference": ["title", "bullet_points", "bullet_points", "bullet_points"],
        "theme": "modern"
    }
    response = requests.post(f"{BASE_URL}/generate", json=data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Generated: {result['filename']}")
        print(f"   Download: {result['download_url']}")
    
    time.sleep(2)  # Rate limiting
    
    # Test 2: Mixed layouts
    print("\n📊 Test 2: Mixed layouts (title, bullets, two-column, image)")
    data = {
        "topic": "Machine Learning",
        "num_slides": 4,
        "layout_preference": ["title", "bullet_points", "two_column", "content_with_image"],
        "theme": "corporate",
        "include_citations": True
    }
    response = requests.post(f"{BASE_URL}/generate", json=data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Generated: {result['filename']}")
        print(f"   Download: {result['download_url']}")
    
    time.sleep(2)
    
    # Test 3: Custom colors and fonts
    print("\n🎨 Test 3: Custom colors and fonts")
    data = {
        "topic": "Cloud Computing",
        "num_slides": 5,
        "layout_preference": ["title", "bullet_points", "two_column", "bullet_points", "content_with_image"],
        "theme": "creative",
        "color_scheme": {
            "primary_color": "#2E86AB",
            "secondary_color": "#A23B72",
            "background_color": "#FFFFFF",
            "text_color": "#333333"
        },
        "font_settings": {
            "title_font": "Arial",
            "body_font": "Calibri",
            "title_size": 44,
            "body_size": 18
        }
    }
    response = requests.post(f"{BASE_URL}/generate", json=data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Generated: {result['filename']}")
        print(f"   Download: {result['download_url']}")
    
    time.sleep(2)
    
    # Test 4: Business strategy with all layouts
    print("\n💼 Test 4: Business strategy with comprehensive layouts")
    data = {
        "topic": "Business Strategy",
        "num_slides": 6,
        "layout_preference": ["title", "bullet_points", "two_column", "bullet_points", "two_column", "content_with_image"],
        "theme": "minimal",
        "include_citations": True
    }
    response = requests.post(f"{BASE_URL}/generate", json=data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Generated: {result['filename']}")
        print(f"   Download: {result['download_url']}")

def test_image_generation_endpoint():
    """Test the new image generation endpoint"""
    print("\n🖼️ Testing Image Generation Endpoint")
    print("=" * 50)
    
    data = {
        "topic": "Digital Transformation",
        "num_slides": 3,
        "layout_preference": ["title", "bullet_points", "content_with_image"],
        "theme": "modern"
    }
    
    response = requests.post(f"{BASE_URL}/generate-with-images", json=data)
    print(f"🖼️ Generate with Images: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Generated: {result['filename']}")
        print(f"   Download: {result['download_url']}")
        print(f"   Message: {result['message']}")

def test_custom_content():
    """Test with custom content"""
    print("\n✏️ Testing Custom Content")
    print("=" * 50)
    
    data = {
        "topic": "Custom Topic",
        "num_slides": 3,
        "theme": "modern",
        "custom_content": [
            {
                "title": "Introduction to Custom Topic",
                "content": "This is a custom introduction slide",
                "layout": "title"
            },
            {
                "title": "Key Points",
                "bullet_points": [
                    "Custom point 1",
                    "Custom point 2",
                    "Custom point 3",
                    "Custom point 4"
                ],
                "layout": "bullet_points"
            },
            {
                "title": "Analysis",
                "left_column": "Pros:\n\n• Advantage 1\n• Advantage 2\n• Advantage 3",
                "right_column": "Cons:\n\n• Disadvantage 1\n• Disadvantage 2\n• Disadvantage 3",
                "layout": "two_column"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/generate", json=data)
    print(f"✏️ Custom Content: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Generated: {result['filename']}")
        print(f"   Download: {result['download_url']}")

def main():
    """Run all tests"""
    print("🚀 Enhanced Slide Generator API Test Suite")
    print("=" * 60)
    
    try:
        test_basic_endpoints()
        test_topic_data_endpoints()
        test_image_generation()
        test_different_layouts()
        test_image_generation_endpoint()
        test_custom_content()
        
        print("\n🎉 All tests completed!")
        print("=" * 60)
        print("📚 API Documentation: https://slide-generator-ai.onrender.com/docs")
        print("🔗 Health Check: https://slide-generator-ai.onrender.com/api/v1/health")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    main() 