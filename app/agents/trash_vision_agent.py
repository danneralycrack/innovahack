"""
Agente de Visión para Análisis de Nivel de Llenado de Carritos de Basura
Utiliza Gemini Vision AI para clasificar imágenes
"""

import google.generativeai as genai
from PIL import Image
import io
import base64
from typing import Literal
from app.config.settings import settings


class TrashBinAgent:
    """
    Agente especializado en analizar imágenes de carritos de basura
    y determinar su nivel de llenado
    """
    
    SYSTEM_PROMPT = """
Eres un experto analista de gestión de residuos. Tu tarea es analizar imágenes de bolsas, carritos o contenedores de basura y determinar su nivel de llenado.

INSTRUCCIONES:
1. Observa cuidadosamente la imagen del contenedor de basura
2. Evalúa la cantidad de residuos visible en relación con la capacidad total del contenedor
3. Clasifica el nivel de llenado de la bolsa, carrito o contenedor de 0 a 100%

FORMATO DE RESPUESTA:
Responde ÚNICAMENTE un porcentaje de llenado entre 0 y 100%.

ej: 50%

No agregues explicaciones adicionales, solo la clasificación.
"""
    
    def __init__(self):
        """Inicializar el agente con la API de Gemini"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    
    def analyze_image(self, image_data: bytes) -> str:
        """
        Analizar imagen de carrito de basura y retornar porcentaje de llenado
        
        Args:
            image_data: Bytes de la imagen (JPEG, PNG, etc.)
            
        Returns:
            str: Porcentaje de llenado (ej: "50%")
        """
        try:
            # Cargar imagen desde bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Generar respuesta con Gemini Vision
            response = self.model.generate_content([
                self.SYSTEM_PROMPT,
                image
            ])
            
            # Extraer y limpiar respuesta
            result = response.text.strip()
            
            # Extraer solo el porcentaje (buscar patrón de número + %)
            import re
            match = re.search(r'(\d+)%', result)
            
            if match:
                percentage = int(match.group(1))
                # Asegurar que esté entre 0-100
                percentage = max(0, min(100, percentage))
                return f"{percentage}%"
            else:
                # Si no se encuentra porcentaje, devolver 50% por defecto
                return "50%"
                
        except Exception as e:
            print(f"Error al analizar imagen: {str(e)}")
            raise Exception(f"Error en el análisis de imagen: {str(e)}")
            raise Exception(f"Error en el análisis de imagen: {str(e)}")
    
    
    def analyze_image_base64(self, base64_image: str) -> str:
        """
        Analizar imagen desde base64
        
        Args:
            base64_image: Imagen codificada en base64
            
        Returns:
            str: Porcentaje de llenado (ej: "50%")
        """
        try:
            # Decodificar base64 a bytes
            image_data = base64.b64decode(base64_image)
            return self.analyze_image(image_data)
        except Exception as e:
            raise Exception(f"Error al decodificar imagen base64: {str(e)}")


# Instancia global del agente
trash_agent = TrashBinAgent()
