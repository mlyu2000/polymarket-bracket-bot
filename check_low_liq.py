import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find_low_liq():
    Config.validate()
    api = PolymarketAPI()
    # fetch with liquidity sort ascending to find low liq markets
    markets = []
    # temporarily override sort
    old_sort = Config.SCAN_SORT_BY
    # can't override easily, fetch directly
    from config import Config as C
    url = f"{C.GAMMA_API_BASE}/markets?limit=100&offset=0&active=true&closed=false&order=liquidity&ascending=true"
    import httpx
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        data = resp.json()
    for m in data:
        import json
        outcomes = m.get("outcomes","[]")
        if isinstance(outcomes, str):
            outcomes = json.loads(outcomes)
        if len(outcomes)!=2:
            continue
        clob = m.get("clobTokenIds","[]")
        if isinstance(clob, str):
            clob = json.loads(clob)
        if len(clob)!=2:
            continue
        liq = float(m.get("liquidity",0))
        print(f"liq={liq} | {m.get('question','')[:80]}")
        if liq < 200:
            books = await api.fetch_order_books_batch([(clob[0], clob[1])])
            yes_book, no_book = books[0]
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                print(f"  sum={total:.3f} Yes@{yes_price:.3f} No@{no_price:.3f}")

asyncio.run(find_low_liq())
