import argparse
import importlib
import sys
import asyncio
from src.router.graph import setup_db, close_db

async def main():
    parser = argparse.ArgumentParser(description="Ejecutar agentes de LangGraph.")
    parser.add_argument("agent", type=str, help="Nombre del agente a ejecutar")
    parser.add_argument("message", type=str, help="Mensaje a enviar al agente", nargs="?", default="")
    parser.add_argument("--hilo", type=str, help="El ID del hilo para mantener la memoria de la conversación", default="cli_thread_1")
    parser.add_argument("--saltos", action="store_true", help="Imprime los nodos por los que pasó el grafo")
    parser.add_argument("--diagrama", action="store_true", help="Imprime el Mermaid del grafo sin ejecutarlo")
    
    args = parser.parse_args()
    agent_name = args.agent
    message = args.message
    thread_id = args.hilo

    try:
        agent_module = importlib.import_module(f"src.{agent_name}.graph")
        graph = agent_module.graph
    except ImportError as e:
        print(f"Error al cargar el agente '{agent_name}': {e}")
        sys.exit(1)

    if args.diagrama:
        try:
            print(f"Diagrama Mermaid para {agent_name}:\n")
            print(graph.get_graph().draw_mermaid())
        except Exception as e:
            print(f"No se pudo generar el diagrama: {e}")
        return

    if not message:
        print("Se requiere un mensaje para ejecutar el agente.")
        return

    await setup_db()

    try:
        config = {"configurable": {"thread_id": thread_id}}
        from langchain_core.messages import HumanMessage
        initial_state = {"messages": [HumanMessage(content=message)]}

        if args.saltos:
            print(f"\nEjecutando agente '{agent_name}' con saltos (hilo: {thread_id})...\n")
            try:
                async for event in graph.astream(initial_state, config=config, stream_mode="updates"):
                    for node_name, node_state in event.items():
                        print(f"-> Nodo: {node_name}")
                        if "motivo" in node_state:
                            print(f"   Motivo: {node_state['motivo']}")
                        if "respuesta" in node_state:
                            print(f"   Respuesta: {node_state['respuesta']}")
                
                final_state = await graph.aget_state(config)
                if final_state and final_state.values:
                    print("\n--- Estado Final ---")
                    print(f"Ruta: {final_state.values.get('ruta')}")
                    print(f"Motivo: {final_state.values.get('motivo')}")
                    print(f"Respuesta: {final_state.values.get('respuesta')}")
            except Exception as e:
                print(f"\nError en la ejecución: {e}")
        else:
            try:
                result = await graph.ainvoke(initial_state, config=config)
                print(f"\nRespuesta: {result.get('respuesta')}")
            except Exception as e:
                print(f"\nError en la ejecución: {e}")
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())