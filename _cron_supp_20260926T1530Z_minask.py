import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        t = ya + na
        priced += 1
        rows.append((t, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}")
    if rows:
        print(f"FLOOR: {rows[0][0]:.4f} | {rows[0][1]}")
    print("--- best-ask sums <= 1.005 (true near-miss list) ---")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"count: {len(nm)}")
    for t, q, ya, na, liq in nm[:10]:
        print(f"  {t:.4f} | Y@{ya:.3f} N@{na:.3f} | liq={liq} | {q}")
    print("--- next 5 above 1.005 ---")
    for t, q, ya, na, liq in [r for r in rows if r[0] > 1.005][:5]:
        print(f"  {t:.4f} | Y@{ya:.3f} N@{na:.3f} | {q}")

asyncio.run(scan())
