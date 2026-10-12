import asyncio
from polymarket_api import PolymarketAPI

async def scan():
    api = PolymarketAPI()
    import httpx
    from config import Config
    gamma_base = Config.GAMMA_API_BASE
    # Fetch markets with liquidity between 100 and 5000
    markets = []
    offset = 0
    while len(markets) < 2000:
        url = f"{gamma_base}/markets?limit=100&offset={offset}&active=true&closed=false&order=liquidity&ascending=false"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            data = resp.json()
        if not data:
            break
        markets.extend(data)
        offset += 100
        if offset > 2000:
            break
    print(f"Fetched {len(markets)}")
    hits = []
    for m in markets:
        liq = float(m.get('liquidity',0))
        if not (100 <= liq <= 5000):
            continue
        # get market details
        # parse token ids
        try:
            clob_ids = json.loads(m.get('clobTokenIds','[]'))
        except:
            continue
        if len(clob_ids)!=2:
            continue
        # fetch books
        yb = await api.fetch_order_book(clob_ids[0])
        nb = await api.fetch_order_book(clob_ids[1])
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        y_price = min(float(a['price']) for a in yb.asks)
        n_price = min(float(a['price']) for a in nb.asks)
        total = y_price + n_price
        if total < 1.0:
            hits.append((total, m.get('question',''), y_price, n_price, liq))
            print(f"{total:.4f} {m.get('question','')[:60]} liq {liq}")
        # limit
        if len(hits) >= 10:
            break

import json
asyncio.run(scan())
