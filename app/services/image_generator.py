import requests
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import os
from typing import Optional, List
from app.core.config import settings


class ImageGenerator:
    def __init__(self):
        self.unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        self.unsplash_secret_key = os.getenv("UNSPLASH_SECRET_KEY")
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
    
    async def generate_image_for_slide(self, topic: str, slide_title: str, image_type: str = "concept") -> Optional[str]:
        """Generate or fetch an appropriate image for a slide"""
        
        try:
            # Try Unsplash first (with secret key for better results)
            if self.unsplash_access_key and self.unsplash_secret_key:
                image_url = await self._get_unsplash_image(topic, slide_title, image_type)
                if image_url:
                    return image_url
            
            # Try Pexels as fallback
            if self.pexels_api_key:
                image_url = await self._get_pexels_image(topic, slide_title, image_type)
                if image_url:
                    return image_url
            
            # Generate placeholder image
            return await self._generate_placeholder_image(topic, slide_title, image_type)
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return await self._generate_placeholder_image(topic, slide_title, image_type)
    
    async def _get_unsplash_image(self, topic: str, slide_title: str, image_type: str) -> Optional[str]:
        """Get image from Unsplash API"""
        try:
            # Create search query based on topic and slide title
            search_query = self._create_search_query(topic, slide_title, image_type)
            
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": search_query,
                "per_page": 1,
                "orientation": "landscape"
            }
            headers = {
                "Authorization": f"Client-ID {self.unsplash_access_key}"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data["results"]:
                return data["results"][0]["urls"]["regular"]
            
            return None
            
        except Exception as e:
            print(f"Unsplash API error: {e}")
            return None
    
    async def _get_pexels_image(self, topic: str, slide_title: str, image_type: str) -> Optional[str]:
        """Get image from Pexels API"""
        try:
            search_query = self._create_search_query(topic, slide_title, image_type)
            
            url = "https://api.pexels.com/v1/search"
            params = {
                "query": search_query,
                "per_page": 1,
                "orientation": "landscape"
            }
            headers = {
                "Authorization": self.pexels_api_key
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data["photos"]:
                return data["photos"][0]["src"]["large"]
            
            return None
            
        except Exception as e:
            print(f"Pexels API error: {e}")
            return None
    
    async def _generate_placeholder_image(self, topic: str, slide_title: str, image_type: str) -> str:
        """Generate a placeholder image with text"""
        try:
            # Create a simple placeholder image
            width, height = 800, 600
            image = Image.new('RGB', (width, height), color='#f0f0f0')
            draw = ImageDraw.Draw(image)
            
            # Try to use a font, fallback to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Add text to the image
            text = f"{topic}\n{slide_title}"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill='#333333', font=font)
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Convert to base64
            img_base64 = base64.b64encode(img_byte_arr).decode()
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            print(f"Error generating placeholder image: {e}")
            return ""
    
    def _create_search_query(self, topic: str, slide_title: str, image_type: str) -> str:
        """Create an appropriate search query for image APIs"""
        
        # Clean and enhance the topic
        topic_clean = topic.replace("Artificial Intelligence", "AI").replace("Machine Learning", "ML")
        
        # Extract key concepts from slide title
        slide_keywords = self._extract_keywords_from_title(slide_title)
        
        # Create contextual search queries based on slide content
        if "implementation" in slide_title.lower() or "strategy" in slide_title.lower():
            return f"{topic_clean} implementation strategy roadmap diagram"
        elif "technology" in slide_title.lower() or "application" in slide_title.lower():
            return f"{topic_clean} technology applications diagram"
        elif "understanding" in slide_title.lower() or "introduction" in slide_title.lower():
            return f"{topic_clean} concept illustration diagram"
        elif "ethics" in slide_title.lower() or "future" in slide_title.lower():
            return f"{topic_clean} ethics future trends visualization"
        elif "data" in slide_title.lower() or "analysis" in slide_title.lower():
            return f"{topic_clean} data analysis visualization"
        elif "business" in slide_title.lower() or "enterprise" in slide_title.lower():
            return f"{topic_clean} business enterprise solution"
        elif "workflow" in slide_title.lower() or "process" in slide_title.lower():
            return f"{topic_clean} workflow process diagram"
        elif "architecture" in slide_title.lower() or "system" in slide_title.lower():
            return f"{topic_clean} architecture system diagram"
        elif "trends" in slide_title.lower() or "development" in slide_title.lower():
            return f"{topic_clean} trends development timeline"
        elif "challenges" in slide_title.lower() or "problems" in slide_title.lower():
            return f"{topic_clean} challenges solutions diagram"
        else:
            # Use slide keywords if available, otherwise fall back to topic
            if slide_keywords:
                return f"{topic_clean} {slide_keywords} diagram illustration"
            else:
                return f"{topic_clean} concept diagram"
    
    def _extract_keywords_from_title(self, slide_title: str) -> str:
        """Extract relevant keywords from slide title for better image search"""
        
        # Remove common words and extract meaningful keywords
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall'
        }
        
        # Split title into words and filter out common words
        words = slide_title.lower().split()
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        
        # Take the most relevant keywords (first 3-4)
        relevant_keywords = keywords[:4]
        
        return ' '.join(relevant_keywords)
    
    def get_image_suggestions(self, topic: str) -> List[str]:
        """Get image suggestions for a topic"""
        suggestions = [
            f"Professional {topic} concept illustration with modern design",
            f"{topic} technology architecture diagram showing components",
            f"{topic} business application workflow diagram",
            f"{topic} data visualization with charts and graphs",
            f"{topic} implementation roadmap with phases and milestones",
            f"{topic} system architecture diagram with connections",
            f"{topic} process flow diagram with decision points",
            f"{topic} timeline showing development and evolution",
            f"{topic} comparison chart showing different approaches",
            f"{topic} infographic with key statistics and facts"
        ]
        return suggestions 