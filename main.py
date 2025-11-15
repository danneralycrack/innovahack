from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import connect_to_mongo, close_mongo_connection
from app.routers import users, routes, websocket_simple

app = FastAPI(
    title="Innova Backend API",
    description="API para gestión de usuarios, rutas y tracking en tiempo real",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()


# Incluir routers
app.include_router(users.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(websocket_simple.router)


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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
