from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from app.schemas.agent import ImageAnalysisRequest, ImageAnalysisResponse
from app.agents.trash_vision_agent import trash_agent
from datetime import datetime
import base64

router = APIRouter(
    prefix="/agent",
    tags=["AI Agent"]
)


@router.post("/analyze-trash-bin", response_model=ImageAnalysisResponse)
async def analyze_trash_bin_image(request: ImageAnalysisRequest):
    """
    Analizar imagen de carrito de basura con IA (Gemini Vision)
    
    Recibe una imagen en base64 y retorna el porcentaje de llenado.
    
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
async def analyze_trash_bin_file(file: UploadFile = File(...)):
    """
    Analizar imagen de carrito de basura subiendo archivo directamente
    
    Acepta formatos: JPG, JPEG, PNG, WEBP
    
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
        
        # Analizar con el agente
        fill_percentage = trash_agent.analyze_image(image_bytes)
        
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
            "model": "gemini-2.0-flash",
            "api_key_configured": api_key_configured,
            "message": "Agente listo para analizar imágenes" if api_key_configured else "⚠️ Configura GEMINI_API_KEY en .env"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
