#!/usr/bin/env python3
"""
Sample Presentation Generator Script

This script generates sample presentations to demonstrate the API capabilities.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.content_generator import ContentGenerator
from app.services.presentation_generator import PresentationGenerator
from app.models.slide_models import Theme, SlideLayout


async def generate_sample_presentations():
    """Generate sample presentations for demonstration"""
    
    print("🎯 Generating Sample Presentations...")
    
    content_generator = ContentGenerator()
    presentation_generator = PresentationGenerator()
    
    # Sample topics
    topics = [
        "Artificial Intelligence in Healthcare",
        "Sustainable Energy Solutions",
        "Digital Marketing Strategies",
        "Machine Learning Fundamentals",
        "Cybersecurity Best Practices"
    ]
    
    themes = [Theme.MODERN, Theme.CORPORATE, Theme.CREATIVE, Theme.MINIMAL]
    
    for i, topic in enumerate(topics):
        print(f"\n📊 Generating presentation {i+1}/5: {topic}")
        
        try:
            # Generate content
            slides = await content_generator.generate_slide_content(
                topic=topic,
                num_slides=5,
                layout_preference=[
                    SlideLayout.TITLE,
                    SlideLayout.BULLET_POINTS,
                    SlideLayout.TWO_COLUMN,
                    SlideLayout.CONTENT_WITH_IMAGE,
                    SlideLayout.BULLET_POINTS
                ]
            )
            
            # Generate presentation with different themes
            theme = themes[i % len(themes)]
            filename = presentation_generator.generate_presentation(
                slides=slides,
                theme=theme,
                include_citations=True
            )
            
            print(f"✅ Generated: {filename} (Theme: {theme.value})")
            
        except Exception as e:
            print(f"❌ Error generating presentation for '{topic}': {e}")
    
    print(f"\n🎉 Sample generation complete! Check the 'samples' directory for generated presentations.")


if __name__ == "__main__":
    asyncio.run(generate_sample_presentations()) 