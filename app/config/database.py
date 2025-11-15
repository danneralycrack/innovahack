from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings


class Database:
    client: AsyncIOMotorClient = None
    

db = Database()


async def get_database():
    return db.client[settings.DATABASE_NAME]


async def connect_to_mongo():
    """Conectar a MongoDB al iniciar la aplicación"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    print("✅ Conectado a MongoDB")


async def close_mongo_connection():
    """Cerrar conexión a MongoDB al apagar la aplicación"""
    db.client.close()
    print("❌ Conexión a MongoDB cerrada")
