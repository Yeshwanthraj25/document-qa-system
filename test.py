import asyncio
import httpx
from src.settings import settings

async def main():
    url = (f"https://api.cloudflare.com/client/v4/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}"
           f"/ai/run/{settings.LLM_MODEL}")
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}"},
            json={"messages": [
                {"role": "system", "content": "Answer in one sentence."},
                {"role": "user", "content": "What is a vector database?"},
            ]},
        )
    print(response.status_code)
    print(response.json())

asyncio.run(main())