import asyncio
from polymarket_api import PolymarketAPI

async def scan():
    api = PolymarketAPI()
    # Fetch with liquidity ascending
    import httpx
    from config import Config
    gamma_base = Config.GAMMA_API_BASE
    markets = []
    offset = 0
    for _ in range(10):
        url = f"{gamma_base}/markets?limit=100&offset={offset}&active=true&closed=false&order=liquidity&ascending=true"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            data = resp.json()
        if not data:
            break
        markets.extend(data)
        offset += 100
        print(f"Fetched {len(markets)} total")
    print(f"Total {len(markets)}")
    # Check first 200 with liquidity >0
    count = 0
    for m in markets:
        liq = float(m.get('liquidity',0))
        if liq <= 0 or liq >= 1000:
            continue
        question = m.get('question','')
        # get token ids
        try:
            clob_ids = json.loads(m.get('clobTokenIds','[]'))
        except:
            continue
        if len(clob_ids)!=2:
            continue
        print(f"{liq:.1f} {question[:60]}")
        count+=1
        if count>=20:
            break

import json
asyncio.run(scan())
