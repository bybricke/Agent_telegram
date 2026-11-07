import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def get_info():
    url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        print(resp.json())

if __name__ == "__main__":
    import asyncio
    asyncio.run(get_info())
