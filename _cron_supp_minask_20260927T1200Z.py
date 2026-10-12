import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        y = min(float(a['price']) for a in yb.asks)
        n = min(float(a['price']) for a in nb.asks)
        rows.append((y + n, m.question[:55], y, n, m.liquidity))
    rows.sort()
    print(f"min-ask scan: {len(markets)} markets, {priced} priced, {dt:.1f}s")
    print(f"brackets (sum<1.00): {sum(1 for r in rows if r[0] < 1.0)}")
    print("top 8 lowest sums:")
    for s, q, y, n, liq in rows[:8]:
        print(f"  {s:.3f} | Y@{y:.3f} N@{n:.3f} | liq={liq} | {q}")
    return rows

asyncio.run(scan())
