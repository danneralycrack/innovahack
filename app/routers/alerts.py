from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId
from app.config.database import get_database
from app.schemas.alert import AlertCreate, AlertResponse

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(alert: AlertCreate, db=Depends(get_database)):
    """
    Crear una alerta de desviación de ruta
    
    Recibe user_id y route_id, consulta las colecciones para obtener nombres
    y registra una alerta con el mensaje "Se desvió de su ruta"
    
    - **user_id**: ID del usuario (recolector)
    - **route_id**: ID de la ruta asignada
    """
    try:
        # Consultar nombre del usuario
        users_collection = db["users"]
        user = await users_collection.find_one({"_id": ObjectId(alert.user_id)})
        
        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"Usuario con ID {alert.user_id} no encontrado"
            )
        
        name_user = user.get("name", "Usuario Desconocido")
        
        # Consultar nombre de la ruta
        routes_collection = db["routes"]
        route = await routes_collection.find_one({"_id": ObjectId(alert.route_id)})
        
        if not route:
            raise HTTPException(
                status_code=404, 
                detail=f"Ruta con ID {alert.route_id} no encontrada"
            )
        
        route_name = route.get("name", "Ruta Desconocida")
        
        # Crear documento de alerta
        alerts_collection = db["alertas"]
        new_alert = {
            "name_user": name_user,
            "route_name": route_name,
            "message": "Se desvió de su ruta",
            "date": datetime.now()
        }
        
        result = await alerts_collection.insert_one(new_alert)
        
        # Retornar alerta creada
        created_alert = await alerts_collection.find_one({"_id": result.inserted_id})
        created_alert["_id"] = str(created_alert["_id"])
        
        return AlertResponse(**created_alert)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al crear alerta: {str(e)}"
        )


@router.get("/", response_model=List[AlertResponse])
async def get_all_alerts(db=Depends(get_database)):
    """
    Obtener todas las alertas registradas
    """
    try:
        alerts_collection = db["alertas"]
        alerts = await alerts_collection.find().sort("date", -1).to_list(length=None)
        
        # Convertir ObjectId a string
        for alert in alerts:
            alert["_id"] = str(alert["_id"])
        
        return alerts
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener alertas: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[AlertResponse])
async def get_alerts_by_user(user_id: str, db=Depends(get_database)):
    """
    Obtener todas las alertas de un usuario específico
    """
    try:
        # Obtener nombre del usuario
        users_collection = db["users"]
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        name_user = user.get("name")
        
        # Buscar alertas por nombre de usuario
        alerts_collection = db["alertas"]
        alerts = await alerts_collection.find({"name_user": name_user}).sort("date", -1).to_list(length=None)
        
        # Convertir ObjectId a string
        for alert in alerts:
            alert["_id"] = str(alert["_id"])
        
        return alerts
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener alertas del usuario: {str(e)}"
        )


@router.get("/route/{route_id}", response_model=List[AlertResponse])
async def get_alerts_by_route(route_id: str, db=Depends(get_database)):
    """
    Obtener todas las alertas de una ruta específica
    """
    try:
        # Obtener nombre de la ruta
        routes_collection = db["routes"]
        route = await routes_collection.find_one({"_id": ObjectId(route_id)})
        
        if not route:
            raise HTTPException(status_code=404, detail="Ruta no encontrada")
        
        route_name = route.get("name")
        
        # Buscar alertas por nombre de ruta
        alerts_collection = db["alertas"]
        alerts = await alerts_collection.find({"route_name": route_name}).sort("date", -1).to_list(length=None)
        
        # Convertir ObjectId a string
        for alert in alerts:
            alert["_id"] = str(alert["_id"])
        
        return alerts
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener alertas de la ruta: {str(e)}"
        )


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(alert_id: str, db=Depends(get_database)):
    """
    Eliminar una alerta por ID
    """
    try:
        alerts_collection = db["alertas"]
        result = await alerts_collection.delete_one({"_id": ObjectId(alert_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Alerta no encontrada")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar alerta: {str(e)}"
        )
