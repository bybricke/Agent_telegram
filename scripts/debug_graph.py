from src.router.graph import graph
from langchain_core.messages import HumanMessage
import traceback

try:
    result = graph.invoke(
        {'messages': [HumanMessage(content='quiero saber de mis zapatillas')]},
        config={"configurable": {"thread_id": "debug_1"}}
    )
    print("Respuesta:", result.get('respuesta'))
except Exception:
    traceback.print_exc()
