from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
import time
import os
import uuid
from datetime import datetime

from app.models.slide_models import (
    SlideGenerationRequest, 
    SlideGenerationResponse, 
    ErrorResponse, 
    HealthCheckResponse,
    SlideLayout,
    Theme
)
from app.services.content_generator import ContentGenerator
from app.services.presentation_generator import PresentationGenerator
from app.services.file_storage import file_storage
from app.core.config import settings

router = APIRouter()
content_generator = ContentGenerator()
presentation_generator = PresentationGenerator()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        version=settings.api_version,
        timestamp=datetime.now().isoformat()
    )


@router.get("/layouts", response_model=List[str])
async def get_available_layouts():
    """Get available slide layouts"""
    return [layout.value for layout in SlideLayout]


@router.get("/themes", response_model=List[str])
async def get_available_themes():
    """Get available themes"""
    return [theme.value for theme in Theme]


@router.post("/generate", response_model=SlideGenerationResponse)
async def generate_presentation(request: SlideGenerationRequest):
    """Generate a PowerPoint presentation"""
    
    start_time = time.time()
    presentation_id = str(uuid.uuid4())
    
    try:
        # Generate slide content
        slides = await content_generator.generate_slide_content(
            topic=request.topic,
            num_slides=request.num_slides,
            layout_preference=request.layout_preference
        )
        
        # Use custom content if provided
        if request.custom_content:
            slides = request.custom_content
        
        # Generate PowerPoint presentation
        filename = presentation_generator.generate_presentation(
            slides=slides,
            theme=request.theme,
            color_scheme=request.color_scheme,
            font_settings=request.font_settings,
            include_citations=request.include_citations
        )
        
        # Save to file storage and get shareable link
        file_path = os.path.join(settings.output_dir, filename)
        storage_info = file_storage.save_presentation(file_path, filename)
        
        processing_time = time.time() - start_time
        
        return SlideGenerationResponse(
            presentation_id=presentation_id,
            filename=filename,
            download_url=storage_info["download_url"],
            message="Presentation generated successfully",
            slides_generated=len(slides),
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating presentation: {str(e)}"
        )


@router.get("/download/{file_id}")
async def download_presentation(file_id: str):
    """Download a generated presentation by file ID"""
    
    file_path = file_storage.get_file_path(file_id)
    
    if not file_path:
        raise HTTPException(
            status_code=404,
            detail="Presentation file not found or expired"
        )
    
    metadata = file_storage.get_file_metadata(file_id)
    original_filename = metadata["original_filename"] if metadata else f"presentation_{file_id}.pptx"
    
    return FileResponse(
        path=file_path,
        filename=original_filename,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


@router.get("/samples")
async def list_sample_presentations():
    """List available sample presentations"""
    
    files = file_storage.list_files()
    return {
        "files": files,
        "total_count": len(files),
        "storage_stats": file_storage.get_storage_stats()
    }


@router.delete("/samples/{file_id}")
async def delete_sample_presentation(file_id: str):
    """Delete a sample presentation by file ID"""
    
    success = file_storage.delete_file(file_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Presentation file not found"
        )
    
    return {"message": f"Presentation {file_id} deleted successfully"}


@router.get("/files/{file_id}/info")
async def get_file_info(file_id: str):
    """Get file information by ID"""
    
    metadata = file_storage.get_file_metadata(file_id)
    
    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    
    return {
        "file_id": file_id,
        "filename": metadata["original_filename"],
        "created_at": metadata["created_at"],
        "expires_at": metadata["expires_at"],
        "download_count": metadata["download_count"],
        "file_size": metadata["file_size"],
        "is_active": metadata["is_active"]
    }


@router.post("/cleanup")
async def cleanup_expired_files():
    """Clean up expired files"""
    
    expired_count = file_storage.cleanup_expired_files()
    
    return {
        "message": f"Cleaned up {expired_count} expired files",
        "expired_count": expired_count
    }


@router.get("/storage/stats")
async def get_storage_stats():
    """Get storage statistics"""
    
    return file_storage.get_storage_stats() 