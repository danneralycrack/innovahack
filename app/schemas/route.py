from pydantic import BaseModel, Field
from typing import List, Optional


class RouteSchema(BaseModel):
    """Schema para el modelo de Ruta"""
    id: Optional[str] = Field(None, alias="_id")
    name: str
    coordinates: List[List[float]]

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Ruta 1",
                "coordinates": [
                    [-63.1921473433504, -17.779723887747977],
                    [-63.19252053116273, -17.781466306413677]
                ]
            }
        }


class RouteResponse(BaseModel):
    """Schema de respuesta para Ruta"""
    id: str = Field(..., alias="_id")
    name: str
    coordinates: List[List[float]]

    class Config:
        populate_by_name = True
