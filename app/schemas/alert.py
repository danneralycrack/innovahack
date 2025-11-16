from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AlertCreate(BaseModel):
    """Schema para crear una alerta de desviación"""
    user_id: str = Field(..., description="ID del usuario que se desvió")
    route_id: str = Field(..., description="ID de la ruta asignada")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "6918c21792cd6492dbd79515",
                "route_id": "6918c12092cd6492dbd79510"
            }
        }


class AlertResponse(BaseModel):
    """Schema de respuesta de alerta"""
    id: str = Field(..., alias="_id")
    name_user: str = Field(..., description="Nombre del usuario")
    route_name: str = Field(..., description="Nombre de la ruta")
    message: str = Field(..., description="Mensaje de la alerta")
    date: datetime = Field(..., description="Fecha y hora de la alerta")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name_user": "Agustin Apaza",
                "route_name": "Ruta 1",
                "message": "Se desvió de su ruta",
                "date": "2025-11-15T10:30:00"
            }
        }
