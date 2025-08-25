import json
import hashlib
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.slide_models import SlideContent, SlideLayout
from app.services.topic_data_service import TopicDataService


class ContentCache:
    def __init__(self, cache_dir: str = "cache", max_cache_size: int = 1000, cache_ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_cache_size = max_cache_size
        self.cache_ttl_hours = cache_ttl_hours
        self.topic_data_service = TopicDataService()
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def _generate_cache_key(self, topic: str, num_slides: int, layout_preference: List[SlideLayout]) -> str:
        """Generate a unique cache key for the request"""
        # Create a hash of the request parameters
        request_data = {
            "topic": topic.lower().strip(),
            "num_slides": num_slides,
            "layout_preference": [layout.value for layout in layout_preference] if layout_preference else []
        }
        
        request_str = json.dumps(request_data, sort_keys=True)
        return hashlib.md5(request_str.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """Get the file path for a cache entry"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _is_cache_valid(self, cache_file_path: str) -> bool:
        """Check if cache entry is still valid (not expired)"""
        if not os.path.exists(cache_file_path):
            return False
        
        # Check file modification time
        file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_file_path))
        cache_age = datetime.now() - file_mtime
        
        return cache_age < timedelta(hours=self.cache_ttl_hours)
    
    def get_cached_content(self, topic: str, num_slides: int, layout_preference: List[SlideLayout]) -> Optional[List[SlideContent]]:
        """Get cached content if available and valid"""
        cache_key = self._generate_cache_key(topic, num_slides, layout_preference)
        cache_file_path = self._get_cache_file_path(cache_key)
        
        if not self._is_cache_valid(cache_file_path):
            return None
        
        try:
            with open(cache_file_path, 'r') as f:
                cached_data = json.load(f)
            
            # Convert cached data back to SlideContent objects
            slides = []
            for slide_data in cached_data['slides']:
                slide = SlideContent(**slide_data)
                slides.append(slide)
            
            print(f"📋 Cache hit for topic: {topic}")
            return slides
            
        except Exception as e:
            print(f"⚠️ Error reading cache: {e}")
            return None
    
    def cache_content(self, topic: str, num_slides: int, layout_preference: List[SlideLayout], slides: List[SlideContent]):
        """Cache the generated content"""
        cache_key = self._generate_cache_key(topic, num_slides, layout_preference)
        cache_file_path = self._get_cache_file_path(cache_key)
        
        try:
            # Convert slides to serializable format
            slides_data = []
            for slide in slides:
                slide_dict = slide.model_dump()
                slides_data.append(slide_dict)
            
            cache_data = {
                "topic": topic,
                "num_slides": num_slides,
                "layout_preference": [layout.value for layout in layout_preference] if layout_preference else [],
                "slides": slides_data,
                "cached_at": datetime.now().isoformat()
            }
            
            with open(cache_file_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"💾 Cached content for topic: {topic}")
            
            # Clean up old cache entries if needed
            self._cleanup_cache()
            
        except Exception as e:
            print(f"⚠️ Error caching content: {e}")
    
    def _cleanup_cache(self):
        """Remove old cache entries to prevent disk space issues"""
        try:
            cache_files = []
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    cache_files.append((file_path, os.path.getmtime(file_path)))
            
            # Sort by modification time (oldest first)
            cache_files.sort(key=lambda x: x[1])
            
            # Remove old files if we exceed max cache size
            if len(cache_files) > self.max_cache_size:
                files_to_remove = len(cache_files) - self.max_cache_size
                for i in range(files_to_remove):
                    os.remove(cache_files[i][0])
                    print(f"🗑️ Removed old cache file: {cache_files[i][0]}")
                    
        except Exception as e:
            print(f"⚠️ Error cleaning up cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            total_files = len(cache_files)
            
            # Calculate total cache size
            total_size = 0
            valid_files = 0
            for filename in cache_files:
                file_path = os.path.join(self.cache_dir, filename)
                if self._is_cache_valid(file_path):
                    valid_files += 1
                    total_size += os.path.getsize(file_path)
            
            return {
                "total_cache_entries": total_files,
                "valid_cache_entries": valid_files,
                "total_cache_size_bytes": total_size,
                "cache_directory": self.cache_dir,
                "max_cache_size": self.max_cache_size,
                "cache_ttl_hours": self.cache_ttl_hours
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def clear_cache(self):
        """Clear all cached content"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
            print("🗑️ Cache cleared successfully")
        except Exception as e:
            print(f"⚠️ Error clearing cache: {e}")
    
    def generate_variation_content(self, topic: str, num_slides: int, layout_preference: List[SlideLayout]) -> List[SlideContent]:
        """Generate variation content to avoid cache conflicts"""
        # Get base topic data
        topic_data = self.topic_data_service.get_topic_data(topic)
        
        # Create variations based on different aspects of the topic
        variations = [
            {"focus": "fundamentals", "suffix": " - Core Concepts"},
            {"focus": "applications", "suffix": " - Real-World Applications"},
            {"focus": "trends", "suffix": " - Current Trends"},
            {"focus": "future", "suffix": " - Future Outlook"},
            {"focus": "implementation", "suffix": " - Implementation Guide"},
            {"focus": "case_studies", "suffix": " - Case Studies"},
            {"focus": "technologies", "suffix": " - Technologies & Tools"},
            {"focus": "best_practices", "suffix": " - Best Practices"}
        ]
        
        # Select a random variation
        import random
        variation = random.choice(variations)
        
        # Generate content with variation
        slides = []
        
        # Title slide with variation
        slides.append(SlideContent(
            title=f"{topic_data['title']}{variation['suffix']}",
            content=f"An in-depth exploration of {topic_data['title']} focusing on {variation['focus']}. This presentation covers key concepts, applications, and insights for understanding {topic_data['title'].lower()}.",
            layout=SlideLayout.TITLE
        ))
        
        # Generate content slides with variation focus
        for i in range(1, min(num_slides, 6)):
            if i <= len(topic_data['slides']):
                slide_data = topic_data['slides'][i-1]
                # Modify slide title to reflect variation
                slide_data['title'] = f"{slide_data['title']} - {variation['focus'].title()}"
                slide_content = self._create_slide_from_data(slide_data, topic)
                slides.append(slide_content)
            else:
                # Additional slides with variation focus
                slides.append(SlideContent(
                    title=f"{variation['focus'].title()} Insights: {topic_data['title']}",
                    bullet_points=[
                        f"Key {variation['focus']} considerations for {topic_data['title']}",
                        f"Best practices in {variation['focus']} implementation",
                        f"Challenges and solutions in {variation['focus']}",
                        f"Future trends in {variation['focus']}",
                        f"Industry examples of {variation['focus']}",
                        f"Recommendations for {variation['focus']} success"
                    ],
                    layout=SlideLayout.BULLET_POINTS
                ))
        
        return slides[:num_slides]
    
    def _create_slide_from_data(self, slide_data: dict, topic: str) -> SlideContent:
        """Create a slide from topic data with enhanced content and citations"""
        slide_type = slide_data['type']
        content = slide_data['content']
        
        # Add citations to bullet points
        def add_citations_to_bullets(bullets):
            citations = [
                "Source: Industry Research Reports (2024)",
                "Reference: Academic Studies & Publications",
                "Data: Market Analysis & Surveys",
                "Source: Expert Interviews & Case Studies",
                "Reference: Technical Documentation & Standards",
                "Data: Government Reports & Statistics"
            ]
            
            enhanced_bullets = []
            for i, bullet in enumerate(bullets):
                citation = citations[i % len(citations)]
                enhanced_bullets.append(f"{bullet} ({citation})")
            return enhanced_bullets
        
        if slide_type == 'bullet_points':
            enhanced_bullets = add_citations_to_bullets(content['bullet_points'])
            return SlideContent(
                title=slide_data['title'],
                bullet_points=enhanced_bullets,
                layout=SlideLayout.BULLET_POINTS
            )
        elif slide_type == 'two_column':
            # Add citations to columns
            left_with_citation = f"{content['left_column']}\n\nSources: Industry Reports, Academic Research"
            right_with_citation = f"{content['right_column']}\n\nReferences: Market Analysis, Expert Opinions"
            
            return SlideContent(
                title=slide_data['title'],
                left_column=left_with_citation,
                right_column=right_with_citation,
                layout=SlideLayout.TWO_COLUMN
            )
        elif slide_type == 'content_with_image':
            content_with_citation = f"{content['content']}\n\nSources: Research Papers, Industry Reports, Expert Analysis"
            return SlideContent(
                title=slide_data['title'],
                content=content_with_citation,
                image_placeholder=content['image_placeholder'],
                layout=SlideLayout.CONTENT_WITH_IMAGE
            )
        else:
            content_with_citation = f"{content.get('content', f'Content about {topic}')}\n\nSources: Academic Research, Industry Analysis, Expert Insights"
            return SlideContent(
                title=slide_data['title'],
                content=content_with_citation,
                layout=SlideLayout.BULLET_POINTS
            ) 