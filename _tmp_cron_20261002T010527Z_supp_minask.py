import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def floor():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        rows.append((ya + na, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"Markets fetched: {len(markets)} | priced (both books have asks): {priced}")
    print("True floor (min-ask Yes+No), 8 closest to 1.00:")
    for total, q, ya, na, liq in rows[:8]:
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    le1 = [r for r in rows if r[0] < 1.0]
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"Min-ask sum<1.00 (true brackets): {len(le1)} | min-ask sum<=1.005 (near-miss): {len(nm)}")
    for total, q, ya, na, liq in nm[:8]:
        print(f"  NEAR {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(floor())
