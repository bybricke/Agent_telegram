from pydantic import BaseModel, Field
from typing import Literal

class Decision(BaseModel):
    ruta: Literal["preventa", "postventa", "generica"] = Field(description="A qué agente va el mensaje.")
    motivo: str = Field(description="Una frase: por qué esa ruta.")

# Arista condicional desde router según ruta. Tres nodos cascarón, cada uno con su prompt mínimo en prompts.py:
# - agente_preventa: responde "Soy el agente de preventa. Recibí: <mensaje>. Pronto podré ayudarte con productos y compras."
# - agente_postventa: responde "Soy el agente de postventa. Recibí: <mensaje>. Pronto podré ayudarte con tu pedido."
# - respuesta_generica: responde en una frase amable que este chat es para la tienda, sin usar el modelo.

PROMPT_ROUTER = """
Clasifica el mensaje del usuario en:
- preventa: intención de compra, preguntas por productos, precios, tallas, stock, promociones, formas de pago antes de comprar.
- postventa: queja, reclamo, seguimiento de un pedido ya hecho, devolución, cambio, garantía, producto dañado.
- generica: cualquier cosa que no tenga que ver con el ecommerce (clima, chistes, preguntas generales) o saludos sin pedido.

Si duda entre preventa y postventa, la clave es si YA compró: si habla de un pedido existente es postventa.
"""
