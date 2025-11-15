from fastapi import WebSocket
from typing import Dict, List
from datetime import datetime
import json


class ConnectionManager:
    """
    Gestor de conexiones WebSocket para tracking en tiempo real
    Maneja conexiones de recolectores y admins por separado
    """
    
    def __init__(self):
        # Diccionario: {user_id: WebSocket}
        self.active_trackers: Dict[str, WebSocket] = {}
        
        # Lista de WebSockets de admins
        self.active_admins: List[WebSocket] = []
        
        # Diccionario: {user_id: {name, lat, lng, route_id, last_update}}
        self.tracker_locations: Dict[str, dict] = {}
    
    
    async def connect_tracker(self, websocket: WebSocket, user_id: str, user_name: str):
        """Conectar un recolector"""
        await websocket.accept()
        self.active_trackers[user_id] = websocket
        
        # Notificar a todos los admins que un recolector se conectó
        await self.broadcast_to_admins({
            "type": "user_connected",
            "user_id": user_id,
            "name": user_name,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"✅ Tracker conectado: {user_name} ({user_id})")
    
    
    async def disconnect_tracker(self, user_id: str, user_name: str):
        """Desconectar un recolector"""
        if user_id in self.active_trackers:
            del self.active_trackers[user_id]
        
        if user_id in self.tracker_locations:
            del self.tracker_locations[user_id]
        
        # Notificar a todos los admins que un recolector se desconectó
        await self.broadcast_to_admins({
            "type": "user_disconnected",
            "user_id": user_id,
            "name": user_name,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"❌ Tracker desconectado: {user_name} ({user_id})")
    
    
    async def connect_admin(self, websocket: WebSocket):
        """Conectar un admin"""
        await websocket.accept()
        self.active_admins.append(websocket)
        
        # Enviar lista de usuarios activos al admin recién conectado
        active_users = [
            {
                "user_id": user_id,
                **data
            }
            for user_id, data in self.tracker_locations.items()
        ]
        
        await websocket.send_json({
            "type": "active_users",
            "users": active_users,
            "count": len(active_users)
        })
        
        print(f"✅ Admin conectado. Total admins: {len(self.active_admins)}")
    
    
    def disconnect_admin(self, websocket: WebSocket):
        """Desconectar un admin"""
        if websocket in self.active_admins:
            self.active_admins.remove(websocket)
        
        print(f"❌ Admin desconectado. Total admins: {len(self.active_admins)}")
    
    
    async def update_tracker_location(self, user_id: str, user_name: str, lat: float, lng: float, route_id: str = None):
        """
        Actualizar ubicación de un recolector y hacer broadcast a admins
        """
        # Guardar en memoria
        self.tracker_locations[user_id] = {
            "name": user_name,
            "lat": lat,
            "lng": lng,
            "route_id": route_id,
            "last_update": datetime.now().isoformat()
        }
        
        # Broadcast a todos los admins
        await self.broadcast_to_admins({
            "type": "location_update",
            "user_id": user_id,
            "name": user_name,
            "lat": lat,
            "lng": lng,
            "route_id": route_id,
            "timestamp": datetime.now().isoformat()
        })
    
    
    async def broadcast_to_admins(self, message: dict):
        """Enviar mensaje a todos los admins conectados"""
        disconnected_admins = []
        
        for admin_ws in self.active_admins:
            try:
                await admin_ws.send_json(message)
            except Exception as e:
                print(f"Error enviando a admin: {e}")
                disconnected_admins.append(admin_ws)
        
        # Limpiar admins desconectados
        for admin_ws in disconnected_admins:
            self.disconnect_admin(admin_ws)
    
    
    def get_active_trackers_count(self) -> int:
        """Obtener cantidad de recolectores activos"""
        return len(self.active_trackers)
    
    
    def get_active_admins_count(self) -> int:
        """Obtener cantidad de admins conectados"""
        return len(self.active_admins)


# Instancia global del gestor
manager = ConnectionManager()
