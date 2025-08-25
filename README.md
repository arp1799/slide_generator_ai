# Slide Generator API

A powerful backend application that generates customizable presentation slides on any topic using Python and AI technology.

## Features

### Core Features
- **Content Generation**: Generate relevant content using Large Language Models (OpenAI GPT)
- **Multiple Slide Layouts**: Support for 4 different slide layouts:
  - Title slide
  - Bullet points (3-5 points)
  - Two-column layout
  - Content with image placeholder
- **Customizable Themes**: 4 built-in themes (Modern, Corporate, Creative, Minimal)
- **Custom Styling**: Support for custom fonts, colors, and color schemes
- **Citations & References**: Automatic inclusion of source citations
- **PowerPoint Export**: Generate .pptx files ready for use

### Advanced Features
- **Request/Response Validation**: Comprehensive input validation using Pydantic
- **Error Handling**: Robust error handling with detailed error messages
- **Rate Limiting**: Built-in rate limiting support
- **API Documentation**: Interactive API documentation with Swagger UI
- **Health Monitoring**: Health check endpoints for monitoring

## Technology Stack

- **Framework**: FastAPI (Python)
- **Content Generation**: OpenAI GPT-3.5-turbo
- **Presentation Generation**: python-pptx
- **Validation**: Pydantic
- **Documentation**: OpenAPI/Swagger
- **Testing**: pytest

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd slide-generator-api
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Optional: Install Hugging Face dependencies for fallback AI generation
pip install -r requirements-huggingface.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
# OpenAI API Key (optional - will use mock content if not provided)
OPENAI_API_KEY=your_openai_api_key_here

# Redis URL (optional - for caching)
REDIS_URL=redis://localhost:6379

# Rate limiting
RATE_LIMIT_PER_MINUTE=60

# Output directory for presentations
OUTPUT_DIR=samples
```

### 5. Run the Application
```bash
# Development mode
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Health Check
```http
GET /health
```
Returns the health status of the API.

#### 2. Get Available Layouts
```http
GET /layouts
```
Returns a list of available slide layouts.

#### 3. Get Available Themes
```http
GET /themes
```
Returns a list of available themes.

#### 4. Generate Presentation
```http
POST /generate
```

**Request Body:**
```json
{
  "topic": "Artificial Intelligence in Healthcare",
  "num_slides": 5,
  "layout_preference": ["title", "bullet_points", "two_column"],
  "theme": "modern",
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
  },
  "include_citations": true,
  "include_image_suggestions": false
}
```

**Response:**
```json
{
  "presentation_id": "uuid-string",
  "filename": "presentation_20231201_143022_abc12345.pptx",
  "download_url": "/api/v1/download/presentation_20231201_143022_abc12345.pptx",
  "message": "Presentation generated successfully",
  "slides_generated": 5,
  "processing_time": 2.34
}
```

#### 5. Download Presentation
```http
GET /download/{filename}
```
Downloads the generated PowerPoint file.

#### 6. List Sample Presentations
```http
GET /samples
```
Returns a list of available sample presentations.

#### 7. Delete Sample Presentation
```http
DELETE /samples/{filename}
```
Deletes a sample presentation file.

### Request Models

#### SlideGenerationRequest
- `topic` (string, required): The topic for the presentation (1-200 characters)
- `num_slides` (integer, required): Number of slides to generate (1-20)
- `layout_preference` (array, optional): Preferred slide layouts
- `theme` (string, optional): Presentation theme (modern, corporate, creative, minimal)
- `color_scheme` (object, optional): Custom color scheme
- `font_settings` (object, optional): Custom font settings
- `custom_content` (array, optional): Custom slide content
- `include_citations` (boolean, optional): Include citations slide
- `include_image_suggestions` (boolean, optional): Include image suggestions

#### SlideLayout Options
- `title`: Title slide layout
- `bullet_points`: Bullet points layout
- `two_column`: Two-column layout
- `content_with_image`: Content with image placeholder

#### Theme Options
- `modern`: Modern blue and purple theme
- `corporate`: Professional blue theme
- `creative`: Creative pink and purple theme
- `minimal`: Minimal gray theme

## Usage Examples

### Basic Presentation Generation
```python
import requests

url = "http://localhost:8000/api/v1/generate"
data = {
    "topic": "Machine Learning Basics",
    "num_slides": 3,
    "theme": "modern"
}

response = requests.post(url, json=data)
result = response.json()

# Download the presentation
download_url = f"http://localhost:8000/api/v1/download/{result['filename']}"
presentation_response = requests.get(download_url)

with open("presentation.pptx", "wb") as f:
    f.write(presentation_response.content)
```

### Custom Content Generation
```python
import requests

url = "http://localhost:8000/api/v1/generate"
data = {
    "topic": "Custom Presentation",
    "num_slides": 2,
    "custom_content": [
        {
            "title": "Introduction",
            "content": "Welcome to our presentation",
            "layout": "title"
        },
        {
            "title": "Key Points",
            "bullet_points": [
                "Point 1: Important information",
                "Point 2: More details",
                "Point 3: Final thoughts"
            ],
            "layout": "bullet_points"
        }
    ],
    "theme": "corporate"
}

response = requests.post(url, json=data)
```

## Project Structure

```
slide-generator-api/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── slide_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── content_generator.py
│   │   └── presentation_generator.py
│   ├── utils/
│   │   └── __init__.py
│   ├── __init__.py
│   └── main.py
├── samples/
├── tests/
├── requirements.txt
├── README.md
└── .env
```

## Testing

Run the test suite:
```bash
pytest tests/
```

## Performance Optimization

The API includes several performance optimizations:
- **Async Processing**: Non-blocking content generation
- **Caching Support**: Redis integration for caching (optional)
- **Efficient File Handling**: Optimized PowerPoint generation
- **Request Validation**: Fast input validation with Pydantic

## Error Handling

The API provides comprehensive error handling:
- **Validation Errors**: Detailed validation error messages
- **File Not Found**: Proper 404 responses for missing files
- **Processing Errors**: Graceful handling of content generation failures
- **Rate Limiting**: Built-in rate limiting to prevent abuse

## Security Considerations

- **Input Validation**: All inputs are validated using Pydantic
- **File Security**: Secure file handling and validation
- **CORS Configuration**: Configurable CORS settings
- **Environment Variables**: Sensitive data stored in environment variables

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Set up proper logging
- Configure CORS for production domains
- Use environment variables for sensitive data
- Set up monitoring and health checks
- Configure rate limiting appropriately

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository. 