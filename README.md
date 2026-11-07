# Ecommerce Agent Router

Agente inteligente basado en LangGraph para enrutar consultas de ecommerce a agentes especializados (Preventa, Postventa, Genérica).

## Configuración
1. `cp .env.example .env` y configura tus variables (GOOGLE_API_KEY, TELEGRAM_TOKEN, etc).
2. `python3 -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`

## Uso
### Correr Router local
`python main.py router "tu mensaje"`
Flags: `--saltos` (ver recorrido), `--diagrama` (ver Mermaid).

### Levantar API
`uvicorn api.app:app --reload --port 8000`
Documentación disponible en: `http://localhost:8000/docs`

### Pruebas
`pytest tests/test_router.py`

## Despliegue en Heroku
1. `heroku create`
2. `heroku config:set GOOGLE_API_KEY=tu_key TELEGRAM_SECRET=tu_secreto MODELO=gemini-1.5-flash`
3. `git push heroku main`

## Conexión Telegram
1. Obtén un token en [@BotFather](https://t.me/botfather).
2. Configura `TELEGRAM_TOKEN`, `TELEGRAM_SECRET` y `PUBLIC_URL` en variables de Heroku.
3. Ejecuta los scripts de configuración:
   - `python3 scripts/set_webhook.py`
   - `python3 scripts/webhook_info.py` (para verificar)
4. Pruebas: Escribe al bot y revisa logs con `heroku logs --tail`.
5. Troubleshooting: Verifica que la URL sea HTTPS, el secreto coincida y el token sea correcto.
