import json
import pytest
from src.router.graph import graph
from langchain_core.messages import HumanMessage

def load_casos():
    with open('tests/casos_router.json', 'r') as f:
        return json.load(f)

@pytest.mark.parametrize("caso", load_casos())
def test_router(caso):
    config = {"configurable": {"thread_id": "test"}}
    res = graph.invoke({"messages": [HumanMessage(content=caso['mensaje'])]}, config=config)
    assert res.get("ruta") == caso['esperado'], f"Fallo en: {caso['mensaje']}"

def test_minimo_aciertos():
    casos = load_casos()
    aciertos = 0
    for caso in casos:
        config = {"configurable": {"thread_id": "test"}}
        res = graph.invoke({"messages": [HumanMessage(content=caso['mensaje'])]}, config=config)
        if res.get("ruta") == caso['esperado']:
            aciertos += 1
    
    # Exigir al menos 13/15 (86.6%)
    assert aciertos >= 13, f"Solo se obtuvieron {aciertos} de {len(casos)} aciertos"