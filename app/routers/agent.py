from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from app.schemas.agent import ImageAnalysisRequest, ImageAnalysisResponse, UpdateRutaCompletadaRequest
from app.agents.trash_vision_agent import trash_agent
from app.config.database import get_database
from datetime import datetime, timedelta
from bson import ObjectId
import base64

router = APIRouter(
    prefix="/agent",
    tags=["AI Agent"]
)


@router.post("/analyze-trash-bin", response_model=ImageAnalysisResponse)
async def analyze_trash_bin_image(request: ImageAnalysisRequest, db=Depends(get_database)):
    """
    Analizar imagen de carrito de basura con IA (Gemini Vision)
    
    Recibe una imagen en base64 y retorna el porcentaje de llenado.
    Guarda el resultado en la colección "rutas_completadas".
    
    **Ejemplo de uso:**
    ```python
    import base64
    import requests
    
    # Leer imagen
    with open("carrito.jpg", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()
    
    # Enviar a API
    response = requests.post(
        "http://localhost:8000/api/agent/analyze-trash-bin",
        json={"image_base64": image_base64}
    )
    print(response.json())
    # Salida: {"fill_percentage": "50%", "timestamp": "..."}
    ```
    """
    try:
        # Analizar imagen con el agente
        fill_percentage = trash_agent.analyze_image_base64(request.image_base64)
        
        print(f"📊 Porcentaje analizado: {fill_percentage}")
        
        # Guardar en la colección "rutas_completadas"
        rutas_completadas_collection = db["rutas_completadas"]
        bolivia_time = datetime.utcnow() - timedelta(hours=4)
     
        nuevo_documento = {
            "nombre": "Juan Agustin",
            "ruta": "Ruta 5 - UPSA",
            "foto_base64": request.image_base64,
            "volumen_porcentual": fill_percentage,
            "timestamp": bolivia_time
        }
        
        print(f"💾 Intentando guardar en rutas_completadas...")
        result = await rutas_completadas_collection.insert_one(nuevo_documento)
        print(f"✅ Documento guardado con ID: {result.inserted_id}")
        
        return ImageAnalysisResponse(
            fill_percentage=fill_percentage,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al analizar la imagen: {str(e)}"
        )


@router.post("/analyze-trash-bin-file")
async def analyze_trash_bin_file(file: UploadFile = File(...), db=Depends(get_database)):
    """
    Analizar imagen de carrito de basura subiendo archivo directamente
    
    Acepta formatos: JPG, JPEG, PNG, WEBP
    Guarda el resultado en la colección "rutas_completadas".
    
    **Ejemplo con curl:**
    ```bash
    curl -X POST "http://localhost:8000/api/agent/analyze-trash-bin-file" \
         -H "accept: application/json" \
         -H "Content-Type: multipart/form-data" \
         -F "file=@carrito.jpg"
    ```
    """
    try:
        # Validar tipo de archivo
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser una imagen (JPG, PNG, WEBP)"
            )
        
        # Leer bytes de la imagen
        image_bytes = await file.read()
        
        # Convertir a base64 para guardar en BD
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Analizar con el agente
        fill_percentage = trash_agent.analyze_image(image_bytes)
        
        print(f"📊 Porcentaje analizado: {fill_percentage}")
        
        # Guardar en la colección "rutas_completadas"
        rutas_completadas_collection = db["rutas_completadas"]
        nuevo_documento = {
            "nombre": "Juan Agustin",
            "ruta": "Ruta 5 - UPSA",
            "foto_base64": image_base64,
            "volumen_porcentual": fill_percentage,
            "timestamp": datetime.now()
        }
        
        print(f"💾 Intentando guardar en rutas_completadas...")
        result = await rutas_completadas_collection.insert_one(nuevo_documento)
        print(f"✅ Documento guardado con ID: {result.inserted_id}")
        
        return ImageAnalysisResponse(
            fill_percentage=fill_percentage,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la imagen: {str(e)}"
        )


@router.get("/rutas-completadas")
async def get_rutas_completadas(db=Depends(get_database)):
    """
    Obtener todos los registros de rutas completadas
    
    Retorna la lista de análisis guardados con nombre, foto en base64 y volumen porcentual.
    """
    try:
        rutas_completadas_collection = db["rutas_completadas"]
        
        # Obtener todos los documentos
        rutas = await rutas_completadas_collection.find().to_list(length=None)
        
        # Convertir ObjectId a string
        for ruta in rutas:
            ruta["_id"] = str(ruta["_id"])
        
        return {
            "total": len(rutas),
            "rutas_completadas": rutas
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener rutas completadas: {str(e)}"
        )


@router.patch("/rutas-completadas/{ruta_id}")
async def update_ruta_completada(
    ruta_id: str,
    update_data: UpdateRutaCompletadaRequest,
    db=Depends(get_database)
):
    """
    Actualizar volumen porcentual de una ruta completada
    
    - **ruta_id**: ID del documento a actualizar
    - **volumen_porcentual**: Nuevo porcentaje de llenado
    
    **Ejemplo:**
    ```
    PATCH /api/agent/rutas-completadas/691966ffab69f8db8601d70d
    {
      "volumen_porcentual": "85%"
    }
    ```
    """
    try:
        rutas_completadas_collection = db["rutas_completadas"]
        
        # Verificar que el ID sea válido
        if not ObjectId.is_valid(ruta_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de ruta inválido"
            )
        
        # Actualizar documento
        result = await rutas_completadas_collection.update_one(
            {"_id": ObjectId(ruta_id)},
            {
                "$set": {
                    "volumen_porcentual": update_data.volumen_porcentual,
                    "updated_at": datetime.now()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ruta completada con ID {ruta_id} no encontrada"
            )
        
        # Obtener documento actualizado
        updated_ruta = await rutas_completadas_collection.find_one({"_id": ObjectId(ruta_id)})
        updated_ruta["_id"] = str(updated_ruta["_id"])
        
        return {
            "message": "Volumen porcentual actualizado exitosamente",
            "ruta_completada": updated_ruta
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar ruta completada: {str(e)}"
        )


@router.get("/health")
async def agent_health_check():
    """Verificar que el agente de IA está funcionando"""
    try:
        # Verificar que la API key está configurada
        from app.config.settings import settings
        api_key_configured = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here")
        
        return {
            "status": "ok" if api_key_configured else "warning",
            "agent": "Trash Vision AI",
            "model": "gemini-2.5-flash",
            "api_key_configured": api_key_configured,
            "message": "Agente listo para analizar imágenes" if api_key_configured else "⚠️ Configura GEMINI_API_KEY en .env"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
