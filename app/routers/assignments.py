from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId
from app.config.database import get_database
from app.schemas.assignment import AssignmentCreate, AssignmentResponse

router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(assignment: AssignmentCreate, db=Depends(get_database)):
    """
    Crear una nueva asignación de ruta a usuario
    
    - **user_id**: ID del usuario (recolector)
    - **route_id**: ID de la ruta a asignar
    """
    try:
        # Verificar que el usuario existe
        users_collection = db["users"]
        user = await users_collection.find_one({"_id": ObjectId(assignment.user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar que la ruta existe
        routes_collection = db["routes"]
        route = await routes_collection.find_one({"_id": ObjectId(assignment.route_id)})
        if not route:
            raise HTTPException(status_code=404, detail="Ruta no encontrada")
        
        # Actualizar el atributo assigned de la ruta a 1
        await routes_collection.update_one(
            {"_id": ObjectId(assignment.route_id)},
            {"$set": {"assigned": 1}}
        )

        # Crear la asignación
        assignments_collection = db["assignment"]
        new_assignment = {
            "user_id": assignment.user_id,
            "route_id": assignment.route_id,
            "assigned_at": datetime.now()
        }
        
        result = await assignments_collection.insert_one(new_assignment)
        
        # Obtener el documento creado
        created_assignment = await assignments_collection.find_one({"_id": result.inserted_id})
        created_assignment["_id"] = str(created_assignment["_id"])
        
        return created_assignment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear asignación: {str(e)}")


@router.get("/", response_model=List[AssignmentResponse])
async def get_assignments(db=Depends(get_database)):
    """
    Obtener todas las asignaciones
    """
    try:
        assignments_collection = db["assignment"]
        assignments = await assignments_collection.find().to_list(length=None)
        
        # Convertir ObjectId a string
        for assignment in assignments:
            assignment["_id"] = str(assignment["_id"])
        
        return assignments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener asignaciones: {str(e)}")


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(assignment_id: str, db=Depends(get_database)):
    """
    Obtener una asignación por ID
    """
    try:
        assignments_collection = db["assignment"]
        assignment = await assignments_collection.find_one({"_id": ObjectId(assignment_id)})
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        assignment["_id"] = str(assignment["_id"])
        return assignment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener asignación: {str(e)}")


@router.get("/user/{user_id}", response_model=List[AssignmentResponse])
async def get_assignments_by_user(user_id: str, db=Depends(get_database)):
    """
    Obtener todas las asignaciones de un usuario
    """
    try:
        assignments_collection = db["assignment"]
        assignments = await assignments_collection.find({"user_id": user_id}).to_list(length=None)
        
        # Convertir ObjectId a string
        for assignment in assignments:
            assignment["_id"] = str(assignment["_id"])
        
        return assignments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener asignaciones: {str(e)}")


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(assignment_id: str, db=Depends(get_database)):
    """
    Eliminar una asignación
    """
    try:
        assignments_collection = db["assignment"]
        result = await assignments_collection.delete_one({"_id": ObjectId(assignment_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar asignación: {str(e)}")
