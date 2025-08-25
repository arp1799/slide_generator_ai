from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from enum import Enum


class SlideLayout(str, Enum):
    TITLE = "title"
    BULLET_POINTS = "bullet_points"
    TWO_COLUMN = "two_column"
    CONTENT_WITH_IMAGE = "content_with_image"


class Theme(str, Enum):
    MODERN = "modern"
    CORPORATE = "corporate"
    CREATIVE = "creative"
    MINIMAL = "minimal"


class ColorScheme(BaseModel):
    primary_color: str = "#2E86AB"
    secondary_color: str = "#A23B72"
    background_color: str = "#FFFFFF"
    text_color: str = "#333333"


class FontSettings(BaseModel):
    title_font: str = "Arial"
    body_font: str = "Calibri"
    title_size: int = 44
    body_size: int = 18


class SlideContent(BaseModel):
    title: str
    content: Optional[str] = None
    bullet_points: Optional[List[str]] = None
    left_column: Optional[str] = None
    right_column: Optional[str] = None
    image_placeholder: Optional[str] = None
    layout: SlideLayout


class SlideGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200, description="The topic for the presentation")
    num_slides: int = Field(..., ge=1, le=20, description="Number of slides to generate (1-20)")
    layout_preference: Optional[List[SlideLayout]] = None
    theme: Theme = Theme.MODERN
    color_scheme: Optional[ColorScheme] = None
    font_settings: Optional[FontSettings] = None
    custom_content: Optional[List[SlideContent]] = None
    include_citations: bool = True
    include_image_suggestions: bool = False
    
    @field_validator('num_slides')
    @classmethod
    def validate_num_slides(cls, v):
        if v < 1 or v > 20:
            raise ValueError('Number of slides must be between 1 and 20')
        return v


class SlideGenerationResponse(BaseModel):
    presentation_id: str
    filename: str
    download_url: str
    message: str
    slides_generated: int
    processing_time: float


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    timestamp: str 