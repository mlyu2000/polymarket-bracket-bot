import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
logging.basicConfig(level=logging.ERROR)
async def go():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    nm = []
    for m,(yb,nb) in zip(markets,books):
        if yb and nb and yb.asks and nb.asks:
            y = min(float(a['price']) for a in yb.asks)
            n = min(float(a['price']) for a in nb.asks)
            t = y+n
            if t <= 1.005: nm.append((t,m.question[:55],y,n,m.liquidity))
    nm.sort()
    print(f"markets={len(markets)} best-ask near-misses(<=1.005)={len(nm)}")
    for t,q,y,n,l in nm[:5]: print(f"  {t:.4f} | Yes@{y:.3f} No@{n:.3f} | {q}")
asyncio.run(go())
