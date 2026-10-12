import asyncio
from config import Config
import httpx

async def debug():
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"{Config.GAMMA_API_BASE}/markets?limit=1&offset=0&active=true&closed=false&order=volume&ascending=false"
        resp = await client.get(url)
        m = resp.json()[0]
        print('outcomes', m.get('outcomes'))
        print('clobTokenIds', m.get('clobTokenIds'))
        # fetch market details
        mid = m.get('id')
        resp2 = await client.get(f"{Config.GAMMA_API_BASE}/markets/{mid}")
        details = resp2.json()
        print('details outcomes', details.get('outcomes'))
        print('details clobTokenIds', details.get('clobTokenIds'))
        # check condition
        cond_id = details.get('conditionId')
        print('conditionId', cond_id)

asyncio.run(debug())
