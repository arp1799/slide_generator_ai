try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Transformers not available - install with: pip install -r requirements-huggingface.txt")

from typing import List
import json
from app.models.slide_models import SlideLayout, SlideContent
from app.core.config import settings


class HuggingFaceGenerator:
    def __init__(self):
        if not TRANSFORMERS_AVAILABLE:
            self.generator = None
            return
            
        self.model_name = settings.huggingface_model  # Use model from settings
        self.tokenizer = None
        self.model = None
        self.generator = None
        self._load_model()
    
    def _load_model(self):
        """Load the Hugging Face model"""
        try:
            print("🔄 Loading Hugging Face model...")
            
            # Use token if available
            token = settings.huggingface_token
            if token:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, token=token)
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name, token=token)
            else:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            print("✅ Hugging Face model loaded successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not load Hugging Face model: {e}")
            self.generator = None
    
    async def generate_slide_content(self, topic: str, num_slides: int, layout_preference: List[SlideLayout] = None) -> List[SlideContent]:
        """Generate slide content using Hugging Face model"""
        
        if not self.generator:
            # Fallback to mock content if model not loaded
            return self._generate_mock_content(topic, num_slides, layout_preference)
        
        try:
            layouts = layout_preference or [SlideLayout.TITLE, SlideLayout.BULLET_POINTS, SlideLayout.TWO_COLUMN]
            
            slides = []
            
            # Title slide
            slides.append(SlideContent(
                title=f"{topic} - Presentation",
                content=f"An overview of {topic}",
                layout=SlideLayout.TITLE
            ))
            
            # Generate content slides
            for i in range(1, min(num_slides, 6)):
                slide_content = await self._generate_slide_text(topic, i, layouts[i % len(layouts)])
                slides.append(slide_content)
            
            return slides[:num_slides]
            
        except Exception as e:
            print(f"Error generating content with Hugging Face: {e}")
            return self._generate_mock_content(topic, num_slides, layout_preference)
    
    async def _generate_slide_text(self, topic: str, slide_num: int, layout: SlideLayout) -> SlideContent:
        """Generate text for a specific slide"""
        
        if layout == SlideLayout.TITLE:
            return SlideContent(
                title=f"Slide {slide_num}: {topic}",
                content=f"Introduction to {topic}",
                layout=layout
            )
        
        elif layout == SlideLayout.BULLET_POINTS:
            # Generate bullet points using the model
            prompt = f"Create 4 bullet points about {topic}:"
            try:
                response = self.generator(
                    prompt,
                    max_length=100,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True
                )
                
                generated_text = response[0]['generated_text']
                # Extract bullet points from generated text
                bullet_points = self._extract_bullet_points(generated_text, topic)
                
                return SlideContent(
                    title=f"Key Points about {topic}",
                    bullet_points=bullet_points,
                    layout=layout
                )
            except:
                # Fallback bullet points
                bullet_points = [
                    f"Important aspect of {topic}",
                    f"Key benefit of {topic}",
                    f"Main consideration for {topic}",
                    f"Future of {topic}"
                ]
                return SlideContent(
                    title=f"Key Points about {topic}",
                    bullet_points=bullet_points,
                    layout=layout
                )
        
        elif layout == SlideLayout.TWO_COLUMN:
            return SlideContent(
                title=f"{topic} Analysis",
                left_column=f"Advantages:\n\n• Benefit 1\n• Benefit 2\n• Benefit 3",
                right_column=f"Considerations:\n\n• Point 1\n• Point 2\n• Point 3",
                layout=layout
            )
        
        elif layout == SlideLayout.CONTENT_WITH_IMAGE:
            return SlideContent(
                title=f"{topic} Overview",
                content=f"Comprehensive overview of {topic} and its applications in modern technology and business.",
                image_placeholder=f"Diagram or chart showing {topic} concepts",
                layout=layout
            )
        
        else:
            return SlideContent(
                title=f"Slide {slide_num}: {topic}",
                content=f"Content about {topic}",
                layout=layout
            )
    
    def _extract_bullet_points(self, text: str, topic: str) -> List[str]:
        """Extract bullet points from generated text"""
        lines = text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                bullet_points.append(line[1:].strip())
            elif line and any(keyword in line.lower() for keyword in ['point', 'benefit', 'advantage', 'feature']):
                bullet_points.append(line)
        
        # If no bullet points found, create generic ones
        if not bullet_points:
            bullet_points = [
                f"First important point about {topic}",
                f"Second key aspect of {topic}",
                f"Third consideration for {topic}",
                f"Fourth benefit of {topic}"
            ]
        
        return bullet_points[:4]  # Return max 4 bullet points
    
    def _generate_mock_content(self, topic: str, num_slides: int, layout_preference: List[SlideLayout] = None) -> List[SlideContent]:
        """Generate mock content as fallback"""
        
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