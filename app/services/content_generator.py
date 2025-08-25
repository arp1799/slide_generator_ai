import openai
from typing import List, Dict, Any
import json
from app.core.config import settings
from app.models.slide_models import SlideLayout, SlideContent
from app.services.huggingface_generator import HuggingFaceGenerator
import os


class ContentGenerator:
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        else:
            # Fallback to environment variable
            openai.api_key = openai.api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize Hugging Face generator as fallback
        self.hf_generator = HuggingFaceGenerator()
    
    async def generate_slide_content(self, topic: str, num_slides: int, layout_preference: List[SlideLayout] = None) -> List[SlideContent]:
        """Generate slide content using OpenAI API"""
        
        if not openai.api_key:
            # Fallback to Hugging Face model for demo purposes
            print("🔄 No OpenAI API key found, using Hugging Face model...")
            return await self.hf_generator.generate_slide_content(topic, num_slides, layout_preference)
        
        try:
            # Create a structured prompt for slide generation
            prompt = self._create_slide_prompt(topic, num_slides, layout_preference)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional presentation designer. Generate structured slide content in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return self._parse_slide_content(content, num_slides, layout_preference)
            
        except Exception as e:
            print(f"Error generating content with OpenAI: {e}")
            # Fallback to Hugging Face model
            print("🔄 Falling back to Hugging Face model...")
            return await self.hf_generator.generate_slide_content(topic, num_slides, layout_preference)
    
    def _create_slide_prompt(self, topic: str, num_slides: int, layout_preference: List[SlideLayout] = None) -> str:
        """Create a structured prompt for slide generation"""
        
        layouts = layout_preference or [SlideLayout.TITLE, SlideLayout.BULLET_POINTS, SlideLayout.TWO_COLUMN]
        layout_names = [layout.value for layout in layouts]
        
        prompt = f"""
        Create a {num_slides}-slide presentation about "{topic}". 
        
        Use these layouts: {', '.join(layout_names)}
        
        Return the response as a JSON array with this structure:
        [
            {{
                "title": "Slide Title",
                "layout": "layout_type",
                "content": "Main content text",
                "bullet_points": ["point1", "point2", "point3"],
                "left_column": "Left column content",
                "right_column": "Right column content",
                "image_placeholder": "Description of image to include"
            }}
        ]
        
        Guidelines:
        - First slide should be a title slide
        - Include relevant bullet points (3-5 per slide)
        - Make content engaging and informative
        - Use professional language
        - Include citations where appropriate
        """
        
        return prompt
    
    def _parse_slide_content(self, content: str, num_slides: int, layout_preference: List[SlideLayout] = None) -> List[SlideContent]:
        """Parse the generated content into SlideContent objects"""
        try:
            # Extract JSON from the response
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            json_content = content[json_start:json_end]
            
            slides_data = json.loads(json_content)
            slides = []
            
            for slide_data in slides_data[:num_slides]:
                layout = SlideLayout(slide_data.get('layout', 'bullet_points'))
                
                slide = SlideContent(
                    title=slide_data.get('title', 'Untitled Slide'),
                    content=slide_data.get('content'),
                    bullet_points=slide_data.get('bullet_points'),
                    left_column=slide_data.get('left_column'),
                    right_column=slide_data.get('right_column'),
                    image_placeholder=slide_data.get('image_placeholder'),
                    layout=layout
                )
                slides.append(slide)
            
            return slides
            
        except Exception as e:
            print(f"Error parsing slide content: {e}")
            return self._generate_mock_content("", num_slides, layout_preference)
    
    def _generate_mock_content(self, topic: str, num_slides: int, layout_preference: List[SlideLayout] = None) -> List[SlideContent]:
        """Generate mock content for demo purposes"""
        
        layouts = layout_preference or [SlideLayout.TITLE, SlideLayout.BULLET_POINTS, SlideLayout.TWO_COLUMN]
        
        slides = []
        
        # Title slide
        slides.append(SlideContent(
            title=f"{topic} - Presentation",
            content=f"An overview of {topic}",
            layout=SlideLayout.TITLE
        ))
        
        # Content slides
        for i in range(1, min(num_slides, 4)):
            if i == 1:
                slides.append(SlideContent(
                    title=f"Introduction to {topic}",
                    bullet_points=[
                        f"Definition and scope of {topic}",
                        "Historical background and development",
                        "Current trends and applications",
                        "Future prospects and challenges"
                    ],
                    layout=SlideLayout.BULLET_POINTS
                ))
            elif i == 2:
                slides.append(SlideContent(
                    title=f"Key Concepts of {topic}",
                    left_column="Core Principles:\n\n• Fundamental concepts\n• Basic terminology\n• Essential frameworks",
                    right_column="Applications:\n\n• Real-world examples\n• Industry use cases\n• Success stories",
                    layout=SlideLayout.TWO_COLUMN
                ))
            elif i == 3:
                slides.append(SlideContent(
                    title=f"Advanced Topics in {topic}",
                    content=f"Exploring advanced concepts and methodologies related to {topic}",
                    image_placeholder="Diagram showing advanced concepts and relationships",
                    layout=SlideLayout.CONTENT_WITH_IMAGE
                ))
        
        # Add more slides if needed
        for i in range(4, num_slides):
            slides.append(SlideContent(
                title=f"Slide {i+1}: {topic}",
                bullet_points=[
                    f"Point 1 about {topic}",
                    f"Point 2 about {topic}",
                    f"Point 3 about {topic}",
                    f"Point 4 about {topic}"
                ],
                layout=SlideLayout.BULLET_POINTS
            ))
        
        return slides[:num_slides] 