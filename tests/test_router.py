import pytest
import json
from src.router.graph import graph
from langchain_core.messages import HumanMessage

def cargar_casos():
    with open("tests/casos_router.json", "r") as f:
        return json.load(f)

@pytest.mark.parametrize("caso", cargar_casos())
def test_router_casos(caso):
    result = graph.invoke({"messages": [HumanMessage(content=caso["mensaje"])]})
    assert result["ruta"] == caso["esperado"]

def test_router_performance():
    casos = cargar_casos()
    aciertos = 0
    for caso in casos:
        result = graph.invoke({"messages": [HumanMessage(content=caso["mensaje"])]})
        if result["ruta"] == caso["esperado"]:
            aciertos += 1
            
    assert aciertos >= 13
