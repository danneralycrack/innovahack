from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from bson import ObjectId
import json
from datetime import datetime

from app.config.database import get_database
from app.services.connection_manager import manager
from app.schemas.tracking import LocationUpdate

router = APIRouter()


@router.websocket("/ws/tracker/{user_id}")
async def websocket_tracker_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket para RECOLECTORES (App Móvil)
    
    El recolector envía su ubicación GPS en tiempo real.
    
    Mensajes esperados del cliente:
    {
        "type": "location_update",
        "lat": -17.779723,
        "lng": -63.192147
    }
    """
    # Obtener información del usuario desde la BD
    db = websocket.app.state.db
    users_collection = db["users"]
    
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            await websocket.close(code=1008, reason="Usuario no encontrado")
            return
        
        user_name = user.get("name", "Usuario Desconocido")
        
        # Obtener ruta asignada (si existe)
        assignments_collection = db["assignment"]
        assignment = await assignments_collection.find_one({
            "user_id": user_id
        })
        route_id = assignment.get("route_id") if assignment else None
        
    except Exception as e:
        await websocket.close(code=1011, reason=f"Error al verificar usuario: {str(e)}")
        return
    
    # Conectar el tracker
    await manager.connect_tracker(websocket, user_id, user_name)
    
    # Actualizar estado en BD: is_online = true
    try:
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_online": True}}
        )
    except:
        pass
    
    try:
        # Enviar confirmación de conexión
        await websocket.send_json({
            "type": "connected",
            "message": f"Conectado como {user_name}",
            "user_id": user_id,
            "route_id": route_id
        })
        
        # Escuchar mensajes del cliente
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Procesar actualización de ubicación
                if message.get("type") == "location_update":
                    lat = message.get("lat")
                    lng = message.get("lng")
                    
                    if lat is not None and lng is not None:
                        # Actualizar ubicación en memoria y broadcast a admins
                        await manager.update_tracker_location(
                            user_id=user_id,
                            user_name=user_name,
                            lat=lat,
                            lng=lng,
                            route_id=route_id
                        )
                        
                        # Actualizar last_location en BD
                        try:
                            await users_collection.update_one(
                                {"_id": ObjectId(user_id)},
                                {
                                    "$set": {
                                        "last_location": {
                                            "lat": lat,
                                            "lng": lng,
                                            "updated_at": datetime.now()
                                        }
                                    }
                                }
                            )
                        except:
                            pass
                        
                        # Confirmar recepción al tracker
                        await websocket.send_json({
                            "type": "location_received",
                            "timestamp": datetime.now().isoformat()
                        })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Formato JSON inválido"
                })
    
    except WebSocketDisconnect:
        # Desconectar tracker
        await manager.disconnect_tracker(user_id, user_name)
        
        # Actualizar estado en BD: is_online = false
        try:
            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_online": False}}
            )
        except:
            pass


@router.websocket("/ws/admin/{admin_id}")
async def websocket_admin_endpoint(websocket: WebSocket, admin_id: str):
    """
    WebSocket para ADMINS (Web React)
    
    El admin solo ESCUCHA las actualizaciones de ubicación de todos los recolectores.
    Recibe automáticamente las ubicaciones en tiempo real.
    
    Mensajes que recibe:
    - Lista inicial de usuarios activos
    - Actualizaciones de ubicación en tiempo real
    - Notificaciones de conexión/desconexión
    """
    # Verificar que es admin
    db = websocket.app.state.db
    users_collection = db["users"]
    
    try:
        admin = await users_collection.find_one({"_id": ObjectId(admin_id)})
        if not admin or admin.get("rol") != "Admin":
            await websocket.close(code=1008, reason="No autorizado. Solo admins pueden conectarse")
            return
    except Exception as e:
        await websocket.close(code=1011, reason=f"Error al verificar admin: {str(e)}")
        return
    
    # Conectar admin
    await manager.connect_admin(websocket)
    
    try:
        # El admin solo escucha, no envía datos
        # Pero mantenemos la conexión abierta
        while True:
            # Recibir mensajes (aunque no se espera que el admin envíe nada)
            data = await websocket.receive_text()
            
            # Opcionalmente, puedes manejar comandos del admin aquí
            try:
                message = json.loads(data)
                
                # Ejemplo: admin pide lista actualizada de usuarios
                if message.get("type") == "get_active_users":
                    active_users = [
                        {
                            "user_id": user_id,
                            **data
                        }
                        for user_id, data in manager.tracker_locations.items()
                    ]
                    
                    await websocket.send_json({
                        "type": "active_users",
                        "users": active_users,
                        "count": len(active_users)
                    })
            
            except json.JSONDecodeError:
                pass
    
    except WebSocketDisconnect:
        manager.disconnect_admin(websocket)


@router.get("/tracking/status")
async def get_tracking_status():
    """
    Endpoint REST para obtener el estado del sistema de tracking
    """
    return {
        "active_trackers": manager.get_active_trackers_count(),
        "active_admins": manager.get_active_admins_count(),
        "tracked_users": len(manager.tracker_locations),
        "locations": manager.tracker_locations
    }
