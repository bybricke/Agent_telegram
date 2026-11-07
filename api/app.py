from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel, Field
import os
import logging
from dotenv import load_dotenv
from src.router.graph import graph
from langchain_core.messages import HumanMessage

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags_metadata = [
    {"name": "salud", "description": "Comprobaciones del estado del sistema."},
    {"name": "chat", "description": "Interacción con el agente router."},
    {"name": "telegram", "description": "Webhook de Telegram."},
]

app = FastAPI(
    title="Ecommerce Router API",
    description="API para gestionar el enrutamiento de consultas de un ecommerce en preventa, postventa o genérica.",
    version="1.0.0",
    openapi_tags=tags_metadata
)

class ChatRequest(BaseModel):
    user_id: str = Field(..., example="user_123", description="ID único del usuario para mantener la sesión.")
    texto: str = Field(..., example="¿tienen la polera azul en talla M?", description="Mensaje del usuario al agente.")

class ChatResponse(BaseModel):
    ruta: str = Field(..., example="preventa", description="Agente destino elegido.")
    motivo: str = Field(..., example="El usuario pregunta por la disponibilidad de un producto.", description="Razón de la clasificación.")
    respuesta: str = Field(..., example="Soy el agente de preventa. Recibí: ¿tienen la polera azul en talla M?. Pronto podré ayudarte con productos y compras.", description="Respuesta del agente.")

@app.get("/health", tags=["salud"])
async def health():
    return {"ok": True, "modelo": os.getenv("MODELO", "gemini-1.5-flash")}

@app.post("/chat", response_model=ChatResponse, tags=["chat"], responses={
    200: {"description": "Consulta procesada exitosamente."},
    422: {"description": "Error de validación de datos."},
    502: {"description": "Error en el servicio de IA."}
})
async def chat(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.user_id}}
        result = graph.invoke({"messages": [HumanMessage(content=request.texto)]}, config=config)
        return {
            "ruta": result.get("ruta"),
            "motivo": result.get("motivo"),
            "respuesta": result.get("respuesta")
        }
    except Exception as e:
        logger.error(f"Error procesando chat para {request.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ocurrió un error al procesar tu solicitud. Por favor intenta más tarde."
        )

@app.post("/telegram", tags=["telegram"], include_in_schema=False)
async def telegram_webhook(request: Request):
    return {"ok": True}
