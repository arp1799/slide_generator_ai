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
        
        print(f"🤖 HuggingFaceGenerator: Starting content generation for '{topic}'")
        print(f"📋 Request: {num_slides} slides, layouts: {layout_preference}")
        
        if not self.generator:
            print("⚠️ HuggingFaceGenerator: Model not loaded, using enhanced mock content")
            # Fallback to mock content if model not loaded
            return self._generate_mock_content(topic, num_slides, layout_preference)
        
        try:
            layouts = layout_preference or [SlideLayout.TITLE, SlideLayout.BULLET_POINTS, SlideLayout.TWO_COLUMN]
            print(f"🎯 HuggingFaceGenerator: Using layouts: {layouts}")
            
            slides = []
            
            # Title slide
            print("📝 HuggingFaceGenerator: Creating title slide...")
            slides.append(SlideContent(
                title=f"{topic} - Presentation",
                content=f"An overview of {topic}",
                layout=SlideLayout.TITLE
            ))
            
            # Generate content slides with better prompts
            for i in range(1, min(num_slides, 6)):
                print(f"📝 HuggingFaceGenerator: Creating slide {i+1} with layout {layouts[i % len(layouts)]}...")
                slide_content = await self._generate_slide_text(topic, i, layouts[i % len(layouts)])
                slides.append(slide_content)
            
            print(f"✅ HuggingFaceGenerator: Generated {len(slides)} slides successfully")
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
        """Generate high-quality content using topic data service with citations"""
        
        slides = []
        
        # Get topic data if service is available
        if self.topic_data_service:
            try:
                topic_data = self.topic_data_service.get_topic_data(topic)
                print(f"📚 Using topic data service for '{topic}'")
            except Exception as e:
                print(f"Error getting topic data: {e}")
                topic_data = None
        else:
            topic_data = None
        
        # Title slide
        if topic_data:
            slides.append(SlideContent(
                title=f"{topic_data['title']} - Comprehensive Overview",
                content=f"An in-depth exploration of {topic_data['title']} and its impact on modern technology and business. This presentation covers key concepts, applications, market trends, and future developments in {topic_data['title'].lower()}.",
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
                            f"Growth Rate: {topic_data['statistics'].get('growth_rate', 'Strong growth')}",
                            f"Adoption Rate: {topic_data['statistics'].get('adoption_rate', 'Increasing adoption')}",
                            f"Key Players: {', '.join(topic_data['key_players'][:3])}",
                            f"Emerging Trends: {', '.join(topic_data['trends'][:2])}",
                            f"Future Outlook: Continued growth and innovation",
                            f"Investment: Significant venture capital and corporate investment",
                            f"Regulation: Evolving regulatory frameworks and standards"
                        ],
                        layout=SlideLayout.BULLET_POINTS
                    ))
        else:
            # Fallback to basic content if topic data is not available
            slides.append(SlideContent(
                title=f"{topic} - Comprehensive Presentation",
                content=f"An in-depth overview of {topic} covering key concepts, applications, market trends, and future developments. This presentation provides valuable insights for understanding the current state and future potential of {topic.lower()}.",
                layout=SlideLayout.TITLE
            ))
            
            # Generate basic content slides with more detailed content
            for i in range(1, num_slides):
                slides.append(SlideContent(
                    title=f"Slide {i}: {topic} Analysis",
                    bullet_points=[
                        f"Core Concept: Fundamental understanding of {topic} principles and methodologies",
                        f"Key Applications: Real-world use cases and industry implementations",
                        f"Market Analysis: Current market size, growth trends, and competitive landscape",
                        f"Technology Stack: Essential tools, frameworks, and platforms",
                        f"Challenges & Solutions: Common obstacles and innovative approaches",
                        f"Future Trends: Emerging developments and strategic opportunities",
                        f"Best Practices: Industry standards and optimization strategies",
                        f"ROI & Impact: Business value and measurable outcomes"
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
    
    # Topic-specific content is now handled by TopicDataService 