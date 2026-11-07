from fastapi import FastAPI, Request, HTTPException, status, Header
from pydantic import BaseModel, Field
import os
import logging
import httpx
from dotenv import load_dotenv
from src.router.graph import graph
from langchain_core.messages import HumanMessage

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_SECRET = os.getenv("TELEGRAM_SECRET")

tags_metadata = [
    {"name": "salud", "description": "Comprobaciones del estado del sistema."},
    {"name": "chat", "description": "Interacción con el agente router."},
    {"name": "telegram", "description": "Webhook de Telegram."},
]

app = FastAPI(
    title="Ecommerce Router API",
    description="API para gestionar el enrutamiento de consultas de un ecommerce.",
    version="1.0.0",
    openapi_tags=tags_metadata
)

class ChatRequest(BaseModel):
    user_id: str = Field(..., example="user_123", description="ID único del usuario.")
    texto: str = Field(..., example="¿tienen la polera azul en talla M?", description="Mensaje del usuario.")

@app.get("/health", tags=["salud"])
async def health():
    return {"ok": True, "modelo": os.getenv("MODELO", "gemini-1.5-flash")}

@app.post("/chat", tags=["chat"])
async def chat(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.user_id}}
        result = graph.invoke({"messages": [HumanMessage(content=request.texto)]}, config=config)
        return result
    except Exception as e:
        logger.error(f"Error procesando chat: {e}")
        raise HTTPException(status_code=502, detail="Error en el servicio de IA.")

@app.post("/telegram", tags=["telegram"], include_in_schema=False)
async def telegram_webhook(
    request: Request, 
    x_telegram_bot_api_secret_token: str = Header(None)
):
    if x_telegram_bot_api_secret_token != TELEGRAM_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Secret mismatch")

    update = await request.json()
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    if not chat_id or not text:
        return {"ok": True}

    # Procesar en background/async
    async def process_message(chat_id, text):
        try:
            config = {"configurable": {"thread_id": str(chat_id)}}
            result = graph.invoke({"messages": [HumanMessage(content=text)]}, config=config)
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    json={"chat_id": chat_id, "text": result.get("respuesta")}
                )
        except Exception as e:
            logger.error(f"Error en procesamiento de webhook: {e}")

    import asyncio
    asyncio.create_task(process_message(chat_id, text))
    
    return {"ok": True}
