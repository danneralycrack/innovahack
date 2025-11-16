from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class ImageAnalysisRequest(BaseModel):
    """Schema para request de análisis de imagen"""
    image_base64: str = Field(..., description="Imagen del carrito de basura en formato base64")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            }
        }


class ImageAnalysisResponse(BaseModel):
    """Schema para respuesta de análisis"""
    fill_percentage: str = Field(..., description="Porcentaje de llenado del carrito (ej: 50%)")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "fill_percentage": "50%",
                "timestamp": "2025-11-15T10:30:00"
            }
        }


class UpdateRutaCompletadaRequest(BaseModel):
    """Schema para actualizar una ruta completada"""
    volumen_porcentual: str = Field(..., description="Nuevo porcentaje de llenado (ej: 75%)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "volumen_porcentual": "85%"
            }
        }
