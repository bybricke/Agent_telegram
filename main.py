import argparse
import sys
import importlib

def main():
    parser = argparse.ArgumentParser(description="Ejecutor de agentes LangGraph")
    parser.add_argument("agente", help="Nombre de la carpeta del agente en src/")
    parser.add_argument("mensaje", help="Mensaje para el agente")
    parser.add_argument("--saltos", action="store_true", help="Imprimir nodos recorridos")
    parser.add_argument("--diagrama", action="store_true", help="Imprimir el diagrama Mermaid")
    
    args = parser.parse_args()
    
    try:
        graph_module = importlib.import_module(f"src.{args.agente}.graph")
        graph = graph_module.graph
        
        if args.diagrama:
            print(graph.get_graph().draw_mermaid())
            return

        config = {"configurable": {"thread_id": "1"}}
        inputs = {"messages": [("user", args.mensaje)]}
        
        for output in graph.stream(inputs, config=config):
            if args.saltos:
                print(f"Nodo alcanzado: {list(output.keys())[0]}")
            
    except ImportError:
        print(f"Error: No se pudo encontrar el agente '{args.agente}'")
    except Exception as e:
        print(f"Error al ejecutar el agente: {e}")

if __name__ == "__main__":
    main()
