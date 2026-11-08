import json
from src.router.graph import graph
from langchain_core.messages import HumanMessage

def run_tests():
    with open('tests/casos_router.json', 'r') as f:
        casos = json.load(f)

    aciertos = 0
    resultados = []

    print(f"{'Mensaje':<50} | {'Esperado':<10} | {'Obtenido':<10} | {'Status'}")
    print("-" * 90)

    for caso in casos:
        config = {"configurable": {"thread_id": "test"}}
        res = graph.invoke({"messages": [HumanMessage(content=caso['mensaje'])]}, config=config)
        
        obtenido = res.get("ruta")
        status = "✔" if obtenido == caso['esperado'] else "✘"
        if status == "✔": aciertos += 1
        
        resultados.append((caso['mensaje'], caso['esperado'], obtenido, status, res.get("motivo")))
        print(f"{caso['mensaje'][:48]:<50} | {caso['esperado']:<10} | {obtenido:<10} | {status}")

    print("-" * 90)
    print(f"Resultado final: {aciertos}/{len(casos)} ({aciertos/len(casos)*100:.1f}%)")
    
    if aciertos < len(casos):
        print("\nFallados:")
        for r in resultados:
            if r[3] == "✘":
                print(f"- {r[0]} | Esperado: {r[1]}, Obtenido: {r[2]} | Motivo: {r[4]}")

if __name__ == "__main__":
    run_tests()