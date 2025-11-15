from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AssignmentCreate(BaseModel):
    """Schema para crear una asignación (request que recibes)"""
    user_id: str = Field(..., description="ID del usuario (recolector)")
    route_id: str = Field(..., description="ID de la ruta asignada")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "6918c21792cd6492dbd79515",
                "route_id": "6918c12092cd6492dbd79510"
            }
        }


class AssignmentSchema(BaseModel):
    """Schema completo para la colección en MongoDB"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    route_id: str
    assigned_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="active")  # active, completed, cancelled

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": "6918c21792cd6492dbd79515",
                "route_id": "6918c12092cd6492dbd79510",
                "assigned_at": "2025-11-15T10:30:00",
                "status": "active"
            }
        }


class AssignmentResponse(BaseModel):
    """Schema de respuesta"""
    id: str = Field(..., alias="_id")
    user_id: str
    route_id: str
    assigned_at: datetime

    class Config:
        populate_by_name = True
