import json
import importlib
from langchain_core.messages import HumanMessage

def test_router():
    with open("tests/casos_router.json", "r") as f:
        casos = json.load(f)
    
    graph_module = importlib.import_module("src.router.graph")
    graph = graph_module.graph
    
    resultados = []
    aciertos = 0
    
    print(f"{'Mensaje':<45} | {'Esperado':<10} | {'Obtenido':<10} | {'Res'}")
    print("-" * 80)
    
    for i, caso in enumerate(casos):
        m, esperado = caso["mensaje"], caso["esperado"]
        config = {"configurable": {"thread_id": f"test_{i}"}}
        result = graph.invoke({"messages": [HumanMessage(content=m)]}, config=config)
        obtenido = result.get("ruta")
        motivo = result.get("motivo")
        
        ok = obtenido == esperado
        if ok: aciertos += 1
        else: resultados.append((m, esperado, obtenido, motivo))
        
        print(f"{m:<45} | {esperado:<10} | {obtenido:<10} | {'✔' if ok else '✘'}")
        
    print(f"\nResumen: {aciertos}/{len(casos)} ({aciertos/len(casos)*100:.1f}%)")
    
    if resultados:
        print("\nFallos:")
        for m, esp, obt, mot in resultados:
            print(f"- {m}: Esperado {esp}, Obtuvo {obt} (Motivo: {mot})")

if __name__ == "__main__":
    test_router()
