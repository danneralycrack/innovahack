from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.config.database import get_database
from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=List[UserResponse])
async def get_users(db=Depends(get_database)):
    """
    Obtener todos los usuarios
    """
    try:
        users_collection = db["users"]
        users = await users_collection.find().to_list(length=None)
        
        # Convertir ObjectId a string
        for user in users:
            user["_id"] = str(user["_id"])
        
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db=Depends(get_database)):
    """
    Obtener un usuario por ID
    """
    try:
        from bson import ObjectId
        users_collection = db["users"]
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")


#@router.post("/assign-route")