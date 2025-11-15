# 🚀 Innova Backend API

Backend desarrollado con FastAPI y MongoDB para gestión de usuarios, rutas y tracking en tiempo real con WebSockets.

## 📁 Estructura del Proyecto

```
backend-innova/
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py       # Configuración de MongoDB
│   │   └── settings.py       # Variables de entorno
│   ├── models/
│   │   └── __init__.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── users.py          # Endpoints de usuarios
│   │   ├── routes.py         # Endpoints de rutas
│   │   └── websocket_simple.py  # WebSocket de ejemplo
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py           # Schemas de usuarios
│   │   └── route.py          # Schemas de rutas
│   └── services/
│       └── __init__.py
├── main.py                   # Aplicación principal
├── requirements.txt          # Dependencias
├── .env                      # Variables de entorno (no subir a git)
├── .env.example             # Ejemplo de variables de entorno
├── .gitignore
└── test_websocket.html      # Cliente de prueba para WebSocket
```

## 🔧 Instalación

### 1. Crear entorno virtual

```powershell
python -m venv venv
```

### 2. Activar entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Edita el archivo `.env` y reemplaza `<db_password>` con tu contraseña real de MongoDB:

```env
MONGODB_URL=mongodb+srv://danner:TU_PASSWORD_AQUI@cluster0.hffv09d.mongodb.net/?appName=Cluster0
DATABASE_NAME=innova_db
```

## 🚀 Ejecutar el Proyecto

```powershell
python main.py
```

O con uvicorn directamente:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: http://localhost:8000

## 📚 Documentación API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints Disponibles

### REST API

#### Usuarios
- `GET /api/users` - Obtener todos los usuarios
- `GET /api/users/{user_id}` - Obtener un usuario por ID

#### Rutas
- `GET /api/routes` - Obtener todas las rutas
- `GET /api/routes/{route_id}` - Obtener una ruta por ID

### WebSocket

#### WebSocket Simple (Ejemplo)
- `WS /ws/simple/{client_name}` - WebSocket de ejemplo para chat en tiempo real

**Cómo probar el WebSocket:**

1. Asegúrate de que el servidor esté corriendo
2. Abre el archivo `test_websocket.html` en tu navegador
3. Ingresa tu nombre y haz clic en "Conectar"
4. Abre varias pestañas para simular múltiples clientes
5. Envía mensajes y verás cómo se transmiten en tiempo real

**O usa la consola del navegador:**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/simple/TuNombre');

ws.onopen = () => {
    console.log('Conectado!');
    ws.send(JSON.stringify({ message: 'Hola desde el navegador' }));
};

ws.onmessage = (event) => {
    console.log('Mensaje recibido:', JSON.parse(event.data));
};
```

## 📊 Estructura de Datos MongoDB

### Colección: users

```json
{
  "_id": ObjectId,
  "name": "string",
  "phone": number,
  "rol": "string"  // "Admin" o "Recolector"
}
```

### Colección: routes

```json
{
  "_id": ObjectId,
  "name": "string",
  "coordinates": [[longitude, latitude], ...]
}
```

## 🔮 Próximos Pasos

- [ ] Implementar WebSocket para tracking en tiempo real de recolectores
- [ ] Endpoint para actualizar ubicación de recolectores
- [ ] Sistema de notificaciones para desviaciones de ruta
- [ ] Autenticación y autorización
- [ ] CRUD completo para usuarios y rutas

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **Motor**: Driver asíncrono de MongoDB
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI
- **WebSockets**: Comunicación en tiempo real

## 📝 Notas

- El WebSocket simple es para entender el funcionamiento básico
- Próximamente se implementará el WebSocket complejo con lógica de tracking
- Asegúrate de tener acceso a la base de datos MongoDB Atlas
