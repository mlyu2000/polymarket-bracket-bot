import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    floor = (9.9, None)
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            t = ya + na
            if t < floor[0]:
                floor = (t, m.question[:60])
            if t <= 1.005:
                rows.append((t, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    return len(markets), priced, rows, floor

n, priced, rows, floor = asyncio.run(scan())
print(f"markets={n} priced={priced} true-best-ask near-misses(sum<=1.005)={len(rows)}")
print(f"global floor: sum={floor[0]:.4f} | {floor[1]}")
for t, q, ya, na, liq in rows[:12]:
    print(f"  {t:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
