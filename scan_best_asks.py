import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI

async def scan_best():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    found = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            total = yp + np_
            if total < 1.01:
                found.append((total, yp, np_, m.liquidity, m.question[:70]))
    found.sort(key=lambda x: x[0])
    print(f"Scanned {len(markets)} in {time.time()-t0:.1f}s, found {len(found)} with total <1.01")
    for f in found[:20]:
        print(f"{f[0]:.4f} yes {f[1]:.3f} no {f[2]:.3f} liq {f[3]} {f[4]}")

asyncio.run(scan_best())
