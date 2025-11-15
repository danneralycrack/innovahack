from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class LocationUpdate(BaseModel):
    """Schema para actualización de ubicación desde app móvil"""
    type: Literal["location_update"] = "location_update"
    lat: float = Field(..., description="Latitud GPS")
    lng: float = Field(..., description="Longitud GPS")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "location_update",
                "lat": -17.779723,
                "lng": -63.192147
            }
        }


class LocationBroadcast(BaseModel):
    """Schema para broadcast de ubicación a admins"""
    type: Literal["location_update"] = "location_update"
    user_id: str
    name: str
    lat: float
    lng: float
    route_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "location_update",
                "user_id": "6918c21792cd6492dbd79515",
                "name": "Agustin Apaza",
                "lat": -17.779723,
                "lng": -63.192147,
                "route_id": "6918c12092cd6492dbd79510",
                "timestamp": "2025-11-15T10:30:00"
            }
        }


class UserStatus(BaseModel):
    """Schema para estado de conexión/desconexión"""
    type: Literal["user_connected", "user_disconnected"]
    user_id: str
    name: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ActiveUsersResponse(BaseModel):
    """Schema para lista de usuarios activos"""
    type: Literal["active_users"] = "active_users"
    users: list[dict]
