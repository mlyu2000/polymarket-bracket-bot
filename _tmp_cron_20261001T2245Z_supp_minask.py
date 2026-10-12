import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    best = []
    npriced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            total = ya + na
            npriced += 1
            best.append((total, m.question[:60], ya, na, m.liquidity))
    best.sort()
    print(f"[min-ask] priced markets: {npriced}")
    print("[min-ask] TRUE BRACKETS (best-ask sum < 1.00):")
    tb = [b for b in best if b[0] < 1.0]
    if not tb:
        print("  none")
    for t, q, ya, na, liq in tb:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print(f"[min-ask] top 5 lowest best-ask sums:")
    for t, q, ya, na, liq in best[:5]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    nm = [b for b in best if 1.0 <= b[0] <= 1.005]
    print(f"[min-ask] near-miss count (1.00<=sum<=1.005): {len(nm)}")

asyncio.run(scan())
