import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class TopicDataService:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self._load_topic_data()
    
    def _load_topic_data(self):
        """Load topic data from JSON files"""
        self.topic_data = {}
        
        # AI and Machine Learning Data
        self.topic_data["ai"] = {
            "title": "Artificial Intelligence",
            "slides": [
                {
                    "title": "Understanding Artificial Intelligence",
                    "type": "bullet_points",
                    "content": {
                        "bullet_points": [
                            "Definition: AI systems that can perform tasks requiring human intelligence",
                            "Types: Narrow AI (specific tasks) vs General AI (human-like intelligence)",
                            "Key Technologies: Machine Learning, Deep Learning, Neural Networks",
                            "Applications: Healthcare, Finance, Transportation, Entertainment"
                        ]
                    }
                },
                {
                    "title": "AI Technologies and Applications",
                    "type": "two_column",
                    "content": {
                        "left_column": "Core Technologies:\n\n• Machine Learning Algorithms\n• Deep Neural Networks\n• Natural Language Processing\n• Computer Vision",
                        "right_column": "Industry Applications:\n\n• Healthcare: Diagnosis & Treatment\n• Finance: Fraud Detection\n• Transportation: Autonomous Vehicles\n• Retail: Personalized Shopping"
                    }
                },
                {
                    "title": "AI Implementation Strategy",
                    "type": "content_with_image",
                    "content": {
                        "content": "Strategic approach to implementing AI solutions in organizations",
                        "image_placeholder": "AI implementation roadmap diagram"
                    }
                },
                {
                    "title": "AI Ethics and Future Trends",
                    "type": "bullet_points",
                    "content": {
                        "bullet_points": [
                            "Ethical Considerations: Bias, Privacy, Transparency",
                            "Regulatory Framework: Data Protection and AI Governance",
                            "Future Trends: Quantum AI, Edge Computing, AI Democratization",
                            "Challenges: Job Displacement, Security, Trust"
                        ]
                    }
                }
            ],
            "statistics": {
                "market_size": "$136.6 billion (2022)",
                "growth_rate": "37.3% CAGR",
                "adoption_rate": "35% of organizations"
            },
            "key_players": ["OpenAI", "Google", "Microsoft", "Amazon", "IBM"],
            "trends": ["Generative AI", "Edge AI", "AI Ethics", "Quantum AI"]
        }
        
        # Machine Learning Data
        self.topic_data["machine_learning"] = {
            "title": "Machine Learning",
            "slides": [
                {
                    "title": "Machine Learning Fundamentals",
                    "type": "bullet_points",
                    "content": {
                        "bullet_points": [
                            "Definition: Algorithms that learn patterns from data",
                            "Types: Supervised, Unsupervised, Reinforcement Learning",
                            "Key Concepts: Training, Testing, Validation, Overfitting",
                            "Applications: Prediction, Classification, Clustering, Recommendation"
                        ]
                    }
                },
                {
                    "title": "ML Algorithms and Techniques",
                    "type": "two_column",
                    "content": {
                        "left_column": "Supervised Learning:\n\n• Linear Regression\n• Logistic Regression\n• Decision Trees\n• Random Forest\n• Support Vector Machines",
                        "right_column": "Unsupervised Learning:\n\n• K-Means Clustering\n• Hierarchical Clustering\n• Principal Component Analysis\n• Autoencoders\n• Generative Models"
                    }
                },
                {
                    "title": "Deep Learning and Neural Networks",
                    "type": "content_with_image",
                    "content": {
                        "content": "Advanced machine learning using neural networks with multiple layers",
                        "image_placeholder": "Neural network architecture diagram"
                    }
                },
                {
                    "title": "ML Implementation Best Practices",
                    "type": "bullet_points",
                    "content": {
                        "bullet_points": [
                            "Data Quality: Clean, relevant, and sufficient data",
                            "Model Selection: Choose appropriate algorithms for the problem",
                            "Evaluation: Use proper metrics and validation techniques",
                            "Deployment: Monitor, maintain, and update models"
                        ]
                    }
                }
            ],
            "statistics": {
                "market_size": "$21.17 billion (2022)",
                "growth_rate": "38.8% CAGR",
                "adoption_rate": "57% of organizations"
            },
            "key_players": ["Google", "Microsoft", "Amazon", "IBM", "Facebook"],
            "trends": ["AutoML", "MLOps", "Federated Learning", "Explainable AI"]
        }
        
        # Digital Transformation Data
        self.topic_data["digital_transformation"] = {
            "title": "Digital Transformation",
            "slides": [
                {
                    "title": "Digital Transformation Overview",
                    "type": "bullet_points",
                    "content": {
                        "bullet_points": [
                            "Definition: Integration of digital technology into all business areas",
                            "Key Drivers: Customer expectations, competitive pressure, efficiency gains",
                            "Technologies: Cloud Computing, IoT, Big Data, Mobile",
                            "Benefits: Improved efficiency, better customer experience, cost reduction"
                        ]
                    }
                },
                {
                    "title": "Technology Implementation Framework",
                    "type": "two_column",
                    "content": {
                        "left_column": "Planning Phase:\n\n• Assessment & Strategy\n• Technology Selection\n• Resource Planning\n• Risk Management",
                        "right_column": "Execution Phase:\n\n• Pilot Programs\n• Training & Adoption\n• Integration\n• Monitoring"
                    }
                },
                {
                    "title": "Emerging Technology Trends",
                    "type": "content_with_image",
                    "content": {
                        "content": "Latest developments in technology that are shaping the future",
                        "image_placeholder": "Technology trends timeline diagram"
                    }
                }
            ],
            "statistics": {
                "market_size": "$1.8 trillion (2022)",
                "growth_rate": "23% CAGR",
                "adoption_rate": "70% of organizations"
            },
            "key_players": ["Microsoft", "Google", "Amazon", "Salesforce", "Oracle"],
            "trends": ["Cloud Migration", "AI Integration", "Remote Work", "Cybersecurity"]
        }
        
        # Cloud Computing Data
        self.topic_data["cloud_computing"] = {
            "title": "Cloud Computing",
            "slides": [
                {
                    "title": "Cloud Computing Fundamentals",
                    "type": "bullet_points",
                    "content": {
                        "bullet_points": [
                            "Definition: On-demand computing resources over the internet",
                            "Service Models: IaaS, PaaS, SaaS",
                            "Deployment Models: Public, Private, Hybrid, Multi-cloud",
                            "Benefits: Scalability, Cost-effectiveness, Flexibility, Security"
                        ]
                    }
                },
                {
                    "title": "Cloud Service Models",
                    "type": "two_column",
                    "content": {
                        "left_column": "Infrastructure as a Service (IaaS):\n\n• Virtual Machines\n• Storage\n• Networking\n• Load Balancers",
                        "right_column": "Platform as a Service (PaaS):\n\n• Development Tools\n• Database Management\n• Business Analytics\n• Operating Systems"
                    }
                },
                {
                    "title": "Cloud Security and Compliance",
                    "type": "content_with_image",
                    "content": {
                        "content": "Security measures and compliance standards for cloud environments",
                        "image_placeholder": "Cloud security framework diagram"
                    }
                }
            ],
            "statistics": {
                "market_size": "$371.4 billion (2022)",
                "growth_rate": "17.5% CAGR",
                "adoption_rate": "94% of organizations"
            },
            "key_players": ["AWS", "Microsoft Azure", "Google Cloud", "IBM", "Oracle"],
            "trends": ["Multi-cloud", "Edge Computing", "Serverless", "Green Cloud"]
        }
        
        # Business Strategy Data
        self.topic_data["business_strategy"] = {
            "title": "Business Strategy",
            "slides": [
                {
                    "title": "Strategic Business Planning",
                    "type": "bullet_points",
                    "content": {
                        "bullet_points": [
                            "Vision and Mission: Clear organizational direction and purpose",
                            "Market Analysis: Understanding competition and opportunities",
                            "Resource Allocation: Optimal distribution of time, money, and talent",
                            "Performance Metrics: KPIs and success measurement"
                        ]
                    }
                },
                {
                    "title": "Business Strategy Framework",
                    "type": "two_column",
                    "content": {
                        "left_column": "Internal Analysis:\n\n• Strengths & Weaknesses\n• Core Competencies\n• Resource Assessment\n• Organizational Culture",
                        "right_column": "External Analysis:\n\n• Market Opportunities\n• Competitive Threats\n• Industry Trends\n• Regulatory Environment"
                    }
                },
                {
                    "title": "Leadership and Management",
                    "type": "content_with_image",
                    "content": {
                        "content": "Effective leadership strategies for organizational success",
                        "image_placeholder": "Leadership framework diagram"
                    }
                }
            ],
            "statistics": {
                "success_rate": "67% of strategic initiatives succeed",
                "time_to_implement": "3-5 years average",
                "roi": "2.5x average return on strategy investment"
            },
            "key_frameworks": ["SWOT Analysis", "Porter's Five Forces", "Balanced Scorecard", "Blue Ocean Strategy"],
            "trends": ["Digital Strategy", "Sustainability", "Agile Strategy", "Data-Driven Decisions"]
        }
    
    def get_topic_data(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive data for a specific topic"""
        topic_lower = topic.lower()
        
        # Map topic variations to data keys
        topic_mapping = {
            "ai": "ai",
            "artificial intelligence": "ai",
            "machine learning": "machine_learning",
            "ml": "machine_learning",
            "digital transformation": "digital_transformation",
            "cloud computing": "cloud_computing",
            "cloud": "cloud_computing",
            "business strategy": "business_strategy",
            "strategy": "business_strategy"
        }
        
        # Find matching topic
        for key, value in topic_mapping.items():
            if key in topic_lower:
                return self.topic_data.get(value)
        
        # Return default structure for unknown topics
        return self._get_default_topic_data(topic)
    
    def _get_default_topic_data(self, topic: str) -> Dict[str, Any]:
        """Generate default topic data structure"""
        return {
            "title": topic,
            "slides": [
                {
                    "title": f"Introduction to {topic}",
                    "type": "bullet_points",
                    "content": {
                        "bullet_points": [
                            f"Definition and scope of {topic}",
                            f"Historical development and evolution",
                            f"Current applications and use cases",
                            f"Future trends and opportunities"
                        ]
                    }
                },
                {
                    "title": f"{topic} Analysis",
                    "type": "two_column",
                    "content": {
                        "left_column": f"Key Concepts:\n\n• Fundamental principles\n• Core methodologies\n• Essential frameworks\n• Best practices",
                        "right_column": f"Applications:\n\n• Real-world examples\n• Industry implementations\n• Success stories\n• Case studies"
                    }
                },
                {
                    "title": f"Advanced {topic} Topics",
                    "type": "content_with_image",
                    "content": {
                        "content": f"Exploring advanced concepts and methodologies in {topic}",
                        "image_placeholder": f"Advanced {topic} concepts diagram"
                    }
                }
            ],
            "statistics": {
                "market_size": "Growing market",
                "adoption_rate": "Increasing adoption"
            },
            "key_players": ["Industry leaders"],
            "trends": ["Emerging trends", "Innovation", "Growth"]
        }
    
    def get_slide_content(self, topic: str, slide_index: int) -> Optional[Dict[str, Any]]:
        """Get specific slide content for a topic"""
        topic_data = self.get_topic_data(topic)
        if topic_data and slide_index < len(topic_data["slides"]):
            return topic_data["slides"][slide_index]
        return None
    
    def get_topic_statistics(self, topic: str) -> Dict[str, str]:
        """Get statistics for a topic"""
        topic_data = self.get_topic_data(topic)
        return topic_data.get("statistics", {})
    
    def get_topic_trends(self, topic: str) -> List[str]:
        """Get trends for a topic"""
        topic_data = self.get_topic_data(topic)
        return topic_data.get("trends", [])
    
    def get_available_topics(self) -> List[str]:
        """Get list of available topics with comprehensive data"""
        return list(self.topic_data.keys()) 