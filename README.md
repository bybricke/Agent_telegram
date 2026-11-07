# Ecommerce Router API

## Configuración
Para ejecutar la aplicación localmente:

1. Crea un entorno virtual: `python3 -m venv .venv`
2. Actívalo: `source .venv/bin/activate`
3. Instala dependencias: `pip install -r requirements.txt`
4. Crea tu archivo `.env` basado en `.env.example` y agrega tu `GOOGLE_API_KEY`.

## Ejecución
Levanta el servidor con:
```bash
uvicorn api.app:app --reload --port 8000
```

## Pruebas
Puedes probar el endpoint de chat directamente con curl:
```bash
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user123", "texto": "¿tienen la polera azul en talla M?"}'
```

La documentación Swagger completa está disponible en: `http://localhost:8000/docs`
