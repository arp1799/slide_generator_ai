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
from app.services.topic_data_service import TopicDataService
from app.services.image_generator import ImageGenerator


class HuggingFaceGenerator:
    def __init__(self):
        try:
            # Initialize services (always available)
            self.topic_data_service = TopicDataService()
            self.image_generator = ImageGenerator()
        except Exception as e:
            print(f"Error initializing services: {e}")
            # Create dummy services as fallback
            self.topic_data_service = None
            self.image_generator = None
        
        if not TRANSFORMERS_AVAILABLE:
            self.generator = None
            return
            
        # Use better model if token is available, otherwise use lightweight model
        if settings.huggingface_token:
            self.model_name = "microsoft/DialoGPT-large"  # Better model with token
        else:
            self.model_name = settings.huggingface_model  # Lightweight model without token
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
            
            # Generate content slides with better prompts
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
            prompt = f"Create 4 professional bullet points about {topic} for a business presentation:"
            try:
                response = self.generator(
                    prompt,
                    max_length=150,
                    num_return_sequences=1,
                    temperature=0.8,
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
                # Enhanced fallback bullet points
                bullet_points = [
                    f"Understanding the fundamentals of {topic}",
                    f"Key benefits and advantages of {topic}",
                    f"Important considerations and challenges",
                    f"Future trends and developments in {topic}"
                ]
                return SlideContent(
                    title=f"Key Points about {topic}",
                    bullet_points=bullet_points,
                    layout=layout
                )
        
        elif layout == SlideLayout.TWO_COLUMN:
            return SlideContent(
                title=f"{topic} Analysis",
                left_column=f"Advantages:\n\n• Enhanced efficiency and productivity\n• Cost-effective solutions\n• Improved user experience\n• Scalable implementation",
                right_column=f"Considerations:\n\n• Implementation challenges\n• Resource requirements\n• Training and adoption\n• Maintenance and updates",
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
        """Generate high-quality content using topic data service"""
        
        slides = []
        
        # Get topic data if service is available
        if self.topic_data_service:
            try:
                topic_data = self.topic_data_service.get_topic_data(topic)
            except Exception as e:
                print(f"Error getting topic data: {e}")
                topic_data = None
        else:
            topic_data = None
        
        # Title slide
        if topic_data:
            slides.append(SlideContent(
                title=f"{topic_data['title']} - Comprehensive Overview",
                content=f"An in-depth exploration of {topic_data['title']} and its impact on modern technology and business",
                layout=SlideLayout.TITLE
            ))
            
            # Generate content slides from topic data
            for i in range(1, min(num_slides, len(topic_data['slides']) + 1)):
                if i <= len(topic_data['slides']):
                    slide_data = topic_data['slides'][i-1]
                    slide_content = self._create_slide_from_data(slide_data, topic)
                    slides.append(slide_content)
                else:
                    # Additional slides with statistics and trends
                    slides.append(SlideContent(
                        title=f"Market Insights: {topic_data['title']}",
                        bullet_points=[
                            f"Market Size: {topic_data['statistics'].get('market_size', 'Growing market')}",
                            f"Key Players: {', '.join(topic_data['key_players'][:3])}",
                            f"Emerging Trends: {', '.join(topic_data['trends'][:2])}",
                            f"Future Outlook: Continued growth and innovation"
                        ],
                        layout=SlideLayout.BULLET_POINTS
                    ))
        else:
            # Fallback to basic content if topic data is not available
            slides.append(SlideContent(
                title=f"{topic} - Presentation",
                content=f"An overview of {topic}",
                layout=SlideLayout.TITLE
            ))
            
            # Generate basic content slides
            for i in range(1, num_slides):
                slides.append(SlideContent(
                    title=f"Slide {i}: {topic}",
                    bullet_points=[
                        f"First important point about {topic}",
                        f"Second key aspect of {topic}",
                        f"Third consideration for {topic}",
                        f"Fourth benefit of {topic}"
                    ],
                    layout=SlideLayout.BULLET_POINTS
                ))
        
        return slides[:num_slides]
    
    def _create_slide_from_data(self, slide_data: dict, topic: str) -> SlideContent:
        """Create a slide from topic data"""
        
        slide_type = slide_data['type']
        content = slide_data['content']
        
        if slide_type == 'bullet_points':
            return SlideContent(
                title=slide_data['title'],
                bullet_points=content['bullet_points'],
                layout=SlideLayout.BULLET_POINTS
            )
        elif slide_type == 'two_column':
            return SlideContent(
                title=slide_data['title'],
                left_column=content['left_column'],
                right_column=content['right_column'],
                layout=SlideLayout.TWO_COLUMN
            )
        elif slide_type == 'content_with_image':
            return SlideContent(
                title=slide_data['title'],
                content=content['content'],
                image_placeholder=content['image_placeholder'],
                layout=SlideLayout.CONTENT_WITH_IMAGE
            )
        else:
            return SlideContent(
                title=slide_data['title'],
                content=content.get('content', f"Content about {topic}"),
                layout=SlideLayout.BULLET_POINTS
            )
    
    # Topic-specific content is now handled by TopicDataService 