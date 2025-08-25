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
        """Generate high-quality mock content based on topic"""
        
        layouts = layout_preference or [SlideLayout.TITLE, SlideLayout.BULLET_POINTS, SlideLayout.TWO_COLUMN]
        
        slides = []
        
        # Title slide
        slides.append(SlideContent(
            title=f"{topic} - Comprehensive Overview",
            content=f"An in-depth exploration of {topic} and its impact on modern technology and business",
            layout=SlideLayout.TITLE
        ))
        
        # Generate topic-specific content
        topic_content = self._get_topic_specific_content(topic)
        
        # Content slides
        for i in range(1, min(num_slides, len(topic_content) + 1)):
            if i <= len(topic_content):
                slides.append(topic_content[i-1])
            else:
                # Fallback slides
                slides.append(SlideContent(
                    title=f"Additional Insights on {topic}",
                    bullet_points=[
                        f"Emerging trends in {topic}",
                        f"Industry best practices",
                        f"Future developments and innovations",
                        f"Strategic recommendations"
                    ],
                    layout=SlideLayout.BULLET_POINTS
                ))
        
        return slides[:num_slides]
    
    def _get_topic_specific_content(self, topic: str) -> List[SlideContent]:
        """Generate topic-specific content based on common presentation topics"""
        
        topic_lower = topic.lower()
        
        # AI and Machine Learning topics
        if any(keyword in topic_lower for keyword in ['ai', 'artificial intelligence', 'machine learning', 'ml']):
            return [
                SlideContent(
                    title="Understanding Artificial Intelligence",
                    bullet_points=[
                        "Definition: AI systems that can perform tasks requiring human intelligence",
                        "Types: Narrow AI (specific tasks) vs General AI (human-like intelligence)",
                        "Key Technologies: Machine Learning, Deep Learning, Neural Networks",
                        "Applications: Healthcare, Finance, Transportation, Entertainment"
                    ],
                    layout=SlideLayout.BULLET_POINTS
                ),
                SlideContent(
                    title="AI Technologies and Applications",
                    left_column="Core Technologies:\n\n• Machine Learning Algorithms\n• Deep Neural Networks\n• Natural Language Processing\n• Computer Vision",
                    right_column="Industry Applications:\n\n• Healthcare: Diagnosis & Treatment\n• Finance: Fraud Detection\n• Transportation: Autonomous Vehicles\n• Retail: Personalized Shopping",
                    layout=SlideLayout.TWO_COLUMN
                ),
                SlideContent(
                    title="AI Implementation Strategy",
                    content="Strategic approach to implementing AI solutions in organizations",
                    image_placeholder="AI implementation roadmap diagram",
                    layout=SlideLayout.CONTENT_WITH_IMAGE
                ),
                SlideContent(
                    title="AI Ethics and Future Trends",
                    bullet_points=[
                        "Ethical Considerations: Bias, Privacy, Transparency",
                        "Regulatory Framework: Data Protection and AI Governance",
                        "Future Trends: Quantum AI, Edge Computing, AI Democratization",
                        "Challenges: Job Displacement, Security, Trust"
                    ],
                    layout=SlideLayout.BULLET_POINTS
                )
            ]
        
        # Technology topics
        elif any(keyword in topic_lower for keyword in ['technology', 'tech', 'digital', 'innovation']):
            return [
                SlideContent(
                    title="Digital Transformation Overview",
                    bullet_points=[
                        "Definition: Integration of digital technology into all business areas",
                        "Key Drivers: Customer expectations, competitive pressure, efficiency gains",
                        "Technologies: Cloud Computing, IoT, Big Data, Mobile",
                        "Benefits: Improved efficiency, better customer experience, cost reduction"
                    ],
                    layout=SlideLayout.BULLET_POINTS
                ),
                SlideContent(
                    title="Technology Implementation Framework",
                    left_column="Planning Phase:\n\n• Assessment & Strategy\n• Technology Selection\n• Resource Planning\n• Risk Management",
                    right_column="Execution Phase:\n\n• Pilot Programs\n• Training & Adoption\n• Integration\n• Monitoring",
                    layout=SlideLayout.TWO_COLUMN
                ),
                SlideContent(
                    title="Emerging Technology Trends",
                    content="Latest developments in technology that are shaping the future",
                    image_placeholder="Technology trends timeline diagram",
                    layout=SlideLayout.CONTENT_WITH_IMAGE
                )
            ]
        
        # Business topics
        elif any(keyword in topic_lower for keyword in ['business', 'strategy', 'management', 'leadership']):
            return [
                SlideContent(
                    title="Strategic Business Planning",
                    bullet_points=[
                        "Vision and Mission: Clear organizational direction and purpose",
                        "Market Analysis: Understanding competition and opportunities",
                        "Resource Allocation: Optimal distribution of time, money, and talent",
                        "Performance Metrics: KPIs and success measurement"
                    ],
                    layout=SlideLayout.BULLET_POINTS
                ),
                SlideContent(
                    title="Business Strategy Framework",
                    left_column="Internal Analysis:\n\n• Strengths & Weaknesses\n• Core Competencies\n• Resource Assessment\n• Organizational Culture",
                    right_column="External Analysis:\n\n• Market Opportunities\n• Competitive Threats\n• Industry Trends\n• Regulatory Environment",
                    layout=SlideLayout.TWO_COLUMN
                ),
                SlideContent(
                    title="Leadership and Management",
                    content="Effective leadership strategies for organizational success",
                    image_placeholder="Leadership framework diagram",
                    layout=SlideLayout.CONTENT_WITH_IMAGE
                )
            ]
        
        # Default content for other topics
        else:
            return [
                SlideContent(
                    title=f"Introduction to {topic}",
                    bullet_points=[
                        f"Definition and scope of {topic}",
                        f"Historical development and evolution",
                        f"Current applications and use cases",
                        f"Future trends and opportunities"
                    ],
                    layout=SlideLayout.BULLET_POINTS
                ),
                SlideContent(
                    title=f"{topic} Analysis",
                    left_column=f"Key Concepts:\n\n• Fundamental principles\n• Core methodologies\n• Essential frameworks\n• Best practices",
                    right_column=f"Applications:\n\n• Real-world examples\n• Industry implementations\n• Success stories\n• Case studies",
                    layout=SlideLayout.TWO_COLUMN
                ),
                SlideContent(
                    title=f"Advanced {topic} Topics",
                    content=f"Exploring advanced concepts and methodologies in {topic}",
                    image_placeholder=f"Advanced {topic} concepts diagram",
                    layout=SlideLayout.CONTENT_WITH_IMAGE
                )
            ] 