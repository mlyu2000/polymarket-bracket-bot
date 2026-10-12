import asyncio
import json
import httpx
from config import Config

async def scan():
    gamma_base = Config.GAMMA_API_BASE
    markets = []
    offset = 0
    for i in range(5):
        url = f"{gamma_base}/markets?limit=100&offset={offset}&active=true&closed=false&order=liquidity&ascending=false"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            data = resp.json()
        if not data:
            break
        markets.extend(data)
        offset += 100
        print(f"Batch {i} fetched {len(data)}")
    print(f"Total {len(markets)}")
    cnt=0
    for m in markets:
        liq = float(m.get('liquidity',0))
        if 100 <= liq <= 5000:
            cnt+=1
            if cnt<=5:
                print(f"{liq:.1f} {m.get('question','')[:60]}")
    print("count",cnt)

asyncio.run(scan())
