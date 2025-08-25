import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data


class TestLayoutsEndpoint:
    def test_get_layouts(self):
        """Test getting available layouts"""
        response = client.get("/api/v1/layouts")
        assert response.status_code == 200
        layouts = response.json()
        assert isinstance(layouts, list)
        assert "title" in layouts
        assert "bullet_points" in layouts
        assert "two_column" in layouts
        assert "content_with_image" in layouts


class TestThemesEndpoint:
    def test_get_themes(self):
        """Test getting available themes"""
        response = client.get("/api/v1/themes")
        assert response.status_code == 200
        themes = response.json()
        assert isinstance(themes, list)
        assert "modern" in themes
        assert "corporate" in themes
        assert "creative" in themes
        assert "minimal" in themes


class TestGenerateEndpoint:
    def test_generate_presentation_basic(self):
        """Test basic presentation generation"""
        data = {
            "topic": "Test Topic",
            "num_slides": 3
        }
        response = client.post("/api/v1/generate", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "presentation_id" in result
        assert "filename" in result
        assert "download_url" in result
        assert "slides_generated" in result
        assert result["slides_generated"] == 3

    def test_generate_presentation_with_theme(self):
        """Test presentation generation with theme"""
        data = {
            "topic": "Test Topic",
            "num_slides": 2,
            "theme": "corporate"
        }
        response = client.post("/api/v1/generate", json=data)
        assert response.status_code == 200

    def test_generate_presentation_invalid_slides(self):
        """Test presentation generation with invalid number of slides"""
        data = {
            "topic": "Test Topic",
            "num_slides": 25  # More than max allowed
        }
        response = client.post("/api/v1/generate", json=data)
        assert response.status_code == 422

    def test_generate_presentation_empty_topic(self):
        """Test presentation generation with empty topic"""
        data = {
            "topic": "",
            "num_slides": 3
        }
        response = client.post("/api/v1/generate", json=data)
        assert response.status_code == 422

    def test_generate_presentation_custom_content(self):
        """Test presentation generation with custom content"""
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
                        "Point 2: More details"
                    ],
                    "layout": "bullet_points"
                }
            ]
        }
        response = client.post("/api/v1/generate", json=data)
        assert response.status_code == 200


class TestDownloadEndpoint:
    def test_download_nonexistent_file(self):
        """Test downloading a file that doesn't exist"""
        response = client.get("/api/v1/download/nonexistent.pptx")
        assert response.status_code == 404

    def test_download_existing_file(self):
        """Test downloading an existing file"""
        # First generate a presentation
        data = {
            "topic": "Test Download",
            "num_slides": 1
        }
        generate_response = client.post("/api/v1/generate", json=data)
        assert generate_response.status_code == 200
        
        download_url = generate_response.json()["download_url"]
        file_id = download_url.split("/")[-1]  # Extract file ID from URL
        
        # Then download it
        download_response = client.get(f"/api/v1/download/{file_id}")
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.presentationml.presentation"


class TestSamplesEndpoint:
    def test_list_samples(self):
        """Test listing sample presentations"""
        response = client.get("/api/v1/samples")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "files" in data
        assert "total_count" in data
        assert "storage_stats" in data

    def test_delete_nonexistent_sample(self):
        """Test deleting a sample that doesn't exist"""
        response = client.delete("/api/v1/samples/nonexistent.pptx")
        assert response.status_code == 404

    def test_delete_existing_sample(self):
        """Test deleting an existing sample"""
        # First generate a presentation
        data = {
            "topic": "Test Delete",
            "num_slides": 1
        }
        generate_response = client.post("/api/v1/generate", json=data)
        assert generate_response.status_code == 200
        
        download_url = generate_response.json()["download_url"]
        file_id = download_url.split("/")[-1]  # Extract file ID from URL
        
        # Then delete it
        delete_response = client.delete(f"/api/v1/samples/{file_id}")
        assert delete_response.status_code == 200


class TestRootEndpoints:
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_api_info_endpoint(self):
        """Test API info endpoint"""
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data 