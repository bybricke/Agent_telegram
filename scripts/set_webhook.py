import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
SECRET = os.getenv("TELEGRAM_SECRET")

async def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    params = {
        "url": f"{PUBLIC_URL}/telegram",
        "secret_token": SECRET
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, params=params)
        print(resp.json())

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
