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

# Inicialización del modelo con clave explícita
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

def agente_preventa(state: State):
    mensaje = state["messages"][-1].content
    prompt = (
        "Eres un asistente de preventa de ecommerce. Responde breve y útil. "
        f"Mensaje: {mensaje}"
    )
    respuesta = llm.invoke(prompt)
    texto = respuesta.content if hasattr(respuesta, 'content') else str(respuesta)
    return {"respuesta": texto.strip()}

def agente_postventa(state: State):
    mensaje = state["messages"][-1].content
    prompt = (
        "Eres un asistente de postventa de ecommerce. Responde breve y útil sobre pedidos. "
        f"Mensaje: {mensaje}"
    )
    respuesta = llm.invoke(prompt)
    texto = respuesta.content if hasattr(respuesta, 'content') else str(respuesta)
    return {"respuesta": texto.strip()}

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

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
