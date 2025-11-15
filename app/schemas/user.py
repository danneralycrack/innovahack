from pydantic import BaseModel, Field
from typing import Optional


class UserSchema(BaseModel):
    """Schema para el modelo de Usuario"""
    id: Optional[str] = Field(None, alias="_id")
    name: str
    phone: int
    rol: str

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Danner Aly",
                "phone": 67914341,
                "rol": "Admin"
            }
        }


class UserResponse(BaseModel):
    """Schema de respuesta para Usuario"""
    id: str = Field(..., alias="_id")
    name: str
    phone: int
    rol: str

    class Config:
        populate_by_name = True
