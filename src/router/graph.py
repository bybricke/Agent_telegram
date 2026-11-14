from typing import Annotated, TypedDict, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from src.router.prompts import Decision, PROMPT_ROUTER
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=os.getenv("MODELO", "gemini-1.5-flash"), 
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
router_llm = llm.with_structured_output(Decision)

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    ruta: str
    motivo: str
    respuesta: str

def router_node(state: State):
    mensaje = state["messages"][-1].content
    decision = router_llm.invoke(f"{PROMPT_ROUTER}\n\nMensaje: {mensaje}")
    print(f"[DEBUG] Mensaje: {mensaje} | Ruta elegida: {decision.ruta}")
    return {"ruta": decision.ruta, "motivo": decision.motivo}

def format_respuesta(respuesta):
    texto = ""
    if isinstance(respuesta, list):
        for item in respuesta:
            if isinstance(item, dict) and 'text' in item: texto += item['text']
            elif hasattr(item, 'content'): texto += item.content
            else: texto += str(item)
    elif hasattr(respuesta, 'content'):
        texto = respuesta.content
    else:
        texto = str(respuesta)
    
    # Limpieza final: extraer solo el texto si el formato es JSON complejo
    texto_str = str(texto)
    if texto_str.startswith("[{") and "'text':" in texto_str:
        try:
            data = eval(texto_str)
            if isinstance(data, list) and len(data) > 0 and 'text' in data[0]:
                texto_str = data[0]['text']
        except:
            pass
    
    return {"respuesta": texto_str.strip()}

def agente_preventa(state: State):
    mensaje = state["messages"][-1].content
    prompt = f"Eres asistente preventa de ecommerce. Responde breve y útil. Mensaje: {mensaje}"
    return format_respuesta(llm.invoke(prompt))

def agente_postventa(state: State):
    mensaje = state["messages"][-1].content
    prompt = f"Eres asistente postventa de ecommerce. Responde breve y útil sobre pedidos. Mensaje: {mensaje}"
    return format_respuesta(llm.invoke(prompt))

def respuesta_generica(state: State):
    return {"respuesta": "Lo siento, solo puedo ayudarte con consultas sobre la tienda ecommerce."}

def route_condition(state: State):
    return state["ruta"]

builder = StateGraph(State)
builder.add_node("router", router_node)
builder.add_node("preventa", agente_preventa)
builder.add_node("postventa", agente_postventa)
builder.add_node("generica", respuesta_generica)

builder.add_edge(START, "router")
builder.add_conditional_edges("router", route_condition, {
    "preventa": "preventa",
    "postventa": "postventa",
    "generica": "generica"
})
builder.add_edge("preventa", END)
builder.add_edge("postventa", END)
builder.add_edge("generica", END)

# Configuración de Memoria
db_url = os.getenv("DATABASE_URL")
pool = None
memory_type = "ram"
memory = None
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

graph = builder.compile(checkpointer=memory)

async def setup_db():
    global pool, memory, memory_type, graph
    if db_url and memory_type == "ram":
        try:
            from psycopg_pool import AsyncConnectionPool
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
            
            pool = AsyncConnectionPool(
                conninfo=db_url,
                min_size=1,
                max_size=2,
                check=AsyncConnectionPool.check_connection,
                open=False
            )
            await pool.open()
            
            postgres_memory = AsyncPostgresSaver(pool)
            await postgres_memory.setup()
            
            # Recompilamos el grafo con Postgres
            memory = postgres_memory
            memory_type = "postgres"
            graph = builder.compile(checkpointer=memory)
            print("[INFO] Base de datos conectada. Usando PostgresSaver.")
        except Exception as e:
            print(f"[ERROR] Error inicializando PostgresSaver, se mantendrá memoria RAM: {e}")

async def close_db():
    global pool
    if pool is not None:
        try:
            await pool.close()
        except Exception as e:
            print(f"[ERROR] Error cerrando pool de Postgres: {e}")
