# 🚀 Deployment Guide: GitHub + Render

Complete guide to deploy the Slide Generator API to GitHub and Render with downloadable links.

## 📋 Prerequisites

### **1. GitHub Account**
- Create a GitHub account at https://github.com
- Install Git on your local machine

### **2. Render Account**
- Sign up at https://render.com
- Connect your GitHub account

### **3. API Keys (Optional but Recommended)**
- **OpenAI API Key**: Get from https://platform.openai.com/
- **Hugging Face Token**: Get from https://huggingface.co/settings/tokens
- These enable real AI content generation (OpenAI primary, Hugging Face fallback)

## 🔧 Step-by-Step Deployment

### **Step 1: Prepare Your Local Repository**

```bash
# Initialize Git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Slide Generator API"

# Add remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/slide-generator-api.git

# Push to GitHub
git push -u origin main
```

### **Step 2: Create GitHub Repository**

1. **Go to GitHub.com** and click "New repository"
2. **Repository name**: `slide-generator-api`
3. **Description**: "A powerful API for generating customizable presentation slides"
4. **Visibility**: Public or Private (your choice)
5. **Don't initialize** with README (we already have one)
6. **Click "Create repository"**

### **Step 3: Push Code to GitHub**

```bash
# Follow the commands from Step 1
git push -u origin main
```

### **Step 4: Deploy on Render**

1. **Go to Render.com** and sign in
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Select the `slide-generator-api` repository**
5. **Configure the service**:
   - **Name**: `slide-generator-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or paid for better performance)

### **Step 5: Configure Environment Variables**

In Render dashboard, go to **Environment** tab and add:

```env
# Required for real content generation
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here

# Optional settings
REDIS_URL=redis://localhost:6379
RATE_LIMIT_PER_MINUTE=60
OUTPUT_DIR=samples
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### **Step 6: Deploy**

1. **Click "Create Web Service"**
2. **Wait for deployment** (usually 2-5 minutes)
3. **Your API will be available at**: `https://your-app-name.onrender.com`

## 🔗 Downloadable Links System

### **How It Works**

1. **User generates presentation** → API creates file with unique ID
2. **File stored securely** → 7-day expiry, download tracking
3. **Shareable link provided** → `https://your-app.onrender.com/api/v1/download/{file_id}`
4. **User downloads file** → Direct download with original filename

### **Example Flow**

```bash
# 1. Generate presentation
curl -X POST "https://your-app.onrender.com/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI in Healthcare", "num_slides": 5}'

# Response:
{
  "presentation_id": "abc123",
  "filename": "AI_in_Healthcare.pptx",
  "download_url": "/api/v1/download/abc123-def456-ghi789",
  "message": "Presentation generated successfully",
  "slides_generated": 5,
  "processing_time": 0.05
}

# 2. Download link (share with user)
https://your-app.onrender.com/api/v1/download/abc123-def456-ghi789
```

## 🛠️ Testing Your Deployment

### **1. Health Check**
```bash
curl https://your-app.onrender.com/api/v1/health
```

### **2. Generate Presentation**
```bash
curl -X POST "https://your-app.onrender.com/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test Presentation", "num_slides": 3}'
```

### **3. Test Download Link**
```bash
# Use the download_url from the response above
curl -O "https://your-app.onrender.com/api/v1/download/{file_id}"
```

## 📊 File Management Features

### **List All Files**
```bash
curl https://your-app.onrender.com/api/v1/samples
```

### **Get File Info**
```bash
curl https://your-app.onrender.com/api/v1/files/{file_id}/info
```

### **Storage Statistics**
```bash
curl https://your-app.onrender.com/api/v1/storage/stats
```

### **Cleanup Expired Files**
```bash
curl -X POST https://your-app.onrender.com/api/v1/cleanup
```

## 🔒 Security Features

- ✅ **File expiry**: 7-day automatic cleanup
- ✅ **Unique IDs**: No predictable file paths
- ✅ **Download tracking**: Monitor usage
- ✅ **Rate limiting**: Prevent abuse
- ✅ **Input validation**: Secure API endpoints

## 🚀 Production Optimizations

### **For Better Performance**

1. **Upgrade Render Plan**: Free → Paid for better resources
2. **Add Redis**: For caching and session management
3. **CDN**: For faster file downloads
4. **Monitoring**: Set up alerts and logging

### **Environment Variables for Production**

```env
# Performance
WORKERS=4
LOG_LEVEL=WARNING

# Security
CORS_ORIGINS=["https://yourdomain.com"]
RATE_LIMIT_PER_MINUTE=100

# Storage
OUTPUT_DIR=/opt/render/project/src/samples
MAX_FILE_SIZE=52428800  # 50MB
```

## 🐛 Troubleshooting

### **Common Issues**

1. **Build fails**: Check `requirements.txt` and Python version
2. **API key not working**: Verify OpenAI API key in environment variables
3. **Files not downloading**: Check file storage permissions
4. **Slow responses**: Consider upgrading Render plan

### **Logs and Debugging**

- **Render logs**: Available in dashboard
- **Application logs**: Check `/api/v1/health` endpoint
- **File storage**: Use `/api/v1/storage/stats` endpoint

## 📈 Monitoring and Analytics

### **Health Monitoring**
```bash
# Check API health
curl https://your-app.onrender.com/api/v1/health

# Check storage stats
curl https://your-app.onrender.com/api/v1/storage/stats
```

### **Usage Tracking**
- **Download counts**: Tracked per file
- **Storage usage**: Monitor disk space
- **Response times**: Available in Render dashboard

## 🎯 Next Steps

1. **Custom Domain**: Add your own domain
2. **SSL Certificate**: Automatic with Render
3. **Database**: Add PostgreSQL for persistent storage
4. **Authentication**: Add user accounts
5. **Analytics**: Track usage patterns

## 📞 Support

- **GitHub Issues**: Report bugs and feature requests
- **Render Support**: For deployment issues
- **Documentation**: Check `/docs` endpoint for API docs

---

**🎉 Your Slide Generator API is now live and ready for production use!** 