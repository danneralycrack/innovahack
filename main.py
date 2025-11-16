from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import connect_to_mongo, close_mongo_connection, get_database
from app.routers import users, routes, websocket_simple, assignments, tracking, agent, alerts

app = FastAPI(
    title="Innova Backend API",
    description="API para gestión de usuarios, rutas y tracking en tiempo real",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=False,  # Cambiar a False cuando allow_origins es "*"
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
    expose_headers=["*"],  # Exponer todos los headers
)


# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    # Guardar referencia a la BD en app.state para usar en WebSockets
    from app.config.database import db
    from app.config.settings import settings
    app.state.db = db.client[settings.DATABASE_NAME]


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()


# Incluir routers
app.include_router(users.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(assignments.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")  # Alertas de desviación
app.include_router(agent.router, prefix="/api")  # Agente de IA
app.include_router(tracking.router)  # WebSocket de tracking
app.include_router(websocket_simple.router)  # WebSocket de ejemplo


# Ruta raíz
@app.get("/")
async def root():
    return {
        "message": "Bienvenido a Innova Backend API",
        "version": "1.0.0",
        "endpoints": {
            "users": "/api/users",
            "routes": "/api/routes",
            "websocket_simple": "/ws/simple/{client_name}",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API funcionando correctamente"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
