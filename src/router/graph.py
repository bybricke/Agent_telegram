from typing import Annotated, TypedDict, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
# from src.router.graph import graph
from src.router.prompts import Decision, PROMPT_ROUTER
import os

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    ruta: str
    motivo: str
    respuesta: str

llm = ChatGoogleGenerativeAI(model=os.getenv("MODELO", "gemini-1.5-flash"), temperature=0)
router_llm = llm.with_structured_output(Decision)

def router_node(state: State):
    mensaje = state["messages"][-1].content
    decision = router_llm.invoke(f"{PROMPT_ROUTER}\n\nMensaje: {mensaje}")
    return {"ruta": decision.ruta, "motivo": decision.motivo}

def agente_preventa(state: State):
    mensaje = state["messages"][-1].content
    respuesta = llm.invoke(f"Eres un asistente de preventa de una tienda. Responde amablemente al cliente: {mensaje}")
    return {"respuesta": respuesta.content}

def agente_postventa(state: State):
    mensaje = state["messages"][-1].content
    respuesta = llm.invoke(f"Eres un asistente de postventa de una tienda. Ayuda al cliente con su problema: {mensaje}")
    return {"respuesta": respuesta.content}

def respuesta_generica(state: State):
    return {"respuesta": "Este chat es para la tienda, lo siento pero no puedo ayudarte con temas ajenos al ecommerce."}

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
