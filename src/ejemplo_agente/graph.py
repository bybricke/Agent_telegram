from langchain_core.messages import BaseMessage
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from src.ejemplo_agente.prompts import PROMPT_NODO_1

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def nodo_1(state: State):
    # Aquí usarías el PROMPT_NODO_1 y llamarías al modelo
    return {"messages": [("ai", f"Respuesta basada en: {PROMPT_NODO_1}")]}

builder = StateGraph(State)
builder.add_node("nodo_1", nodo_1)
builder.add_edge(START, "nodo_1")
builder.add_edge("nodo_1", END)

graph = builder.compile()
