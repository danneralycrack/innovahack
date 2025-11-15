from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.config.database import get_database
from app.schemas.route import RouteResponse

router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)


@router.get("/", response_model=List[RouteResponse])
async def get_routes(db=Depends(get_database)):
    """
    Obtener todas las rutas
    """
    try:
        routes_collection = db["routes"]
        routes = await routes_collection.find().to_list(length=None)
        
        # Convertir ObjectId a string
        for route in routes:
            route["_id"] = str(route["_id"])
        
        return routes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener rutas: {str(e)}")


@router.get("/{route_id}", response_model=RouteResponse)
async def get_route(route_id: str, db=Depends(get_database)):
    """
    Obtener una ruta por ID
    """
    try:
        from bson import ObjectId
        routes_collection = db["routes"]
        route = await routes_collection.find_one({"_id": ObjectId(route_id)})
        
        if not route:
            raise HTTPException(status_code=404, detail="Ruta no encontrada")
        
        route["_id"] = str(route["_id"])
        return route
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ruta: {str(e)}")
