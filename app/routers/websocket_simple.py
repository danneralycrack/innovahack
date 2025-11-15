from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json

router = APIRouter()

# Lista para mantener las conexiones activas
active_connections: List[WebSocket] = []


@router.websocket("/ws/simple/{client_name}")
async def websocket_simple_endpoint(websocket: WebSocket, client_name: str):
    """
    WebSocket simple de ejemplo para entender el funcionamiento.
    
    Uso:
    1. Conecta desde el navegador o cliente WebSocket a: ws://localhost:8000/ws/simple/TuNombre
    2. Envía mensajes en formato JSON: {"message": "Hola"}
    3. El servidor retransmitirá el mensaje a todos los clientes conectados
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Enviar mensaje de bienvenida
        await websocket.send_json({
            "type": "connection",
            "message": f"¡Bienvenido {client_name}! Conectado al WebSocket",
            "connected_clients": len(active_connections)
        })
        
        # Notificar a todos que un nuevo cliente se conectó
        await broadcast({
            "type": "user_joined",
            "client_name": client_name,
            "message": f"{client_name} se ha unido al chat",
            "connected_clients": len(active_connections)
        }, exclude=websocket)
        
        # Escuchar mensajes del cliente
        while True:
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                
                # Retransmitir el mensaje a todos los clientes
                await broadcast({
                    "type": "message",
                    "from": client_name,
                    "message": message_data.get("message", data),
                    "connected_clients": len(active_connections)
                })
                
            except json.JSONDecodeError:
                # Si no es JSON, enviar como texto simple
                await broadcast({
                    "type": "message",
                    "from": client_name,
                    "message": data,
                    "connected_clients": len(active_connections)
                })
    
    except WebSocketDisconnect:
        # Cliente desconectado
        active_connections.remove(websocket)
        await broadcast({
            "type": "user_left",
            "client_name": client_name,
            "message": f"{client_name} se ha desconectado",
            "connected_clients": len(active_connections)
        })


async def broadcast(message: dict, exclude: WebSocket = None):
    """
    Enviar un mensaje a todos los clientes conectados
    
    Args:
        message: Diccionario con el mensaje a enviar
        exclude: WebSocket a excluir del broadcast (opcional)
    """
    for connection in active_connections:
        if connection != exclude:
            try:
                await connection.send_json(message)
            except:
                # Si hay error al enviar, remover la conexión
                active_connections.remove(connection)
