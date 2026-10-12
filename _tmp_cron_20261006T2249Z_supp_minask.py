import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def floor():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    both_sides = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            both_sides += 1
            ym = min(float(a['price']) for a in yb.asks)
            nm = min(float(a['price']) for a in nb.asks)
            t = ym + nm
            if t <= 1.010:
                rows.append((t, m.question[:55], ym, nm, m.liquidity))
    rows.sort()
    print(f"both_sides_priced={both_sides}")
    print("--- min-ask totals <=1.010 ---")
    for t, q, yp, np_, liq in rows[:10]:
        print(f"  {t:.3f} | yes {yp:.3f} no {np_:.3f} | liq {liq} | {q}")
    if rows:
        print(f"floor={rows[0][0]:.3f}")
    print(f"band<=1.005={sum(1 for r in rows if r[0]<=1.005)}")

asyncio.run(floor())
