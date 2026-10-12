import asyncio, logging, time
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
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            rows.append((ya + na, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"min-ask sums computed: {len(rows)}")
print("floor (best 8):")
for s, q, ya, na, liq in rows[:8]:
    print(f"  {s:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq:,.0f} | {q}")
brackets = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"BRACKETS sum<1.00: {len(brackets)} | near-misses 1.000-1.005: {len(near)}")
