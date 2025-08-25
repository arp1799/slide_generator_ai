# Quick Start Guide

Get up and running with the Slide Generator API in minutes!

## 🚀 Quick Setup

### 1. Clone and Setup
```bash
git clone <repository-url>
cd slide-generator-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the API
```bash
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### 3. Generate Your First Presentation

#### Using the CLI Tool
```bash
# Check API health
python cli.py health

# Generate a presentation
python cli.py generate "Machine Learning Basics" --slides 5 --theme modern

# List available themes
python cli.py themes

# List available layouts
python cli.py layouts
```

#### Using cURL
```bash
# Generate a presentation
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine Learning Basics",
    "num_slides": 5,
    "theme": "modern"
  }'

# Download the presentation
curl -O "http://localhost:8000/api/v1/download/[filename]"
```

#### Using Python
```python
import requests

# Generate presentation
response = requests.post("http://localhost:8000/api/v1/generate", json={
    "topic": "Machine Learning Basics",
    "num_slides": 5,
    "theme": "modern"
})

result = response.json()
print(f"Generated: {result['filename']}")

# Download presentation
download_url = f"http://localhost:8000/api/v1/download/{result['filename']}"
presentation = requests.get(download_url)

with open("presentation.pptx", "wb") as f:
    f.write(presentation.content)
```

## 🎨 Available Themes

- **modern**: Blue and purple theme
- **corporate**: Professional blue theme  
- **creative**: Pink and purple theme
- **minimal**: Clean gray theme

## 📋 Available Layouts

- **title**: Title slide layout
- **bullet_points**: Bullet points layout (3-5 points)
- **two_column**: Two-column layout
- **content_with_image**: Content with image placeholder

## 🔧 Configuration

Create a `.env` file for custom configuration:
```env
# OpenAI API Key (optional - will use mock content if not provided)
OPENAI_API_KEY=your_openai_api_key_here

# Output directory for presentations
OUTPUT_DIR=samples

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
```

## 🐳 Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t slide-generator-api .
docker run -p 8000:8000 slide-generator-api
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Generate sample presentations
python generate_samples.py
```

## 📚 Next Steps

- Explore the [full documentation](README.md)
- Check out the [API documentation](http://localhost:8000/docs)
- Try different themes and layouts
- Customize colors and fonts
- Add your own content

## 🆘 Need Help?

- Check the [API documentation](http://localhost:8000/docs)
- Review the [full README](README.md)
- Open an issue in the repository 