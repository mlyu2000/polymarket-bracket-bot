import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        rows.append((ya + na, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    priced = len(rows)
    print(f"markets={len(markets)} priced={priced}")
    if rows:
        print(f"true_best_ask_floor_sum={rows[0][0]:.4f}")
    print("top-8 lowest YES+NO best-ask sums (true metric):")
    for t, q, ya, na, liq in rows[:8]:
        flag = " <1.00!" if t < 1.0 else (" <=1.005!" if t <= 1.005 else "")
        print(f"  {t:.4f} | Y@{ya:.3f} N@{na:.3f} | liq={liq} | {q}{flag}")
    print(f"brackets_sum_lt_1.00={sum(1 for r in rows if r[0] < 1.0)}")
    print(f"near_misses_le_1.005={sum(1 for r in rows if r[0] <= 1.005)}")

asyncio.run(supp())
